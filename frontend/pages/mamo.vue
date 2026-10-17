<script setup lang="ts">
import { MAMO_ACCOUNT, MAMO_POSTS, MAMO_TOPICS, type MamoPost, type MamoTopic } from '~/data/mamo'

const { $t } = useNuxtApp()

// The logo lives in frontend/public/. The extension has to match what the file
// actually is - it arrived named .png and was a JPEG, which the server would
// have sent as image/png. Browsers sniff past that; not everything does.
// The wordmark takes over on an error, so a missing file shows a name rather
// than a broken image.
const avatar = '/mamo-avatar.jpg'
const avatarMissing = ref(false)

useSeoMeta({
  title: () => $t('mamo.title'),
  description: MAMO_ACCOUNT.about
})

// MAMO_POSTS is newest first, so the first one is the featured post and also
// the date the account was last updated.
const latest = MAMO_POSTS[0]
const lastUpdated = latest?.date ?? ''

// Only offer a topic chip if at least one post has that topic, so a filter
// never leads to an empty list.
const topics = MAMO_TOPICS.filter(t => MAMO_POSTS.some(p => p.topic === t))
const topicCount = (t: MamoTopic) => MAMO_POSTS.filter(p => p.topic === t).length

const activeTopic = ref<MamoTopic | 'all'>('all')

// With no filter, the latest post is already shown big above, so the grid
// starts from the second one. With a filter on, the grid is the whole answer
// and includes it.
const listed = computed(() =>
  activeTopic.value === 'all'
    ? MAMO_POSTS.slice(1)
    : MAMO_POSTS.filter(p => p.topic === activeTopic.value)
)

// A cover that fails to load falls back to the topic tile, same as a post that
// never had one.
const brokenCovers = ref<string[]>([])
const hasCover = (post: MamoPost) => !!post.cover && !brokenCovers.value.includes(post.cover)
function coverFailed(post: MamoPost) {
  if (post.cover) brokenCovers.value.push(post.cover)
}

// Two ways in: the author's own WeChat, which is how people get into the group
// chat, and the official account itself. Each has a QR code for someone on a
// laptop, and a name to copy for someone already on their phone, who cannot
// scan a code on their own screen.
const contacts = computed(() => [
  {
    title: $t('mamo.groupTitle'),
    hint: $t('mamo.groupHint'),
    label: $t('mamo.wechatIdLabel'),
    value: MAMO_ACCOUNT.wechatId,
    mono: true,
    qr: '/img/mamo/qr-wechat.png',
    qrAlt: $t('mamo.groupQrAlt')
  },
  {
    title: $t('mamo.accountTitle'),
    hint: $t('mamo.accountHint'),
    label: $t('mamo.accountNameLabel'),
    value: MAMO_ACCOUNT.name,
    mono: false,
    qr: '/img/mamo/qr-official-account.png',
    qrAlt: $t('mamo.accountQrAlt')
  }
])

// Copy buttons for the two WeChat names. The text is selectable as well, so a
// browser that blocks the clipboard API still leaves a way to copy it.
const copied = ref<string | null>(null)
let copiedTimer: ReturnType<typeof setTimeout> | undefined
async function copy(text: string) {
  try {
    await navigator.clipboard.writeText(text)
    copied.value = text
    clearTimeout(copiedTimer)
    copiedTimer = setTimeout(() => { copied.value = null }, 2000)
  } catch {
    copied.value = null
  }
}
onBeforeUnmount(() => clearTimeout(copiedTimer))
</script>

<template>
  <div class="container mamo">
    <section class="hero">
      <div class="hero-main">
        <div class="identity">
          <img
            v-if="!avatarMissing"
            :src="avatar"
            class="avatar avatar--image"
            :alt="MAMO_ACCOUNT.name"
            width="72"
            height="72"
            @error="avatarMissing = true"
          >
          <div v-else class="avatar" aria-hidden="true">马莫</div>
          <div>
            <h1>{{ MAMO_ACCOUNT.name }}</h1>
            <p class="small muted tagline">{{ MAMO_ACCOUNT.region }} · {{ $t('mamo.tagline') }}</p>
          </div>
        </div>
        <p class="about">{{ MAMO_ACCOUNT.about }}</p>
        <ul class="stats small">
          <li><strong>{{ MAMO_POSTS.length }}</strong> {{ $t('mamo.postCount') }}</li>
          <li>{{ $t('mamo.channel') }}：{{ MAMO_ACCOUNT.channel }}</li>
          <li v-if="lastUpdated">{{ $t('mamo.updated') }} <span class="mono">{{ lastUpdated }}</span></li>
        </ul>
      </div>

      <!-- The footer links here with #follow. -->
      <aside id="follow" class="follow card" :aria-label="$t('mamo.followHeading')">
        <h2 class="follow-heading">{{ $t('mamo.followHeading') }}</h2>
        <div v-for="c in contacts" :key="c.value" class="follow-row">
          <img :src="c.qr" :alt="c.qrAlt" class="qr" width="112" height="112" loading="lazy">
          <div class="follow-text">
            <h3 class="follow-title">{{ c.title }}</h3>
            <p class="tiny muted">{{ c.hint }}</p>
            <p class="id small">
              <span class="muted">{{ c.label }}</span>
              <span class="value" :class="{ mono: c.mono }">{{ c.value }}</span>
              <button type="button" class="copy" @click="copy(c.value)">
                {{ copied === c.value ? $t('mamo.copied') : $t('mamo.copy') }}
              </button>
            </p>
          </div>
        </div>
        <p class="tiny muted note">{{ $t('mamo.notOfficial') }}</p>
        <!-- Announces the copy result to screen readers; the button label
             changing is not read out on its own. -->
        <span class="visually-hidden" aria-live="polite">{{ copied ? $t('mamo.copied') : '' }}</span>
      </aside>
    </section>

    <section v-if="latest" class="block">
      <h2 class="block-heading">{{ $t('mamo.latest') }}</h2>
      <component
        :is="latest.url ? 'a' : 'div'"
        :href="latest.url || undefined"
        :target="latest.url ? '_blank' : undefined"
        :rel="latest.url ? 'noopener noreferrer' : undefined"
        class="featured card"
      >
        <div class="cover cover--featured">
          <img
            v-if="hasCover(latest)"
            :src="latest.cover"
            alt=""
            width="720"
            height="306"
            @error="coverFailed(latest)"
          >
          <div v-else class="cover-tile" aria-hidden="true">
            <span>{{ $t(`mamo.topic.${latest.topic}`) }}</span>
          </div>
        </div>
        <div class="featured-body">
          <p class="post-meta tiny">
            <span class="badge badge--new">{{ $t('mamo.new') }}</span>
            <span class="topic">{{ $t(`mamo.topic.${latest.topic}`) }}</span>
            <span class="mono muted">{{ latest.date }}</span>
          </p>
          <h3 class="featured-title">{{ latest.title }}</h3>
          <p v-if="latest.summary" class="small muted">{{ latest.summary }}</p>
          <span v-if="latest.url" class="read small">{{ $t('mamo.openInWeChat') }} ↗</span>
          <span v-else class="tiny muted missing">{{ $t('mamo.noLink') }}</span>
        </div>
      </component>
    </section>

    <section class="block">
      <div class="list-head">
        <h2 class="block-heading">{{ $t('mamo.articlesHeading') }}</h2>
        <div class="chips" role="group" :aria-label="$t('mamo.filterLabel')">
          <button
            type="button"
            class="chip"
            :aria-pressed="activeTopic === 'all'"
            @click="activeTopic = 'all'"
          >
            {{ $t('mamo.allTopics') }} <span class="count">{{ MAMO_POSTS.length }}</span>
          </button>
          <button
            v-for="t in topics"
            :key="t"
            type="button"
            class="chip"
            :aria-pressed="activeTopic === t"
            @click="activeTopic = t"
          >
            {{ $t(`mamo.topic.${t}`) }} <span class="count">{{ topicCount(t) }}</span>
          </button>
        </div>
      </div>

      <ul class="grid">
        <li v-for="post in listed" :key="post.title">
          <component
            :is="post.url ? 'a' : 'div'"
            :href="post.url || undefined"
            :target="post.url ? '_blank' : undefined"
            :rel="post.url ? 'noopener noreferrer' : undefined"
            class="post card"
          >
            <div class="cover">
              <img
                v-if="hasCover(post)"
                :src="post.cover"
                alt=""
                width="720"
                height="306"
                loading="lazy"
                @error="coverFailed(post)"
              >
              <div v-else class="cover-tile" aria-hidden="true">
                <span>{{ $t(`mamo.topic.${post.topic}`) }}</span>
              </div>
            </div>
            <div class="post-body">
              <p class="post-meta tiny">
                <span class="topic">{{ $t(`mamo.topic.${post.topic}`) }}</span>
                <span class="mono muted">{{ post.date }}</span>
              </p>
              <h3 class="post-title">{{ post.title }}</h3>
              <p v-if="post.summary" class="tiny muted summary">{{ post.summary }}</p>
              <span v-if="post.url" class="read tiny">{{ $t('mamo.openInWeChat') }} ↗</span>
              <span v-else class="tiny muted missing">{{ $t('mamo.noLink') }}</span>
            </div>
          </component>
        </li>
      </ul>
    </section>
  </div>
</template>

<style scoped>
.mamo { max-width: 1040px; padding-bottom: var(--s7); }

/* --- hero ---------------------------------------------------------------- */
.hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 380px;
  gap: var(--s5);
  align-items: center;
  padding: var(--s6);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: linear-gradient(135deg, var(--blue-50), var(--surface) 70%);
}
.identity { display: flex; align-items: center; gap: var(--s4); margin-bottom: var(--s4); }
.identity h1 { margin: 0; }
.tagline { margin: var(--s1) 0 0; }
.avatar {
  display: grid;
  place-items: center;
  width: 72px; height: 72px;
  flex: none;
  border-radius: var(--radius-pill);
  background: var(--navy);
  color: var(--text-inverse);
  font-size: 0.95rem;
  font-weight: 700;
  box-shadow: 0 0 0 4px var(--surface), var(--shadow);
}
.avatar--image { object-fit: cover; background: var(--surface); }
.about { max-width: var(--measure); margin-bottom: var(--s4); }
.stats {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s2);
  margin: 0;
  padding: 0;
  list-style: none;
}
.stats li {
  padding: var(--s1) var(--s3);
  border: 1px solid var(--border);
  border-radius: var(--radius-pill);
  background: var(--surface);
  color: var(--muted);
}
.stats strong { color: var(--text); }

.follow {
  padding: var(--s5);
  scroll-margin-top: calc(var(--header-h, 64px) + var(--s4));
}
.follow-heading { margin-bottom: var(--s3); font-size: 1.05rem; }
.follow-row {
  display: flex;
  align-items: center;
  gap: var(--s4);
  padding: var(--s4) 0;
  border-top: 1px solid var(--border);
}
.follow-row p { margin: 0; }
.qr {
  flex: none;
  width: 112px;
  height: 112px;
  padding: var(--s1);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface);
}
.follow-text { min-width: 0; }
.follow-title { margin: 0 0 var(--s1); font-size: 0.95rem; }
.id { display: flex; flex-wrap: wrap; align-items: baseline; gap: var(--s2); margin-top: var(--s2) !important; }
.value { font-weight: 600; user-select: all; }
.copy {
  padding: 0;
  border: 0;
  background: none;
  color: var(--blue-700);
  font: inherit;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
}
.copy:hover { text-decoration: underline; }
.note { margin: var(--s3) 0 0; padding-top: var(--s3); border-top: 1px solid var(--border); }

/* --- sections ------------------------------------------------------------ */
.block { margin-top: var(--s7); }
.block-heading { margin-bottom: var(--s4); }
.list-head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--s3);
  margin-bottom: var(--s4);
}
.list-head .block-heading { margin: 0; }

.chips { display: flex; flex-wrap: wrap; gap: var(--s2); }
.chip {
  min-height: 36px;
  padding: 0 var(--s3);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-pill);
  background: var(--surface);
  color: var(--text);
  font: inherit;
  font-size: 0.875rem;
  cursor: pointer;
}
.chip:hover { background: var(--surface-2); }
.chip[aria-pressed='true'] { background: var(--ink); border-color: var(--ink); color: var(--text-inverse); }
.chip .count { margin-left: var(--s1); opacity: 0.65; font-variant-numeric: tabular-nums; }

/* --- covers -------------------------------------------------------------- */
/* WeChat covers are 2.35:1. Keeping that ratio means the title text most
   covers have on them is not cropped off. */
.cover {
  aspect-ratio: 2.35 / 1;
  overflow: hidden;
  background: var(--surface-2);
}
.cover img { display: block; width: 100%; height: 100%; object-fit: cover; }
.cover-tile {
  display: grid;
  place-items: center;
  height: 100%;
  background: linear-gradient(135deg, var(--navy), var(--brand));
  color: var(--text-inverse);
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 600;
}

/* --- featured post ------------------------------------------------------- */
.featured {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr);
  overflow: hidden;
  color: inherit;
}
a.featured:hover { text-decoration: none; border-color: var(--border-strong); box-shadow: var(--shadow); }
.cover--featured { aspect-ratio: auto; min-height: 100%; }
.cover--featured img { aspect-ratio: 2.35 / 1; }
.featured-body { display: flex; flex-direction: column; justify-content: center; padding: var(--s5); }
.featured-title {
  margin: var(--s2) 0 var(--s3);
  font-family: var(--font-display);
  font-size: clamp(1.1rem, 1rem + 0.5vw, 1.35rem);
  line-height: 1.4;
}

/* --- post grid ----------------------------------------------------------- */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: var(--s4);
  margin: 0;
  padding: 0;
  list-style: none;
}
.post {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  color: inherit;
  transition: box-shadow 0.15s ease, transform 0.15s ease;
}
a.post:hover { text-decoration: none; border-color: var(--border-strong); box-shadow: var(--shadow); transform: translateY(-2px); }
.post-body { display: flex; flex-direction: column; flex: 1; padding: var(--s4); }
.post-title {
  margin: var(--s2) 0;
  font-size: 0.98rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.summary {
  margin-bottom: var(--s3);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* --- shared bits --------------------------------------------------------- */
.post-meta { display: flex; flex-wrap: wrap; align-items: center; gap: var(--s2); margin: 0; }
.topic {
  padding: 1px var(--s2);
  border-radius: var(--radius-pill);
  background: var(--blue-50);
  color: var(--blue-700);
  font-weight: 600;
}
.badge--new {
  padding: 1px var(--s2);
  border-radius: var(--radius-pill);
  background: var(--warning-bg);
  color: var(--soon);
  font-weight: 700;
}
.read { margin-top: auto; color: var(--blue-700); font-weight: 600; }
.featured .read { margin-top: var(--s2); }
.missing { margin-top: auto; font-style: italic; }

@media (prefers-reduced-motion: reduce) {
  .post { transition: none; }
  a.post:hover { transform: none; }
}

@media (max-width: 860px) {
  .hero { grid-template-columns: 1fr; padding: var(--s5); }
  .featured { grid-template-columns: 1fr; }
  .cover--featured { aspect-ratio: 2.35 / 1; min-height: 0; }
}
@media (max-width: 480px) {
  .hero { padding: var(--s4); }
  .follow { padding: var(--s4); }
  .qr { width: 92px; height: 92px; }
  .identity { gap: var(--s3); }
  .avatar { width: 56px; height: 56px; }
}
</style>
