<script setup lang="ts">
/**
 * Every Monash Malaysia tuition fee on one page.
 *
 * The rows are the official /ugfees and /pgfees tables as last read, grouped the
 * way Monash groups them: by level, then by school. A degree page shows its own
 * row; this page is for comparing, and for the rows that are not one degree
 * (Monash English, a PhD in each school, the two DHES streams).
 */
import { deltaAt, feeNote, feeTitle, filterFees, formatAmount, type FeeRow } from '~/utils/tuition'
import { INTAKES_2027, intake2027Status, currentIntakeReview, type IntakePeriod } from '~/utils/intake2027'

type Source = { title: string; url: string; level: string; last_checked: string | null }
type Table = {
  selection?: { year: number | null; intake: string | null; campus: string }
  admissions_coverage?: { rows: number; linked_programme_rows: number; verified_programme_rows: number; explicit_notice_rows: number; conflict_rows: number }
  year: number | null
  sections: { source: string; year?: number | null; level: string; schools: { school: string; rows: FeeRow[] }[] }[]
  general: string[]
  sources: Record<string, Source>
  previous: { year: number; kind: 'versions' | 'printed'; sources: Record<string, { title: string; url: string; read_on?: string }> } | null
}

const { $t } = useNuxtApp()
const { locale } = useLocale()
const route = useRoute()
const router = useRouter()

const requestedYear = Number(route.query.year)
const selectedYear = ref(Number.isInteger(requestedYear) && requestedYear >= 1990 && requestedYear <= 2100 ? requestedYear : 2027)
const selectedIntake = ref<IntakePeriod>(['february', 'july', 'october'].includes(String(route.query.intake)) ? route.query.intake as IntakePeriod : 'october')
const { data, error, status } = await useApiFetch<Table>(
  () => `/v1/fees?year=${selectedYear.value}&intake=${selectedIntake.value}&campus=Malaysia`,
  { watch: [selectedYear, selectedIntake] }
)
const selectionMatches = computed(() => data.value?.selection?.year === selectedYear.value && data.value?.selection?.intake === selectedIntake.value)
const feeYears = computed(() => [...new Set([2027, 2028, selectedYear.value, ...(data.value?.sections.map(s => s.year).filter((y): y is number => y != null) || [])])].sort())
useErrorStatus(error)

const query = ref(String(route.query.q || ''))
const statuses = ['open', 'closed', 'suspended', 'conflict', 'not_verified']
const admissionsFilter = ref(statuses.includes(String(route.query.admissions)) ? String(route.query.admissions) : '')
const intakeStatuses = [...statuses, 'not_offered_on_campus']
const intakeLabels: Record<string, string> = {open:'明确开放', closed:'明确关闭', suspended:'明确暂停', conflict:'来源冲突', not_verified:'未核实', not_offered_on_campus:'明确未在该校区开设'}
const intakeFilter = ref(intakeStatuses.includes(String(route.query.intake_status)) ? String(route.query.intake_status) : '')
watch([query, admissionsFilter, selectedYear, selectedIntake, intakeFilter], ([q, admissions, year, intake, intakeStatus]) => {
  router.replace({ query: { ...route.query, q: q.trim() || undefined, admissions: admissions || undefined, year, intake, intake_status: intakeStatus || undefined } })
})

const sections = computed(() =>
  (selectionMatches.value ? data.value?.sections || [] : [])
    .map(section => ({
      ...section,
      schools: section.schools
        .map(group => ({ ...group, rows: filterFees(group.rows, query.value).filter(row =>
          (!admissionsFilter.value || (row.admissions?.status || 'not_verified') === admissionsFilter.value) &&
          (!intakeFilter.value || (row.admissions?.intake_status || 'not_verified') === intakeFilter.value)
        ) }))
        .filter(group => group.rows.length)
    }))
    .filter(section => section.schools.length)
)

const empty = computed(() => !data.value?.sections?.length)
const intakeEvidence = computed(() => INTAKES_2027.find(item => item.id === selectedIntake.value)!)
const reviewedIntake = computed(() => currentIntakeReview(intakeEvidence.value, selectedYear.value))
/** "2027-10-15" as 2027年10月15日 in Chinese; English keeps the ISO date. */
const day = (iso: string) => {
  const [y, m, d] = iso.split('-').map(Number)
  return locale.value === 'zh' && y && m && d ? `${y}年${m}月${d}日` : iso
}
const intakeLabel = (id: IntakePeriod) => {
  if (locale.value === 'zh') return `2027年${id === 'february' ? '2月' : id === 'july' ? '7月' : '10月'}入学`
  return `${id === 'february' ? 'February' : id === 'july' ? 'July' : 'October'} 2027`
}


function label(row: FeeRow) {
  const title = feeTitle(row, locale.value)
  return row.variant ? `${title} · ${row.variant}` : title
}

/** The undergraduate table gives a bare number of years ("3"). */
function duration(text: string) {
  return /^\d+(\.\d+)?$/.test(text) ? $t('courses.years', { n: text }) : text
}

function schoolName(key: string) {
  const text = $t(`fees.school.${key}`)
  return text === `fees.school.${key}` ? key : text
}

function modeName(mode: string | null) {
  if (!mode) return ''
  const key = `fees.mode.${mode.toLowerCase().replace(/\s+/g, '')}`
  const text = $t(key)
  return text === key ? mode : text
}

const title = computed(() =>
  data.value?.year ? $t('fees.title', { year: data.value.year }) : $t('fees.titleNoYear')
)
useSeoMeta({ title, description: () => $t('fees.lede') })
</script>

<template>
  <div class="page">
    <ErrorState v-if="error" :error="error" />
    <template v-else>
      <header class="intro">
        <p class="crumb"><NuxtLink to="/courses">{{ $t('courses.title') }}</NuxtLink></p>
        <h1>{{ title }}</h1>
        <p class="lede">{{ $t('fees.lede') }}</p>
        <div class="intake-selection">
          <p>{{ locale === 'zh' ? '适用校区：马来西亚' : 'Campus: Malaysia' }}</p>
          <label>{{ locale === 'zh' ? '入学年份' : 'Intake year' }}
            <select v-model.number="selectedYear" class="field" aria-label="Intake year">
              <option v-for="year in feeYears" :key="year" :value="year">{{ year }}</option>
            </select>
          </label>
          <label>{{ locale === 'zh' ? '入学批次' : 'Intake period' }}
            <select v-model="selectedIntake" class="field" aria-label="Intake period">
              <option v-for="item in INTAKES_2027" :key="item.id" :value="item.id">{{ locale === 'zh' ? ({february: '2月', july: '7月', october: '10月'})[item.id] : item.id }}</option>
            </select>
          </label>
          <p v-if="!reviewedIntake" class="small muted">{{ locale === 'zh' ? '所选年份或批次的名单与一般截止日期尚未核实。旧年份资料不自动适用于此选择。' : 'The selected year or intake list and general deadlines are unverified. Earlier-year information does not establish applicability.' }}</p>
        </div>
        <section v-if="reviewedIntake" class="intake-evidence" aria-labelledby="intake-evidence-title">
          <h2 id="intake-evidence-title">{{ locale === 'zh' ? '2027年各批次招生信息' : '2027 intake evidence' }}</h2>
          <p class="small muted">{{ locale === 'zh'
            ? '学费已经公布，不代表该学位在每个批次都开放申请。请选择入学批次查看学校公布的资料'
            : 'A published fee does not mean applications for that degree or intake are open. Select the intake to see what Monash has actually published.' }}</p>
          <div class="intake-facts small">
            <p>{{ locale === 'zh' ? '马来西亚学生申请截止' : 'Malaysian students apply by' }}{{ locale === 'zh' ? '：' : ' ' }}<strong>{{ day(intakeEvidence.generalDeadlineMalaysia) }}</strong></p>
            <p>{{ locale === 'zh' ? '国际学生申请截止' : 'International students apply by' }}{{ locale === 'zh' ? '：' : ' ' }}<strong>{{ day(intakeEvidence.generalDeadlineInternational) }}</strong></p>
          </div>
          <p class="small muted">{{ intakeEvidence.hasVerifiedDegreeList
            ? (locale === 'zh' ? '学校已公布10月可选课程名单，下方按课程原名精确标注。未列入名单的学位统一显示“未核实”，不能推断停招' : 'An explicit October available-courses list exists. Exact title matches are marked below; other degrees remain unverified, not discontinued.')
            : (locale === 'zh' ? '目前只有该批次的申请截止日期资料，未找到逐学位可选课程名单，因此下方招生状态全部显示“未核实”' : 'Published deadlines are available, but no intake-specific degree-by-degree list was verified. All degree statuses therefore remain unverified.') }}</p>
          <p class="small muted" v-if="intakeEvidence.exceptionsApply">{{ locale === 'zh' ? '部分专业有特别截止日期，例如医学、临床心理学或专业心理咨询，请以官网对应类别为准' : 'Special deadlines apply to some programmes, including medicine and certain psychology/counselling degrees. Check the matching official category.' }}</p>
          <p class="small muted">{{ locale === 'zh' ? '一般截止日期不能证明某个学位当前开放申请' : 'General deadlines do not establish that a programme is accepting applications.' }} ·
            <a :href="intakeEvidence.source" target="_blank" rel="noopener external">{{ locale === 'zh' ? '查看官方招生页面' : 'Official intake page' }} ↗</a>
            · {{ locale === 'zh' ? '资料核对日期' : 'Reviewed' }}：{{ day(intakeEvidence.checkedOn) }}
          </p>
        </section>
        <p class="fee-planner-link"><NuxtLink to="/fees/planner">{{ locale === 'zh' ? '自己估算学费、减免和生活费' : 'Estimate tuition, discounts and living costs' }} →</NuxtLink></p>
      </header>

      <EmptyState v-if="empty" :title="$t('fees.emptyTitle')" :hint="$t('fees.emptyBody')" />
      <template v-else>
        <p v-if="data?.admissions_coverage" class="source-coverage" role="status">
          {{ locale === 'zh' ? '课程来源覆盖（全部收费行）' : 'Programme-source coverage (all fee rows)' }}：
          {{ data.admissions_coverage.linked_programme_rows }}/{{ data.admissions_coverage.rows }}
          {{ locale === 'zh' ? '有课程链接；' : 'linked; ' }}
          {{ data.admissions_coverage.verified_programme_rows }}
          {{ locale === 'zh' ? '来源索引有效。有效来源不等于已开放申请；未匹配、未抓取或过期的来源仍显示未核实。' : 'have a current matching source indexed. A current source does not mean applications are open; unmatched, unindexed or stale sources remain unverified.' }}
        </p>
        <input
          v-model="query"
          class="field filter"
          type="search"
          :placeholder="$t('fees.filter')"
          :aria-label="$t('fees.filter')"
          autocomplete="off"
        />

        <label class="intake-status-filter">
          {{ locale === 'zh' ? '筛选所选批次的申请状态' : 'Filter selected-intake application status' }}
          <select v-model="intakeFilter" class="field">
            <option value="">{{ locale === 'zh' ? '全部状态' : 'All statuses' }}</option>
            <option v-for="state in intakeStatuses" :key="state" :value="state">{{ locale === 'zh' ? intakeLabels[state] || state : state }}</option>
          </select>
        </label>
        <p v-if="status === 'pending' || !selectionMatches" role="status">{{ locale === 'zh' ? '正在核对所选年份和批次…' : 'Checking the selected year and intake…' }}</p>
        <label class="admissions-filter">
          {{ locale === 'zh' ? '筛选当前申请通知（与未来批次分开）' : 'Filter current application notices (separate from future intake)' }}
          <select v-model="admissionsFilter" class="field">
            <option value="">{{ locale === 'zh' ? '全部状态' : 'All statuses' }}</option>
            <option value="open">{{ locale === 'zh' ? '明确开放' : 'Explicitly open' }}</option>
            <option value="closed">{{ locale === 'zh' ? '明确关闭' : 'Explicitly closed' }}</option>
            <option value="suspended">{{ locale === 'zh' ? '明确暂停' : 'Explicitly suspended' }}</option>
            <option value="conflict">{{ locale === 'zh' ? '来源冲突' : 'Conflicting sources' }}</option>
            <option value="not_verified">{{ locale === 'zh' ? '未核实' : 'Not verified' }}</option>
          </select>
        </label>

        <ul class="keys small">
          <li>{{ $t('fees.keyBasis') }}</li>
          <li>{{ $t('fees.excludes') }}</li>
          <li>{{ $t('fees.noTotal') }}</li>
          <li v-if="data?.previous">
            {{ $t(data.previous.kind === 'printed' ? 'fees.previousNote' : 'fees.previousNoteStored', { year: data.previous.year }) }}
            <template v-for="([key, source], n) in Object.entries(data.previous.sources)" :key="key">
              <template v-if="n">, </template>
              <a :href="source.url" rel="noopener external" target="_blank">{{ source.title }}</a>
            </template>
          </li>
        </ul>

        <p v-if="!sections.length" class="small muted">{{ $t('fees.noMatch', { q: query }) }}</p>

        <section v-for="section in sections" :key="section.source" class="level">
          <h2>{{ $t(`fees.level.${section.level}`) }}<span v-if="section.year"> · {{ section.year }}</span></h2>
          <p class="tiny muted">
            <a :href="data!.sources[section.source]?.url" rel="noopener external" target="_blank">{{ data!.sources[section.source]?.title }}</a>
            <template v-if="data!.sources[section.source]?.last_checked">
              · <LastChecked :value="data!.sources[section.source]!.last_checked" />
            </template>
          </p>

          <div v-for="group in section.schools" :key="group.school" class="school">
            <h3>{{ schoolName(group.school) }}</h3>
            <div class="table" role="table" :aria-label="schoolName(group.school)">
              <div class="tr th" role="row">
                <span role="columnheader">{{ $t('fees.course') }}</span>
                <span role="columnheader">{{ $t('fees.domestic') }}</span>
                <span role="columnheader">{{ $t('fees.international') }}</span>
                <span role="columnheader">{{ $t('fees.basis') }}</span>
              </div>
              <div v-for="(row, i) in group.rows" :key="i" class="tr" role="row">
                <span class="name" role="cell">
                  <b>{{ label(row) }}</b>
                  <span class="tiny fee-publication" v-if="row.fee_publication">
                    {{ locale === 'zh' ? '所选年份学费' : 'Fees for selected year' }}：{{ row.fee_publication.status === 'published' ? (locale === 'zh' ? '已公布' : 'Published') : (locale === 'zh' ? '未核实' : 'Not verified') }}
                    <template v-if="row.fee_publication.reason === 'different_fee_year'"> · {{ locale === 'zh' ? '当前收费来源年份' : 'Fee source year' }} {{ row.fee_publication.published_year }}</template>
                    <template v-if="row.fee_publication.reason === 'stale_source' || row.fee_publication.reason === 'refresh_failed'"> · {{ locale === 'zh' ? '来源过期或刷新失败，显示的是已存档金额' : 'Stale or failed refresh; amounts are retained snapshots' }}</template>
                  </span>
                  <span v-if="locale === 'zh' && row.title_zh" class="tiny muted en">{{ row.title }}</span>
                  <span v-if="selectedYear === 2027" class="tiny" :class="intake2027Status(row.title, selectedIntake, selectedYear) === 'listed' ? 'intake-listed' : 'intake-unverified'">
                    {{ intake2027Status(row.title, selectedIntake, selectedYear) === 'listed'
                      ? (locale === 'zh' ? '该批次官方名单列出' : 'Listed for this intake')
                      : (locale === 'zh' ? '该批次招生状态未核实' : 'Intake status unverified') }}
                  </span>
                  <span class="tiny muted">
                    <template v-if="row.duration && !row.variant">{{ duration(row.duration) }}</template>
                    <template v-if="row.mode"> · {{ modeName(row.mode) }}</template>
                  </span>
                  <AdmissionsNotice v-if="row.admissions" :evidence="row.admissions" compact />
                  <span v-if="row.covers.length" class="tiny muted covers">
                    {{ $t('fees.covers') }}{{ locale === 'zh' ? '：' : ': ' }}{{ row.covers.join(', ') }}
                  </span>
                  <span v-if="row.note" class="tiny note">{{ feeNote(row.note, locale) }}</span>
                  <span v-if="row.unreadable" class="tiny warn">{{ $t('fees.unreadable') }}</span>
                </span>
                <span class="money" role="cell" :data-label="$t('fees.domestic')">
                  <span v-for="(a, n) in row.domestic" :key="n">
                    {{ formatAmount(a) }}<small v-if="a.label"> {{ a.label }}</small>
                    <FeeDelta :delta="deltaAt(row.change, 'domestic', n)" :year="row.change?.year" />
                  </span>
                </span>
                <span class="money" role="cell" :data-label="$t('fees.international')">
                  <span v-for="(a, n) in row.international" :key="n">
                    {{ formatAmount(a) }}<small v-if="a.label"> {{ a.label }}</small>
                    <FeeDelta :delta="deltaAt(row.change, 'international', n)" :year="row.change?.year" />
                  </span>
                </span>
                <span role="cell" :data-label="$t('fees.basis')">
                  <span v-if="row.basis" class="basis" :class="`basis--${row.basis}`">{{ $t(`fees.basis.${row.basis}`) }}</span>
                </span>
              </div>
            </div>
          </div>
        </section>

        <section v-if="data?.general?.length" class="general">
          <h2>{{ $t('fees.general') }}</h2>
          <ul class="small">
            <li v-for="line in data.general" :key="line">{{ line }}</li>
          </ul>
        </section>
      </template>
    </template>
  </div>
</template>

<style scoped>
.intake-selection { display: flex; flex-wrap: wrap; gap: var(--s3); align-items: end; margin-block: var(--s4); }
.intake-selection label { display: grid; gap: var(--s2); max-width: 100%; }
.intake-selection p { flex-basis: 100%; }

.admissions-filter { display: grid; gap: 6px; max-width: 520px; margin-block: var(--s3); }
.admissions-filter select { min-height: 44px; }
.page { max-width: 960px; margin: 0 auto; padding: var(--s5) var(--s4) var(--s7); }
.crumb { margin: 0 0 var(--s2); font-size: 0.85rem; }
.intro h1 { margin: 0 0 var(--s2); }
.lede { margin: 0 0 var(--s4); color: var(--muted); }
.filter {
  width: 100%; max-width: 28rem; margin-bottom: var(--s3);
  padding: var(--s2) var(--s3); border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm); font: inherit; background: var(--surface); color: var(--text);
}
.keys { margin: 0 0 var(--s5); padding-left: 1.2em; color: var(--muted); display: grid; gap: var(--s1); }

.level { margin-bottom: var(--s6); }
.level h2 { margin: 0 0 var(--s1); font-size: 1.15rem; }
.level > .tiny { margin: 0 0 var(--s3); overflow-wrap: anywhere; }
.school { margin-bottom: var(--s4); }
.school h3 { margin: 0 0 var(--s2); font-size: 0.95rem; color: var(--navy); }

.table { border: 1px solid var(--border); border-radius: var(--radius); background: var(--surface); }
.tr {
  display: grid; grid-template-columns: minmax(0, 2.4fr) minmax(0, 1fr) minmax(0, 1fr) 6.5rem;
  gap: var(--s3); padding: var(--s3); border-top: 1px solid var(--border); align-items: start;
}
.tr:first-child { border-top: 0; }
.th { font-size: 0.75rem; color: var(--muted); padding-block: var(--s2); }
.name { display: grid; gap: 2px; min-width: 0; }
.en { font-style: italic; }
.covers, .note, .warn { overflow-wrap: anywhere; }
.warn { color: var(--warning); }
.money { display: grid; gap: 2px; font: 600 0.95rem var(--font-mono); color: var(--navy); }
.money small { display: block; font: 400 0.75rem var(--font); color: var(--muted); }
.basis {
  display: inline-block; padding: 0 var(--s2); border-radius: 999px;
  font-size: 0.8rem; font-weight: 600; border: 1px solid currentColor; white-space: nowrap;
}
.basis--full_course { color: var(--warning); }
.basis--per_year { color: var(--blue); }

.general h2 { font-size: 1.05rem; margin: 0 0 var(--s2); }
.general ul { margin: 0; padding-left: 1.2em; display: grid; gap: var(--s1); }

/* On a phone each row becomes a small card, with the fee labels written out. */
@media (max-width: 640px) {
  .th { display: none; }
  .tr { grid-template-columns: 1fr 1fr; }
  .name { grid-column: 1 / -1; }
  .tr > [data-label]::before {
    content: attr(data-label); display: block;
    font: 400 0.7rem var(--font); color: var(--muted);
  }
}
.fee-planner-link { margin-top: var(--s2); font-weight: 600; }
.intake-explainer { line-height: 1.6; }
.intake-listed { display: inline-block; color: var(--success); font-weight: 600; }
.intake-unverified { display: inline-block; color: var(--muted); }
.intake-evidence { background: var(--surface-2); border: 1px solid var(--border); padding: var(--s4); border-radius: var(--radius); margin-bottom: var(--s4); }
.intake-evidence h2 { margin: 0 0 var(--s2); font-size: 1.05rem; }
.intake-evidence p { margin: var(--s2) 0; }
.intake-picker { display: grid; max-width: 240px; gap: var(--s1); font-size: .9rem; font-weight: 600; }
.intake-picker select { min-height: 44px; }
.intake-facts { display: flex; flex-wrap: wrap; gap: 4px var(--s5); margin: var(--s3) 0; }
.intake-facts p { margin: 0; }
</style>

<style scoped>
.source-coverage { padding: var(--s3); border: 1px solid var(--border); border-radius: 8px; overflow-wrap: anywhere; }
</style>
