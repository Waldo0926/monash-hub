<script setup lang="ts">
const { user, restore, signOut } = useAuth()
const { unread, start, stop } = useNotifications()
const route = useRoute()
const { $t } = useNuxtApp()

onMounted(async () => {
  await restore()
  start()
})
onBeforeUnmount(stop)

const links = computed(() => [
  { to: '/units', label: $t('nav.units') },
  { to: '/courses', label: $t('nav.courses') },
  { to: '/plan', label: $t('nav.plan') },
  { to: '/tree', label: $t('nav.tree') },
  { to: '/guides', label: $t('nav.guides') },
  { to: '/community', label: $t('nav.community') },
  { to: '/mamo', label: $t('nav.mamo') }
])

const query = ref('')
watch(() => route.query.q, q => { query.value = (q as string) || '' }, { immediate: true })

function search(value: string) {
  if (value) navigateTo({ path: '/search', query: { q: value } })
}
</script>

<template>
  <header class="header">
    <div class="container inner">
      <NuxtLink to="/" class="brand">
        <span class="brand-mark">MH</span>
        <span class="brand-text">Monash Hub</span>
      </NuxtLink>

      <nav class="nav" :aria-label="$t('nav.mainLabel')">
        <NuxtLink v-for="link in links" :key="link.to" :to="link.to" class="nav-link">
          {{ link.label }}
        </NuxtLink>
      </nav>

      <div class="header-search">
        <SearchInput v-model="query" :placeholder="$t('search.placeholderShort')" @submit="search" />
      </div>

      <div class="account">
        <LanguageSwitcher />
        <template v-if="user">
          <NuxtLink to="/notifications" class="bell" :aria-label="$t('nav.notifications')">
            <span aria-hidden="true">🔔</span>
            <span v-if="unread > 0" class="dot">{{ unread > 99 ? '99+' : unread }}</span>
          </NuxtLink>
          <NuxtLink to="/community" class="nav-link nickname">{{ user.nickname }}</NuxtLink>
          <button class="btn btn--ghost btn--small" @click="signOut">{{ $t('nav.signOut') }}</button>
        </template>
        <NuxtLink v-else to="/login" class="btn btn--ghost btn--small">{{ $t('nav.signIn') }}</NuxtLink>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 20;
  background: var(--navy);
  color: var(--text-inverse);
}
.inner {
  display: flex;
  align-items: center;
  gap: var(--s4);
  min-height: var(--header-h);
}
.brand { display: flex; align-items: center; gap: var(--s2); color: var(--text-inverse); font-weight: 700; }
.brand:hover { text-decoration: none; }
.brand-mark {
  display: grid;
  place-items: center;
  width: 32px; height: 32px;
  border-radius: var(--radius-sm);
  background: var(--blue);
  font-size: 0.8rem;
  letter-spacing: 0.02em;
}
/* The navigation takes the space between the brand and the search rather than
   sitting in a clump against the brand with a hole after it. `space-evenly`
   rather than `space-between` so the first link does not end up flush against
   the wordmark. */
.nav { display: flex; flex: 1; justify-content: space-evenly; gap: var(--s3); }
.nav-link { color: rgba(255, 255, 255, 0.88); font-size: 0.95rem; white-space: nowrap; }
.nav-link:hover, .router-link-active { color: #fff; }
.header-search { flex: 1; max-width: 420px; }
.account { display: flex; align-items: center; gap: var(--s2); }

.bell {
  position: relative;
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  color: var(--text-inverse);
  font-size: 1rem;
}
.bell:hover { background: rgba(255, 255, 255, 0.12); text-decoration: none; }
.dot {
  position: absolute;
  top: 0;
  right: 0;
  min-width: 18px;
  padding: 0 4px;
  border-radius: var(--radius-pill);
  background: var(--danger);
  color: #fff;
  font-size: 0.65rem;
  font-weight: 700;
  line-height: 18px;
  text-align: center;
}

/* On a phone the header keeps the brand, language and account only; navigation
   moves to the bottom bar and search lives on the page itself. */
@media (max-width: 980px) {
  .nav, .header-search, .nickname { display: none; }
  .account { margin-left: auto; }
}
</style>
