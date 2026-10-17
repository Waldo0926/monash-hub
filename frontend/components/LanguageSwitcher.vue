<script setup lang="ts">
/**
 * Language switcher.
 *
 * A native <select>: it is one tag, it is keyboard and screen-reader correct
 * without any work, and on a phone it opens the platform picker instead of a
 * custom menu that has to be re-tested on every device. Each language is
 * written in itself, because a switcher labelled in a language you cannot read
 * is not a switcher.
 */
import { LOCALES, type LocaleCode } from '~/i18n'

const { locale, setLocale } = useLocale()
const { $t } = useNuxtApp()

function onChange(event: Event) {
  const next = (event.target as HTMLSelectElement).value as LocaleCode
  if (next === locale.value) return
  setLocale(next)

  // A language change affects navigation assembled in composables as well as
  // text rendered directly in templates. Reload from the cookie so the whole
  // page is server-rendered in one locale; otherwise a stale hydrated header
  // can show English links beside a Chinese selector until the next visit.
  if (import.meta.client) window.location.reload()
}
</script>

<template>
  <div class="switcher">
    <PlanIcon name="globe" class="globe" />
    <label class="visually-hidden" for="language-switcher">{{ $t('nav.language') }}</label>
    <select
      id="language-switcher"
      class="select"
      :value="locale"
      @change="onChange"
    >
      <option v-for="option in LOCALES" :key="option.code" :value="option.code">
        {{ option.label }}
      </option>
    </select>
    <PlanIcon name="chevron-down" :size="14" class="caret" />
  </div>
</template>

<style scoped>
/* No box of its own: it sits in the header's account tray, so it only needs a
   globe in front and a caret behind. Both icons ignore the pointer, so a click
   anywhere on the row still opens the native picker. */
.switcher { position: relative; display: flex; align-items: center; color: var(--text); }
.globe, .caret { position: absolute; pointer-events: none; }
.globe { left: 10px; color: var(--muted); }
.caret { right: 8px; color: var(--muted); }
.select {
  appearance: none;
  -webkit-appearance: none;
  height: 32px;
  padding: 0 28px 0 32px;
  border: 0;
  border-radius: var(--radius-pill);
  background: transparent;
  color: inherit;
  font: inherit;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.15s;
}
/* The popup list is drawn by the platform, so its options get readable
   colours of their own rather than inheriting whatever the header uses. */
.select option { background: var(--surface); color: var(--text); }
.select:hover { background: rgba(12, 27, 42, 0.06); }
.select:focus-visible { outline-offset: 0; border-radius: var(--radius-pill); }
</style>
