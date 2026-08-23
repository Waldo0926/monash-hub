/**
 * The "send me a code" half of registration and password reset.
 *
 * The notice it produces is deliberately non-committal — "if this address can
 * be used, a code is on its way" — because the endpoint behind it answers the
 * same way whether or not the address has an account, and the wording on screen
 * has to match that or the whole precaution is undone by the UI.
 */
export function useVerificationCode(purpose: 'registration' | 'password_reset') {
  const { $t } = useNuxtApp()

  const sending = ref(false)
  const cooldown = ref(0)
  const notice = ref('')
  const error = ref('')
  const deliveryConfigured = ref(true)
  let timer: ReturnType<typeof setInterval> | undefined

  function startCooldown(seconds: number) {
    cooldown.value = seconds
    clearInterval(timer)
    timer = setInterval(() => {
      cooldown.value -= 1
      if (cooldown.value <= 0) {
        clearInterval(timer)
        cooldown.value = 0
      }
    }, 1000)
  }

  onBeforeUnmount(() => clearInterval(timer))

  async function send(email: string) {
    if (sending.value || cooldown.value > 0) return
    sending.value = true
    notice.value = ''
    error.value = ''
    try {
      const result = await apiFetch<{
        expires_in_seconds: number
        resend_available_in_seconds: number
        delivery_configured: boolean
      }>('/v1/auth/verification-code', { method: 'POST', body: { email: email.trim(), purpose } })

      deliveryConfigured.value = result.delivery_configured
      notice.value = $t('auth.codeSent', {
        email: email.trim(),
        minutes: Math.max(1, Math.round(result.expires_in_seconds / 60))
      })
      startCooldown(result.resend_available_in_seconds)
    } catch (caught: any) {
      if (caught?.status === 429 || caught?.statusCode === 429) {
        startCooldown(Number(caught?.response?.headers?.get?.('retry-after')) || 60)
      }
      error.value = caught?.data?.detail || $t('state.generic')
    } finally {
      sending.value = false
    }
  }

  return { send, sending, cooldown, notice, error, deliveryConfigured }
}
