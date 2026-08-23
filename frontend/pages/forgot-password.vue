<script setup lang="ts">
/**
 * Password reset.
 *
 * Same contract as registration: the submit button stays live and names the
 * first field that still needs work. Succeeding signs every other device out,
 * which is stated on screen before the person commits — if the reset is because
 * someone else had the password, that is the part that matters.
 */
const { $t } = useNuxtApp()
const { applySession } = useAuth()
const code = useVerificationCode('password_reset')

const form = reactive({ email: '', code: '', password: '', confirm: '' })
const submitting = ref(false)
const serverError = ref('')
const done = ref(false)

type FieldName = 'email' | 'code' | 'password' | 'confirm'
const FIELD_ORDER: FieldName[] = ['email', 'code', 'password', 'confirm']

const touched = reactive<Record<FieldName, boolean>>({
  email: false, code: false, password: false, confirm: false
})
const attempted = ref(false)

const emailInput = ref<HTMLInputElement | null>(null)
const codeInput = ref<HTMLInputElement | null>(null)
const passwordField = ref<{ focus: () => void } | null>(null)
const confirmField = ref<{ focus: () => void } | null>(null)

const errors = computed<Record<FieldName, string>>(() => {
  const passwordKey = passwordProblem(form.password, [form.email])
  let confirm = ''
  if (!form.confirm) confirm = $t('auth.errConfirm')
  else if (form.confirm !== form.password) confirm = $t('auth.errConfirmMatch')

  return {
    email: emailLooksValid(form.email) ? '' : $t('auth.errEmail'),
    code: /^\d{6}$/.test(form.code.trim()) ? '' : $t('auth.errCode'),
    password: passwordKey ? $t(passwordKey) : '',
    confirm
  }
})

function errorFor(field: FieldName): string {
  return attempted.value || touched[field] ? errors.value[field] : ''
}

function focusField(field: FieldName) {
  const targets: Record<FieldName, { focus: () => void } | null> = {
    email: emailInput.value,
    code: codeInput.value,
    password: passwordField.value,
    confirm: confirmField.value
  }
  targets[field]?.focus()
}

function sendCode() {
  if (!emailLooksValid(form.email)) {
    touched.email = true
    focusField('email')
    return
  }
  code.send(form.email)
}

async function submit() {
  if (submitting.value) return
  attempted.value = true
  serverError.value = ''

  const firstBad = FIELD_ORDER.find(field => errors.value[field] !== '')
  if (firstBad) {
    serverError.value = $t('auth.errSomething')
    focusField(firstBad)
    return
  }

  submitting.value = true
  try {
    const result = await apiFetch<any>('/v1/auth/password-reset', {
      method: 'POST',
      body: {
        email: form.email.trim(),
        verification_code: form.code.trim(),
        password: form.password
      }
    })
    applySession(result.token, result.user)
    done.value = true
  } catch (caught: any) {
    serverError.value = caught?.data?.detail || $t('state.generic')
  } finally {
    submitting.value = false
  }
}

useSeoMeta({ title: () => $t('auth.metaForgot'), robots: 'noindex' })
</script>

<template>
  <div class="container narrow">
    <div v-if="done" class="card section">
      <h1>{{ $t('auth.forgotTitle') }}</h1>
      <p class="notice">{{ $t('auth.resetDone') }}</p>
      <NuxtLink to="/community" class="btn">{{ $t('auth.goToCommunity') }}</NuxtLink>
    </div>

    <div v-else class="card section">
      <h1>{{ $t('auth.forgotTitle') }}</h1>
      <p class="small muted">{{ $t('auth.forgotLead') }}</p>

      <form class="form" novalidate @submit.prevent="submit">
        <div class="field-row">
          <label for="email" class="tiny muted">{{ $t('auth.email') }}</label>
          <input
            id="email"
            ref="emailInput"
            v-model="form.email"
            class="field"
            :class="{ bad: errorFor('email') }"
            type="email"
            autocomplete="email"
            @blur="touched.email = true"
          >
          <p v-if="errorFor('email')" class="tiny bad-text" role="alert">{{ errorFor('email') }}</p>
        </div>

        <div class="field-row">
          <label for="code" class="tiny muted">{{ $t('auth.code') }}</label>
          <div class="code-row">
            <input
              id="code"
              ref="codeInput"
              v-model="form.code"
              class="field"
              :class="{ bad: errorFor('code') }"
              inputmode="numeric"
              maxlength="6"
              autocomplete="one-time-code"
              :placeholder="$t('auth.codePlaceholder')"
              @blur="touched.code = true"
            >
            <button
              type="button"
              class="btn btn--ghost"
              :disabled="code.sending.value || code.cooldown.value > 0"
              @click="sendCode"
            >
              <template v-if="code.sending.value">{{ $t('auth.sending') }}</template>
              <template v-else-if="code.cooldown.value > 0">
                {{ $t('auth.resendIn', { seconds: code.cooldown.value }) }}
              </template>
              <template v-else>{{ $t('auth.sendCode') }}</template>
            </button>
          </div>
          <p v-if="errorFor('code')" class="tiny bad-text" role="alert">{{ errorFor('code') }}</p>
          <p v-if="code.notice.value" class="tiny notice">{{ code.notice.value }}</p>
          <p v-if="!code.deliveryConfigured.value" class="tiny bad-text">
            {{ $t('auth.deliveryNotConfigured') }}
          </p>
          <p v-if="code.error.value" class="tiny bad-text" role="alert">{{ code.error.value }}</p>
        </div>

        <PasswordField
          ref="passwordField"
          v-model="form.password"
          :label="$t('auth.newPassword')"
          :hint="$t('auth.passwordHint')"
          :error="errorFor('password')"
          autocomplete="new-password"
          @blur="touched.password = true"
        />

        <PasswordField
          ref="confirmField"
          v-model="form.confirm"
          :label="$t('auth.confirmPassword')"
          :placeholder="$t('auth.confirmPlaceholder')"
          :error="errorFor('confirm')"
          autocomplete="new-password"
          @blur="touched.confirm = true"
        />

        <p v-if="serverError" class="small bad-text" role="alert">{{ serverError }}</p>

        <button class="btn" type="submit" :disabled="submitting">
          {{ submitting ? $t('auth.working') : $t('auth.resetPassword') }}
        </button>
      </form>

      <p class="small"><NuxtLink to="/login">{{ $t('auth.backToSignIn') }}</NuxtLink></p>
    </div>
  </div>
</template>

<style scoped>
.narrow { max-width: 480px; }
.section { padding: var(--s5); }
.form { display: grid; gap: var(--s4); margin: var(--s5) 0; }
.field-row { display: grid; gap: var(--s1); }
.field-row p { margin: 0; }
.code-row { display: flex; gap: var(--s2); }
.code-row .field { flex: 1; }
.bad { border-color: var(--danger); }
.bad-text { color: var(--danger); }
.notice { color: var(--success); }
</style>
