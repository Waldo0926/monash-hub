<script setup lang="ts">
/**
 * Your own account.
 *
 * Clicking your name used to go to the community, which answered a question
 * nobody asked: what the name is for is finding your way back to what *you*
 * wrote. So this is the page it goes to now — your picture, your bio, and the
 * three lists that were previously unreachable, because a question you asked
 * last month could only be found by scrolling the category you asked it in.
 *
 * There is deliberately no public version of this page. Every endpoint behind
 * it is "the signed-in user" with no id parameter, so there is nothing to
 * enumerate: what a stranger can see of you is still only your nickname on a
 * post.
 */
const { $t } = useNuxtApp()
const { user, restore, signOut } = useAuth()

definePageMeta({ middleware: undefined })

const profile = ref<any>(null)
const activity = ref<any>({ posts: [], answered: [], bookmarks: [] })
const loading = ref(true)
const saving = ref(false)
const notice = ref('')
const error = ref('')

const nickname = ref('')
const bio = ref('')
const tab = ref<'posts' | 'answered' | 'bookmarks'>('posts')
const uploading = ref(false)
const avatarInput = ref<HTMLInputElement | null>(null)

async function load() {
  loading.value = true
  error.value = ''
  try {
    profile.value = await apiFetch<any>('/v1/profile')
    nickname.value = profile.value.nickname
    bio.value = profile.value.bio || ''
    activity.value = await apiFetch<any>('/v1/profile/activity')
  } catch (caught: any) {
    // 401 is not an error worth a red box: it means "sign in", and the template
    // already says so.
    if (caught?.status !== 401 && caught?.statusCode !== 401) {
      error.value = caught?.data?.detail || $t('state.generic')
    }
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await restore()
  await load()
})

const dirty = computed(
  () =>
    !!profile.value &&
    (nickname.value.trim() !== profile.value.nickname ||
      bio.value.trim() !== (profile.value.bio || ''))
)

async function save() {
  if (saving.value || !dirty.value) return
  saving.value = true
  notice.value = ''
  error.value = ''
  try {
    profile.value = await apiFetch<any>('/v1/profile', {
      method: 'PATCH',
      body: { nickname: nickname.value.trim(), bio: bio.value.trim() }
    })
    nickname.value = profile.value.nickname
    bio.value = profile.value.bio || ''
    notice.value = $t('profile.saved')
    // The header shows the nickname, so it has to hear about the change.
    if (user.value) user.value.nickname = profile.value.nickname
  } catch (caught: any) {
    error.value = caught?.data?.detail || $t('state.generic')
  } finally {
    saving.value = false
  }
}

async function onAvatar(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  uploading.value = true
  notice.value = ''
  error.value = ''
  try {
    const form = new FormData()
    form.append('file', file)
    profile.value = await apiFetch<any>('/v1/profile/avatar', { method: 'POST', body: form })
    if (user.value) user.value.avatar_url = profile.value.avatar_url
    notice.value = $t('profile.avatarSaved')
  } catch (caught: any) {
    error.value = caught?.data?.detail || $t('profile.avatarFailed')
  } finally {
    uploading.value = false
  }
}

async function clearAvatar() {
  uploading.value = true
  try {
    profile.value = await apiFetch<any>('/v1/profile/avatar', { method: 'DELETE' })
    if (user.value) user.value.avatar_url = null
  } catch (caught: any) {
    error.value = caught?.data?.detail || $t('state.generic')
  } finally {
    uploading.value = false
  }
}

/**
 * A picture that will not load is worse than no picture: the browser draws a
 * broken-image icon where a face should be. If the file is missing - an old
 * URL, a bad mount, a deploy that lost the volume - fall back to the letter.
 */
const avatarBroken = ref(false)
watch(() => profile.value?.avatar_url, () => { avatarBroken.value = false })
const showAvatar = computed(() => !!profile.value?.avatar_url && !avatarBroken.value)

/** The letter shown when there is no picture, and a colour that follows the name. */
const initial = computed(() => (profile.value?.nickname || '?').trim().charAt(0).toUpperCase())
const initialHue = computed(() => {
  const name = profile.value?.nickname || ''
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = (hash * 31 + name.charCodeAt(i)) % 360
  return hash
})

const shown = computed(() => activity.value[tab.value] || [])
const joined = computed(() =>
  profile.value?.joined_at ? new Date(profile.value.joined_at).toLocaleDateString() : null
)

useSeoMeta({ title: () => $t('profile.metaTitle'), robots: 'noindex' })
</script>

<template>
  <div class="container narrow page">
    <div v-if="loading" class="card section"><Skeleton :lines="4" /></div>

    <div v-else-if="!profile" class="card section">
      <h1>{{ $t('profile.title') }}</h1>
      <p class="small muted">{{ $t('profile.signedOut') }}</p>
      <NuxtLink to="/login" class="btn">{{ $t('nav.signIn') }}</NuxtLink>
    </div>

    <template v-else>
      <section class="card section head">
        <div class="identity">
          <img v-if="showAvatar" :src="profile.avatar_url" class="avatar" alt=""
               @error="avatarBroken = true">
          <span v-else class="avatar avatar--letter"
                :style="{ background: `hsl(${initialHue} 55% 88%)`, color: `hsl(${initialHue} 60% 28%)` }">
            {{ initial }}
          </span>
          <div class="who">
            <h1>{{ profile.nickname }}</h1>
            <p class="tiny muted">{{ profile.email }}</p>
            <p v-if="joined" class="tiny muted">{{ $t('profile.joined', { date: joined }) }}</p>
          </div>
        </div>

        <div class="avatar-actions">
          <label class="btn btn--ghost btn--small file">
            {{ uploading ? $t('profile.uploading') : $t('profile.changeAvatar') }}
            <input ref="avatarInput" type="file" accept="image/*" :disabled="uploading"
                   @change="onAvatar">
          </label>
          <button v-if="profile.avatar_url" class="btn btn--ghost btn--small" type="button"
                  :disabled="uploading" @click="clearAvatar">
            {{ $t('profile.removeAvatar') }}
          </button>
        </div>
        <p class="tiny muted">{{ $t('profile.avatarHelp') }}</p>
      </section>

      <section class="stats">
        <div class="card stat">
          <p class="figure">{{ profile.counts.posts }}</p>
          <p class="tiny muted">{{ $t('profile.statPosts') }}</p>
        </div>
        <div class="card stat">
          <p class="figure">{{ profile.counts.answers }}</p>
          <p class="tiny muted">{{ $t('profile.statAnswers') }}</p>
        </div>
        <div class="card stat">
          <p class="figure">{{ profile.counts.bookmarks }}</p>
          <p class="tiny muted">{{ $t('profile.statBookmarks') }}</p>
        </div>
      </section>

      <section class="card section">
        <h2>{{ $t('profile.details') }}</h2>
        <div class="field-row">
          <label for="nickname" class="tiny muted">{{ $t('auth.nickname') }}</label>
          <input id="nickname" v-model="nickname" class="field" autocomplete="username">
          <p class="tiny muted">{{ $t('profile.nicknameHelp') }}</p>
        </div>
        <div class="field-row">
          <label for="bio" class="tiny muted">{{ $t('profile.bio') }}</label>
          <textarea id="bio" v-model="bio" class="field" rows="3" maxlength="280"
                    :placeholder="$t('profile.bioPlaceholder')" />
          <p class="tiny muted">{{ bio.length }}/280</p>
        </div>
        <p v-if="notice" class="tiny notice">{{ notice }}</p>
        <p v-if="error" class="tiny bad-text" role="alert">{{ error }}</p>
        <button class="btn" type="button" :disabled="!dirty || saving" @click="save">
          {{ saving ? $t('auth.working') : $t('profile.save') }}
        </button>
      </section>

      <section class="card section">
        <h2>{{ $t('profile.activity') }}</h2>
        <div class="tabs">
          <button v-for="key in (['posts', 'answered', 'bookmarks'] as const)" :key="key"
                  class="tab" :class="{ 'tab--on': tab === key }" type="button" @click="tab = key">
            {{ $t(`profile.tab.${key}`) }}
          </button>
        </div>
        <div v-if="shown.length" class="grid">
          <PostCard v-for="post in shown" :key="post.id" :post="post" />
        </div>
        <EmptyState v-else :title="$t(`profile.empty.${tab}`)" :hint="$t('profile.emptyHint')">
          <NuxtLink to="/community" class="btn">{{ $t('nav.community') }}</NuxtLink>
        </EmptyState>
      </section>

      <section class="card section">
        <button class="btn btn--ghost btn--small" type="button" @click="signOut">
          {{ $t('nav.signOut') }}
        </button>
      </section>
    </template>
  </div>
</template>

<style scoped>
.narrow { max-width: 860px; }
.page { display: grid; gap: var(--s4); padding: var(--s5) var(--s4) var(--s7); }
.section { padding: var(--s5); }

.head { display: grid; gap: var(--s3); }
.identity { display: flex; align-items: center; gap: var(--s4); }
.avatar {
  width: 96px; height: 96px; border-radius: 50%; object-fit: cover;
  border: 1px solid var(--border); flex: none;
}
.avatar--letter {
  display: grid; place-items: center;
  font-size: 2.4rem; font-weight: 600; border: 0;
}
.who h1 { margin: 0 0 var(--s1); }
.who p { margin: 0; }
.avatar-actions { display: flex; flex-wrap: wrap; gap: var(--s2); }
/* The real file input is unusable and styled differently by every browser. */
.file { position: relative; overflow: hidden; cursor: pointer; }
.file input { position: absolute; inset: 0; opacity: 0; cursor: pointer; }

.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: var(--s4); }
.stat { padding: var(--s4) var(--s5); }
.stat p { margin: 0; }
.figure { font-size: 2rem; font-weight: 600; line-height: 1.1; }

.field-row { display: grid; gap: var(--s1); margin-bottom: var(--s4); }
.field-row p { margin: 0; }
textarea.field { resize: vertical; }
.notice { color: var(--success); }
.bad-text { color: var(--danger); }

.tabs { display: flex; flex-wrap: wrap; gap: var(--s2); margin: var(--s3) 0 var(--s4); }
.tab {
  padding: 6px 14px; border: 1px solid var(--border-strong); border-radius: var(--radius-pill);
  background: var(--surface); color: var(--text); font: inherit; font-size: 0.85rem;
  cursor: pointer;
}
.tab--on { background: var(--navy); border-color: var(--navy); color: var(--text-inverse); }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: var(--s3); }

@media (max-width: 560px) {
  .identity { flex-direction: column; align-items: flex-start; }
}
</style>
