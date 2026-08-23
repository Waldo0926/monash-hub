<script setup lang="ts">
const { $t } = useNuxtApp()
const { user, restore, signIn } = useAuth()
const { refresh: refreshNotifications } = useNotifications()

onMounted(restore)

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
.narrow { max-width: 480px; }
.section { padding: var(--s5); }
.form { display: grid; gap: var(--s4); margin: var(--s5) 0; }
.field-row { display: grid; gap: var(--s1); }
.bad-text { color: var(--danger); }
.links { display: flex; justify-content: space-between; gap: var(--s3); flex-wrap: wrap; }
</style>
