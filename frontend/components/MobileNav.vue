<script setup lang="ts">
// Phones keep the four most-used destinations thumb-reachable. Everything in
// the desktop header is also available from the fifth "More" destination, so
// shrinking the header never makes a section disappear.
const { $t } = useNuxtApp()
const { user } = useAuth()
const { unread } = useNotifications()
const route = useRoute()

const menuOpen = ref(false)
const menuButton = ref<HTMLButtonElement | null>(null)
const closeButton = ref<HTMLButtonElement | null>(null)
let previousBodyOverflow = ''

const primaryItems = computed(() => [
  { to: '/', label: $t('nav.home'), icon: '⌂', badge: 0 },
  { to: '/search', label: $t('nav.search'), icon: '⌕', badge: 0 },
  { to: '/community', label: $t('nav.community'), icon: '☰', badge: 0 },
  user.value
    ? { to: '/notifications', label: $t('nav.notifications'), icon: '🔔', badge: unread.value }
    : { to: '/login', label: $t('nav.account'), icon: '◍', badge: 0 }
])

const sectionItems = useSectionNavigation()

const sectionActive = computed(() => sectionItems.value.some(item =>
  item.to !== '/community' &&
  (route.path === item.to || route.path.startsWith(`${item.to}/`))
))

function closeMenu(restoreFocus = true) {
  if (!menuOpen.value) return
  menuOpen.value = false
  if (restoreFocus) nextTick(() => menuButton.value?.focus())
}

watch(menuOpen, async (open) => {
  if (!import.meta.client) return
  if (open) {
    previousBodyOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    await nextTick()
    closeButton.value?.focus()
  } else {
    document.body.style.overflow = previousBodyOverflow
  }
})

watch(() => route.fullPath, () => closeMenu(false))
onBeforeUnmount(() => {
  if (import.meta.client) document.body.style.overflow = previousBodyOverflow
})
</script>

<template>
  <nav class="mobile-nav" :aria-label="$t('nav.mainLabel')">
    <NuxtLink v-for="item in primaryItems" :key="item.to" :to="item.to" class="item">
      <span class="icon" aria-hidden="true">
        {{ item.icon }}
        <span v-if="item.badge > 0" class="dot">{{ item.badge > 99 ? '99+' : item.badge }}</span>
      </span>
      <span class="label">{{ item.label }}</span>
    </NuxtLink>
    <button
      ref="menuButton"
      type="button"
      class="item more-button"
      :class="{ active: sectionActive }"
      :aria-expanded="menuOpen"
      aria-controls="mobile-section-menu"
      @click="menuOpen = true"
    >
      <span class="icon" aria-hidden="true">▦</span>
      <span class="label">{{ $t('nav.more') }}</span>
    </button>
  </nav>

  <Teleport to="body">
    <div
      v-if="menuOpen"
      class="menu-layer"
      role="presentation"
      @click.self="closeMenu()"
      @keydown.esc.prevent="closeMenu()"
    >
      <section
        id="mobile-section-menu"
        class="section-menu"
        role="dialog"
        aria-modal="true"
        aria-labelledby="mobile-section-menu-title"
      >
        <header class="menu-header">
          <h2 id="mobile-section-menu-title">{{ $t('nav.allSections') }}</h2>
          <button
            ref="closeButton"
            type="button"
            class="close-button"
            :aria-label="$t('nav.closeMenu')"
            @click="closeMenu()"
          >
            ×
          </button>
        </header>
        <div class="section-grid">
          <NuxtLink
            v-for="item in sectionItems"
            :key="item.to"
            :to="item.to"
            class="section-link"
          >
            <span class="section-icon" aria-hidden="true">{{ item.icon }}</span>
            <span>{{ item.label }}</span>
          </NuxtLink>
        </div>
      </section>
    </div>
  </Teleport>
</template>

<style scoped>
.mobile-nav { display: none; }
.menu-layer { display: none; }

@media (max-width: 980px) {
  .mobile-nav {
    position: fixed;
    inset: auto 0 0 0;
    z-index: 30;
    display: grid;
    /* minmax(0, 1fr), not 1fr: a long label in any language must not make
       the bar wider than the screen it is fixed to. */
    grid-template-columns: repeat(5, minmax(0, 1fr));
    background: var(--surface);
    border-top: 1px solid var(--border);
    padding-bottom: env(safe-area-inset-bottom);
  }
  .item {
    display: grid;
    justify-items: center;
    align-content: center;
    gap: 2px;
    min-width: 0;
    min-height: 56px;
    padding: var(--s2) 2px;
    color: var(--muted);
    font: inherit;
    font-size: 0.68rem;
    line-height: 1.15;
    text-align: center;
  }
  .item:hover { text-decoration: none; }
  .item.router-link-exact-active,
  .item.active { color: var(--blue-700); }
  .more-button { border: 0; background: transparent; cursor: pointer; }
  .label {
    width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
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

  .menu-layer {
    position: fixed;
    inset: 0;
    z-index: 40;
    display: flex;
    align-items: flex-end;
    padding: var(--s3) var(--s3) calc(64px + env(safe-area-inset-bottom));
    background: rgba(15, 23, 42, 0.46);
  }
  .section-menu {
    width: min(100%, 560px);
    max-height: calc(100dvh - 96px - env(safe-area-inset-bottom));
    margin: 0 auto;
    overflow-y: auto;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    background: var(--surface);
    box-shadow: var(--shadow);
    padding: var(--s4);
  }
  .menu-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--s3);
    margin-bottom: var(--s3);
  }
  .menu-header h2 { margin: 0; font-size: 1.1rem; }
  .close-button {
    display: grid;
    place-items: center;
    width: 44px;
    height: 44px;
    flex: none;
    border: 1px solid var(--border);
    border-radius: 50%;
    background: var(--surface);
    color: var(--text);
    font-size: 1.6rem;
    line-height: 1;
    cursor: pointer;
  }
  .section-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: var(--s2);
  }
  .section-link {
    display: flex;
    align-items: center;
    gap: var(--s3);
    min-width: 0;
    min-height: 58px;
    padding: var(--s3);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--text);
    font-weight: 650;
  }
  .section-link:hover { text-decoration: none; background: var(--surface-2); }
  .section-link.router-link-active {
    border-color: var(--blue);
    background: var(--blue-50);
    color: var(--blue-700);
  }
  .section-icon {
    display: grid;
    place-items: center;
    width: 30px;
    height: 30px;
    flex: none;
    border-radius: var(--radius-sm);
    background: var(--surface-2);
    color: var(--blue-700);
    font-size: 1rem;
    font-weight: 800;
  }
}

</style>
