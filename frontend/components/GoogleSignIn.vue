<script setup lang="ts">
/**
 * The "continue with Google" button.
 *
 * It renders nothing at all when the server has no Google credentials
 * configured, rather than showing a button that answers 503. A deployment
 * without keys should look like a deployment without the feature.
 *
 * The mark is Google's own four-colour G, drawn inline. Their branding
 * guidelines require the real mark rather than an approximation, and inlining
 * it keeps the button working without a request to a Google CDN — which on this
 * site would be the only third-party asset on the sign-in page.
 */
const props = withDefaults(defineProps<{ next?: string }>(), { next: '/' })

const { $t } = useNuxtApp()
const available = ref(false)
const busy = ref(false)
const error = ref('')

onMounted(async () => {
  // A HEAD-ish probe: the start endpoint answers 503 when unconfigured, so
  // asking it is also how we find out whether to show anything.
  try {
    await apiFetch<{ url: string }>(`/v1/auth/google/start?next=${encodeURIComponent(props.next)}`)
    available.value = true
  } catch {
    available.value = false
  }
})

async function go() {
  if (busy.value) return
  busy.value = true
  error.value = ''
  try {
    const { url } = await apiFetch<{ url: string }>(
      `/v1/auth/google/start?next=${encodeURIComponent(props.next)}`
    )
    window.location.href = url
  } catch {
    error.value = $t('auth.google.unavailable')
    busy.value = false
  }
}
</script>

<template>
  <div v-if="available" class="google">
    <button class="gbtn" type="button" :disabled="busy" @click="go">
      <svg class="g" viewBox="0 0 18 18" aria-hidden="true" focusable="false">
        <path fill="#4285F4" d="M17.64 9.2c0-.64-.06-1.25-.16-1.84H9v3.48h4.84a4.14 4.14 0 0 1-1.8 2.72v2.26h2.92c1.7-1.57 2.68-3.88 2.68-6.62z"/>
        <path fill="#34A853" d="M9 18c2.43 0 4.47-.8 5.96-2.18l-2.92-2.26c-.81.54-1.84.86-3.04.86-2.34 0-4.32-1.58-5.03-3.7H.96v2.33A9 9 0 0 0 9 18z"/>
        <path fill="#FBBC05" d="M3.97 10.72a5.4 5.4 0 0 1 0-3.44V4.95H.96a9 9 0 0 0 0 8.1l3.01-2.33z"/>
        <path fill="#EA4335" d="M9 3.58c1.32 0 2.5.45 3.44 1.35l2.58-2.59C13.46.9 11.43 0 9 0A9 9 0 0 0 .96 4.95l3.01 2.33C4.68 5.16 6.66 3.58 9 3.58z"/>
      </svg>
      <span>{{ busy ? $t('auth.google.redirecting') : $t('auth.google.button') }}</span>
    </button>
    <p v-if="error" class="tiny bad-text" role="alert">{{ error }}</p>
    <p class="divider"><span>{{ $t('auth.google.or') }}</span></p>
  </div>
</template>

<style scoped>
.google { display: grid; gap: var(--s3); margin-bottom: var(--s4); }
.gbtn {
  display: flex; align-items: center; justify-content: center; gap: var(--s3);
  width: 100%; min-height: 44px;
  padding: 0 var(--s4);
  /* Google's guidelines: their mark on white or on their blue, never recoloured
     and never on an arbitrary background. White it is. */
  background: #fff;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  color: #1f1f1f;
  font: inherit; font-weight: 500;
  cursor: pointer;
}
.gbtn:hover:not(:disabled) { background: var(--surface-2); }
.gbtn:disabled { opacity: 0.6; cursor: default; }
.g { width: 18px; height: 18px; flex: none; }
.bad-text { color: var(--danger); margin: 0; }

/* A rule with the word "or" sitting in it, so the two ways in read as
   alternatives rather than as a stack of buttons. */
.divider {
  display: flex; align-items: center; gap: var(--s3);
  margin: var(--s2) 0 0;
  color: var(--muted); font-size: 0.8rem;
}
.divider::before, .divider::after {
  content: ""; flex: 1; height: 1px; background: var(--border);
}
</style>
