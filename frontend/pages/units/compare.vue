<script setup lang="ts">
/**
 * Compare two *explicit* Handbook years. Never fall back silently when one
 * is missing: the difference between a 404 and a changed rule matters.
 */
import { compareUnitSnapshots, type UnitSnapshot } from '~/utils/unitCompare'
import { loadCommencementRules, type CommencementRules } from '~/utils/commencementRules'

const route = useRoute()
const router = useRouter()
const config = useRuntimeConfig()
const { locale } = useLocale()
const zh = computed(() => locale.value === 'zh')
const code = ref(String(route.query.code || '').toUpperCase())
const from = ref(Number(route.query.from) || 0)
const to = ref(Number(route.query.to) || 0)
const busy = ref(false)
const courseCode = ref(String(route.query.course || '').toUpperCase())
const commencementYear = ref<number | null>(Number(route.query.commenced) || null)
const { plan } = usePlan()
const message = ref('')
const result = shallowRef<{ code: string; fromYear: number; toYear: number; before: UnitSnapshot | null; after: UnitSnapshot | null; commencement: CommencementRules | null } | null>(null)
const changedInputs = computed(() => result.value && (code.value.trim().toUpperCase() !== result.value.code || from.value !== result.value.fromYear || to.value !== result.value.toYear || courseCode.value.trim().toUpperCase() !== (result.value.commencement?.code || '') || (courseCode.value.trim() && commencementYear.value !== result.value.commencement?.year)))

const { data: filters } = await useApiFetch<{ years: number[] }>('/v1/units/filters')
const years = computed(() => filters.value?.years || [])
watch(years, (available) => {
  if (!available.length) return
  if (!available.includes(to.value)) to.value = available[0]!
  if (!available.includes(from.value)) from.value = available.find(y => y !== to.value) || available[0]!
}, { immediate: true })

const namesEn = {
  title: 'Unit title', credit_points: 'Credit points', level: 'Level', has_exam: 'Exam listed',
  offerings: 'Campuses and teaching periods', assessments: 'Assessments',
  requisites: 'Prerequisites, corequisites and prohibitions',
  assessment_summary: 'Assessment overview', workload_requirements: 'Workload'
}
const namesZh = {
  title: '课程名称', credit_points: '学分', level: '课程级别', has_exam: '是否列出考试',
  offerings: '校区和开课学期', assessments: '考核项目',
  requisites: '先修、同修和禁修条件',
  assessment_summary: '考核说明', workload_requirements: '学习负担'
}
const names = computed(() => zh.value ? namesZh : namesEn)
const statusZh = { added: '新增', removed: '移除', changed: '变化', unchanged: '相同', unavailable: '无法比较' }
const statusEn = { added: 'Added', removed: 'Removed', changed: 'Changed', unchanged: 'Unchanged', unavailable: 'Unavailable' }
const rows = computed(() => result.value ? compareUnitSnapshots(result.value.before, result.value.after) : [])
const changes = computed(() => rows.value.filter(row => ['added', 'removed', 'changed'].includes(row.status)))
const unavailable = computed(() => rows.value.filter(row => row.status === 'unavailable'))
const same = computed(() => rows.value.filter(row => row.status === 'unchanged'))

/** Requisite rules stay in the Handbook's words; only the joining words are put into Chinese. */
function shown(row: { field: string }, value: string) {
  if (!zh.value || row.field !== 'requisites') return value
  return value
    .replace(/^Prerequisite:/gm, '先修条件：').replace(/^Corequisite:/gm, '同修条件：').replace(/^Prohibition:/gm, '禁修：')
    .replace(/ AND /g, ' 且 ').replace(/ OR /g, ' 或 ')
}

function notFound(error: unknown): boolean {
  if (!error || typeof error !== 'object') return false
  const e = error as { status?: number; statusCode?: number; response?: { status?: number } }
  return [e.status, e.statusCode, e.response?.status].includes(404)
}
async function load(codeValue: string, year: number): Promise<UnitSnapshot | null> {
  try {
    // Compare the original Handbook wording, not potentially staggered translated snapshots.
    const snapshot = await apiFetch<UnitSnapshot>(`/v1/units/${encodeURIComponent(codeValue)}?year=${year}&locale=en`)
    if (snapshot.unit_code !== codeValue || snapshot.academic_year !== year) throw new Error('Handbook identity mismatch')
    return snapshot
  } catch (error) {
    if (notFound(error)) return null
    throw error
  }
}

async function compare() {
  if (busy.value) return
  const wanted = code.value.trim().toUpperCase()
  result.value = null
  message.value = ''
  if (!/^[A-Z]{2,8}\d{3,5}$/.test(wanted) || !years.value.includes(from.value) || !years.value.includes(to.value) || from.value === to.value) {
    message.value = zh.value ? '请填写正确的课程代码，并选择两个不同的已收录年份' : 'Enter a valid unit code and choose two different loaded Handbook years.'
    return
  }
  const requestFrom = from.value
  const requestTo = to.value
  const degreeCode = courseCode.value.trim().toUpperCase()
  const commenced = commencementYear.value
  if (degreeCode && (!Number.isInteger(commenced) || !commenced || commenced < 1990 || commenced > 2100)) {
    message.value = zh.value ? '请填写对应学位的入学年份' : 'Enter the commencement year for the selected degree.'
    return
  }
  busy.value = true
  try {
    const [before, after, commencement] = await Promise.all([
      load(wanted, requestFrom), load(wanted, requestTo),
      degreeCode && commenced ? loadCommencementRules(apiFetch, degreeCode, commenced) : Promise.resolve(null)
    ])
    result.value = { code: wanted, fromYear: requestFrom, toYear: requestTo, before, after, commencement }
    code.value = wanted
    await router.replace({ query: { code: wanted, from: String(requestFrom), to: String(requestTo), course: degreeCode || undefined, commenced: degreeCode && commenced ? String(commenced) : undefined } })
  } catch {
    message.value = zh.value ? '暂时无法读取Handbook，请稍后重试' : 'Could not read the Handbook right now. Please try again.'
  } finally {
    busy.value = false
  }
}

// A link from a unit page or the search box carries the code; compare at once.
onMounted(() => {
  if (!route.query.course && plan.value.courseCode) {
    courseCode.value = plan.value.courseCode
    commencementYear.value = plan.value.startYear
  }
  if (route.query.code) void compare()
})
useSeoMeta({
  title: () => zh.value ? 'Handbook年份比较 | Monash Hub' : 'Compare Handbook years | Monash Hub',
  description: () => zh.value ? '比较同一门Monash课程在不同年份的开课信息、先修课与考核' : 'Compare unit requisites, offerings and assessments across published Handbook years.'
})
useHead({ link: [{ rel: 'canonical', href: `${config.public.siteUrl}/units/compare` }] })
</script>

<template>
  <div class="container compare-page">
    <header class="intro">
      <p class="crumb"><NuxtLink to="/units">{{ zh ? '课程搜索' : 'Unit search' }}</NuxtLink></p>
      <h1>{{ zh ? 'Handbook年份比较' : 'Compare Handbook years' }}</h1>
      <p class="lede">{{ zh ? '对照同一门课程在两个年份的先修要求、考核和开课安排。仅比较已收录的Handbook版本' : 'See how a unit changed between two loaded Handbook editions. Every result links back to the original sources.' }}</p>
    </header>

    <form class="compare-form card" @submit.prevent="compare">
      <label>{{ zh ? '学位代码（可选）' : 'Degree code (optional)' }}
        <input v-model="courseCode" class="compare-input" maxlength="16" placeholder="C2001" :disabled="busy">
      </label>
      <label>{{ zh ? '学位入学年份' : 'Degree commencement year' }}
        <input v-model.number="commencementYear" class="compare-input" type="number" min="1990" max="2100" :required="!!courseCode.trim()" :disabled="busy">
      </label>
      <label>{{ zh ? '课程代码' : 'Unit code' }}
        <input v-model="code" class="compare-input" type="text" placeholder="FIT2102" maxlength="16" required autocomplete="off" :disabled="busy">
      </label>
      <label>{{ zh ? '原年份' : 'From year' }}
        <select v-model.number="from" class="compare-input" required :disabled="busy">
          <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
        </select>
      </label>
      <label>{{ zh ? '新年份' : 'To year' }}
        <select v-model.number="to" class="compare-input" required :disabled="busy">
          <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
        </select>
      </label>
      <button type="submit" class="compare-submit" :disabled="busy || years.length < 2">{{ busy ? (zh ? '正在比较…' : 'Comparing…') : (zh ? '比较变化' : 'Compare') }}</button>
    </form>
    <p v-if="message" role="alert" class="compare-message">{{ message }}</p>
    <p v-if="!years.length" class="small muted">{{ zh ? '暂时没有可用的Handbook年份' : 'No Handbook years are available right now.' }}</p>
    <p v-if="years.length === 1" class="small muted" role="status">
      {{ zh ? '目前仅收录一个Handbook年份，暂时无法比较。课程搜索中的年份变化入口仍可使用，待其他年份有资料后再比较' : 'Only one Handbook year is indexed. Comparison needs two years; the search shortcut remains available until more editions are loaded.' }}
    </p>

    <template v-if="result">
      <CommencementRulesNotice v-if="result.commencement" :evidence="result.commencement" :show-structure="true" />
      <p v-if="changedInputs" class="compare-warning" role="status">{{ zh ? '选择已改变。下方仍为上次比较结果，请点击“比较变化”更新。' : 'Selection changed. The results below still show the last comparison; press Compare to update.' }}</p>
      <p class="small muted comparison-context">{{ result.code }} · {{ result.fromYear }} → {{ result.toYear }}</p>
      <div v-if="!result.before || !result.after" class="card compare-warning" role="status">
        <h2>{{ zh ? '有年份未收录这门课' : 'A selected edition does not list this unit' }}</h2>
        <p>{{ zh ? '这不等于课程已经取消或要求被移除。只有两个年份都有对应记录时，才会显示正式差异' : 'Missing data is not proof the unit was discontinued or its rules were removed. Comparison requires records in both years.' }}</p>
        <p>{{ result.fromYear }}：{{ result.before ? (zh ? '有记录' : 'Available') : (zh ? '未找到记录' : 'Not found') }} · {{ result.toYear }}：{{ result.after ? (zh ? '有记录' : 'Available') : (zh ? '未找到记录' : 'Not found') }}</p>
      </div>
      <template v-else>
        <p class="compare-summary">{{ changes.length
          ? (zh ? `${result.fromYear}年和${result.toYear}年之间有${changes.length}项不同` : `${changes.length} ${changes.length === 1 ? 'field differs' : 'fields differ'} between ${result.fromYear} and ${result.toYear}`)
          : (zh ? `两年可核实的字段没有发现差异` : `No differences in the verifiable fields`) }}</p>
        <p v-if="unavailable.length" class="compare-warning" role="status">
          {{ zh ? `以下字段资料不足，不能判断相同或变化：${unavailable.map(row => names[row.field]).join('、')}` : `Insufficient source data to compare: ${unavailable.map(row => names[row.field]).join(', ')}` }}
        </p>
        <div class="compare-grid">
          <section v-for="row in changes" :key="row.field" class="card compare-row">
            <div class="compare-row-head">
              <h2>{{ names[row.field] }}</h2>
              <span class="compare-tag">{{ zh ? statusZh[row.status] : statusEn[row.status] }}</span>
            </div>
            <div class="compare-two">
              <div><strong>{{ result.fromYear }}</strong><pre>{{ row.from ? shown(row, row.from) : (zh ? '未列出' : 'Not listed') }}</pre></div>
              <div><strong>{{ result.toYear }}</strong><pre>{{ row.to ? shown(row, row.to) : (zh ? '未列出' : 'Not listed') }}</pre></div>
            </div>
          </section>
        </div>
        <details v-if="same.length" class="compare-same">
          <summary>{{ zh ? `两年相同：${same.map(row => names[row.field]).join('、')}` : `Same in both years: ${same.map(row => names[row.field]).join(', ')}` }}</summary>
          <dl>
            <div v-for="row in same" :key="row.field">
              <dt>{{ names[row.field] }}</dt>
              <dd><pre>{{ row.from ? shown(row, row.from) : (zh ? '未列出' : 'Not listed') }}</pre></dd>
            </div>
          </dl>
        </details>
      </template>
      <div class="compare-sources card">
        <h2>{{ zh ? '原始资料' : 'Original sources' }}</h2>
        <p v-if="result.before?.source_url"><a :href="result.before.source_url" target="_blank" rel="noopener external">{{ result.fromYear }} Monash Handbook ↗</a><template v-if="result.before.last_checked"> · <LastChecked :value="result.before.last_checked" /></template></p>
        <p v-if="result.after?.source_url"><a :href="result.after.source_url" target="_blank" rel="noopener external">{{ result.toYear }} Monash Handbook ↗</a><template v-if="result.after.last_checked"> · <LastChecked :value="result.after.last_checked" /></template></p>
        <p class="small muted">{{ zh ? '这里只比较当前抓取的数据，不代表学校已批准选课、先修豁免、交换学分或毕业资格。考核和开课信息可能继续变化，请以原始页面为准。课程单元的Handbook年份不代替你入学年份对应的学位规则' : 'These are snapshots, not enrolment, prerequisite-waiver, credit-transfer or graduation approvals. Confirm current details on Monash’s original pages. The unit Handbook year does not replace the commencement-year course rules that apply to your degree.' }}</p>
        <p><NuxtLink to="/plan">{{ zh ? '查看按入学年份读取学位规则的课程图' : 'Open the course map with degree rules for your commencement year' }} →</NuxtLink></p>
      </div>
    </template>
  </div>
</template>

<style scoped>
.compare-page { max-width: 980px; margin-inline: auto; }
.intro { margin-bottom: var(--s5); }
.lede { color: var(--muted); max-width: 65ch; }
.compare-form { display: flex; flex-wrap: wrap; align-items: end; gap: var(--s3); padding: var(--s5); }
.compare-form label { display: grid; gap: 6px; font-weight: 600; flex: 1 1 160px; font-size: .9rem; }
.compare-input { min-height: 44px; border: 1px solid var(--border-strong); border-radius: 8px; padding: 8px 12px; font: inherit; width: 100%; background: var(--surface); }
.compare-submit { min-height: 44px; border: 0; border-radius: 8px; padding: 10px 18px; background: var(--ink); color: var(--text-inverse); cursor: pointer; }
.compare-submit:disabled { opacity: .6; cursor: wait; }
.compare-message { color: var(--danger); }
.compare-summary { margin: var(--s5) 0; font-weight: 600; }
.compare-grid { display: grid; gap: var(--s3); }
.compare-row { padding: var(--s4) var(--s5); }
.compare-same { margin-top: var(--s4); padding: var(--s4) var(--s5); border: 1px solid var(--border); border-radius: var(--radius); background: var(--surface); }
.compare-same summary { cursor: pointer; color: var(--muted); font-size: .9rem; padding: 10px 0; }
.compare-same dl { margin: var(--s3) 0 0; display: grid; gap: var(--s3); }
.compare-same dt { font-weight: 600; font-size: .9rem; }
.compare-same dd { margin: 0; }
.compare-same pre { white-space: pre-wrap; word-break: break-word; font: inherit; font-size: .88rem; margin: var(--s1) 0 0; color: var(--muted); }
.compare-row-head { display: flex; align-items: baseline; justify-content: space-between; gap: 14px; margin-bottom: 16px; }
.compare-row h2, .compare-sources h2, .compare-warning h2 { font-size: 1rem; margin: 0; }
.compare-tag { font-size: .8rem; background: var(--surface-2); color: var(--muted); border-radius: 5px; padding: 3px 8px; white-space: nowrap; }
.compare-two { display: grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap: var(--s5); }
.compare-two > div + div { border-left: 1px solid var(--border); padding-left: var(--s5); }
.compare-two pre { white-space: pre-wrap; word-break: break-word; font: inherit; font-size: .88rem; margin: var(--s2) 0 0; }
.compare-sources, .compare-warning { margin-top: var(--s5); padding: var(--s5); }
.compare-sources p { margin-top: var(--s2); overflow-wrap: anywhere; }
@media (max-width: 620px) { .compare-submit { width: 100%; } .compare-two { grid-template-columns: 1fr; } .compare-two > div + div { border-left: 0; border-top: 1px solid var(--border); padding: 12px 0 0; } }
</style>
