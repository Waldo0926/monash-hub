<script setup lang="ts">
/**
 * Where Google's redirect lands.
 *
 * The session token arrives in the URL *fragment* rather than the query string,
 * because a fragment is never sent to a server: it stays out of our access
 * logs, out of nginx's, and out of any proxy between. The first thing this page
 * does is take it out of the address bar as well, so it does not sit in the
 * history entry or get copied when somebody shares the URL.
 *
 * Nothing is rendered for long. On success it replaces itself with wherever the
 * person was going; on failure it hands them back to the sign-in page with a
 * reason.
 */
const { $t } = useNuxtApp()
const { applySession } = useAuth()
const failed = ref(false)

definePageMeta({ layout: 'default' })

onMounted(async () => {
  const fragment = new URLSearchParams(window.location.hash.replace(/^#/, ''))
  const token = fragment.get('token')
  const next = fragment.get('next') || '/'

  // Out of the address bar before anything else can read it.
  history.replaceState(null, '', window.location.pathname)

  if (!token) {
    failed.value = true
    return
  }
  try {
    localStorage.setItem('mh_token', token)
    const account = await apiFetch<any>('/v1/auth/me')
    applySession(token, account)
    // `next` came back through our own signed state, so it is a path we issued
    // rather than anything a visitor could aim somewhere else.
    await navigateTo(next.startsWith('/') && !next.startsWith('//') ? next : '/', {
      replace: true
    })
  } catch {
    localStorage.removeItem('mh_token')
    failed.value = true
  }
})

useSeoMeta({ title: () => $t('auth.google.finishing'), robots: 'noindex' })
</script>

<template>
  <div class="container narrow page">
    <div class="card section">
      <template v-if="failed">
        <h1>{{ $t('auth.google.failedTitle') }}</h1>
        <p class="small muted">{{ $t('auth.google.failedBody') }}</p>
        <NuxtLink to="/login" class="btn">{{ $t('nav.signIn') }}</NuxtLink>
      </template>
      <template v-else>
        <h1>{{ $t('auth.google.finishing') }}</h1>
        <Skeleton :lines="2" />
      </template>
    </div>
  </div>
</template>

<style scoped>
.narrow { max-width: 480px; }
.page { padding: var(--s7) var(--s4); }
.section { padding: var(--s5); }
</style>
