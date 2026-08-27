<script setup lang="ts">
// Bottom navigation on phones: four destinations, thumb-reachable, each a
// 44px+ target. The desktop header is not squeezed onto a small screen.
const { $t } = useNuxtApp()
const { user } = useAuth()
const { unread } = useNotifications()

const items = computed(() => [
  { to: '/', label: $t('nav.home'), icon: '⌂', badge: 0 },
  { to: '/search', label: $t('nav.search'), icon: '⌕', badge: 0 },
  { to: '/community', label: $t('nav.community'), icon: '☰', badge: 0 },
  user.value
    ? { to: '/notifications', label: $t('nav.notifications'), icon: '🔔', badge: unread.value }
    : { to: '/login', label: $t('nav.account'), icon: '◍', badge: 0 }
])
</script>

<template>
  <nav class="mobile-nav" :aria-label="$t('nav.mainLabel')">
    <NuxtLink v-for="item in items" :key="item.to" :to="item.to" class="item">
      <span class="icon" aria-hidden="true">
        {{ item.icon }}
        <span v-if="item.badge > 0" class="dot">{{ item.badge > 99 ? '99+' : item.badge }}</span>
      </span>
      <span class="label">{{ item.label }}</span>
    </NuxtLink>
  </nav>
</template>

<style scoped>
.mobile-nav { display: none; }
@media (max-width: 980px) {
  .mobile-nav {
    position: fixed;
    inset: auto 0 0 0;
    z-index: 30;
    display: grid;
    /* minmax(0, 1fr), not 1fr: a long label in any language must not make
       the bar wider than the screen it is fixed to. */
    grid-template-columns: repeat(4, minmax(0, 1fr));
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
  .icon { position: relative; font-size: 1.15rem; line-height: 1; }
  .dot {
    position: absolute;
    top: -6px;
    left: 12px;
    min-width: 16px;
    padding: 0 3px;
    border-radius: var(--radius-pill);
    background: var(--danger);
    color: #fff;
    font-size: 0.6rem;
    font-weight: 700;
    line-height: 16px;
  }
}
</style>
