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
  setLocale((event.target as HTMLSelectElement).value as LocaleCode)
}
</script>

<template>
  <div class="switcher">
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
  </div>
</template>

<style scoped>
.switcher { display: flex; align-items: center; }
.select {
  min-height: 36px;
  padding: 0 var(--s2);
  border: 1px solid rgba(255, 255, 255, 0.35);
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-inverse);
  font: inherit;
  font-size: 0.85rem;
  cursor: pointer;
}
/* The popup list is drawn by the platform, so its options need readable
   colours of their own rather than inheriting the dark header. */
.select option { background: var(--surface); color: var(--text); }
.select:hover { border-color: rgba(255, 255, 255, 0.6); }
</style>
