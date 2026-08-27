<script setup lang="ts">
import { MAMO_ACCOUNT, MAMO_POSTS } from '~/data/mamo'

const { $t } = useNuxtApp()

// The logo lives in frontend/public/. The extension has to match what the file
// actually is - it arrived named .png and was a JPEG, which the server would
// have sent as image/png. Browsers sniff past that; not everything does.
// The wordmark takes over on an error, so a missing file shows a name rather
// than a broken image.
const avatar = '/mamo-avatar.jpg'
const avatarMissing = ref(false)

useSeoMeta({
  title: () => `${$t('mamo.title')} — Monash Hub`,
  description: MAMO_ACCOUNT.about
})

function formatted(date: string) {
  const [y, m, d] = date.split('-')
  return `${y}-${m}-${d}`
}
</script>

<template>
  <div class="container narrow">
    <header class="head">
      <img
        v-if="!avatarMissing"
        :src="avatar"
        class="avatar avatar--image"
        :alt="MAMO_ACCOUNT.name"
        @error="avatarMissing = true"
      >
      <div v-else class="avatar" aria-hidden="true">马莫</div>
      <div>
        <h1>{{ MAMO_ACCOUNT.name }}</h1>
        <p class="tiny muted">{{ MAMO_ACCOUNT.region }} · {{ $t('mamo.tagline') }}</p>
      </div>
    </header>

    <section class="card section">
      <h2 class="small">{{ $t('mamo.aboutHeading') }}</h2>
      <p>{{ MAMO_ACCOUNT.about }}</p>
      <p class="tiny muted meta">
        <span>{{ $t('mamo.channel') }}：{{ MAMO_ACCOUNT.channel }}</span>
        <span>{{ $t('mamo.originals', { n: MAMO_ACCOUNT.originals }) }}</span>
      </p>
      <p class="tiny muted">{{ $t('mamo.searchHint') }}</p>
      <p class="tiny muted">{{ $t('mamo.notOfficial') }}</p>
    </section>

    <h2 class="small heading">{{ $t('mamo.articlesHeading') }}</h2>
    <ul class="posts">
      <li v-for="post in MAMO_POSTS" :key="post.title" class="card post">
        <p class="tiny muted">{{ formatted(post.date) }}</p>
        <component
          :is="post.url ? 'a' : 'span'"
          :href="post.url || undefined"
          :target="post.url ? '_blank' : undefined"
          :rel="post.url ? 'noopener noreferrer' : undefined"
          class="post-title"
          :class="{ 'post-title--plain': !post.url }"
        >
          {{ post.title }}
        </component>
        <p v-if="post.summary" class="small muted">{{ post.summary }}</p>
        <p class="tiny muted meta">
          <span v-if="post.url" class="open">{{ $t('mamo.openInWeChat') }} ↗</span>
          <span v-else class="missing">{{ $t('mamo.noLink') }}</span>
        </p>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.narrow { max-width: 720px; }
.head { display: flex; align-items: center; gap: var(--s3); margin-bottom: var(--s4); }
.avatar--image { object-fit: cover; background: none; }
.avatar {
  display: grid;
  place-items: center;
  width: 52px; height: 52px;
  flex: none;
  border-radius: var(--radius-pill);
  background: var(--navy);
  color: var(--text-inverse);
  font-size: 0.85rem;
  font-weight: 700;
}
.head h1 { margin: 0; }
.section { padding: var(--s5); }
.heading { margin: var(--s5) 0 var(--s3); }
.posts { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--s3); }
.post { padding: var(--s4); }
.post-title {
  display: block;
  margin: var(--s1) 0 var(--s2);
  font-weight: 600;
  line-height: 1.45;
}
.post-title--plain { color: var(--text); }
.meta { display: flex; flex-wrap: wrap; gap: var(--s3); margin-top: var(--s2); }
.missing { font-style: italic; }
</style>
