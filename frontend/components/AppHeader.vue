<script setup lang="ts">

// A missing avatar file must not leave a broken-image icon in the header. It
// falls back to the name alone, which is what was there before pictures.
const avatarBroken = ref(false)
const { user, restore, signOut } = useAuth()
const { unread, start, stop } = useNotifications()
const route = useRoute()
const { $t } = useNuxtApp()

onMounted(async () => {
  await restore()
  start()
})
onBeforeUnmount(stop)

const links = useHeaderNavigation()

// The planning tools open as a small menu. It closes on a page change, a click
// elsewhere or Escape, and it is a real button so a keyboard reaches it.
const openMenu = ref<string | null>(null)
const menuRoot = ref<HTMLElement | null>(null)
function toggleMenu(label: string) {
  openMenu.value = openMenu.value === label ? null : label
}
function closeOnOutside(event: MouseEvent) {
  if (openMenu.value && menuRoot.value && !menuRoot.value.contains(event.target as Node)) openMenu.value = null
}
watch(() => route.fullPath, () => { openMenu.value = null })
onMounted(() => document.addEventListener('click', closeOnOutside))
onBeforeUnmount(() => document.removeEventListener('click', closeOnOutside))
const groupActive = (children: { to: string }[]) =>
  children.some(c => route.path === c.to || route.path.startsWith(`${c.to}/`))

// Shown in the avatar circle when there is no picture. Array.from keeps a
// Chinese or emoji first character whole.
const initial = computed(() => (Array.from(user.value?.nickname?.trim() || '')[0] ?? '?').toUpperCase())

const query = ref('')
watch(() => route.query.q, q => { query.value = (q as string) || '' }, { immediate: true })

function search(value: string) {
  if (value) navigateTo({ path: '/search', query: { q: value } })
}
</script>

<template>
  <header class="header">
    <div class="inner">
      <NuxtLink to="/" class="brand">
        <AppLogo :size="30" tone="onLight" />
        <span class="brand-text">Monash Hub</span>
      </NuxtLink>

      <nav ref="menuRoot" class="nav" :aria-label="$t('nav.mainLabel')" @keydown.esc="openMenu = null">
        <template v-for="link in links" :key="link.label">
          <NuxtLink v-if="link.to" :to="link.to" class="nav-link">
            {{ link.label }}
          </NuxtLink>
          <div v-else class="nav-group">
            <button
              type="button"
              class="nav-link nav-button"
              :class="{ 'router-link-active': groupActive(link.children || []) }"
              :aria-expanded="openMenu === link.label"
              @click="toggleMenu(link.label)"
            >
              {{ link.label }}
              <PlanIcon name="chevron-down" :size="14" />
            </button>
            <div v-if="openMenu === link.label" class="nav-menu">
              <NuxtLink v-for="child in link.children" :key="child.to" :to="child.to">{{ child.label }}</NuxtLink>
            </div>
          </div>
        </template>
      </nav>

      <div class="header-search">
        <SearchInput
          v-model="query"
          inset
          :placeholder="$t('search.placeholderShort')"
          @submit="search"
        />
      </div>

      <NuxtLink to="/parents" class="parents-link">{{ $t('nav.parents') }}</NuxtLink>

      <!-- One tray for language and account. The controls inside are flat until
           hovered and only the main action is raised, so the corner reads as one
           group instead of a row of separate boxes. -->
      <div class="account">
        <LanguageSwitcher />
        <template v-if="user">
          <NuxtLink to="/notifications" class="icon-btn bell" :aria-label="$t('nav.notifications')">
            <PlanIcon name="bell" :size="18" />
            <span v-if="unread > 0" class="dot">{{ unread > 99 ? '99+' : unread }}</span>
          </NuxtLink>
          <!-- Your own name goes to your own page. It used to go to the
               community, which answered a question nobody was asking. -->
          <NuxtLink to="/profile" class="chip nickname" :aria-label="user.nickname">
            <img v-if="user.avatar_url && !avatarBroken" :src="user.avatar_url"
                 class="avatar" alt="" @error="avatarBroken = true">
            <span v-else class="avatar avatar--initial" aria-hidden="true">{{ initial }}</span>
            <span class="nickname-text">{{ user.nickname }}</span>
          </NuxtLink>
          <button type="button" class="icon-btn sign-out" :aria-label="$t('nav.signOut')"
                  :title="$t('nav.signOut')" @click="signOut">
            <PlanIcon name="logout" :size="18" />
          </button>
        </template>
        <NuxtLink v-else to="/login" class="chip">{{ $t('nav.signIn') }}</NuxtLink>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 20;
  /* White with a hairline, not a solid brand-blue bar. The blue slab was the
     loudest thing on every page and pushed the content down a level; the mark
     carries the brand colour now. */
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  color: var(--text);
}
/* Full width rather than the page container: the brand belongs against the left
   edge and the account against the right, while the middle of the header is
   shared deliberately between navigation and search. */
.inner {
  display: flex;
  align-items: center;
  gap: var(--s2);
  min-height: var(--header-h);
  padding: 0 var(--s3);
}
.brand {
  display: flex; align-items: center; gap: var(--s2);
  color: var(--text); font-weight: 600; flex: none;
  letter-spacing: -0.01em;
}
.brand:hover { text-decoration: none; }

/* Navigation follows the content instead of forcing every label into an equal
   column. Short labels therefore stay compact, long labels get the room they
   actually need, and the remaining space is shared evenly between links. */
.nav {
  display: flex;
  align-items: stretch;
  justify-content: space-evenly;
  flex: 1 1 560px;
  max-width: 680px;
  min-width: 0;
  gap: clamp(10px, 1vw, 24px);
  padding-inline: clamp(2px, 0.35vw, 8px);
}
.nav-link {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  color: var(--muted);
  font-size: 0.84rem;
  line-height: 1.15;
  text-align: center;
  white-space: nowrap;
  padding: 7px 3px;
  border-bottom: 2px solid transparent;
}
.nav-link:hover { color: var(--text); text-decoration: none; }
.nav .router-link-active { color: var(--text); border-bottom-color: var(--text); }
.nav-group { position: relative; display: flex; }
.nav-button {
  gap: 2px;
  border-top: 0;
  border-inline: 0;
  background: none;
  font: inherit;
  font-size: 0.84rem;
  cursor: pointer;
}
.nav-button:hover { color: var(--text); }
.nav-menu {
  position: absolute;
  top: calc(100% + 6px);
  left: 50%;
  transform: translateX(-50%);
  display: grid;
  min-width: 10em;
  padding: 6px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--surface);
  box-shadow: var(--shadow-sm);
}
.nav-menu a { padding: 8px 12px; border-radius: 6px; color: var(--text); font-size: 0.875rem; white-space: nowrap; }
.nav-menu a:hover { background: var(--surface-2); text-decoration: none; }
.nav-menu .router-link-active { color: var(--brand); }

/* Search can give up a little width before the navigation does. This keeps long
   destinations such as WAM/GPA calculator visually separate from Community. */
.header-search { flex: 1 1 360px; min-width: 170px; max-width: 520px; }
.account {
  display: flex;
  align-items: center;
  gap: 2px;
  flex: none;
  margin-left: var(--s1);
  padding: 4px;
  border-radius: var(--radius-pill);
  background: var(--surface-2);
}

.parents-link {
  flex: none;
  margin-left: var(--s2);
  color: var(--muted);
  font-size: 0.84rem;
  white-space: nowrap;
}
.parents-link:hover, .parents-link.router-link-active { color: var(--text); text-decoration: none; }

/* The raised piece in the tray: sign in, or your own name once signed in. */
.chip {
  display: inline-flex;
  align-items: center;
  gap: var(--s2);
  height: 32px;
  padding: 0 var(--s4);
  border-radius: var(--radius-pill);
  background: var(--surface);
  box-shadow: 0 0 0 1px rgba(12, 27, 42, 0.06), 0 1px 3px rgba(12, 27, 42, 0.1);
  color: var(--text);
  font-size: 0.85rem;
  font-weight: 600;
  white-space: nowrap;
  transition: box-shadow 0.15s, color 0.15s;
}
.chip:hover {
  color: var(--brand);
  text-decoration: none;
  box-shadow: 0 0 0 1px rgba(12, 27, 42, 0.08), 0 2px 6px rgba(12, 27, 42, 0.14);
}
.nickname { padding-left: 4px; }
.avatar {
  width: 24px; height: 24px; border-radius: 50%; object-fit: cover; flex: none;
}
.avatar--initial {
  display: grid;
  place-items: center;
  background: var(--blue-50);
  color: var(--brand);
  font-size: 0.75rem;
  font-weight: 700;
}

.icon-btn {
  position: relative;
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  padding: 0;
  border: 0;
  border-radius: 50%;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  transition: background-color 0.15s, color 0.15s;
}
.icon-btn:hover { background: rgba(12, 27, 42, 0.06); color: var(--text); text-decoration: none; }
.dot {
  position: absolute;
  top: 1px;
  right: 0;
  min-width: 8px;
  padding: 0 3px;
  border: 2px solid var(--surface-2);
  border-radius: var(--radius-pill);
  background: var(--danger);
  color: #fff;
  font-size: 0.58rem;
  font-weight: 700;
  line-height: 12px;
  text-align: center;
  box-sizing: content-box;
}

/* Below this width there is not enough room for six intrinsic-width labels,
   search and account controls without crowding. Navigation moves to the bottom
   bar and search lives on the page instead. */
@media (max-width: 1180px) {
  .nav, .header-search, .parents-link, .nickname-text { display: none; }
  .nickname { padding: 0 4px; }
  .account { margin-left: auto; }
}
/* Signing out is also on the profile page, so a phone keeps the tray short. */
@media (max-width: 520px) {
  .sign-out { display: none; }
}
</style>
