<script setup lang="ts">
// Bottom navigation on phones: four destinations, thumb-reachable, each a
// 44px+ target. The desktop header is not squeezed onto a small screen.
const items = [
  { to: '/', label: 'Home', icon: '⌂' },
  { to: '/search', label: 'Search', icon: '⌕' },
  { to: '/community', label: 'Community', icon: '☰' },
  { to: '/login', label: 'Account', icon: '◍' }
]
</script>

<template>
  <nav class="mobile-nav" aria-label="Primary">
    <NuxtLink v-for="item in items" :key="item.to" :to="item.to" class="item">
      <span class="icon" aria-hidden="true">{{ item.icon }}</span>
      <span class="label">{{ item.label }}</span>
    </NuxtLink>
  </nav>
</template>

<style scoped>
.mobile-nav { display: none; }
@media (max-width: 900px) {
  .mobile-nav {
    position: fixed;
    inset: auto 0 0 0;
    z-index: 30;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    background: var(--surface);
    border-top: 1px solid var(--border);
    padding-bottom: env(safe-area-inset-bottom);
  }
  .item {
    display: grid;
    justify-items: center;
    gap: 2px;
    min-height: 56px;
    padding: var(--s2) 0;
    color: var(--muted);
    font-size: 0.72rem;
  }
  .item:hover { text-decoration: none; }
  .item.router-link-exact-active { color: var(--blue-700); }
  .icon { font-size: 1.15rem; line-height: 1; }
}
</style>
