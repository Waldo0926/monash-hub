<script setup lang="ts">
import { LOCALES } from '~/i18n'

// <html lang> follows the switcher. Screen readers pick pronunciation from it,
// and search engines use it to decide who a page is for.
const { locale } = useLocale()
const htmlLang = computed(
  () => LOCALES.find(option => option.code === locale.value)?.htmlLang ?? 'en'
)
useHead({ htmlAttrs: { lang: htmlLang } })
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
