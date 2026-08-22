<script setup lang="ts">
const { user, restore, signOut } = useAuth()
const route = useRoute()
onMounted(restore)

const links = [
  { to: '/units', label: 'Units' },
  { to: '/guides', label: 'Guides' },
  { to: '/community', label: 'Community' },
  { to: '/exchange', label: 'Exchange' }
]

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

      <nav class="nav" aria-label="Main">
        <NuxtLink v-for="link in links" :key="link.to" :to="link.to" class="nav-link">
          {{ link.label }}
        </NuxtLink>
      </nav>

      <div class="header-search">
        <SearchInput v-model="query" placeholder="Search…" @submit="search" />
      </div>

      <div class="account">
        <template v-if="user">
          <NuxtLink to="/community" class="nav-link">{{ user.nickname }}</NuxtLink>
          <button class="btn btn--ghost btn--small" @click="signOut">Sign out</button>
        </template>
        <NuxtLink v-else to="/login" class="btn btn--ghost btn--small">Sign in</NuxtLink>
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
.nav { display: flex; gap: var(--s4); }
.nav-link { color: rgba(255, 255, 255, 0.88); font-size: 0.95rem; }
.nav-link:hover, .router-link-active { color: #fff; }
.header-search { flex: 1; max-width: 420px; margin-left: auto; }
.account { display: flex; align-items: center; gap: var(--s2); }

/* On a phone the header keeps the brand and the sign-in only; navigation moves
   to the bottom bar and search lives on the page itself. */
@media (max-width: 900px) {
  .nav, .header-search { display: none; }
  .account { margin-left: auto; }
}
</style>
