<script setup lang="ts">
/** Financial scenarios only, using fee values *as printed* by Monash Malaysia. */
import { feeTitle, formatAmount, type FeeRow } from '~/utils/tuition'
import { estimateFeeScenario } from '~/utils/feeScenario'

type Source = { title: string; url: string; level: string; last_checked: string | null }
type FeeTable = {
  year: number | null
  sections: { source: string; level: string; schools: { school: string; rows: FeeRow[] }[] }[]
  sources: Record<string, Source>
}
const { locale } = useLocale()
const zh = computed(() => locale.value === 'zh')
const { data, error } = await useApiFetch<FeeTable>('/v1/fees')
const rows = computed(() => data.value?.sections.flatMap(s => s.schools.flatMap(g => g.rows)) || [])
// The same title (Doctor of Philosophy) sits under several schools, so the list is grouped by school.
const groups = computed(() => {
  let i = 0
  return (data.value?.sections || []).flatMap(s => s.schools.map(g => ({
    school: g.school,
    options: g.rows.map(row => ({ row, index: i++ }))
  })))
})
const { $t } = useNuxtApp()
function schoolName(key: string) {
  const text = $t(`fees.school.${key}`)
  return text === `fees.school.${key}` ? key : text
}
const rowIndex = ref(0)
const feeSide = ref<'domestic' | 'international'>('international')
const amountIndex = ref(0)
const remainingYears = ref(1)
const scholarshipPercent = ref(0)
const livingPerYear = ref(0)
const chosen = computed(() => rows.value[rowIndex.value] ?? null)
const options = computed(() => chosen.value?.[feeSide.value] || [])
watch([rowIndex, feeSide], () => { amountIndex.value = 0 })
// Start from the whole degree; a student part-way through lowers it.
watch(chosen, (row) => {
  const years = parseFloat(row?.duration ?? '')
  if (row?.basis === 'per_year' && years > 0 && years <= 12) remainingYears.value = years
}, { immediate: true })
const estimate = computed(() => chosen.value ? estimateFeeScenario({
  row: chosen.value, feeSide: feeSide.value, amountIndex: amountIndex.value,
  yearsRemaining: remainingYears.value, scholarshipPercent: scholarshipPercent.value,
  livingPerYear: livingPerYear.value
}) : null)
const source = computed(() => chosen.value ? data.value?.sources?.[chosen.value.source] : null)
function money(value: number) {
  return 'RM' + new Intl.NumberFormat('en-MY', { maximumFractionDigits: 2 }).format(value)
}
useSeoMeta({
  title: () => zh.value ? '学费和奖学金估算 | Monash Hub' : 'Tuition and scholarship scenario | Monash Hub',
  description: () => zh.value ? '根据学校公布的学费和自己输入的减免比例，估算剩余费用' : 'Estimate costs from sourced Malaysia tuition rows and your own assumptions.'
})
</script>

<template>
  <div class="page fee-planner">
    <header class="intro">
      <p><NuxtLink to="/fees">{{ zh ? '返回官方学费列表' : 'Back to published fee table' }}</NuxtLink></p>
      <h1>{{ zh ? '学费与奖学金估算' : 'Tuition & scholarship scenario' }}</h1>
      <p class="muted">{{ zh ? '使用Monash Malaysia公布的学费，自己调整剩余学年、奖学金减免和生活费。不需要登录，也不会保存个人预算' : 'Use the published Malaysia fee rows and adjust the years, discount and living costs yourself. No account or budget storage is required.' }}</p>
    </header>
    <p v-if="error" role="alert">{{ zh ? '无法读取学费数据，请稍后重试' : 'Could not load published tuition fees.' }}</p>
    <p v-else-if="!rows.length">{{ zh ? '暂时没有可用的学费数据' : 'No published fee rows are available right now.' }}</p>
    <template v-else>
      <p class="fee-basis-note">{{ zh ? '数据年份' : 'Fee table year' }}：<strong>{{ data?.year ?? (zh ? '未核实' : 'Unverified') }}</strong> · {{ zh ? '这里的学费信息不代表该学位正在招生，也不代表你已获得奖学金' : 'A fee row does not confirm an open intake or a scholarship award.' }}</p>
      <div class="fee-controls card">
        <label>{{ zh ? '学位／项目' : 'Degree or programme' }}
          <select v-model.number="rowIndex">
            <optgroup v-for="(group, g) in groups" :key="g" :label="schoolName(group.school)">
              <option v-for="{ row, index } in group.options" :key="index" :value="index">{{ feeTitle(row, locale) }}{{ row.variant ? ' · ' + row.variant : '' }}</option>
            </optgroup>
          </select>
        </label>
        <label>{{ zh ? '收费类别' : 'Fee category' }}
          <select v-model="feeSide">
            <option value="international">{{ zh ? '国际学生' : 'International' }}</option>
            <option value="domestic">{{ zh ? '本地学生' : 'Domestic' }}</option>
          </select>
        </label>
        <label>{{ zh ? '所列金额' : 'Published amount' }}
          <select v-model.number="amountIndex" :disabled="!options.length">
            <option v-for="(amount, i) in options" :key="i" :value="i">{{ amount.label ? `${amount.label} · ` : '' }}{{ formatAmount(amount) }}</option>
          </select>
        </label>
        <label>{{ zh ? '估算剩余年数' : 'Years in this scenario' }}
          <input v-model.number="remainingYears" type="number" min="0.5" max="12" step="0.5">
        </label>
        <label>{{ zh ? '学费减免比例（自行填写%）' : 'Tuition discount (your assumption, %)' }}
          <input v-model.number="scholarshipPercent" type="number" min="0" max="100" step="0.1">
        </label>
        <label>{{ zh ? '每年生活费假设（RM）' : 'Living cost assumption per year (RM)' }}
          <input v-model.number="livingPerYear" type="number" min="0" step="100">
        </label>
      </div>
      <section class="card fee-results" aria-live="polite">
        <h2>{{ zh ? '估算结果' : 'Estimated costs' }}</h2>
        <template v-if="estimate">
          <dl>
            <div><dt>{{ zh ? '官方列出的收费基础' : 'Published fee basis' }}</dt><dd>{{ estimate.basis === 'per_year' ? (zh ? '每年' : 'Per year') : (zh ? '整个课程' : 'Full course') }} · {{ money(estimate.published) }}</dd></div>
            <div><dt>{{ zh ? '估算原始学费' : 'Estimated gross tuition' }}</dt><dd>{{ money(estimate.grossTuition) }}</dd></div>
            <div><dt>{{ zh ? '假设减免金额' : 'Assumed discount' }}</dt><dd>−{{ money(estimate.discount) }}</dd></div>
            <div><dt>{{ zh ? '估算学费' : 'Estimated tuition after discount' }}</dt><dd>{{ money(estimate.netTuition) }}</dd></div>
            <div><dt>{{ zh ? '假设生活费' : 'Assumed living costs' }}</dt><dd>{{ money(estimate.living) }}</dd></div>
            <div class="fee-total"><dt>{{ zh ? '估算总额' : 'Estimated total' }}</dt><dd>{{ money(estimate.total) }}</dd></div>
          </dl>
          <p v-if="feeSide === 'international'" class="muted">{{ zh ? '国际学生的学费另加6% SST，上面的金额没有算进去' : 'International students also pay 6% SST on tuition, which is not included above.' }}</p>
          <p v-if="estimate.basis === 'full_course'" class="muted">{{ zh ? '这里使用的是官方列出的整个课程总学费，不会按剩余年数重新分摊；如果你已经完成部分课程，请向学校确认实际应缴余额' : 'The published full-course fee is not prorated by remaining years. Ask Monash for your actual balance if you have completed part of the degree.' }}</p>
        </template>
        <p v-else>{{ zh ? '该学位的金额或收费基础无法可靠读取，不能进行估算。请查看官网原表' : 'The amount or fee basis is missing or unreadable. No estimate can be made; check the official table.' }}</p>
      </section>
      <footer class="fee-source">
        <p v-if="source?.url">{{ zh ? '学费来源' : 'Published source' }}：<a :href="source.url" target="_blank" rel="noopener external">{{ source.title || 'Monash Malaysia' }} ↗</a> <template v-if="source.last_checked"> · <LastChecked :value="source.last_checked" /></template></p>
        <p class="muted">{{ zh ? '这是个人计算器，不是Monash收费通知或奖学金资格评估。奖学金可能只覆盖部分学期或收费项目，汇率、额外费用和生活费也可能变化' : 'This is a scenario calculator, not an invoice or a scholarship eligibility assessment. Award terms, periods, extra charges and actual living costs may differ.' }}</p>
      </footer>
    </template>
  </div>
</template>

<style scoped>
.fee-planner { max-width: 940px; margin: 0 auto; }
.intro { margin-bottom: var(--s5); }
.fee-basis-note { padding: var(--s3); background: var(--surface-2); border-radius: 8px; }
.fee-controls { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--s4); padding: var(--s5); margin: var(--s5) 0; }
.fee-controls label { display: grid; gap: 6px; font-weight: 600; }
.fee-controls input, .fee-controls select { width: 100%; min-height: 44px; padding: 8px 12px; border: 1px solid var(--border-strong); border-radius: 8px; background: var(--surface); font: inherit; }
.fee-results { padding: var(--s5); }
.fee-results h2 { margin-bottom: var(--s4); }
.fee-results dl > div { display: flex; justify-content: space-between; flex-wrap: wrap; gap: var(--s2); padding: 10px 0; border-bottom: 1px solid var(--border); }
.fee-results dd { margin: 0; font-weight: 600; font-variant-numeric: tabular-nums; }
.fee-total { font-size: 1.15rem; }
.fee-source { margin: var(--s5) 0; font-size: .88rem; }
@media (max-width: 620px) { .fee-controls { grid-template-columns: 1fr; } }
</style>
