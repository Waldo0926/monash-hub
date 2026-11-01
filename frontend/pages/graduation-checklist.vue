<script setup lang="ts">
/**
 * Graduation preparation only. The faculty, not this app, decides whether
 * course requirements, exemptions and transfer credits have been satisfied.
 */
const { plan } = usePlan()
const { locale } = useLocale()
const zh = computed(() => locale.value === 'zh')
const report = shallowRef<{ issues: Array<{ unit_code: string; kind: string; severity: string; year: number; teaching_period: string; detail?: Record<string, unknown> }>; credit_points?: number } | null>(null)
const checking = ref(false)
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
  missing_corequisite: { en: 'Corequisite needs checking', zh: '并修要求有待核对' },
  prohibited_with: { en: 'Prohibition conflict', zh: '课程存在禁止同时修读的冲突' },
  duplicate: { en: 'Duplicated unit', zh: '同一门课重复安排' }
} as const
function issueText(kind: string): string {
  const entry = labels[kind as keyof typeof labels]
  return entry ? (zh.value ? entry.zh : entry.en) : kind.replace(/_/g, ' ')
}
async function checkPlan() {
  report.value = null
  failed.value = false
  if (!plan.value.entries.length) return
  checking.value = true
  try {
    report.value = await apiFetch('/v1/plan/check', {
      method: 'POST',
      body: { campus: plan.value.campus, entries: plan.value.entries }
    })
  } catch {
    failed.value = true
  } finally {
    checking.value = false
  }
}
function toggle(id: string, checked: boolean) {
  steps.value = checked ? [...steps.value.filter(x => x !== id), id] : steps.value.filter(x => x !== id)
}
watch(() => JSON.stringify([plan.value.entries, plan.value.campus]), () => { report.value = null })
useSeoMeta({
  title: () => zh.value ? '毕业准备清单｜Monash Hub' : 'Graduation preparation checklist | Monash Hub',
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
      <p>{{ plan.name || (zh ? '未命名计划' : 'Untitled plan') }} · {{ plan.courseCode || (zh ? '未选择学位' : 'No degree selected') }} · {{ plan.campus }} · {{ plan.entries.length }}{{ zh ? '门课' : ' units' }}</p>
      <p class="small muted">{{ zh ? '点击后会将课程代码、年份、学期和校区临时发送至MonashHub的计划检查API，服务端不保存你的计划' : 'Clicking the check button sends unit codes, years, periods and campus to the plan-check API temporarily; the server does not save your plan.' }}</p>
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
              <span class="severity">{{ issue.severity }}</span>
            </li>
          </ul>
          <p class="small muted"><NuxtLink to="/plan">{{ zh ? '返回学位规划查看详细原因和相关课程' : 'Open your plan for detailed findings and source links' }}</NuxtLink></p>
        </template>
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
