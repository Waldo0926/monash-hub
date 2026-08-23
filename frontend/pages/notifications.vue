<script setup lang="ts">
const { $t } = useNuxtApp()
const { user, restore } = useAuth()
onMounted(restore)

useSeoMeta({ title: () => `${$t('notifications.title')} — Monash Hub`, robots: 'noindex' })
</script>

<template>
  <div class="container narrow">
    <h1>{{ $t('notifications.title') }}</h1>
    <NotificationPanel v-if="user" :limit="50" full />
    <div v-else class="card signed-out">
      <p class="small">{{ $t('community.signInToPost') }}</p>
      <NuxtLink to="/login" class="btn">{{ $t('community.signInCta') }}</NuxtLink>
    </div>
  </div>
</template>

<style scoped>
.narrow { max-width: 720px; }
.signed-out { padding: var(--s5); display: grid; gap: var(--s3); justify-items: start; }
</style>
