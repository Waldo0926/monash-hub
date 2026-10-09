<script setup lang="ts">
import type { NuxtError } from '#app'

const props = defineProps<{ error: NuxtError }>()
const { $t } = useNuxtApp()
const is404 = computed(() => props.error?.statusCode === 404)
</script>

<template>
  <!-- Inside the layout, so a wrong link still lands on a page with the
       header and the search box rather than a bare card. -->
  <NuxtLayout>
    <div class="container narrow">
      <div class="card section">
        <h1>{{ is404 ? $t('error.pageMissing') : $t('error.pageBroken') }}</h1>
        <p class="muted">{{ is404 ? $t('error.pageMissingHint') : $t('error.genericHint') }}</p>
        <div class="actions">
          <NuxtLink to="/" class="btn">{{ $t('error.goHome') }}</NuxtLink>
          <NuxtLink to="/search" class="btn btn--ghost">{{ $t('search.title') }}</NuxtLink>
        </div>
      </div>
    </div>
  </NuxtLayout>
</template>

<style scoped>
.narrow { max-width: 620px; margin-top: var(--s7); }
.section { padding: var(--s6); text-align: center; }
.actions { display: flex; gap: var(--s3); justify-content: center; flex-wrap: wrap; }
</style>
