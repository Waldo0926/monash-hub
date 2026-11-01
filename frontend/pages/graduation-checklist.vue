<script setup lang="ts">
import { possibleMissingExplicitUnits } from '~/utils/courseGaps'
/**
 * Graduation preparation only. The faculty, not this app, decides whether
 * course requirements, exemptions and transfer credits have been satisfied.
 */
const { plan } = usePlan()
const { locale } = useLocale()
const campusName = useCampusName()
const zh = computed(() => locale.value === 'zh')
const report = shallowRef<{ issues: Array<{ unit_code: string; kind: string; severity: string; year: number; teaching_period: string; detail?: Record<string, unknown> }>; credit_points?: number } | null>(null)
const checking = ref(false)
const degree = shallowRef<any>(null)
const degreeUnavailable = ref(false)
const candidateGaps = computed(() => degree.value?.containers ? possibleMissingExplicitUnits(degree.value.containers, plan.value.entries.map(e => e.unit_code)) : [])
const potentialCreditShortfall = computed(() => {
  const expected = Number(degree.value?.credit_points)
  const planned = Number(report.value?.credit_points)
  return expected > 0 && Number.isFinite(planned) ? Math.max(0, expected - planned) : null
})
const failed = ref(false)
const steps = ref<string[]>([])
const checks = [
  { id: 'structure', en: 'Check the applicable course map and all compulsory units', zh: '核对入学年份对应的学位结构和全部必修课' },
  { id: 'credits', en: 'Confirm credit points and any remaining electives', zh: '核对总学分和剩余选修要求' },
  { id: 'transfer', en: 'Confirm overseas or transferred credit has been officially recorded', zh: '确认交换或转学学分已获批准并入账' },
  { id: 'results', en: 'Check results, hurdles and unresolved assessments', zh: '确认成绩、Hurdle要求和待处理考核' },
  { id: 'admin', en: 'Review outstanding fees and administration holds', zh: '确认欠费和行政限制是否处理完毕' },
  { id: 'application', en: 'Check the current graduation application and conferral procedure', zh: '查询最新毕业申请和学位授予流程' }
]
const findings = computed(() => report.value?.issues || [])
const labels = {
  not_in_year: { en: 'Not found in that Handbook year', zh: '指定Handbook年份未找到课程' },
  not_offered_at_campus: { en: 'Not offered at the selected campus', zh: '当前校区未开设' },
  not_offered_in_period: { en: 'Not offered in the planned period', zh: '所选学期未开设' },
  missing_prerequisite: { en: 'Prerequisite needs checking', zh: '先修要求有待核对' },
  missing_corequisite: { en: 'Corequisite needs checking', zh: '同修要求有待核对' },
  prohibited_with: { en: 'Prohibition conflict', zh: '和计划里的另一门课禁修冲突' },
  duplicate: { en: 'Duplicated unit', zh: '同一门课重复安排' }
} as const
function severityText(severity: string): string {
  if (!zh.value) return severity
  return severity === 'error' ? '需要处理' : severity === 'warning' ? '需要留意' : severity === 'info' ? '提示' : severity
}
function issueText(kind: string): string {
  const entry = labels[kind as keyof typeof labels]
  return entry ? (zh.value ? entry.zh : entry.en) : kind.replace(/_/g, ' ')
}
async function checkPlan() {
  report.value = null
  degree.value = null
  degreeUnavailable.value = false
  failed.value = false
  if (!plan.value.entries.length) return
  checking.value = true
  try {
    report.value = await apiFetch('/v1/plan/check', {
      method: 'POST',
      body: { campus: plan.value.campus, entries: plan.value.entries }
    })
    // Compare against the course Handbook of the year the student commenced,
    // never silently substitute the newest degree rules. The source may be
    // absent for older years; unknown means unknown, not "all requirements met".
    if (plan.value.courseCode && Number.isInteger(plan.value.startYear)) {
      const params = new URLSearchParams({ year: String(plan.value.startYear), campus: plan.value.campus })
      try {
        degree.value = await apiFetch<any>(`/v1/courses/${encodeURIComponent(plan.value.courseCode)}?${params}`)
      } catch {
        degreeUnavailable.value = true
      }
    }
  } catch {
    failed.value = true
  } finally {
    checking.value = false
  }
}
function toggle(id: string, checked: boolean) {
  steps.value = checked ? [...steps.value.filter(x => x !== id), id] : steps.value.filter(x => x !== id)
}
watch(() => JSON.stringify([plan.value.entries, plan.value.campus, plan.value.startYear, plan.value.courseCode]), () => { report.value = null; degree.value = null; degreeUnavailable.value = false })
useSeoMeta({
  title: () => zh.value ? '毕业准备清单 | Monash Hub' : 'Graduation preparation checklist | Monash Hub',
  description: () => zh.value ? '根据自己的课程计划和官方流程检查待确认事项，不代替学校毕业资格审核' : 'Prepare for graduation using your study plan without claiming official clearance.'
})
</script>

<template>
  <div class="page graduation-page">
    <header class="intro">
      <p><NuxtLink to="/plan">{{ zh ? '返回学位规划' : 'Back to degree planner' }}</NuxtLink></p>
      <h1>{{ zh ? '毕业准备清单' : 'Graduation preparation checklist' }}</h1>
      <p class="muted">{{ zh ? '帮你整理可能遗漏的课程和行政事项。所有勾选只在当前页面有效，不代表学校批准毕业' : 'Review possible study-plan conflicts and administrative tasks. Your ticks stay on this page and are not proof of university clearance.' }}</p>
    </header>
    <section class="card graduation-section">
      <h2>{{ zh ? '现有学位计划' : 'Your study plan' }}</h2>
      <p>{{ plan.name || (zh ? '未命名计划' : 'Untitled plan') }} · {{ plan.courseCode || (zh ? '未选择学位' : 'No degree selected') }} · {{ campusName(plan.campus) }} · {{ plan.entries.length }}{{ zh ? '门课' : ' units' }}</p>
      <p class="small muted">{{ zh ? '点击后会将课程代码、年份、学期和校区临时发送至Monash Hub的计划检查接口，服务端不保存你的计划' : 'Clicking the check button sends unit codes, years, periods and campus to the plan-check API temporarily; the server does not save your plan.' }}</p>
      <button type="button" class="check-button" :disabled="checking || !plan.entries.length" @click="checkPlan">
        {{ checking ? (zh ? '检查中…' : 'Checking…') : (zh ? '检查课程安排' : 'Check planned units') }}
      </button>
      <p v-if="!plan.entries.length"><NuxtLink to="/plan">{{ zh ? '先添加课程到学位规划' : 'Add units to your plan first' }}</NuxtLink></p>
      <p v-if="failed" role="alert">{{ zh ? '当前无法检查计划，请稍后再试' : 'Could not check the plan. Try again later.' }}</p>
      <template v-if="report">
        <p v-if="!findings.length">{{ zh ? '目前未发现开课、先修或重复安排的冲突。但不能据此判定符合全部毕业要求' : 'No scheduling or prerequisite issues were reported. This does not confirm degree completion.' }}</p>
        <template v-else>
          <p>{{ zh ? `有${findings.length}项需要核对` : `${findings.length} findings need review` }}</p>
          <ul class="findings">
            <li v-for="(issue, i) in findings" :key="i">
              <strong>{{ issue.unit_code }} · {{ issue.year }}</strong>
              <span>{{ issueText(issue.kind) }}</span>
              <span class="severity">{{ severityText(issue.severity) }}</span>
            </li>
          </ul>
          <p class="small muted"><NuxtLink to="/plan">{{ zh ? '返回学位规划查看详细原因和相关课程' : 'Open your plan for detailed findings and source links' }}</NuxtLink></p>
        </template>
      </template>
    </section>
    <section v-if="report && plan.courseCode" class="card graduation-section">
      <h2>{{ zh ? '可能遗漏的学位要求' : 'Possible course requirement gaps' }}</h2>
      <p v-if="degreeUnavailable" class="small muted">
        {{ zh ? '没有找到入学年份对应的学位Handbook，无法核对完整课程结构。请查看当年的官方Course Map' : 'The Handbook for your commencement-year degree could not be loaded. Check the applicable official course map.' }}
      </p>
      <template v-else-if="degree">
        <p v-if="potentialCreditShortfall !== null">
          {{ zh ? '计划所列学分' : 'Credits in plan' }}：{{ report.credit_points || 0 }} /
          {{ degree.credit_points }}
          <span v-if="potentialCreditShortfall > 0">{{ zh ? `（可能还差${potentialCreditShortfall}学分）` : `(possible shortfall: ${potentialCreditShortfall} points)` }}</span>
        </p>
        <p class="small muted">{{ zh ? '这里数的是课程计划，不代表这些课程已经通过或交换学分已入账' : 'These are planned, not necessarily passed or officially credited, units.' }}</p>
        <p v-if="candidateGaps.length">
          {{ zh ? '下面是结构中单独列出的课程，尚未出现在你的计划里。请逐项核对是否必修、可替代或已获减免' : 'These units appear individually in the Handbook structure but not in your plan. Check whether they are required, substituted or exempted.' }}
        </p>
        <ul v-if="candidateGaps.length" class="findings">
          <li v-for="gap in candidateGaps" :key="gap.code">
            <strong>{{ gap.code }}</strong><span>{{ gap.part }}</span>
          </li>
        </ul>
        <p v-else class="small muted">{{ zh ? '没有发现可直接列出的单门课程遗漏；这不代表选修、专业方向和全部必修要求已满足' : 'No single-unit candidates found; this does not confirm majors, electives or full degree completion.' }}</p>
        <p v-if="degree.source_url"><a :href="degree.source_url" target="_blank" rel="noopener external">{{ zh ? '查看入学年份对应的官方Handbook' : 'View the relevant official Handbook edition' }} ↗</a></p>
      </template>
    </section>
    <section class="card graduation-section">
      <h2>{{ zh ? '需要自己确认的事项' : 'Things to confirm yourself' }}</h2>
      <div v-for="item in checks" :key="item.id" class="check-item">
        <label><input type="checkbox" :checked="steps.includes(item.id)" @change="toggle(item.id, ($event.target as HTMLInputElement).checked)"> {{ zh ? item.zh : item.en }}</label>
      </div>
      <p class="small muted">{{ zh ? '这些事项随学校政策、校区、学位和入学年份变化，不能自动勾选' : 'Requirements vary by course, campus and commencement year, so none of these are automatically marked complete.' }}</p>
    </section>
    <footer class="graduation-footer">
      <p>{{ zh ? '最终以Monash Handbook、学院审核、成绩单和学校毕业部门通知为准' : 'Only Monash Handbook requirements, faculty review, your transcript and graduation services can confirm eligibility.' }}</p>
      <a href="https://www.monash.edu/students/admin/graduations" target="_blank" rel="noopener external">{{ zh ? '查看Monash官方毕业信息' : 'Official Monash graduation information' }} ↗</a>
    </footer>
  </div>
</template>

<style scoped>
.graduation-page { max-width: 860px; margin-inline: auto; }
.intro { margin-bottom: var(--s5); }
.graduation-section { padding: var(--s5); margin-bottom: var(--s4); }
.graduation-section h2 { font-size: 1.2rem; margin-bottom: var(--s4); }
.check-button { padding: 10px 18px; min-height: 44px; border-radius: 8px; border: 0; color: var(--text-inverse); background: var(--ink); cursor: pointer; }
.check-button:disabled { opacity: .55; }
.check-item { padding: 12px 0; border-bottom: 1px solid var(--border); }
.check-item input { width: 18px; height: 18px; vertical-align: middle; margin-right: 6px; }
.findings { list-style: none; margin: 12px 0; padding: 0; }
.findings li { display: flex; flex-wrap: wrap; gap: 6px 16px; padding: 10px 0; border-bottom: 1px solid var(--border); }
.severity { font-size: .8rem; color: var(--muted); }
.graduation-footer { font-size: .9rem; margin-bottom: var(--s6); }
</style>
