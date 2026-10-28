<script setup lang="ts">
/**
 * The 马莫百科 block on the home page: what the account is, a few of its real
 * posts, and a way to follow it.
 *
 * Everything comes from data/mamo.ts, the same file the /mamo page reads, so the
 * two cannot drift apart. The QR code is the account's own one from /mamo#follow.
 * Nothing here is a pop-up or a gate: a student who only came to look up a unit
 * scrolls past it.
 *
 * A phone cannot scan a code on its own screen, so the follow panel also carries
 * the account name with a copy button. Inside WeChat's browser a long press on
 * the code does work, and the hint says so on touch screens.
 */
import { MAMO_ACCOUNT, MAMO_POSTS } from '~/data/mamo'
import { translate } from '~/i18n'

// The parents page is Chinese whatever the interface language is.
const props = defineProps<{ zh?: boolean }>()
const { $t } = useNuxtApp()
const t = (key: string) => (props.zh ? translate('zh', key) : $t(key))

// Every title starts with the account name; on the home page it is already in
// the heading above, so the list reads better without it.
const recent = MAMO_POSTS.slice(0, 3).map(post => ({
  ...post,
  short: post.title.replace(/^马莫百科[｜|]\s*/, '')
}))

const copied = ref(false)
let copiedTimer: ReturnType<typeof setTimeout> | undefined
async function copyName() {
  try {
    await navigator.clipboard.writeText(MAMO_ACCOUNT.name)
    copied.value = true
    clearTimeout(copiedTimer)
    copiedTimer = setTimeout(() => { copied.value = false }, 2000)
  } catch {
    // The name is selectable text, so a blocked clipboard still leaves a way.
    copied.value = false
  }
}
onBeforeUnmount(() => clearTimeout(copiedTimer))
</script>

<template>
  <section class="mamo-intro" aria-labelledby="mamo-intro-title">
    <div class="about">
      <p class="eyebrow">
        <img src="/mamo-avatar.jpg" alt="" width="28" height="28" class="avatar">
        <span>{{ t('home.mamo.eyebrow') }}</span>
      </p>
      <h2 id="mamo-intro-title">{{ t('home.mamo.title') }}</h2>
      <p class="body">{{ t('home.mamo.body') }}</p>

      <h3 class="recent-title">{{ t('home.mamo.recent') }}</h3>
      <ul class="recent">
        <li v-for="post in recent" :key="post.title">
          <a
            v-if="post.url"
            :href="post.url"
            target="_blank"
            rel="noopener noreferrer"
            lang="zh-CN"
          >
            <span class="date mono">{{ post.date.slice(5) }}</span>
            <span class="post-title">{{ post.short }}</span>
          </a>
          <span v-else lang="zh-CN">
            <span class="date mono">{{ post.date.slice(5) }}</span>
            <span class="post-title">{{ post.short }}</span>
          </span>
        </li>
      </ul>

      <div class="actions">
        <NuxtLink to="/mamo" class="btn">{{ t('home.mamo.open') }}</NuxtLink>
        <NuxtLink to="/mamo#follow" class="ask small">{{ t('home.mamo.ask') }} →</NuxtLink>
      </div>
    </div>

    <div class="follow">
      <!-- Opening the image on its own gives a phone a full-size code to zoom
           or save, without a pop-up of our own. -->
      <a href="/img/mamo/qr-official-account.png" target="_blank" class="qr-link">
        <img
          src="/img/mamo/qr-official-account.png"
          :alt="t('mamo.accountQrAlt')"
          width="160"
          height="160"
          class="qr"
          loading="lazy"
        >
      </a>
      <div class="follow-text">
        <h3 class="follow-title">{{ t('mamo.accountTitle') }}</h3>
        <p class="name">
          <span class="value">{{ MAMO_ACCOUNT.name }}</span>
          <button type="button" class="copy" @click="copyName">
            {{ copied ? t('mamo.copied') : t('mamo.copy') }}
          </button>
        </p>
        <p class="hint tiny muted hint--desktop">{{ t('home.mamo.scanDesktop') }}</p>
        <p class="hint tiny muted hint--touch">{{ t('home.mamo.scanPhone') }}</p>
      </div>
      <span class="visually-hidden" aria-live="polite">{{ copied ? t('mamo.copied') : '' }}</span>
    </div>
  </section>
</template>

<style scoped>
/* A band of its own rather than one more tile: light blue on the left for what
   the account is, a white panel on the right for following it. */
.mamo-intro {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 340px);
  gap: var(--s6);
  align-items: center;
  padding: clamp(20px, 3vw, 36px);
  border: 1px solid var(--border);
  border-radius: 16px;
  background: linear-gradient(120deg, var(--blue-50), var(--surface) 75%);
}

.eyebrow {
  display: flex;
  align-items: center;
  gap: var(--s2);
  margin: 0 0 var(--s3);
  color: var(--muted-2);
  font-size: 0.8rem;
  letter-spacing: 0.04em;
}
.avatar { flex: none; width: 28px; height: 28px; border-radius: 50%; object-fit: cover; box-shadow: 0 0 0 2px var(--surface); }
h2 {
  margin: 0 0 var(--s3);
  font-size: clamp(1.4rem, 1.1rem + 1vw, 1.9rem);
  line-height: 1.25;
  letter-spacing: -0.01em;
}
.body { max-width: 36em; margin: 0 0 var(--s5); color: var(--muted); }

.recent-title {
  margin: 0 0 var(--s2);
  color: var(--muted-2);
  font-family: var(--font);
  font-size: 0.8rem;
  font-weight: 400;
  letter-spacing: 0.04em;
}
.recent { margin: 0 0 var(--s5); padding: 0; list-style: none; border-top: 1px solid var(--border); }
.recent li { border-bottom: 1px solid var(--border); }
.recent a, .recent li > span {
  display: grid;
  grid-template-columns: 3.4em minmax(0, 1fr);
  gap: var(--s3);
  align-items: baseline;
  padding: 10px 0;
  color: inherit;
}
.recent a:hover { text-decoration: none; }
.recent a:hover .post-title { color: var(--brand); }
.date { color: var(--muted-2); font-size: 0.8rem; font-variant-numeric: tabular-nums; }
.post-title {
  font-size: 0.95rem;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.actions { display: flex; flex-wrap: wrap; align-items: center; gap: var(--s3) var(--s5); }
.ask { color: var(--brand); font-weight: 500; }

.follow {
  display: grid;
  justify-items: center;
  gap: var(--s3);
  padding: var(--s5);
  border: 1px solid var(--border);
  border-radius: 14px;
  background: var(--surface);
  box-shadow: var(--shadow-sm);
  text-align: center;
}
.qr-link { display: block; line-height: 0; border-radius: var(--radius-sm); }
.qr {
  width: 160px;
  height: 160px;
  padding: var(--s2);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: #fff;
}
.follow-text p { margin: 0; }
.follow-title { margin: 0 0 var(--s1); font-family: var(--font); font-size: 0.95rem; font-weight: 600; }
.name { display: flex; justify-content: center; align-items: baseline; gap: var(--s2); margin-bottom: var(--s2) !important; }
.value { font-weight: 600; user-select: all; }
.copy {
  min-height: 32px;
  padding: 0 var(--s3);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-pill);
  background: var(--surface);
  color: var(--blue-700);
  font: inherit;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
}
.copy:hover { background: var(--surface-2); }
.hint:lang(ko), .body:lang(ko) { word-break: keep-all; }
.hint--touch { display: none; }

/* Touch screens get the long-press hint instead of "scan with WeChat". */
@media (hover: none) and (pointer: coarse) {
  .hint--desktop { display: none; }
  .hint--touch { display: block; }
}

@media (max-width: 860px) {
  .mamo-intro { grid-template-columns: 1fr; gap: var(--s5); }
}
@media (max-width: 560px) {
  .follow {
    grid-template-columns: 112px minmax(0, 1fr);
    justify-items: start;
    align-items: start;
    padding: var(--s4);
    text-align: left;
  }
  .qr { width: 112px; height: 112px; padding: var(--s1); }
  .name { justify-content: flex-start; }
}
</style>
