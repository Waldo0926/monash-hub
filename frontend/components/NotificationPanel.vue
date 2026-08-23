<script setup lang="ts">
/**
 * The notification list, on the home page and on /notifications.
 *
 * Client-only by design: it is per-account, so rendering it on the server would
 * mean a page that cannot be cached and a hydration mismatch for anyone whose
 * token the server never saw. It renders nothing at all for a signed-out
 * reader, which is also the honest thing for it to do.
 */
const props = withDefaults(defineProps<{ limit?: number; full?: boolean }>(), {
  limit: 5,
  full: false
})

const { $t } = useNuxtApp()
const { user, restore } = useAuth()
const { unread, refresh: refreshBadge } = useNotifications()

const items = ref<any[]>([])
const loading = ref(false)
const loaded = ref(false)

async function load() {
  if (!user.value) return
  loading.value = true
  try {
    const result = await apiFetch<any>(`/v1/notifications?limit=${props.limit}`)
    items.value = result.results
    unread.value = result.unread
  } finally {
    loading.value = false
    loaded.value = true
  }
}

async function markAllRead() {
  await apiFetch('/v1/notifications/read', { method: 'POST', body: {} })
  items.value = items.value.map(item => ({ ...item, is_read: true }))
  await refreshBadge()
}

async function open(item: any) {
  if (!item.is_read) {
    await apiFetch('/v1/notifications/read', { method: 'POST', body: { ids: [item.id] } })
    await refreshBadge()
  }
  navigateTo(`/community/post/${item.post_id}`)
}

onMounted(async () => {
  await restore()
  await load()
})
watch(user, load)

function messageFor(item: any) {
  const key = item.kind === 'accepted' ? 'notifications.accepted' : 'notifications.answered'
  return $t(key, { actor: item.actor || '—' })
}
</script>

<template>
  <section v-if="user && (full || items.length || loading)" class="panel card">
    <div class="head">
      <h2>
        {{ $t('notifications.title') }}
        <span v-if="unread > 0" class="count tiny">{{ $t('notifications.unread', { count: unread }) }}</span>
      </h2>
      <button v-if="unread > 0" class="btn btn--ghost btn--small" @click="markAllRead">
        {{ $t('notifications.markAllRead') }}
      </button>
    </div>

    <Skeleton v-if="loading && !loaded" :lines="3" />

    <ul v-else-if="items.length" class="list">
      <li v-for="item in items" :key="item.id" :class="{ unread: !item.is_read }">
        <button class="item" @click="open(item)">
          <span class="message">{{ messageFor(item) }}</span>
          <span class="title small">{{ item.post_title }}</span>
          <span v-if="item.excerpt" class="excerpt tiny muted">{{ item.excerpt }}</span>
        </button>
      </li>
    </ul>

    <p v-else class="small muted empty">
      {{ $t('notifications.empty') }} — {{ $t('notifications.emptyHint') }}
    </p>

    <NuxtLink v-if="!full && items.length" to="/notifications" class="small more">
      {{ $t('notifications.viewAll') }}
    </NuxtLink>
  </section>
</template>

<style scoped>
.panel { padding: var(--s5); }
.head { display: flex; align-items: center; justify-content: space-between; gap: var(--s3); }
.head h2 { display: flex; align-items: center; gap: var(--s3); margin-bottom: var(--s4); font-size: 1.05rem; }
.count { color: var(--blue-700); font-weight: 600; }
.list { list-style: none; margin: 0; padding: 0; }
.list li + li { border-top: 1px solid var(--border); }
.item {
  display: grid;
  gap: 2px;
  width: 100%;
  min-height: 44px;
  padding: var(--s3) var(--s3) var(--s3) var(--s4);
  border: 0;
  border-left: 3px solid transparent;
  background: none;
  font: inherit;
  text-align: left;
  cursor: pointer;
}
.item:hover { background: var(--surface-2); }
.unread .item { border-left-color: var(--blue); }
.unread .message { font-weight: 600; }
.title { color: var(--text); }
.excerpt { display: block; }
.empty { margin: 0; }
.more { display: inline-block; margin-top: var(--s3); }
</style>
