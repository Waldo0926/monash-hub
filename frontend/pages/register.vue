<script setup lang="ts">
/**
 * Registration.
 *
 * The submit button stays live even when the form is incomplete. A greyed-out
 * button cannot explain itself: the person is left comparing their password
 * against a placeholder, guessing which rule they missed. So every rule is
 * checked on click, the first field that fails is named and focused, and a
 * rule is also shown early once the person has left that field — the point at
 * which they have finished their thought about it.
 */
const { $t } = useNuxtApp()
const { user, restore, applySession } = useAuth()
const code = useVerificationCode('registration')

onMounted(restore)

const form = reactive({ nickname: '', email: '', password: '', confirm: '', code: '' })
const submitting = ref(false)
const serverError = ref('')

type FieldName = 'nickname' | 'email' | 'password' | 'confirm' | 'code'
const FIELD_ORDER: FieldName[] = ['nickname', 'email', 'password', 'confirm', 'code']

const touched = reactive<Record<FieldName, boolean>>({
  nickname: false, email: false, password: false, confirm: false, code: false
})
const attempted = ref(false)

const nicknameInput = ref<HTMLInputElement | null>(null)
const emailInput = ref<HTMLInputElement | null>(null)
const codeInput = ref<HTMLInputElement | null>(null)
const passwordField = ref<{ focus: () => void } | null>(null)
const confirmField = ref<{ focus: () => void } | null>(null)

const errors = computed<Record<FieldName, string>>(() => {
  const nicknameKey = nicknameProblem(form.nickname)
  const passwordKey = passwordProblem(form.password, [form.nickname, form.email])

  let confirm = ''
  if (!form.confirm) confirm = $t('auth.errConfirm')
  else if (form.confirm !== form.password) confirm = $t('auth.errConfirmMatch')

  return {
    nickname: nicknameKey ? $t(nicknameKey) : '',
    email: emailLooksValid(form.email) ? '' : $t('auth.errEmail'),
    password: passwordKey ? $t(passwordKey) : '',
    confirm,
    code: /^\d{6}$/.test(form.code.trim()) ? '' : $t('auth.errCode')
  }
})

function errorFor(field: FieldName): string {
  return attempted.value || touched[field] ? errors.value[field] : ''
}

function focusField(field: FieldName) {
  const targets: Record<FieldName, { focus: () => void } | null> = {
    nickname: nicknameInput.value,
    email: emailInput.value,
    password: passwordField.value,
    confirm: confirmField.value,
    code: codeInput.value
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
    const result = await apiFetch<any>('/v1/auth/signup', {
      method: 'POST',
      body: {
        nickname: form.nickname.trim(),
        email: form.email.trim(),
        password: form.password,
        verification_code: form.code.trim()
      }
    })
    applySession(result.token, result.user)
    navigateTo('/community')
  } catch (caught: any) {
    serverError.value = caught?.data?.detail || $t('state.generic')
  } finally {
    submitting.value = false
  }
}

useSeoMeta({ title: () => $t('auth.metaSignUp'), robots: 'noindex' })
</script>

<template>
  <div class="container narrow">
    <div v-if="user" class="card section">
      <h1>{{ $t('auth.signedInAs', { nickname: user.nickname }) }}</h1>
      <NuxtLink to="/community" class="btn">{{ $t('auth.goToCommunity') }}</NuxtLink>
    </div>

    <div v-else class="card section">
      <h1>{{ $t('auth.signUpTitle') }}</h1>
      <p class="small muted">{{ $t('auth.lead') }}</p>

      <form class="form" novalidate @submit.prevent="submit">
        <div class="field-row">
          <label for="nickname" class="tiny muted">{{ $t('auth.nickname') }}</label>
          <input
            id="nickname"
            ref="nicknameInput"
            v-model="form.nickname"
            class="field"
            :class="{ bad: errorFor('nickname') }"
            :placeholder="$t('auth.nicknamePlaceholder')"
            autocomplete="username"
            :aria-invalid="errorFor('nickname') ? 'true' : undefined"
            @blur="touched.nickname = true"
          >
          <p v-if="errorFor('nickname')" class="tiny bad-text" role="alert">{{ errorFor('nickname') }}</p>
          <p v-else class="tiny muted">{{ $t('auth.nicknameHint') }}</p>
        </div>

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
            :aria-invalid="errorFor('email') ? 'true' : undefined"
            @blur="touched.email = true"
          >
          <p v-if="errorFor('email')" class="tiny bad-text" role="alert">{{ errorFor('email') }}</p>
          <p v-else class="tiny muted">{{ $t('auth.emailHint') }}</p>
        </div>

        <PasswordField
          ref="passwordField"
          v-model="form.password"
          :label="$t('auth.password')"
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

        <p v-if="serverError" class="small bad-text" role="alert">{{ serverError }}</p>

        <button class="btn" type="submit" :disabled="submitting">
          {{ submitting ? $t('auth.working') : $t('auth.createAccount') }}
        </button>
      </form>

      <p class="small">
        <NuxtLink to="/login">{{ $t('auth.haveAccount') }}</NuxtLink>
      </p>
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
