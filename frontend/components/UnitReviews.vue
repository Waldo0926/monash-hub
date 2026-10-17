<script setup lang="ts">
/**
 * Student ratings of a unit: the averages, the reader's own rating, and the
 * reviews under it.
 *
 * This is community content and is labelled that way. Nothing here touches
 * the Handbook sections above it, and reviews are shown in the language they
 * were written in. Authors show as an initial only (see reviews.py).
 *
 * Anyone can rate, signed in or not. A signed-out rating belongs to this
 * browser through useGuestKey, so it can be edited here but not elsewhere.
 *
 * The list is fetched during SSR as a stranger sees it. On the client it is
 * fetched again with the session or the browser key, which is what brings
 * back the reader's own rating and the "you" marks.
 */
import { STAR_PATH } from './StarRating.vue'

const props = defineProps<{ code: string; campus: string }>()
const emit = defineEmits<{ changed: [] }>()

const { $t } = useNuxtApp()
const { user, restore } = useAuth()
const campusName = useCampusName()
const route = useRoute()

const PAGE = 10
type Sort = 'recent' | 'highest' | 'lowest'
const sort = ref<Sort>('recent')

const { data, error } = await useApiFetch<any>(
  () => `/v1/reviews/units/${props.code}?sort=${sort.value}&limit=${PAGE}`,
  { watch: false }
)

/**
 * The first page again, with whatever identifies the reader right now. Not
 * useFetch's refresh: its headers were fixed at setup, before a signed-out
 * reader's first rating made their browser key.
 */
async function reload() {
  try {
    data.value = await apiFetch<any>(
      `/v1/reviews/units/${props.code}?sort=${sort.value}&limit=${PAGE}`,
      { headers: guestHeaders() }
    )
  } catch {
    // Keep what is on screen; the next save or reload tries again.
  }
}
watch(sort, reload)

// Pages after the first, appended by "show more". Reset whenever the first
// page is fetched again, so a new sort or a saved rating starts clean.
const more = ref<any[]>([])
const loadingMore = ref(false)
watch(data, () => { more.value = [] })

const summary = computed(() => data.value?.summary)
const total = computed(() => data.value?.total ?? 0)
const items = computed(() => [...(data.value?.results || []), ...more.value])
const mine = computed(() => data.value?.mine || null)

async function loadMore() {
  loadingMore.value = true
  try {
    const page = await apiFetch<any>(
      `/v1/reviews/units/${props.code}?sort=${sort.value}&limit=${PAGE}&offset=${items.value.length}`,
      { headers: guestHeaders() }
    )
    more.value = [...more.value, ...(page.results || [])]
  } finally {
    loadingMore.value = false
  }
}

onMounted(async () => {
  await restore()
  if (user.value || readGuestKey()) await reload()
})
watch(() => user.value?.id, (now, before) => { if (now !== before) reload() })

// --- summary -------------------------------------------------------------------

// Fewer ratings than this and the average comes with a word of caution. Same
// number the API uses before a unit can be sorted by rating.
const FEW = 3

const QUALITY = ['teaching', 'content', 'assessment'] as const
const SCALE = ['difficulty', 'workload'] as const
const DIMENSIONS = [...QUALITY, ...SCALE] as const
type Dimension = typeof DIMENSIONS[number]

const distribution = computed(() => {
  const d = summary.value?.distribution || {}
  const max = Math.max(1, ...Object.values(d).map(Number))
  return [5, 4, 3, 2, 1].map((star) => ({ star, count: Number(d[star] || 0), width: (Number(d[star] || 0) / max) * 100 }))
})

function dim(name: Dimension) {
  return summary.value?.dimensions?.[name] || { average: null, count: 0 }
}

/** "Moderate", "Hard" and so on for a 1 to 5 average on the difficulty and workload scales. */
function scaleWord(name: 'difficulty' | 'workload', value: number | null): string {
  if (value == null) return ''
  const step = Math.min(5, Math.max(1, Math.round(value)))
  return $t(`reviews.${name}Scale.${step}`)
}

// --- the reader's rating -----------------------------------------------------------

const PERIODS = ['S1', 'S2', 'SA', 'SB', 'W', 'FY'] as const
const PERIOD_KEYS: Record<string, string> = {
  S1: 'plan.period.First semester', S2: 'plan.period.Second semester',
  SA: 'plan.period.Summer semester A', SB: 'plan.period.Summer semester B',
  W: 'plan.period.Winter semester', FY: 'plan.period.Full year'
}
function periodName(short: string | null | undefined): string {
  if (!short) return ''
  const key = PERIOD_KEYS[short]
  return key ? $t(key) : short
}

const CAMPUSES = CAMPUS_CHOICES
const thisYear = new Date().getFullYear()
const YEARS = Array.from({ length: 8 }, (_, i) => thisYear - i)

const blank = () => ({
  overall: null as number | null,
  teaching: null as number | null,
  content: null as number | null,
  assessment: null as number | null,
  difficulty: null as number | null,
  workload: null as number | null,
  body: '',
  taken_year: null as number | null,
  taken_period: '',
  campus: props.campus || ''
})
const form = reactive(blank())
const editing = ref(false)
const saving = ref(false)
const formError = ref('')
const notice = ref('')

function startEditing() {
  Object.assign(form, blank())
  if (mine.value) {
    for (const key of Object.keys(form) as (keyof typeof form)[]) {
      const value = mine.value[key]
      ;(form as any)[key] = value ?? (typeof (form as any)[key] === 'string' ? '' : null)
    }
  }
  formError.value = ''
  notice.value = ''
  editing.value = true
}

/** Picking a star on the short prompt opens the full form with that score in it. */
function quickRate(value: number | null) {
  startEditing()
  form.overall = value
}

async function save() {
  if (!form.overall) {
    formError.value = $t('reviews.needOverall')
    return
  }
  saving.value = true
  formError.value = ''
  try {
    await apiFetch(`/v1/reviews/units/${props.code}`, {
      method: 'PUT',
      headers: guestHeaders(true),
      body: {
        ...form,
        body: form.body.trim() || null,
        taken_period: form.taken_period || null,
        campus: form.campus || null
      }
    })
    editing.value = false
    notice.value = $t('reviews.saved')
    await reload()
    emit('changed')
  } catch (caught) {
    formError.value = apiErrorMessage(caught, $t)
  } finally {
    saving.value = false
  }
}

async function removeMine() {
  if (!window.confirm($t('reviews.deleteConfirm'))) return
  saving.value = true
  try {
    await apiFetch(`/v1/reviews/units/${props.code}`, { method: 'DELETE', headers: guestHeaders() })
    editing.value = false
    notice.value = $t('reviews.deleted')
    await reload()
    emit('changed')
  } catch (caught) {
    formError.value = apiErrorMessage(caught, $t)
  } finally {
    saving.value = false
  }
}

const loginLink = computed(() => `/login?next=${encodeURIComponent(`${route.path}#reviews`)}`)

// --- reporting -------------------------------------------------------------------

const REPORT_REASONS = ['spam', 'abuse', 'privacy', 'advertising', 'misinformation', 'other'] as const
const reporting = ref<number | null>(null)
const reportReason = ref<string>('abuse')
const reportDetail = ref('')
const reportBusy = ref(false)

function report(id: number) {
  reporting.value = id
  reportReason.value = 'abuse'
  reportDetail.value = ''
}

async function sendReport() {
  if (reporting.value == null) return
  reportBusy.value = true
  try {
    await apiFetch('/v1/community/reports', {
      method: 'POST',
      body: {
        target_type: 'review',
        target_id: reporting.value,
        reason: reportReason.value,
        detail: reportDetail.value.trim() || null
      }
    })
    notice.value = $t('community.reported')
  } catch (caught) {
    notice.value = apiErrorMessage(caught, $t)
  } finally {
    reportBusy.value = false
    reporting.value = null
  }
}

// --- display helpers -----------------------------------------------------------------

function when(review: any): string {
  const parts = [
    review.taken_period ? periodName(review.taken_period) : '',
    review.taken_year ? String(review.taken_year) : '',
  ].filter(Boolean).join(' ')
  const where = review.campus ? campusName(review.campus) : ''
  return [parts && $t('reviews.took', { when: parts }), where].filter(Boolean).join(' · ')
}

function date(value: string | null): string {
  return value ? new Date(value).toLocaleDateString() : ''
}

function scoresOf(review: any) {
  return DIMENSIONS.filter((name) => review[name]).map((name) => ({ name, value: review[name] }))
}
</script>

<template>
  <section id="reviews" class="card section reviews">
    <SectionHead icon="ratings" :title="$t('reviews.title')">
      <SourceBadge kind="community" />
    </SectionHead>
    <p class="tiny muted lede">{{ $t('reviews.note') }}</p>

    <ErrorState v-if="error" :error="error" />

    <template v-else-if="data">
      <!-- Averages ------------------------------------------------------------ -->
      <div v-if="summary?.count" class="summary">
        <div class="score">
          <span class="score-number">{{ Number(summary.average).toFixed(1) }}</span>
          <StarRating :value="summary.average" size="lg" />
          <span class="small muted">
            {{ summary.count === 1 ? $t('reviews.countOne') : $t('reviews.count', { count: summary.count }) }}
          </span>
        </div>

        <ol class="bars" :aria-label="$t('reviews.distribution')">
          <li v-for="row in distribution" :key="row.star" class="bar-row">
            <span class="bar-label">{{ row.star }}</span>
            <svg class="bar-star" viewBox="0 0 24 24" aria-hidden="true"><path :d="STAR_PATH" /></svg>
            <span class="bar"><span class="bar-fill" :style="{ width: `${row.width}%` }" /></span>
            <span class="bar-count">{{ row.count }}</span>
          </li>
        </ol>

        <dl class="dims">
          <div v-for="name in QUALITY" :key="name" class="dim">
            <dt>{{ $t(`reviews.dim.${name}`) }}</dt>
            <dd v-if="dim(name).count">
              <StarRating :value="dim(name).average" size="sm" />
              <strong>{{ Number(dim(name).average).toFixed(1) }}</strong>
              <span class="tiny muted">({{ dim(name).count }})</span>
            </dd>
            <dd v-else class="tiny muted">{{ $t('reviews.noAnswers') }}</dd>
          </div>
          <div v-for="name in SCALE" :key="name" class="dim">
            <dt>{{ $t(`reviews.dim.${name}`) }}</dt>
            <dd v-if="dim(name).count">
              <span class="meter" aria-hidden="true">
                <span v-for="i in 5" :key="i" class="meter-step" :class="{ on: i <= Math.round(dim(name).average) }" />
              </span>
              <strong>{{ scaleWord(name, dim(name).average) }}</strong>
              <span class="tiny muted">{{ Number(dim(name).average).toFixed(1) }} ({{ dim(name).count }})</span>
            </dd>
            <dd v-else class="tiny muted">{{ $t('reviews.noAnswers') }}</dd>
          </div>
        </dl>
      </div>
      <p v-if="summary?.count && summary.count < FEW" class="tiny muted few">{{ $t('reviews.few') }}</p>

      <!-- The reader's own rating ------------------------------------------------ -->
      <div class="mine">
        <form v-if="editing" class="form" @submit.prevent="save">
          <h3 class="form-title">{{ mine ? $t('reviews.editTitle') : $t('reviews.rateTitle', { code }) }}</h3>
          <div class="form-row form-row--overall">
            <span class="form-label">{{ $t('reviews.overall') }}</span>
            <StarInput v-model="form.overall" name="overall" :label="$t('reviews.overall')" size="lg" />
          </div>
          <div class="form-dims">
            <div v-for="name in DIMENSIONS" :key="name" class="form-row">
              <span class="form-label">
                {{ $t(`reviews.dim.${name}`) }}
                <span class="tiny muted">{{ $t(`reviews.hint.${name}`) }}</span>
              </span>
              <StarInput v-model="form[name]" :name="name" :label="$t(`reviews.dim.${name}`)" optional />
            </div>
          </div>
          <label class="form-label" for="review-body">{{ $t('reviews.body') }}</label>
          <textarea
            id="review-body"
            v-model="form.body"
            class="field"
            rows="5"
            maxlength="3000"
            :placeholder="$t('reviews.bodyPlaceholder')"
          />
          <div class="form-when">
            <label>
              <span class="form-label">{{ $t('reviews.takenYear') }}</span>
              <select v-model="form.taken_year" class="field">
                <option :value="null">{{ $t('reviews.notSaying') }}</option>
                <option v-for="y in YEARS" :key="y" :value="y">{{ y }}</option>
              </select>
            </label>
            <label>
              <span class="form-label">{{ $t('reviews.takenPeriod') }}</span>
              <select v-model="form.taken_period" class="field">
                <option value="">{{ $t('reviews.notSaying') }}</option>
                <option v-for="p in PERIODS" :key="p" :value="p">{{ periodName(p) }}</option>
              </select>
            </label>
            <label>
              <span class="form-label">{{ $t('reviews.campus') }}</span>
              <select v-model="form.campus" class="field">
                <option value="">{{ $t('reviews.notSaying') }}</option>
                <option v-for="c in CAMPUSES" :key="c" :value="c">{{ campusName(c) }}</option>
              </select>
            </label>
          </div>
          <p v-if="user" class="tiny muted">{{ $t('reviews.privacy') }}</p>
          <p v-else class="tiny muted">
            {{ $t('reviews.privacyGuest') }} {{ $t('reviews.guestNote') }}
            <NuxtLink :to="loginLink">{{ $t('reviews.guestSignIn') }}</NuxtLink>
          </p>
          <p v-if="formError" class="small bad-text" role="alert">{{ formError }}</p>
          <div class="form-actions">
            <button class="btn btn--small" type="submit" :disabled="saving">
              {{ mine ? $t('reviews.update') : $t('reviews.submit') }}
            </button>
            <button class="btn btn--ghost btn--small" type="button" :disabled="saving" @click="editing = false">
              {{ $t('community.cancel') }}
            </button>
          </div>
        </form>

        <div v-else-if="mine" class="own">
          <div class="own-head">
            <span class="small"><strong>{{ $t('reviews.yours') }}</strong></span>
            <StarRating :value="mine.overall" size="sm" />
            <span class="small">{{ mine.overall }}/5</span>
            <span class="tiny muted">{{ date(mine.updated_at) }}</span>
          </div>
          <p v-if="mine.hidden" class="tiny warn">{{ $t('reviews.hiddenNote') }}</p>
          <p v-if="mine.body" class="small pre own-body">{{ mine.body }}</p>
          <div class="own-actions">
            <button class="link-btn small" type="button" @click="startEditing">{{ $t('reviews.edit') }}</button>
            <button class="link-btn small danger" type="button" :disabled="saving" @click="removeMine">{{ $t('reviews.delete') }}</button>
          </div>
        </div>

        <div v-else class="prompt">
          <span class="small">{{ summary?.count ? $t('reviews.tookIt', { code }) : $t('reviews.beFirst', { code }) }}</span>
          <StarInput :model-value="null" name="quick" :label="$t('reviews.overall')" @update:model-value="quickRate" />
        </div>

        <p v-if="notice" class="small ok-text" role="status">{{ notice }}</p>
      </div>

      <!-- Reviews --------------------------------------------------------------- -->
      <template v-if="total">
        <div class="list-head">
          <h3 class="side-label">{{ $t('reviews.listTitle', { count: total }) }}</h3>
          <label class="sort tiny">
            <span class="muted">{{ $t('reviews.sortBy') }}</span>
            <select v-model="sort" class="field field--small">
              <option value="recent">{{ $t('reviews.sort.recent') }}</option>
              <option value="highest">{{ $t('reviews.sort.highest') }}</option>
              <option value="lowest">{{ $t('reviews.sort.lowest') }}</option>
            </select>
          </label>
        </div>
        <ul class="list">
          <li v-for="review in items" :key="review.id" class="review">
            <span class="avatar" aria-hidden="true">{{ review.author ? review.author.replace('.', '') : '?' }}</span>
            <div class="review-main">
              <div class="review-head">
                <StarRating :value="review.overall" size="sm" />
                <span class="small"><strong>{{ review.overall }}/5</strong></span>
                <span v-if="review.is_mine" class="you tiny">{{ $t('reviews.you') }}</span>
                <span class="tiny muted">
                  {{ review.author ? $t('reviews.by', { author: review.author }) : $t('reviews.guest') }} · {{ date(review.updated_at) }}
                </span>
              </div>
              <p v-if="when(review)" class="tiny muted when">{{ when(review) }}</p>
              <p v-if="review.body" class="small pre body">{{ review.body }}</p>
              <p v-if="scoresOf(review).length" class="scores">
                <span v-for="s in scoresOf(review)" :key="s.name" class="score-chip tiny">
                  {{ $t(`reviews.dim.${s.name}`) }} {{ s.value }}/5
                </span>
              </p>
              <button v-if="!review.is_mine" class="link-btn tiny muted" type="button" @click="report(review.id)">
                {{ $t('community.report') }}
              </button>
            </div>
          </li>
        </ul>
        <button v-if="items.length < total" class="btn btn--ghost btn--small more" type="button" :disabled="loadingMore" @click="loadMore">
          {{ $t('reviews.more') }}
        </button>
      </template>
    </template>

    <div v-if="reporting != null" class="overlay" role="dialog" aria-modal="true"
         :aria-label="$t('community.reportTitle')" @click.self="reporting = null">
      <form class="card dialog" @submit.prevent="sendReport">
        <h2>{{ $t('community.reportTitle') }}</h2>
        <fieldset class="reasons">
          <legend class="tiny muted">{{ $t('community.reportWhy') }}</legend>
          <label v-for="reason in REPORT_REASONS" :key="reason" class="reason">
            <input v-model="reportReason" type="radio" name="review-reason" :value="reason">
            <span>{{ $t(`community.reportReason.${reason}`) }}</span>
          </label>
        </fieldset>
        <label for="review-report-detail" class="tiny muted">{{ $t('community.reportDetail') }}</label>
        <textarea id="review-report-detail" v-model="reportDetail" class="field" rows="3" maxlength="2000" />
        <div class="dialog-actions">
          <button class="btn btn--small" type="submit" :disabled="reportBusy">{{ $t('community.reportSend') }}</button>
          <button class="btn btn--ghost btn--small" type="button" @click="reporting = null">
            {{ $t('community.cancel') }}
          </button>
        </div>
      </form>
    </div>
  </section>
</template>

<style scoped>
.reviews { padding: var(--s5); }
.lede { margin: calc(-1 * var(--s2)) 0 var(--s4); }
.pre { white-space: pre-line; overflow-wrap: anywhere; }

/* Averages ------------------------------------------------------------------- */
.summary {
  display: grid; grid-template-columns: auto minmax(0, 1fr) minmax(0, 1.2fr); gap: var(--s5);
  align-items: center; padding: var(--s4); border-radius: var(--radius-sm); background: var(--surface-2);
}
.score { display: grid; justify-items: center; gap: var(--s1); padding: 0 var(--s3); }
.score-number { font-size: 2.6rem; font-weight: 700; line-height: 1; letter-spacing: -0.02em; font-variant-numeric: tabular-nums; }
.bars { list-style: none; margin: 0; padding: 0; display: grid; gap: 4px; }
.bar-row { display: grid; grid-template-columns: 10px 12px minmax(0, 1fr) 24px; gap: 6px; align-items: center; font-size: 0.8rem; }
.bar-label { text-align: right; color: var(--muted); font-variant-numeric: tabular-nums; }
.bar-star { width: 12px; height: 12px; fill: var(--star); }
.bar { height: 8px; border-radius: var(--radius-pill); background: var(--border); overflow: hidden; }
.bar-fill { display: block; height: 100%; border-radius: inherit; background: var(--star); }
.bar-count { color: var(--muted); font-variant-numeric: tabular-nums; }
.dims { display: grid; gap: var(--s2); margin: 0; }
.dim { display: flex; justify-content: space-between; align-items: center; gap: var(--s3); font-size: 0.88rem; }
.dim dt { color: var(--muted); }
.dim dd { margin: 0; display: flex; align-items: center; gap: 6px; }
.meter { display: inline-flex; gap: 2px; }
.meter-step { width: 12px; height: 8px; border-radius: 2px; background: var(--border); }
.meter-step.on { background: var(--navy); }
.few { margin: var(--s2) 0 0; }

/* The reader's own rating ----------------------------------------------------- */
.mine {
  display: grid; gap: var(--s3); justify-items: start;
  margin: var(--s4) 0; padding: var(--s4); border: 1px dashed var(--border-strong); border-radius: var(--radius-sm);
}
.mine > p { margin: 0; }
.prompt { display: flex; flex-wrap: wrap; align-items: center; gap: var(--s3); }
.form { display: grid; gap: var(--s3); width: 100%; }
.form-title { margin: 0; font-size: 1.02rem; }
.form-row { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: var(--s2) var(--s4); }
.form-row--overall { justify-content: flex-start; }
.form-dims { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--s2) var(--s5); }
.form-label { display: grid; font-size: 0.88rem; font-weight: 600; }
.form-label .tiny { font-weight: 400; }
.form-when { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--s3); }
.form-when label { display: grid; gap: var(--s1); }
.field {
  width: 100%; padding: var(--s2) var(--s3); border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm); font: inherit; background: var(--surface); color: var(--text);
}
textarea.field { min-height: 110px; resize: vertical; }
.field--small { width: auto; padding: 4px var(--s2); font-size: 0.85rem; }
.form-actions, .own-actions { display: flex; gap: var(--s3); }
.own { display: grid; gap: var(--s2); width: 100%; }
.own-head { display: flex; flex-wrap: wrap; align-items: center; gap: var(--s2); }
.own-body { margin: 0; }
.warn { margin: 0; padding: var(--s2) var(--s3); border-radius: var(--radius-sm); background: var(--warning-bg); color: var(--warning); }
.link-btn {
  padding: 0; border: 0; background: none; color: var(--brand); font-family: inherit; cursor: pointer;
  text-decoration: underline; text-underline-offset: 2px;
}
.link-btn.small { font-size: 0.88rem; }
.link-btn.tiny { font-size: 0.78rem; }
.link-btn.danger { color: var(--danger); }
.link-btn.muted { color: var(--muted-2); text-decoration: none; }
.link-btn.muted:hover { color: var(--danger); text-decoration: underline; }
.ok-text { color: var(--success); }
.bad-text { color: var(--danger); margin: 0; }

/* Reviews ------------------------------------------------------------------- */
.list-head { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: var(--s3); margin-top: var(--s4); }
.side-label {
  margin: 0; font-family: var(--font); font-size: 0.75rem; font-weight: 600; letter-spacing: 0.06em;
  text-transform: uppercase; color: var(--muted);
}
.sort { display: flex; align-items: center; gap: var(--s2); }
.list { list-style: none; margin: var(--s2) 0 0; padding: 0; }
.review { display: grid; grid-template-columns: 36px minmax(0, 1fr); gap: var(--s3); padding: var(--s4) 0; border-bottom: 1px solid var(--border); }
.review:last-child { border-bottom: 0; }
.avatar {
  width: 36px; height: 36px; display: grid; place-items: center; border-radius: 50%;
  background: var(--badge-community-bg); color: var(--badge-community); font-weight: 700; font-size: 0.9rem;
}
.review-main { display: grid; gap: var(--s1); justify-items: start; min-width: 0; }
.review-head { display: flex; flex-wrap: wrap; align-items: center; gap: var(--s2); }
.you { padding: 0 8px; border-radius: var(--radius-pill); background: var(--blue-50); color: var(--brand); font-weight: 600; }
.when, .body { margin: 0; }
.body { max-width: var(--measure); }
.scores { display: flex; flex-wrap: wrap; gap: var(--s1); margin: var(--s1) 0 0; }
.score-chip { padding: 1px 8px; border-radius: var(--radius-pill); background: var(--surface-2); }
.more { margin-top: var(--s3); }

/* Report dialog, as on a community post --------------------------------------- */
.overlay {
  position: fixed; inset: 0; z-index: 50; display: grid; place-items: center;
  padding: var(--s4); background: rgb(0 0 0 / 0.45);
}
.dialog { width: min(440px, 100%); padding: var(--s5); display: grid; gap: var(--s2); }
.dialog h2 { margin: 0 0 var(--s2); font-size: 1.1rem; }
.reasons { border: 0; padding: 0; margin: 0; display: grid; gap: var(--s1); }
.reason { display: flex; gap: var(--s2); align-items: center; min-height: 32px; }
.dialog-actions { display: flex; gap: var(--s2); margin-top: var(--s2); }

@media (max-width: 900px) {
  .summary { grid-template-columns: auto minmax(0, 1fr); }
  .dims { grid-column: 1 / -1; }
}
@media (max-width: 600px) {
  .reviews { padding: var(--s4); }
  .summary { grid-template-columns: 1fr; gap: var(--s4); }
  .score { grid-template-columns: auto auto; justify-content: start; align-items: center; column-gap: var(--s3); padding: 0; }
  .score-number { grid-row: span 2; }
  .form-dims, .form-when { grid-template-columns: 1fr; }
}
</style>
