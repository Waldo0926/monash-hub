<script setup lang="ts">
const { $t } = useNuxtApp()
const { user, restore, signIn } = useAuth()
const { refresh: refreshNotifications } = useNotifications()

onMounted(restore)

// The Google callback sends people back here with a reason when it could not
// finish, because they arrived by clicking a button and a JSON error would be
// no use to them.
const route = useRoute()
const googleProblem = computed(() => {
  const code = route.query.google as string | undefined
  if (!code) return ''
  const known = ['cancelled', 'unverified', 'suspended', 'unavailable']
  return $t(`auth.google.error.${known.includes(code) ? code : 'failed'}`)
})

const form = reactive({ email: '', password: '' })
const submitting = ref(false)
const message = ref('')

async function submit() {
  if (submitting.value) return
  message.value = ''
  submitting.value = true
  try {
    await signIn(form.email.trim(), form.password)
    await refreshNotifications()
    navigateTo('/community')
  } catch (caught: any) {
    message.value = caught?.data?.detail || $t('state.generic')
  } finally {
    submitting.value = false
  }
}

useSeoMeta({ title: () => $t('auth.metaSignIn'), robots: 'noindex' })
</script>

<template>
  <div class="container narrow">
    <div v-if="user" class="card section">
      <h1>{{ $t('auth.signedInAs', { nickname: user.nickname }) }}</h1>
      <NuxtLink to="/community" class="btn">{{ $t('auth.goToCommunity') }}</NuxtLink>
    </div>

    <div v-else class="card section">
      <h1>{{ $t('auth.signInTitle') }}</h1>
      <p class="small muted">{{ $t('auth.lead') }}</p>

      <!-- Only rendered when the server has credentials; see GoogleSignIn.vue. -->
      <GoogleSignIn class="google-row" />

      <p v-if="googleProblem" class="small bad-text" role="alert">{{ googleProblem }}</p>

      <form class="form" novalidate @submit.prevent="submit">
        <div class="field-row">
          <label for="email" class="tiny muted">{{ $t('auth.email') }}</label>
          <input id="email" v-model="form.email" class="field" type="email" autocomplete="email" required>
        </div>
        <PasswordField
          v-model="form.password"
          :label="$t('auth.password')"
          autocomplete="current-password"
        />
        <p v-if="message" class="small bad-text" role="alert">{{ message }}</p>
        <button class="btn" type="submit" :disabled="submitting">
          {{ submitting ? $t('auth.working') : $t('auth.signInTitle') }}
        </button>
      </form>

      <p class="small links">
        <NuxtLink to="/register">{{ $t('auth.needAccount') }}</NuxtLink>
        <NuxtLink to="/forgot-password">{{ $t('auth.forgot') }}</NuxtLink>
      </p>
    </div>
  </div>
</template>

<style scoped>
.google-row { margin-top: var(--s4); }
.bad-text { color: var(--danger); }
.narrow { max-width: 480px; }
.section { padding: var(--s5); }
.form { display: grid; gap: var(--s4); margin: var(--s5) 0; }
.field-row { display: grid; gap: var(--s1); }
.bad-text { color: var(--danger); }
.links { display: flex; justify-content: space-between; gap: var(--s3); flex-wrap: wrap; }
</style>
