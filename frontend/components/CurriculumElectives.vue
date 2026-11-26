<script setup lang="ts">
const props = defineProps<{ scope: { levels: string[]; free: boolean }; campus: string; year: number }>()
const { locale } = useLocale()
const opened = ref(true)
const keyword = ref('')
const query = ref('')
const offset = ref(0)
const limit = 12
const c = computed(() => locale.value === 'zh' ? {
  title: '浏览选修课程', note: '以下是按级别和校区检索的课程，不是获批选修名单。能否计入本部分学分，须核对上方要求、先修课及学院审批；官方名单见相关链接。',
  search: '搜索课程代码或名称', submit: '搜索', loading: '正在加载课程…', error: '课程加载失败，请重试。', retry: '重试', empty: '当前年份和校区没有匹配课程，可切换校区或查看官方名单。',
  previous: '上一页', next: '下一页', count: '门匹配课程', all: '查看完整列表'
} : {
  title: 'Browse elective units', note: 'Results match the level and campus filters; they are not an approved elective list. Check the requirements above, prerequisites and faculty approval. Follow the source links for official lists.',
  search: 'Search unit code or title', submit: 'Search', loading: 'Loading units…', error: 'Units could not be loaded. Please retry.', retry: 'Retry', empty: 'No matching units for this year and campus. Try another campus or the official list.',
  previous: 'Previous', next: 'Next', count: 'matching units', all: 'Open full list'
})
const filters = computed(() => ({
  year: String(props.year),
  ...(props.scope.levels.length ? { level: props.scope.levels } : {}),
  ...(props.campus ? { campus: props.campus } : {}),
  ...(query.value ? { q: query.value } : {})
}))
const endpoint = computed(() => {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset.value), sort: 'code' })
  for (const [key, value] of Object.entries(filters.value)) {
    for (const item of Array.isArray(value) ? value : [value]) params.append(key, item)
  }
  return `/v1/units?${params}`
})
const { data, pending, error, refresh } = useLocalisedApiFetch<any>(() => endpoint.value, {
  server: false, lazy: true, watch: false
})
watch([endpoint, locale], () => { if (opened.value) refresh() })
watch(() => [props.campus, props.year, props.scope.levels.join(',')], () => { offset.value = 0 })
function toggle() {
  opened.value = !opened.value
  if (opened.value && !data.value) refresh()
}
function search() { offset.value = 0; query.value = keyword.value.trim() }
</script>

<template>
  <div class="elective-browser">
    <button type="button" class="btn" :aria-expanded="opened" @click="toggle">{{ c.title }}</button>
    <template v-if="opened">
      <p class="small muted">{{ c.note }}</p>
      <form class="search" @submit.prevent="search">
        <input v-model="keyword" type="search" :aria-label="c.search" :placeholder="c.search">
        <button type="submit" class="btn">{{ c.submit }}</button>
      </form>
      <p v-if="pending" role="status">{{ c.loading }}</p>
      <p v-else-if="error" role="alert">{{ c.error }} <button type="button" @click="refresh()">{{ c.retry }}</button></p>
      <template v-else-if="data">
        <p role="status">{{ data.total }} {{ c.count }}</p>
        <div v-if="data.results?.length" class="results">
          <UnitCard v-for="unit in data.results" :key="unit.unit_code" :unit="unit" />
        </div>
        <p v-else>{{ c.empty }}</p>
        <nav class="pagination" :aria-label="c.title">
          <button class="btn" type="button" :disabled="offset === 0" @click="offset = Math.max(0, offset - limit)">{{ c.previous }}</button>
          <button class="btn" type="button" :disabled="offset + limit >= data.total" @click="offset += limit">{{ c.next }}</button>
          <NuxtLink :to="{ path: '/units', query: filters }">{{ c.all }}</NuxtLink>
        </nav>
      </template>
    </template>
  </div>
</template>

<style scoped>
.elective-browser { margin-block: var(--s3); }
.search, .pagination { display: flex; flex-wrap: wrap; gap: var(--s2); margin-block: var(--s3); align-items: center; }
input { flex: 1; min-width: 0; padding: var(--s2); font: inherit; color: var(--text); background: var(--surface); border: 1px solid var(--border-strong); border-radius: var(--radius-sm); }
.results { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 240px), 1fr)); gap: var(--s2); }
</style>
