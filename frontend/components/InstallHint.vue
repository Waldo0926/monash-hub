<script setup lang="ts">
/**
 * A one-line suggestion to add the site to the home screen.
 *
 * Kept out of the way on purpose: phones only, not on the first pages someone
 * reads (they came for an answer, not an app), never inside the installed app,
 * and "don't show again" means never. The same steps are always in the footer
 * for anyone who closed this and changes their mind.
 */
const STORAGE_KEY = 'mh_install_hint'
const SHOW_AFTER_VIEWS = 3

const route = useRoute()
const { installed } = usePwa()
const visible = ref(false)
const open = ref(false)

interface HintState { views: number, hidden: boolean }

function read(): HintState {
  try {
    const saved = JSON.parse(window.localStorage.getItem(STORAGE_KEY) || '{}')
    return { views: Number(saved.views) || 0, hidden: saved.hidden === true }
  } catch {
    return { views: 0, hidden: false }
  }
}

function write(state: HintState) {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  } catch {
    // Storage blocked: the hint just shows again next time.
  }
}

function countView() {
  const state = read()
  if (state.hidden) return
  state.views += 1
  write(state)
  visible.value = state.views >= SHOW_AFTER_VIEWS
}

function hide() {
  write({ ...read(), hidden: true })
  visible.value = false
}

onMounted(() => {
  // Offline is the wrong moment to suggest anything that needs the network.
  if (isStandalone() || detectPlatform() === 'desktop' || !navigator.onLine) return
  countView()
  watch(() => route.path, countView)
})
</script>

<template>
  <aside v-if="visible && !installed" class="container install-hint" :aria-label="$t('pwa.footerTitle')">
    <div class="hint">
      <AppLogo :size="28" tone="onLight" class="logo" />
      <p class="small text">{{ $t('pwa.hint') }}</p>
      <div class="actions">
        <button type="button" class="btn btn--small" :aria-expanded="open" @click="open = !open">
          {{ $t('pwa.how') }}
        </button>
        <button type="button" class="btn btn--small btn--ghost" @click="hide">{{ $t('pwa.hide') }}</button>
      </div>
      <InstallSteps v-if="open" class="steps" />
    </div>
  </aside>
</template>

<style scoped>
.install-hint { margin-bottom: var(--s5); }
.hint {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: var(--s3);
  align-items: start;
  padding: var(--s3) var(--s4);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--blue-50);
}
.text { margin: 0; align-self: center; }
.actions { grid-column: 1 / -1; display: flex; flex-wrap: wrap; gap: var(--s2); }
.steps { grid-column: 1 / -1; }
</style>
