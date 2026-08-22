<script setup lang="ts">
const route = useRoute()
const { user, restore } = useAuth()
onMounted(restore)

const id = computed(() => Number(route.params.id))
const { data: post, error, refresh } = await useApiFetch<any>(() => `/v1/community/posts/${id.value}`)

const reply = ref('')
const busy = ref(false)
const notice = ref('')

async function answer() {
  if (!reply.value.trim()) return
  busy.value = true
  try {
    await apiFetch(`/v1/community/posts/${id.value}/answers`, {
      method: 'POST',
      body: { body: reply.value }
    })
    reply.value = ''
    await refresh()
  } finally {
    busy.value = false
  }
}

async function vote(targetType: string, targetId: number) {
  await apiFetch(`/v1/community/vote?target_type=${targetType}&target_id=${targetId}`, { method: 'POST' })
  await refresh()
}

async function accept(answerId: number) {
  await apiFetch(`/v1/community/answers/${answerId}/accept`, { method: 'POST' })
  await refresh()
}

async function report(targetType: string, targetId: number) {
  await apiFetch('/v1/community/reports', {
    method: 'POST',
    body: { target_type: targetType, target_id: targetId, reason: 'other' }
  })
  notice.value = 'Reported. A moderator will look at it.'
}

useSeoMeta({ title: () => (post.value ? `${post.value.title} — Monash Hub Community` : 'Community') })
</script>

<template>
  <div class="container narrow">
    <ErrorState v-if="error" :error="error" />

    <article v-else-if="post">
      <p class="tiny muted"><NuxtLink to="/community">Community</NuxtLink> / {{ post.category }}</p>

      <header class="card section">
        <div class="head-top">
          <h1>{{ post.title }}</h1>
          <SourceBadge kind="community" />
        </div>
        <p class="tiny muted">
          {{ post.author }} · {{ post.answer_count }} answers
          <span v-if="post.unit_code">
            · <NuxtLink :to="`/units/${post.unit_code}`" class="mono">{{ post.unit_code }}</NuxtLink>
          </span>
        </p>
        <p class="pre">{{ post.body }}</p>
        <p class="callout tiny">
          This is student experience, not an official Monash rule. Check
          <NuxtLink to="/guides">Official guides</NuxtLink> or the Handbook before you act on it.
        </p>
        <div class="actions">
          <button class="btn btn--ghost btn--small" @click="vote('post', post.id)">
            ♡ {{ post.vote_count }}
          </button>
          <button class="btn btn--ghost btn--small" @click="report('post', post.id)">Report</button>
        </div>
      </header>

      <h2 class="answers-title">{{ post.answers.length }} answers</h2>
      <div class="stack">
        <article v-for="a in post.answers" :key="a.id" class="card section" :class="{ accepted: a.is_accepted }">
          <p class="tiny muted">
            {{ a.author }}
            <span v-if="a.is_accepted" class="accepted-tag"> · marked helpful by the asker</span>
          </p>
          <p class="pre">{{ a.body }}</p>
          <div class="actions">
            <button class="btn btn--ghost btn--small" @click="vote('answer', a.id)">♡ {{ a.vote_count }}</button>
            <button
              v-if="user && !a.is_accepted"
              class="btn btn--ghost btn--small"
              @click="accept(a.id)"
            >
              Mark helpful
            </button>
            <button class="btn btn--ghost btn--small" @click="report('answer', a.id)">Report</button>
          </div>
        </article>
      </div>

      <p v-if="notice" class="notice small">{{ notice }}</p>

      <section class="card section reply">
        <h2>Your answer</h2>
        <template v-if="user">
          <textarea v-model="reply" class="field body" rows="4" placeholder="Share what you actually experienced." />
          <button class="btn" :disabled="busy" @click="answer">
            {{ busy ? 'Posting…' : 'Post answer' }}
          </button>
        </template>
        <template v-else>
          <p class="small">Sign in to answer. Reading stays open to everyone.</p>
          <NuxtLink to="/login" class="btn">Sign in</NuxtLink>
        </template>
      </section>
    </article>
  </div>
</template>

<style scoped>
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
