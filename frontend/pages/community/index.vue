<script setup lang="ts">
const route = useRoute()
const { user, restore } = useAuth()
onMounted(restore)

const query = ref((route.query.q as string) || '')
const category = ref((route.query.category as string) || '')
const sort = ref('recent')
const showCompose = ref(Boolean(route.query.unit))

const draft = reactive({
  title: '',
  body: '',
  category: 'units',
  unit_code: (route.query.unit as string) || '',
  tags: ''
})
const submitting = ref(false)
const submitError = ref('')

const { data: categories } = await useApiFetch<any>('/v1/community/categories')

const path = computed(() => {
  const params = new URLSearchParams()
  if (query.value) params.set('q', query.value)
  if (category.value) params.set('category', category.value)
  params.set('sort', sort.value)
  params.set('limit', '30')
  return `/v1/community/posts?${params.toString()}`
})
const { data, pending, error, refresh } = await useApiFetch<any>(() => path.value, { watch: [path] })

async function submit() {
  submitError.value = ''
  submitting.value = true
  try {
    const post = await apiFetch<any>('/v1/community/posts', {
      method: 'POST',
      body: {
        title: draft.title,
        body: draft.body,
        category: draft.category,
        unit_code: draft.unit_code || null,
        tags: draft.tags.split(',').map(t => t.trim()).filter(Boolean).slice(0, 6)
      }
    })
    navigateTo(`/community/post/${post.id}`)
  } catch (e: any) {
    submitError.value = e?.data?.detail || 'Could not post that. Check the title and body length.'
  } finally {
    submitting.value = false
  }
}

useSeoMeta({
  title: 'Community — Monash Hub',
  description: 'Public, searchable Monash student questions and experience. Anyone can read; posting needs an account.'
})
</script>

<template>
  <div class="container">
    <div class="head">
      <div>
        <h1>Community</h1>
        <p class="muted">
          Student experience, in public and searchable. Official rules live in
          <NuxtLink to="/guides">Official guides</NuxtLink> and
          <NuxtLink to="/units">Units</NuxtLink> — nothing here overrides them.
        </p>
      </div>
      <button class="btn" @click="showCompose = !showCompose">Ask a question</button>
    </div>

    <section v-if="showCompose" class="card compose">
      <h2>Ask a question</h2>
      <template v-if="user">
        <p class="tiny muted">
          Do not post anyone's student ID, phone number, address or private chat screenshots.
          Posting as <strong>{{ user.nickname }}</strong>.
        </p>
        <label class="field-row">
          <span class="tiny muted">Title</span>
          <input v-model="draft.title" class="field" placeholder="What do you want to know?">
        </label>
        <label class="field-row">
          <span class="tiny muted">Details</span>
          <textarea v-model="draft.body" class="field body" rows="5" placeholder="Give enough context for someone to answer." />
        </label>
        <div class="row">
          <label class="field-row">
            <span class="tiny muted">Category</span>
            <select v-model="draft.category" class="field">
              <option v-for="cat in categories?.categories || []" :key="cat.key" :value="cat.key">
                {{ cat.label }}
              </option>
            </select>
          </label>
          <label class="field-row">
            <span class="tiny muted">Unit code (optional)</span>
            <input v-model="draft.unit_code" class="field" placeholder="FIT2102">
          </label>
          <label class="field-row">
            <span class="tiny muted">Tags (comma separated)</span>
            <input v-model="draft.tags" class="field" placeholder="workload, exchange">
          </label>
        </div>
        <p v-if="submitError" class="small err">{{ submitError }}</p>
        <button class="btn" :disabled="submitting" @click="submit">
          {{ submitting ? 'Posting…' : 'Post question' }}
        </button>
      </template>
      <template v-else>
        <p class="small">Reading is open to everyone. Posting needs an account.</p>
        <NuxtLink to="/login" class="btn">Sign in or create an account</NuxtLink>
      </template>
    </section>

    <SearchInput v-model="query" placeholder="Search discussions…" @submit="v => (query = v)" />

    <div class="cats">
      <button class="cat" :class="{ active: !category }" @click="category = ''">All</button>
      <button
        v-for="cat in categories?.categories || []"
        :key="cat.key"
        class="cat"
        :class="{ active: category === cat.key }"
        @click="category = cat.key"
      >
        {{ cat.label }}
      </button>
      <select v-model="sort" class="field sort">
        <option value="recent">Most recent</option>
        <option value="top">Most liked</option>
        <option value="unanswered">Unanswered</option>
      </select>
    </div>

    <ErrorState v-if="error" :error="error" :on-retry="refresh" />
    <Skeleton v-else-if="pending" :lines="6" />
    <template v-else>
      <div v-if="data.results.length" class="grid">
        <PostCard v-for="post in data.results" :key="post.id" :post="post" />
      </div>
      <EmptyState
        v-else
        title="No discussions here yet"
        hint="Someone has to go first — a question with real detail usually gets a real answer."
      >
        <button class="btn" @click="showCompose = true">Ask a question</button>
      </EmptyState>
    </template>
  </div>
</template>

<style scoped>
.head { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--s4); }
.head h1 { margin-bottom: var(--s2); }
.compose { padding: var(--s5); margin-bottom: var(--s5); display: grid; gap: var(--s3); }
.field-row { display: grid; gap: var(--s1); }
.body { min-height: 120px; padding: var(--s3); font-family: inherit; }
.row { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--s3); }
.err { color: var(--danger); }
.cats { display: flex; flex-wrap: wrap; align-items: center; gap: var(--s2); margin: var(--s4) 0 var(--s5); }
.cat {
  padding: 6px 14px;
  min-height: 36px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-pill);
  background: var(--surface);
  font: inherit;
  font-size: 0.85rem;
  cursor: pointer;
}
.cat.active { background: var(--navy); border-color: var(--navy); color: var(--text-inverse); }
.sort { width: auto; min-height: 36px; margin-left: auto; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: var(--s3); }
@media (max-width: 700px) {
  .head { flex-direction: column; }
  .row { grid-template-columns: 1fr; }
  .sort { margin-left: 0; }
}
</style>
