<script setup lang="ts">
const { signIn, signUp, user, restore } = useAuth()
onMounted(restore)

const mode = ref<'in' | 'up'>('in')
const form = reactive({ email: '', nickname: '', password: '' })
const busy = ref(false)
const message = ref('')

async function submit() {
  message.value = ''
  busy.value = true
  try {
    if (mode.value === 'in') await signIn(form.email, form.password)
    else await signUp(form.email, form.nickname, form.password)
    navigateTo('/community')
  } catch (e: any) {
    message.value = e?.data?.detail || 'That did not work. Check the details and try again.'
  } finally {
    busy.value = false
  }
}

useSeoMeta({ title: 'Sign in — Monash Hub', robots: 'noindex' })
</script>

<template>
  <div class="container narrow">
    <div v-if="user" class="card section">
      <h1>Signed in</h1>
      <p>You are signed in as <strong>{{ user.nickname }}</strong>.</p>
      <NuxtLink to="/community" class="btn">Go to the community</NuxtLink>
    </div>

    <div v-else class="card section">
      <h1>{{ mode === 'in' ? 'Sign in' : 'Create an account' }}</h1>
      <p class="small muted">
        You only need an account to post, answer, save or report. Reading is open to everyone, and
        we never ask for your real name or student ID.
      </p>

      <form class="form" @submit.prevent="submit">
        <label class="row">
          <span class="tiny muted">Email</span>
          <input v-model="form.email" class="field" type="email" autocomplete="email" required>
        </label>
        <label v-if="mode === 'up'" class="row">
          <span class="tiny muted">Nickname (this is what other students see)</span>
          <input v-model="form.nickname" class="field" minlength="2" maxlength="48" required>
        </label>
        <label class="row">
          <span class="tiny muted">Password (at least 8 characters)</span>
          <input
            v-model="form.password"
            class="field"
            type="password"
            minlength="8"
            :autocomplete="mode === 'in' ? 'current-password' : 'new-password'"
            required
          >
        </label>
        <p v-if="message" class="small err">{{ message }}</p>
        <button class="btn" type="submit" :disabled="busy">
          {{ busy ? 'Working…' : mode === 'in' ? 'Sign in' : 'Create account' }}
        </button>
      </form>

      <p class="small">
        <button class="link" @click="mode = mode === 'in' ? 'up' : 'in'">
          {{ mode === 'in' ? 'Need an account? Create one' : 'Already have an account? Sign in' }}
        </button>
      </p>
    </div>
  </div>
</template>

<style scoped>
.narrow { max-width: 480px; }
.section { padding: var(--s5); }
.form { display: grid; gap: var(--s3); justify-items: stretch; margin: var(--s4) 0; }
.row { display: grid; gap: var(--s1); }
.err { color: var(--danger); }
.link { border: 0; background: none; padding: 0; color: var(--blue-700); font: inherit; cursor: pointer; }
.link:hover { text-decoration: underline; }
</style>
