/**
 * What the "add to home screen" hint needs to know about this browser.
 *
 * Only Chrome-family browsers on Android (and desktop) offer an install button
 * a page can press for the reader; that arrives as `beforeinstallprompt`, often
 * before any component has mounted, so the plugin catches it and keeps it
 * here. Everywhere else - Safari, WeChat, the browsers Chinese phones ship
 * with - the reader has to do it from the browser's own menu, and the most we
 * can do is say which menu.
 */
import { computed, readonly, ref, shallowRef } from 'vue'

export type InstallPlatform = 'ios' | 'android' | 'wechat' | 'inapp' | 'desktop'

interface InstallPromptEvent extends Event {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

/** Client-only state; the server never sees either of these. */
const installPrompt = shallowRef<InstallPromptEvent | null>(null)
const installed = ref(false)

export function rememberInstallPrompt(event: Event) {
  event.preventDefault()
  installPrompt.value = event as InstallPromptEvent
}

export function markInstalled() {
  installed.value = true
  installPrompt.value = null
}

/** Opened from the home screen rather than in a browser tab. */
export function isStandalone(): boolean {
  if (!import.meta.client) return false
  return window.matchMedia?.('(display-mode: standalone)').matches ||
    (navigator as any).standalone === true
}

export function detectPlatform(userAgent = import.meta.client ? navigator.userAgent : ''): InstallPlatform {
  // In-app browsers first: WeChat on an iPhone still says iPhone, but its
  // menu has no "add to home screen", so the advice is different.
  if (/MicroMessenger/i.test(userAgent)) return 'wechat'
  if (/\bQQ\/|Weibo|DingTalk|Lark|Feishu|FBAN|FBAV|Instagram/i.test(userAgent)) return 'inapp'
  if (/iPhone|iPad|iPod/i.test(userAgent)) return 'ios'
  // iPadOS asks for the desktop site and says Macintosh; touch gives it away.
  if (import.meta.client && /Macintosh/i.test(userAgent) && navigator.maxTouchPoints > 1) return 'ios'
  if (/Android/i.test(userAgent)) return 'android'
  return 'desktop'
}

export function usePwa() {
  async function install(): Promise<boolean> {
    const event = installPrompt.value
    if (!event) return false
    installPrompt.value = null
    await event.prompt()
    const { outcome } = await event.userChoice
    if (outcome === 'accepted') installed.value = true
    return outcome === 'accepted'
  }

  return {
    canPrompt: computed(() => !!installPrompt.value),
    installed: readonly(installed),
    install
  }
}
