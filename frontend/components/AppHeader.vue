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

const links = useSectionNavigation()

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
        <AppLogo :size="34" tone="onDark" />
        <span class="brand-text">Monash Hub</span>
      </NuxtLink>

      <nav class="nav" :aria-label="$t('nav.mainLabel')">
        <NuxtLink v-for="link in links" :key="link.to" :to="link.to" class="nav-link">
          {{ link.label }}
        </NuxtLink>
      </nav>

      <div class="header-search">
        <SearchInput
          v-model="query"
          compact-button
          :placeholder="$t('search.placeholderShort')"
          @submit="search"
        />
      </div>

      <div class="account">
        <LanguageSwitcher />
        <template v-if="user">
          <NuxtLink to="/notifications" class="bell" :aria-label="$t('nav.notifications')">
            <span aria-hidden="true">🔔</span>
            <span v-if="unread > 0" class="dot">{{ unread > 99 ? '99+' : unread }}</span>
          </NuxtLink>
          <!-- Your own name goes to your own page. It used to go to the
               community, which answered a question nobody was asking. -->
          <NuxtLink to="/profile" class="nav-link nickname">
            <img v-if="user.avatar_url && !avatarBroken" :src="user.avatar_url"
                 class="nickname-avatar" alt="" @error="avatarBroken = true">
            {{ user.nickname }}
          </NuxtLink>
          <button class="btn btn--ghost btn--small" @click="signOut">{{ $t('nav.signOut') }}</button>
        </template>
        <NuxtLink v-else to="/login" class="btn btn--ghost btn--small">{{ $t('nav.signIn') }}</NuxtLink>
      </div>
    </div>
  </header>
</template>

<style scoped>
.nickname { display: inline-flex; align-items: center; gap: var(--s2); }
.nickname-avatar {
  width: 24px; height: 24px; border-radius: 50%; object-fit: cover; flex: none;
}
.header {
  position: sticky;
  top: 0;
  z-index: 20;
  background: var(--brand);
  color: var(--text-inverse);
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
  color: var(--text-inverse); font-weight: 700; flex: none;
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
  flex: 1 1 760px;
  max-width: 880px;
  min-width: 0;
  gap: clamp(10px, 1vw, 24px);
  padding-inline: clamp(2px, 0.35vw, 8px);
}
.nav-link {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.86);
  font-size: 0.8rem;
  line-height: 1.15;
  text-align: center;
  white-space: nowrap;
  padding: 7px 3px;
  border-bottom: 2px solid transparent;
}
.nav-link:hover { color: #fff; text-decoration: none; }
.nav .router-link-active { color: #fff; border-bottom-color: rgba(255, 255, 255, 0.75); }

/* Search can give up a little width before the navigation does. This keeps long
   destinations such as WAM/GPA calculator visually separate from Community. */
.header-search { flex: 1 1 360px; min-width: 170px; max-width: 520px; }
.account { display: flex; align-items: center; gap: var(--s1); flex: none; }

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

/* Below this width there is not enough room for eight intrinsic-width labels,
   search and account controls without crowding. Navigation moves to the bottom
   bar and search lives on the page instead. */
@media (max-width: 1420px) {
  .nav, .header-search, .nickname { display: none; }
  .account { margin-left: auto; }
}
</style>
