<script setup lang="ts">
/**
 * Every course plan kept in this browser, side by side.
 *
 * The course map edits one plan at a time; this is where a student keeps the
 * others: the real plan, the one where they switch major, the one a friend
 * exported. Each card has enough of the plan drawn on it (a small grid of the
 * semesters and their units) to tell two plans apart without opening them.
 *
 * Credit points and problem counts come from the same /plan/check the map
 * uses, one call per plan, so the numbers here and on the map cannot differ.
 */
import { MAX_PLANS, type StoredPlan } from '~/composables/usePlan'
import { toCsv } from '~/utils/csv'

const { $t } = useNuxtApp()
const { locale } = useLocale()
const { library, switchTo, create, duplicate, removePlan, rename } = usePlan()

const { data: courseList } = await useLocalisedApiFetch<any>(() => '/v1/courses?limit=200')
const courseByCode = computed(() => {
  const map = new Map<string, any>()
  for (const c of courseList.value?.results || []) map.set(c.course_code, c)
  return map
})

// --- per-plan checks ------------------------------------------------------

interface Checked { points: number; problems: number; titles: Record<string, string> }
const checked = ref<Record<string, Checked>>({})

/** What was last checked for each plan, so an unchanged plan is not sent again. */
const sent = new Map<string, string>()

async function checkAll() {
  for (const stored of library.value.plans) {
    const body = JSON.stringify([stored.state.entries, stored.state.campus])
    if (sent.get(stored.id) === body) continue
    sent.set(stored.id, body)
    if (!stored.state.entries.length) {
      checked.value[stored.id] = { points: 0, problems: 0, titles: {} }
      continue
    }
    try {
      const report = await apiFetch<any>('/v1/plan/check', {
        method: 'POST',
        body: { campus: stored.state.campus, entries: stored.state.entries }
      })
      checked.value[stored.id] = {
        points: report.credit_points ?? 0,
        problems: (report.issues || []).filter((i: any) => i.severity === 'error').length,
        titles: report.unit_titles || {}
      }
    } catch {
      // The card still shows the plan; it just goes without numbers.
      sent.delete(stored.id)
    }
  }
}

onMounted(checkAll)
watch(() => library.value.plans.map((p) => p.updatedAt).join(), checkAll)

// --- drawing a card ----------------------------------------------------------

function displayName(stored: StoredPlan): string {
  return stored.state.name || $t('plans.untitled')
}

function required(stored: StoredPlan): number {
  return Number(courseByCode.value.get(stored.state.courseCode)?.credit_points) || 0
}

function fraction(stored: StoredPlan): number {
  const need = required(stored)
  const have = checked.value[stored.id]?.points ?? 0
  return need ? Math.min(1, have / need) : 0
}

function shortPeriod(period: string): string {
  const key = `plan.period.${period}`
  const label = $t(key)
  return label === key ? period : label
}

/**
 * The rows of the mini map: every year and teaching period the plan has,
 * each with its unit codes. Empty rows are kept, because an empty second year
 * is part of what the plan looks like.
 */
function rows(stored: StoredPlan) {
  const { startYear, years, periods, entries } = stored.state
  const out: { label: string; codes: string[] }[] = []
  for (let y = 0; y < years; y++) {
    for (const period of periods) {
      const year = startYear + y
      out.push({
        label: `${shortPeriod(period)}, ${year}`,
        codes: entries.filter((e) => e.year === year && e.teaching_period === period).map((e) => e.unit_code)
      })
    }
  }
  return out
}

/**
 * A colour per subject area (FIT, MAT, ECO...), only so a glance can tell a
 * computing-heavy plan from a mixed one. Hashed from the prefix rather than
 * listed, because there are hundreds of prefixes.
 */
function tone(code: string): number {
  const prefix = code.replace(/\d.*$/, '')
  let hash = 0
  for (const ch of prefix) hash = (hash * 31 + ch.charCodeAt(0)) >>> 0
  return (hash % 5) + 1
}

function updated(stored: StoredPlan): string {
  try {
    return new Intl.DateTimeFormat(locale.value === 'zh' ? 'zh-CN' : locale.value, {
      dateStyle: 'medium',
      timeStyle: 'short'
    }).format(new Date(stored.updatedAt))
  } catch {
    return new Date(stored.updatedAt).toLocaleString()
  }
}

// --- actions --------------------------------------------------------------------

function open(id: string) {
  switchTo(id)
  navigateTo('/plan')
}

function startNew() {
  if (create()) navigateTo('/plan')
}

function copy(id: string) {
  duplicate(id, (name) => $t('plans.copyOf', { name: name || $t('plans.untitled') }))
}

function confirmDelete(stored: StoredPlan) {
  if (window.confirm($t('plans.deleteConfirm', { name: displayName(stored) }))) removePlan(stored.id)
}

function onRename(stored: StoredPlan, event: Event) {
  rename(stored.id, (event.target as HTMLInputElement).value)
}

function downloadCsv(stored: StoredPlan) {
  const titles = checked.value[stored.id]?.titles || {}
  const head = ['year', 'teaching_period', 'unit_code', 'title']
  const order = (p: string) => stored.state.periods.indexOf(p)
  const body = [...stored.state.entries]
    .sort((a, b) => a.year - b.year || order(a.teaching_period) - order(b.teaching_period))
    .map((e) => [e.year, shortPeriod(e.teaching_period), e.unit_code, titles[e.unit_code] || ''])
  const blob = new Blob([toCsv([head, ...body])], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  const stem = displayName(stored).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
  link.href = url
  link.download = `monash-hub-${stem || 'plan'}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

const full = computed(() => library.value.plans.length >= MAX_PLANS)

useSeoMeta({ title: () => $t('plans.title') })
</script>

<template>
  <div class="page">
    <header class="intro">
      <div>
        <h1>{{ $t('plans.title') }}</h1>
        <p class="lede">{{ $t('plans.lede') }}</p>
      </div>
      <button class="btn" type="button" :disabled="full" @click="startNew">
        <PlanIcon name="plus" />{{ $t('plans.new') }}
      </button>
    </header>

    <ul class="list">
      <li
        v-for="stored in library.plans"
        :key="stored.id"
        class="item"
        :class="{ 'item--active': stored.id === library.activeId }"
      >
        <div class="body">
          <div class="info">
            <div class="name-line">
              <input
                class="name"
                type="text"
                maxlength="60"
                :value="stored.state.name"
                :placeholder="$t('plans.untitled')"
                :aria-label="$t('plans.name')"
                @change="onRename(stored, $event)"
              />
              <span v-if="stored.id === library.activeId" class="badge">{{ $t('plans.active') }}</span>
            </div>
            <p class="degree">
              <template v-if="stored.state.courseCode">
                <span class="mono">{{ stored.state.courseCode }}</span>
                {{ courseByCode.get(stored.state.courseCode)?.title || '' }}
              </template>
              <em v-else>{{ $t('plan.noCourse') }}</em>
            </p>

            <div class="meter" :aria-hidden="!required(stored)">
              <span class="meter-fill" :style="{ width: `${fraction(stored) * 100}%` }" />
            </div>
            <p class="numbers">
              <strong>{{ checked[stored.id]?.points ?? '…' }}</strong>
              <template v-if="required(stored)"> / {{ required(stored) }}</template>
              {{ $t('courses.creditPoints') }}
              <span v-if="required(stored)" class="pct">{{ Math.round(fraction(stored) * 100) }}%</span>
            </p>
            <p v-if="checked[stored.id]?.problems" class="problems">
              <PlanIcon name="alert" :size="13" />{{ $t('plan.errors', { n: checked[stored.id]!.problems }) }}
            </p>

            <p class="updated">
              <span>{{ $t('plans.updated') }}</span>
              {{ updated(stored) }}
            </p>
          </div>

          <!-- A thumbnail of the plan. Codes rather than blank boxes, so two
               plans for the same degree can still be told apart. -->
          <div class="mini" role="img" :aria-label="$t('plans.preview', { name: stored.state.name || $t('plans.untitled') })">
            <div v-for="(row, i) in rows(stored)" :key="i" class="mini-row">
              <span class="mini-label">{{ row.label }}</span>
              <span
                v-for="n in Math.max(4, row.codes.length)"
                :key="n"
                class="mini-cell"
                :class="row.codes[n - 1] ? `tone-${tone(row.codes[n - 1]!)}` : 'mini-cell--empty'"
              >{{ row.codes[n - 1] || '' }}</span>
            </div>
          </div>
        </div>

        <footer class="actions">
          <button class="act" type="button" :disabled="!stored.state.entries.length" @click="downloadCsv(stored)">
            <PlanIcon name="download" :size="15" />CSV
          </button>
          <span class="spacer" />
          <button class="act" type="button" :disabled="full" @click="copy(stored.id)">
            <PlanIcon name="copy" :size="15" />{{ $t('plans.duplicate') }}
          </button>
          <button class="act act--danger" type="button" @click="confirmDelete(stored)">
            <PlanIcon name="trash" :size="15" />{{ $t('plans.delete') }}
          </button>
          <button class="btn btn--small" type="button" @click="open(stored.id)">
            {{ $t('plans.open') }}<PlanIcon name="chevron" :size="15" />
          </button>
        </footer>
      </li>
    </ul>

    <button class="new" type="button" :disabled="full" @click="startNew">
      <PlanIcon name="plus" />
      <span>{{ full ? $t('plans.limit', { n: MAX_PLANS }) : $t('plans.new') }}</span>
    </button>

    <p class="privacy"><PlanIcon name="lock" :size="14" />{{ $t('plan.privacy') }}</p>
  </div>
</template>

<style scoped>
.page { max-width: 1400px; margin: 0 auto; padding: var(--s5) var(--s5) var(--s7); }

.intro {
  display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between;
  gap: var(--s4); margin-bottom: var(--s5);
}
.intro h1 { margin: 0 0 var(--s1); }
.lede { margin: 0; color: var(--muted); max-width: var(--measure-lede); font-size: 0.95rem; }

.list { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--s4); }
.item {
  background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
  box-shadow: var(--shadow); overflow: hidden;
}
.item--active { border-color: var(--brand); box-shadow: 0 0 0 1px var(--brand), var(--shadow); }

.body { display: grid; grid-template-columns: 320px minmax(0, 1fr); }
.info { padding: var(--s5); border-right: 1px solid var(--border); min-width: 0; }

.name-line { display: flex; align-items: center; gap: var(--s2); }
.name {
  flex: 1; min-width: 0; margin-left: -8px; padding: 2px 8px;
  border: 1px solid transparent; border-radius: 6px; background: none;
  font: 600 1.15rem var(--font); color: var(--text);
}
.name::placeholder { color: var(--text); }
.name:hover { border-color: var(--border); }
.name:focus { border-color: var(--brand); outline: none; box-shadow: 0 0 0 3px var(--blue-50); }
.badge {
  flex: none; padding: 2px 8px; border-radius: var(--radius-pill);
  background: var(--blue-50); color: var(--brand-700); font-size: 0.7rem; font-weight: 600;
}
.degree { margin: 2px 0 var(--s4); font-size: 0.85rem; color: var(--muted); }
.degree em { font-style: italic; }
.degree .mono { font-weight: 600; color: var(--navy); margin-right: 4px; }

.meter { height: 6px; background: var(--surface-2); border-radius: var(--radius-pill); overflow: hidden; }
.meter-fill { display: block; height: 100%; background: var(--brand); border-radius: inherit; transition: width 0.4s ease; }
.numbers { display: flex; align-items: baseline; gap: 4px; margin: 6px 0 0; font-size: 0.82rem; color: var(--muted); }
.numbers strong { color: var(--text); font-size: 0.95rem; }
.pct { margin-left: auto; font-family: var(--font-mono); }
.problems { display: flex; align-items: center; gap: 5px; margin: var(--s2) 0 0; font-size: 0.8rem; color: var(--danger); }
.updated { margin: var(--s4) 0 0; font-size: 0.8rem; color: var(--text); }
.updated span {
  display: block; font-size: 0.68rem; font-weight: 600; letter-spacing: 0.06em;
  text-transform: uppercase; color: var(--muted);
}

.mini {
  display: grid; gap: 4px; align-content: start; padding: var(--s5);
  overflow-x: auto; background: #fafbfc;
}
.mini-row {
  display: grid; grid-template-columns: 120px; grid-auto-flow: column; grid-auto-columns: 92px;
  gap: 4px; align-items: center; justify-content: start;
}
.mini-label { font-size: 0.72rem; color: var(--muted); text-align: right; padding-right: var(--s2); white-space: nowrap; }
.mini-cell {
  height: 24px; display: grid; place-items: center; border-radius: 4px;
  font: 600 0.7rem var(--font-mono); color: var(--tone); background: var(--tone-bg);
  border-left: 3px solid var(--tone);
}
.mini-cell--empty { border: 1px dashed var(--border-strong); background: none; }
.tone-1 { --tone: var(--part-1); --tone-bg: var(--part-1-bg); }
.tone-2 { --tone: var(--part-2); --tone-bg: var(--part-2-bg); }
.tone-3 { --tone: var(--part-3); --tone-bg: var(--part-3-bg); }
.tone-4 { --tone: var(--part-4); --tone-bg: var(--part-4-bg); }
.tone-5 { --tone: var(--part-5); --tone-bg: var(--part-5-bg); }

.actions {
  display: flex; align-items: center; gap: var(--s1); flex-wrap: wrap;
  padding: var(--s3) var(--s5); border-top: 1px solid var(--border);
}
.spacer { flex: 1; }
.act {
  display: inline-flex; align-items: center; gap: 6px; min-height: 36px; padding: 0 var(--s3);
  border: 0; border-radius: var(--radius-sm); background: none; color: var(--text);
  font: inherit; font-size: 0.85rem; font-weight: 500; cursor: pointer;
}
.act:hover:not(:disabled) { background: var(--surface-2); }
.act:disabled { color: var(--muted-2); cursor: default; }
.act--danger { color: var(--danger); }
.act--danger:hover { background: var(--danger-bg) !important; }
.btn :deep(svg) { margin: 0 -2px; }

.new {
  display: flex; align-items: center; justify-content: center; gap: var(--s2);
  width: 100%; margin-top: var(--s4); min-height: 96px;
  border: 1.5px dashed var(--border-strong); border-radius: 14px; background: none;
  color: var(--muted); font: inherit; font-weight: 500; cursor: pointer;
}
.new:hover:not(:disabled) { border-color: var(--brand); color: var(--brand); background: var(--blue-50); }
.new:disabled { cursor: default; }

.privacy {
  display: flex; gap: var(--s2); align-items: flex-start; margin: var(--s5) 0 0;
  font-size: 0.78rem; color: var(--muted);
}
.privacy :deep(svg) { margin-top: 3px; }

@media (max-width: 860px) {
  .page { padding: var(--s4) var(--s4) var(--s6); }
  .body { grid-template-columns: minmax(0, 1fr); }
  .info { border-right: 0; border-bottom: 1px solid var(--border); padding: var(--s4); }
  .mini { padding: var(--s3) var(--s4); }
  /* Four cells that share the width, rather than fixed cells that scroll. */
  .mini-row { grid-auto-flow: row; grid-template-columns: 76px repeat(4, minmax(0, 1fr)); }
  .mini-label { font-size: 0.66rem; white-space: normal; line-height: 1.2; }
  .mini-cell { font-size: 0.6rem; border-left-width: 2px; }
  .actions { padding: var(--s2) var(--s3); }
  .spacer { display: none; }
  .actions .btn { margin-left: auto; }
}
</style>
