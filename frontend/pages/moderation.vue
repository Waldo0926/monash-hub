<script setup lang="ts">
/**
 * The report queue.
 *
 * Reports could be filed but only read through the raw API, and never closed,
 * so nobody could actually moderate the forum from the site. This lists what
 * was reported with enough of it to judge, and closes a report either way:
 * hide the content, or dismiss the report.
 *
 * Moderators only - the API refuses everyone else, and this page says so
 * rather than showing an empty queue.
 */
const { $t } = useNuxtApp()
const { user, restore } = useAuth()

const status = ref<'open' | 'resolved' | 'dismissed'>('open')
const queue = ref<any>(null)
const loading = ref(true)
const busy = ref<number | null>(null)
const error = ref('')

async function load() {
  if (!user.value?.is_admin) {
    loading.value = false
    return
  }
  loading.value = true
  error.value = ''
  try {
    queue.value = await apiFetch<any>(`/v1/community/reports?status=${status.value}`)
  } catch (caught: any) {
    error.value = apiErrorMessage(caught, $t)
  } finally {
    loading.value = false
  }
}

async function resolve(id: number, action: 'hide' | 'dismiss') {
  if (action === 'hide' && !window.confirm($t('moderation.hideConfirm'))) return
  busy.value = id
  try {
    await apiFetch(`/v1/community/reports/${id}/resolve?action=${action}`, { method: 'POST' })
    await load()
  } catch (caught: any) {
    error.value = apiErrorMessage(caught, $t)
  } finally {
    busy.value = null
  }
}

onMounted(async () => {
  await restore()
  await load()
})
// The header restores the session too, and may still be waiting on it when
// this page mounts - so load again once the account is known.
watch(user, load)
watch(status, load)

useSeoMeta({ title: () => `${$t('moderation.title')} — Monash Hub`, robots: 'noindex' })
</script>

<template>
  <div class="container narrow page">
    <h1>{{ $t('moderation.title') }}</h1>

    <div v-if="loading" class="card section"><Skeleton :lines="4" /></div>

    <EmptyState v-else-if="!user?.is_admin" :title="$t('moderation.onlyModerators')" :hint="$t('moderation.onlyHint')" />

    <template v-else>
      <div class="tabs">
        <button v-for="key in (['open', 'resolved', 'dismissed'] as const)" :key="key"
                class="tab" :class="{ 'tab--on': status === key }" type="button" @click="status = key">
          {{ $t(`moderation.status.${key}`) }}
        </button>
      </div>

      <p v-if="error" class="small bad-text" role="alert">{{ error }}</p>

      <EmptyState v-if="!queue?.results?.length" :title="$t('moderation.empty')" :hint="$t('moderation.emptyHint')" />

      <article v-for="item in queue?.results || []" :key="item.id" class="card section report">
        <p class="tiny muted meta">
          <span class="reason">{{ $t(`community.reportReason.${item.reason}`) }}</span>
          · {{ item.target_type === 'post' ? $t('moderation.post') : $t('moderation.reply') }}
          · {{ new Date(item.created_at).toLocaleString() }}
        </p>
        <p v-if="item.detail" class="small detail">“{{ item.detail }}”</p>

        <div v-if="item.target" class="target">
          <NuxtLink :to="`/community/post/${item.target.post_id}`" class="small">
            {{ item.target.title || $t('moderation.untitled') }}
          </NuxtLink>
          <p class="small pre excerpt">{{ item.target.excerpt }}</p>
          <p class="tiny muted">
            {{ item.target.anonymous ? $t('community.anonymous') : item.target.author }}
            <span v-if="item.target.hidden"> · {{ $t('moderation.alreadyHidden') }}</span>
            <span v-if="item.target.deleted"> · {{ $t('moderation.deletedByAuthor') }}</span>
          </p>
        </div>
        <p v-else class="small muted">{{ $t('moderation.targetGone') }}</p>

        <div v-if="status === 'open'" class="actions">
          <button class="btn btn--small btn--danger" type="button" :disabled="busy === item.id"
                  @click="resolve(item.id, 'hide')">
            {{ $t('moderation.hide') }}
          </button>
          <button class="btn btn--ghost btn--small" type="button" :disabled="busy === item.id"
                  @click="resolve(item.id, 'dismiss')">
            {{ $t('moderation.dismiss') }}
          </button>
        </div>
      </article>
    </template>
  </div>
</template>

<style scoped>
.narrow { max-width: 860px; }
.page { display: grid; gap: var(--s4); padding: var(--s5) var(--s4) var(--s7); }
.section { padding: var(--s5); }
.tabs { display: flex; flex-wrap: wrap; gap: var(--s2); }
.tab {
  padding: 6px 14px; border: 1px solid var(--border-strong); border-radius: var(--radius-pill);
  background: var(--surface); color: var(--text); font: inherit; font-size: 0.85rem; cursor: pointer;
}
.tab--on { background: var(--blue); border-color: var(--blue); color: #fff; }
.report { display: grid; gap: var(--s2); }
.meta, .detail { margin: 0; }
.reason { font-weight: 600; color: var(--danger); }
.target { padding: var(--s3); border-radius: var(--radius-sm); background: var(--surface-2); }
.target p { margin: var(--s1) 0 0; }
.excerpt { white-space: pre-line; overflow-wrap: anywhere; }
.actions { display: flex; flex-wrap: wrap; gap: var(--s2); }
.btn--danger { background: var(--danger); border-color: var(--danger); color: #fff; }
.bad-text { color: var(--danger); }
</style>
