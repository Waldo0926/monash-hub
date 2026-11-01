<script setup lang="ts">
/**
 * Unified search.
 *
 * Results stay grouped by source instead of being merged into one ranked list:
 * merging them would put a student's opinion next to a Handbook field with no
 * visible difference, which is precisely the failure this product exists to
 * avoid.
 */
const route = useRoute()
const { $t } = useNuxtApp()
const query = ref((route.query.q as string) || '')
const { locale } = useLocale()

const { data, pending, error, refresh } = await useLocalisedApiFetch<any>(
  () => `/v1/search?q=${encodeURIComponent((route.query.q as string) || '')}`,
  { watch: [() => route.query.q] }
)

// The zero-AI router runs alongside search, so one submission produces both an
// answer and a result list.
//
// This resolves during SSR rather than on mount. Filling it in afterwards left
// the server and client markup disagreeing, and the hydration mismatch that
// followed threw out the result groups underneath it.
const { data: answer } = await useAsyncData<any>(
  'ask-answer',
  () => {
    const q = ((route.query.q as string) || '').trim()
    if (!q) return Promise.resolve(null)
    // The answer carries the unit's name, so it needs the reader's language
    // like every other call - requested_locale reads a query parameter.
    return $fetch<any>(apiUrl(`/v1/ask?locale=${locale.value}`), {
      method: 'POST',
      body: { query: q }
    }).catch(() => null)
  },
  // A locale switch must re-run the answer request too. The grouped search
  // results already do this through useLocalisedApiFetch; without this watch,
  // the answer card kept the previous language until the query changed.
  { watch: [() => route.query.q, locale] }
)

watch(() => route.query.q, q => { query.value = (q as string) || '' }, { immediate: true })

function search(value: string) {
  navigateTo({ path: '/search', query: value ? { q: value } : {} })
}

const hasResults = computed(() => (data.value?.groups || []).some((g: any) => g.results?.length))
const missingCategory = ref('units')
const feedbackStatus = ref<'idle' | 'sending' | 'sent' | 'failed'>('idle')
watch(() => route.query.q, () => { feedbackStatus.value = 'idle' })

/**
 * Opt-in feedback: never send free-text queries to the feedback endpoint.
 * Only a well-formed unit/degree code or a controlled topic category goes.
 */
async function sendMissingFeedback() {
  if (!query.value || feedbackStatus.value !== 'idle') return
  feedbackStatus.value = 'sending'
  const term = String(route.query.q || '').trim().toUpperCase()
  const code = /^(?:[A-Z]{3}\\d{4}|[A-Z]\\d{4})$/.test(term) ? term : null
  try {
    await apiFetch('/v1/search/missing', {
      method: 'POST',
      body: { category: missingCategory.value, code }
    })
    feedbackStatus.value = 'sent'
  } catch {
    feedbackStatus.value = 'failed'
  }
}


/**
 * Whether to draw the answer card above the results.
 *
 * The router answers every query, and when it has nothing it answers "Nothing
 * in the Handbook or the indexed official pages answers this". That is fine on
 * its own and wrong sitting above five Handbook units, which is what a reader
 * searching "2102" instead of "FIT2102" got: a failure notice on a page full of
 * results. The router looks up FAQs and official pages, not units, so it does
 * not know what the list below found.
 *
 * The card is worth drawing when it says something - a unit, an FAQ, matching
 * official pages. When its whole content is "there is nothing", the result list
 * has already answered better, and where there is genuinely nothing the empty
 * state below says so once, with somewhere to go next.
 */
const showAnswer = computed(
  () => !!answer.value && !!query.value && answer.value.answer_type !== 'community_fallback'
)

useSeoMeta({
  title: () => (query.value ? query.value : $t('search.title')),
  robots: 'noindex'
})
</script>

<template>
  <div class="container">
    <SearchInput v-model="query" big @submit="search" />

    <ErrorState v-if="error" :error="error" :on-retry="refresh" class="mt" />

    <template v-else>
      <div v-if="showAnswer" class="mt">
        <AnswerBlocks :answer="answer" />
      </div>

      <Skeleton v-if="pending" :lines="6" class="mt" />

      <div v-else-if="query && !hasResults" class="mt">
        <EmptyState :title="$t('search.nothing')" :hint="$t('search.nothingHint')">
          <NuxtLink to="/community" class="btn">{{ $t('units.askCommunity') }}</NuxtLink>
        </EmptyState>
        <div class="missing-feedback card">
          <p><strong>{{ locale === 'zh' ? '找不到需要的资料？' : 'Missing something?' }}</strong></p>
          <p class="small muted">{{ locale === 'zh' ? '可以匿名反馈缺少哪类资料。我们只记录分类和有效课程代码，不保存你的完整搜索内容或账号信息' : 'Optionally flag the missing topic. Only a category or a valid unit code is counted, never your full search, account or identifying details.' }}</p>
          <label class="missing-label">
            {{ locale === 'zh' ? '资料类别' : 'Topic' }}
            <select v-model="missingCategory" class="field" :disabled="feedbackStatus !== 'idle'">
              <option value="units">{{ locale === 'zh' ? '课程' : 'Units' }}</option>
              <option value="degrees">{{ locale === 'zh' ? '学位' : 'Degrees' }}</option>
              <option value="dates">{{ locale === 'zh' ? '重要日期' : 'Academic dates' }}</option>
              <option value="fees">{{ locale === 'zh' ? '学费' : 'Tuition fees' }}</option>
              <option value="policies">{{ locale === 'zh' ? '学校政策' : 'University policies' }}</option>
              <option value="other">{{ locale === 'zh' ? '其他' : 'Other' }}</option>
            </select>
          </label>
          <button type="button" class="btn btn--ghost" :disabled="feedbackStatus !== 'idle'" @click="sendMissingFeedback">
            {{ feedbackStatus === 'sending' ? (locale === 'zh' ? '正在发送…' : 'Sending…') : (locale === 'zh' ? '反馈缺失资料' : 'Send missing-topic feedback') }}
          </button>
          <p v-if="feedbackStatus === 'sent'" role="status" class="small">{{ locale === 'zh' ? '已收到反馈，谢谢' : 'Feedback received. Thanks.' }}</p>
          <p v-if="feedbackStatus === 'failed'" role="alert" class="small">{{ locale === 'zh' ? '发送失败，请稍后再试' : 'Could not send feedback. Please try again later.' }}</p>
        </div>
      </div>

      <div v-else-if="query" class="groups mt">
        <section v-for="group in data.groups" :key="group.kind" class="group">
          <div v-if="group.results.length" class="section-head">
            <h2>
              {{ $t(`search.group${group.kind.charAt(0).toUpperCase()}${group.kind.slice(1)}`) }}
              <SourceBadge :kind="group.badge" />
            </h2>
            <span class="tiny muted">
              {{ group.total === 1 ? $t('search.resultsOne') : $t('search.results', { count: group.total }) }}
            </span>
          </div>

          <div v-if="group.kind === 'handbook' && group.results.length" class="grid">
            <UnitCard v-for="unit in group.results" :key="unit.unit_code" :unit="unit" />
          </div>
          <div v-else-if="group.kind === 'degrees' && group.results.length" class="degree-list">
            <CourseCard v-for="course in group.results" :key="course.course_code" :course="course" />
          </div>
          <div v-else-if="group.kind === 'official' && group.results.length" class="grid">
            <GuideCard v-for="page in group.results" :key="page.slug" :page="page" />
          </div>
          <div v-else-if="group.kind === 'faq' && group.results.length" class="grid">
            <article v-for="faq in group.results" :key="faq.slug" class="faq card">
              <div class="faq-top">
                <SourceBadge kind="official" />
                <CampusNotice :applies-to="faq.applies_to" compact />
              </div>
              <h3>{{ faq.question }}</h3>
              <TranslationNotice v-if="faq.translation" :translation="faq.translation" :source-url="faq.official_url" />
              <p class="small">{{ faq.answer }}</p>
              <a
                v-if="faq.official_url"
                :href="faq.official_url"
                rel="noopener external"
                target="_blank"
                class="small"
              >{{ $t('search.openOfficial') }}</a>
              <LastChecked :value="faq.last_checked" />
            </article>
          </div>
          <div v-else-if="group.kind === 'community' && group.results.length" class="grid">
            <PostCard v-for="post in group.results" :key="post.id" :post="post" />
          </div>
        </section>
      </div>

      <EmptyState v-else class="mt" :title="$t('search.title')" :hint="$t('search.hint')" />
    </template>
  </div>
</template>

<style scoped>
.mt { margin-top: var(--s5); }
.missing-feedback { padding: var(--s4); margin-top: var(--s3); max-width: 680px; }
.missing-label { display: grid; gap: var(--s2); margin: var(--s3) 0; max-width: 240px; }
.groups { display: grid; gap: var(--s6); }
.section-head { display: flex; align-items: baseline; justify-content: space-between; gap: var(--s3); }
.section-head h2 { display: flex; align-items: center; gap: var(--s3); font-size: 1.1rem; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: var(--s3); }
.degree-list { display: grid; gap: var(--s2); }
.faq { padding: var(--s4); }
.faq-top { display: flex; align-items: center; gap: var(--s2); flex-wrap: wrap; }
.faq h3 { margin: var(--s2) 0; font-size: 1rem; }
</style>
