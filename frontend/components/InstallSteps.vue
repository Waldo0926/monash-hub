<script setup lang="ts">
/**
 * How to put the site on this phone's home screen.
 *
 * Where the browser offers its own install dialog (Chrome on Android), one
 * button opens it. Everywhere else it is the browser's menu, so the steps name
 * the menu for the browser the reader is actually in. Worked out after mount:
 * the server cannot see which phone it is talking to.
 */
import type { InstallPlatform } from '~/composables/usePwa'

const { $t } = useNuxtApp()
const { canPrompt, install } = usePwa()
const platform = ref<InstallPlatform | null>(null)
onMounted(() => { platform.value = detectPlatform() })

const STEP_COUNT: Record<InstallPlatform, number> = { ios: 3, android: 3, wechat: 2, inapp: 1, desktop: 1 }
const steps = computed(() => {
  const p = platform.value
  if (!p) return []
  return Array.from({ length: STEP_COUNT[p] }, (_, i) => $t(`pwa.${p}.${i + 1}`))
})
</script>

<template>
  <div v-if="platform" class="install-steps">
    <template v-if="canPrompt">
      <p class="small">{{ $t('pwa.installIntro') }}</p>
      <button type="button" class="btn btn--small" @click="install">{{ $t('pwa.installButton') }}</button>
    </template>
    <ol v-else class="small steps">
      <li v-for="step in steps" :key="step">{{ step }}</li>
    </ol>
  </div>
</template>

<style scoped>
.install-steps p { margin: 0 0 var(--s3); }
.steps { margin: 0; padding-left: 1.25em; }
.steps li + li { margin-top: var(--s1); }
</style>
