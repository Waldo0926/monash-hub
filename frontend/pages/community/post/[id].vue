<script setup lang="ts">
const route = useRoute()
const { $t } = useNuxtApp()
const { user, restore } = useAuth()
onMounted(restore)

const id = computed(() => Number(route.params.id))
const { data: post, error, refresh } = await useApiFetch<any>(() => `/v1/community/posts/${id.value}`)

// The server renders this page as a signed-out reader sees it, because the
// token is in localStorage and the server cannot read it. Once the session is
// restored, ask again with it: that is what fills in your own likes and tells
// you which anonymous post was yours.
watch(user, (signedIn) => {
  if (signedIn) refresh()
})

const reply = ref('')
const replyAnonymously = ref(false)
const busy = ref(false)
const notice = ref('')

/**
 * Every write goes through here.
 *
 * The like button did nothing at all for a signed-out reader: apiFetch throws
 * on the 401 and nobody was catching it, so the click was swallowed and the
 * heart never moved. A button that ignores you is worse than one that tells
 * you to sign in.
 */
async function send(work: () => Promise<unknown>) {
  if (!user.value) {
    notice.value = $t('community.signInFirst')
    return false
  }
  busy.value = true
  notice.value = ''
  try {
    await work()
    await refresh()
    return true
  } catch (failure: any) {
    notice.value = failure?.data?.detail || $t('community.actionFailed')
    return false
  } finally {
    busy.value = false
  }
}

async function answer() {
  if (!reply.value.trim()) return
  const ok = await send(() =>
    apiFetch(`/v1/community/posts/${id.value}/answers`, {
      method: 'POST',
      body: { body: reply.value, anonymous: replyAnonymously.value }
    })
  )
  if (ok) {
    reply.value = ''
    replyAnonymously.value = false
  }
}

async function replyTo(payload: { parentId: number; body: string; anonymous: boolean }) {
  await send(() =>
    apiFetch(`/v1/community/posts/${id.value}/answers`, {
      method: 'POST',
      body: { body: payload.body, parent_id: payload.parentId, anonymous: payload.anonymous }
    })
  )
}

async function vote(targetType: string, targetId: number) {
  await send(() =>
    apiFetch(`/v1/community/vote?target_type=${targetType}&target_id=${targetId}`, {
      method: 'POST'
    })
  )
}

async function accept(answerId: number) {
  await send(() => apiFetch(`/v1/community/answers/${answerId}/accept`, { method: 'POST' }))
}

async function report(targetType: string, targetId: number) {
  const ok = await send(() =>
    apiFetch('/v1/community/reports', {
      method: 'POST',
      body: { target_type: targetType, target_id: targetId, reason: 'other' }
    })
  )
  if (ok) notice.value = $t('community.reported')
}

const askedByMe = computed(() => Boolean(user.value) && post.value?.is_mine)

const poster = computed(() => {
  if (!post.value) return ''
  if (!post.value.anonymous) return post.value.author
  return post.value.is_mine ? $t('community.anonymousMine') : $t('community.anonymous')
})

useSeoMeta({
  title: () => (post.value ? `${post.value.title} — Monash Hub` : $t('community.title'))
})
</script>

<template>
  <div class="container narrow">
    <ErrorState v-if="error" :error="error" />

    <article v-else-if="post">
      <p class="tiny muted">
        <NuxtLink to="/community">{{ $t('community.title') }}</NuxtLink> /
        {{ $t(`communityCategory.${post.category}`) }}
      </p>

      <header class="card section">
        <div class="head-top">
          <h1>{{ post.title }}</h1>
          <SourceBadge kind="community" />
        </div>
        <p class="tiny muted">
          {{ $t('community.by') }}
          <span :class="{ anon: post.anonymous }">{{ poster }}</span> ·
          {{ post.answer_count === 1
            ? $t('community.answersOne')
            : $t('community.answers', { count: post.answer_count }) }}
          <span v-if="post.unit_code">
            · <NuxtLink :to="`/units/${post.unit_code}`" class="mono">{{ post.unit_code }}</NuxtLink>
          </span>
        </p>
        <p class="pre">{{ post.body }}</p>
        <p class="callout tiny">{{ $t('community.experienceNote') }}</p>
        <div class="actions">
          <button
            class="like"
            :class="{ 'like--on': post.viewer_voted }"
            type="button"
            :aria-pressed="post.viewer_voted"
            @click="vote('post', post.id)"
          >{{ post.viewer_voted ? '♥' : '♡' }} {{ post.vote_count }}</button>
          <button class="btn btn--ghost btn--small" @click="report('post', post.id)">
            {{ $t('community.report') }}
          </button>
        </div>
      </header>

      <h2 class="answers-title">
        {{ post.answers.length === 1
          ? $t('community.answersOne')
          : $t('community.answers', { count: post.answers.length }) }}
      </h2>
      <div class="stack">
        <div v-for="a in post.answers" :key="a.id" class="card section">
          <CommunityReply
            :reply="a"
            :depth="0"
            :can-accept="askedByMe"
            :signed-in="Boolean(user)"
            :busy="busy"
            @vote="vote('answer', $event)"
            @accept="accept"
            @report="report('answer', $event)"
            @reply="replyTo"
          />
        </div>
      </div>

      <p v-if="notice" class="notice small">{{ notice }}</p>

      <section class="card section reply">
        <h2>{{ $t('community.yourAnswer') }}</h2>
        <template v-if="user">
          <textarea
            v-model="reply"
            class="field body"
            rows="4"
            :placeholder="$t('community.answerPlaceholder')"
          />
          <label class="anon-check">
            <input v-model="replyAnonymously" type="checkbox" />
            <span>{{ $t('community.postAnonymously') }}</span>
          </label>
          <button class="btn" :disabled="busy" @click="answer">
            {{ busy ? $t('community.posting') : $t('community.postAnswer') }}
          </button>
        </template>
        <template v-else>
          <p class="small">{{ $t('community.signInToAnswer') }}</p>
          <NuxtLink to="/login" class="btn">{{ $t('nav.signIn') }}</NuxtLink>
        </template>
      </section>
    </article>
  </div>
</template>

<style scoped>
.anon { font-style: italic; }
.anon-check {
  display: flex; gap: var(--s2); align-items: center;
  font-size: 0.85rem; color: var(--muted); margin: var(--s2) 0;
}
.like {
  border: 1px solid var(--border-strong); background: var(--surface); color: var(--muted);
  border-radius: var(--radius-pill); padding: var(--s1) var(--s3); font: inherit;
  font-size: 0.82rem; cursor: pointer;
}
.like--on { color: var(--danger); border-color: var(--danger); background: var(--danger-bg); }
.like:hover { border-color: var(--danger); }

.narrow { max-width: 820px; }
.section { padding: var(--s5); }
.head-top { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--s4); }
.pre { white-space: pre-line; }
.callout {
  padding: var(--s3);
  border-radius: var(--radius-sm);
  background: var(--badge-community-bg);
  color: var(--badge-community);
}
.actions { display: flex; gap: var(--s2); flex-wrap: wrap; }
.answers-title { margin: var(--s6) 0 var(--s3); font-size: 1.05rem; }
.accepted { border-color: var(--success); }
.accepted-tag { color: var(--success); font-weight: 600; }
.reply { margin-top: var(--s5); display: grid; gap: var(--s3); justify-items: start; }
.body { min-height: 110px; padding: var(--s3); font-family: inherit; }
.notice { color: var(--success); }
</style>
