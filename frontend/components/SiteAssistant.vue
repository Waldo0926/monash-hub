<script setup lang="ts">
/**
 * The "Ask" button in the corner of every page, and the chat panel it opens.
 *
 * It is the same zero-AI router as the search page (POST /v1/ask), drawn as a
 * conversation so a student can ask from wherever they are without losing the
 * page. No model is called and no key is needed, the same way SecureView's
 * Help Assistant works: every answer is a stored field or a link to one.
 *
 * On top of the router's answer it adds the site's own tools and the 马莫百科
 * posts the question names (utils/assistant.ts), the student posts the router
 * found, and a way on when nothing matched.
 *
 * The chat is kept in sessionStorage so it survives a page change and a
 * reload, and is gone when the tab closes. Nothing is sent anywhere except the
 * question itself.
 */
import { MAMO_POSTS, type MamoPost } from '~/data/mamo'
import { matchMamo, matchTools, type SiteTool } from '~/utils/assistant'

interface Turn {
  id: number
  question: string
  state: 'loading' | 'done' | 'error'
  answer: any
  tools: SiteTool[]
  mamo: MamoPost[]
  error: string
}

const STORAGE_KEY = 'monashhub.assistant.v1'
const MAX_TURNS = 12
const ASKMIRA = 'https://askmira.monash.edu.my/'

const { $t } = useNuxtApp()
const { locale } = useLocale()
const route = useRoute()
const { year } = useHandbookYear()

const open = ref(false)
const draft = ref('')
const turns = ref<Turn[]>([])
const fab = ref<HTMLButtonElement | null>(null)
const input = ref<HTMLTextAreaElement | null>(null)
const log = ref<HTMLElement | null>(null)
let nextId = 1

// The search page already is this, full width, so a second copy in the
// corner would only cover its results.
const hidden = computed(() => route.path === '/search')

// Asked on a unit page, "is there an exam?" is about that unit.
const unitCode = computed(() => {
  if (!route.path.startsWith('/units/')) return null
  const code = String(route.params.code || '').toUpperCase()
  return /^[A-Z]{3}\d{4}$/.test(code) ? code : null
})

const busy = computed(() => turns.value.some(turn => turn.state === 'loading'))

const starters = computed(() => unitCode.value
  ? [
      $t('unit.suggestExam', { code: unitCode.value }),
      $t('unit.suggestPrereq', { code: unitCode.value }),
      $t('unit.suggestMalaysia', { code: unitCode.value })
    ]
  : [1, 2, 3, 4].map(n => $t(`assistant.starter${n}`)))

function restore() {
  try {
    const saved = JSON.parse(sessionStorage.getItem(STORAGE_KEY) || '[]')
    if (Array.isArray(saved)) {
      turns.value = saved.filter((turn: Turn) => turn && turn.state !== 'loading').slice(-MAX_TURNS)
      nextId = turns.value.reduce((max, turn) => Math.max(max, turn.id), 0) + 1
    }
  } catch {
    turns.value = []
  }
}

function persist() {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(turns.value.filter(turn => turn.state !== 'loading')))
  } catch {
    // Private windows and full storage: the chat still works, it just will not
    // be there after a reload.
  }
}

function scrollDown() {
  nextTick(() => {
    if (log.value) log.value.scrollTop = log.value.scrollHeight
  })
}

/** An answer can be longer than the panel, so it is read from its question down. */
function scrollToLatest() {
  nextTick(() => {
    const questions = log.value?.querySelectorAll<HTMLElement>('.bubble--me')
    const last = questions?.[questions.length - 1]
    if (log.value && last) log.value.scrollTop = last.offsetTop - log.value.offsetTop - 12
  })
}

async function ask(text?: string) {
  const question = (text ?? draft.value).trim().slice(0, 500)
  if (!question || busy.value) return
  draft.value = ''

  turns.value.push({
    id: nextId++, question, state: 'loading', answer: null, tools: [], mamo: [], error: ''
  })
  if (turns.value.length > MAX_TURNS) turns.value.splice(0, turns.value.length - MAX_TURNS)
  // The reactive copy, so the changes below reach the template.
  const turn = turns.value[turns.value.length - 1]!
  scrollDown()

  const body: Record<string, unknown> = { query: question }
  if (unitCode.value) body.unit_code = unitCode.value
  if (year.value) body.year = year.value

  try {
    turn.answer = await apiFetch<any>(`/v1/ask?locale=${locale.value}`, { method: 'POST', body })
    turn.tools = matchTools(question)
    turn.mamo = matchMamo(question, MAMO_POSTS)
    turn.state = 'done'
  } catch (caught) {
    turn.error = apiErrorMessage(caught, $t)
    turn.state = 'error'
  }
  persist()
  scrollToLatest()
}

function retry(turn: Turn) {
  turns.value = turns.value.filter(item => item.id !== turn.id)
  ask(turn.question)
}

function clear() {
  turns.value = []
  persist()
  input.value?.focus()
}

/** The router's own card is worth drawing unless all it says is "nothing found". */
function routerAnswered(turn: Turn) {
  return !!turn.answer && turn.answer.answer_type !== 'community_fallback'
}

function foundNothing(turn: Turn) {
  return !routerAnswered(turn) && !turn.tools.length && !turn.mamo.length &&
    !turn.answer?.related_community?.length
}

function onKeydown(event: KeyboardEvent) {
  // Enter sends, Shift+Enter is a new line. A Chinese or Japanese IME uses
  // Enter to pick a word, and that press must not send half a question.
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
    event.preventDefault()
    ask()
  }
}

const isPhone = () => import.meta.client && window.matchMedia('(max-width: 640px)').matches
let previousBodyOverflow = ''

async function show() {
  open.value = true
  await nextTick()
  input.value?.focus()
  scrollToLatest()
}

function hide(restoreFocus = true) {
  if (!open.value) return
  open.value = false
  if (restoreFocus) nextTick(() => fab.value?.focus())
}

watch(open, (value) => {
  if (!import.meta.client) return
  // Full screen on a phone, so the page underneath must not scroll with it.
  if (value && isPhone()) {
    previousBodyOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
  } else if (!value) {
    document.body.style.overflow = previousBodyOverflow
  }
})

// A link followed from the chat on a phone has to show its page. On a wider
// screen the panel sits beside the page and can stay.
watch(() => route.fullPath, () => {
  if (isPhone()) hide(false)
})

onMounted(restore)
onBeforeUnmount(() => {
  if (import.meta.client) document.body.style.overflow = previousBodyOverflow
})
</script>

<template>
  <div v-if="!hidden" class="assistant site-assistant">
    <button
      v-show="!open"
      ref="fab"
      type="button"
      class="fab"
      :aria-label="$t('assistant.open')"
      aria-controls="site-assistant"
      :aria-expanded="open"
      @click="show"
    >
      <PlanIcon name="chat" :size="22" />
      <span class="fab-label">{{ $t('assistant.fab') }}</span>
    </button>

    <section
      v-if="open"
      id="site-assistant"
      class="panel"
      role="dialog"
      :aria-label="$t('assistant.title')"
      @keydown.esc="hide()"
    >
      <header class="panel-head">
        <span class="mark" aria-hidden="true"><PlanIcon name="chat" :size="18" /></span>
        <div class="head-text">
          <h2>{{ $t('assistant.title') }}</h2>
          <p class="tiny">{{ $t('assistant.subtitle') }}</p>
        </div>
        <button
          v-if="turns.length"
          type="button"
          class="icon-btn"
          :aria-label="$t('assistant.clear')"
          :title="$t('assistant.clear')"
          @click="clear"
        ><PlanIcon name="trash" :size="18" /></button>
        <button
          type="button"
          class="icon-btn"
          :aria-label="$t('assistant.close')"
          :title="$t('assistant.close')"
          @click="hide()"
        ><PlanIcon name="close" :size="18" /></button>
      </header>

      <div ref="log" class="log" aria-live="polite">
        <div class="bubble bubble--bot">
          <p>{{ unitCode ? $t('assistant.greetingUnit', { code: unitCode }) : $t('assistant.greeting') }}</p>
          <p v-if="!turns.length" class="tiny muted starters-label">{{ $t('assistant.starters') }}</p>
          <div v-if="!turns.length" class="chips">
            <button
              v-for="starter in starters"
              :key="starter"
              type="button"
              class="chip-btn"
              @click="ask(starter)"
            >{{ starter }}</button>
          </div>
        </div>

        <template v-for="turn in turns" :key="turn.id">
          <p class="bubble bubble--me">{{ turn.question }}</p>

          <div v-if="turn.state === 'loading'" class="bubble bubble--bot thinking">
            <PlanIcon name="spinner" :size="16" />
            <span>{{ $t('assistant.thinking') }}</span>
          </div>

          <div v-else-if="turn.state === 'error'" class="bubble bubble--bot error" role="alert">
            <p>{{ turn.error }}</p>
            <button type="button" class="btn btn--small" @click="retry(turn)">{{ $t('assistant.retry') }}</button>
          </div>

          <div v-else class="reply">
            <div v-if="turn.tools.length" class="tools">
              <p class="tiny muted section-label">{{ $t('assistant.tools') }}</p>
              <NuxtLink v-for="tool in turn.tools" :key="tool.id" :to="tool.to" class="tool">
                <span class="tool-text">
                  <strong>{{ $t(`assistant.tool.${tool.id}`) }}</strong>
                  <span class="tiny muted">{{ $t(`assistant.tool.${tool.id}.desc`) }}</span>
                </span>
                <PlanIcon name="chevron" :size="16" />
              </NuxtLink>
            </div>

            <AnswerBlocks
              v-if="routerAnswered(turn)"
              class="answer-card"
              :answer="turn.answer"
              :on-ask="ask"
            />

            <div v-if="turn.mamo.length" class="tools">
              <p class="tiny muted section-label">{{ $t('assistant.mamo') }}</p>
              <a
                v-for="post in turn.mamo"
                :key="post.url"
                :href="post.url"
                class="tool"
                rel="noopener external"
                target="_blank"
              >
                <span class="tool-text">
                  <strong>{{ post.title.replace(/^马莫百科\s*[｜|]\s*/, '') }}</strong>
                  <span v-if="post.summary" class="tiny muted">{{ post.summary }}</span>
                </span>
                <PlanIcon name="external" :size="16" />
              </a>
            </div>

            <div v-if="turn.answer?.related_community?.length" class="tools">
              <p class="tiny muted section-label">
                {{ $t('assistant.community') }} <SourceBadge kind="community" />
              </p>
              <NuxtLink
                v-for="post in turn.answer.related_community.slice(0, 3)"
                :key="post.id"
                :to="`/community/post/${post.id}`"
                class="tool"
              >
                <span class="tool-text">
                  <strong>{{ post.title }}</strong>
                  <span class="tiny muted">
                    {{ post.answer_count === 1 ? $t('assistant.answersOne') : $t('assistant.answers', { count: post.answer_count }) }}
                  </span>
                </span>
                <PlanIcon name="chevron" :size="16" />
              </NuxtLink>
            </div>

            <div v-if="foundNothing(turn)" class="bubble bubble--bot">
              <p>{{ $t('assistant.nothing') }}</p>
            </div>

            <div class="way-on">
              <NuxtLink :to="{ path: '/search', query: { q: turn.question } }" class="tiny">
                {{ $t('assistant.allResults') }}
              </NuxtLink>
              <template v-if="!routerAnswered(turn)">
                <NuxtLink to="/community" class="tiny">{{ $t('units.askCommunity') }}</NuxtLink>
                <a :href="ASKMIRA" class="tiny" rel="noopener external" target="_blank">{{ $t('assistant.askMira') }}</a>
              </template>
            </div>
          </div>
        </template>
      </div>

      <form class="composer" @submit.prevent="ask()">
        <label for="site-assistant-input" class="sr-only">{{ $t('assistant.placeholder') }}</label>
        <textarea
          id="site-assistant-input"
          ref="input"
          v-model="draft"
          rows="1"
          maxlength="500"
          :placeholder="$t('assistant.placeholder')"
          enterkeyhint="send"
          @keydown="onKeydown"
        />
        <button
          type="submit"
          class="send"
          :disabled="!draft.trim() || busy"
          :aria-label="$t('assistant.send')"
          :title="$t('assistant.send')"
        ><PlanIcon name="send" :size="18" /></button>
      </form>
    </section>
  </div>
</template>

<style scoped>
/* Above the page and the phone tab bar (z-index 30), below dialogs (50). */
.assistant { position: fixed; right: var(--s5); bottom: var(--s5); z-index: 35; }

.fab {
  display: inline-flex;
  align-items: center;
  gap: var(--s2);
  min-height: 52px;
  padding: 0 var(--s5) 0 var(--s4);
  border: 0;
  border-radius: var(--radius-pill);
  background: var(--ink);
  color: var(--text-inverse);
  font: 600 0.95rem var(--font);
  box-shadow: 0 12px 30px -12px rgba(12, 27, 42, 0.55);
  cursor: pointer;
}
.fab:hover { background: var(--brand-700); }

.panel {
  display: flex;
  flex-direction: column;
  width: min(420px, calc(100vw - 2 * var(--s5)));
  height: min(640px, calc(100dvh - var(--header-h) - 2 * var(--s5)));
  border: 1px solid var(--border);
  border-radius: 18px;
  background: var(--bg);
  box-shadow: 0 24px 60px -20px rgba(12, 27, 42, 0.45);
  overflow: hidden;
}

.panel-head {
  display: flex;
  align-items: center;
  gap: var(--s3);
  padding: var(--s3) var(--s3) var(--s3) var(--s4);
  border-bottom: 1px solid var(--border);
  background: var(--surface);
}
.mark {
  display: grid;
  place-items: center;
  flex: none;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--ink);
  color: var(--text-inverse);
}
.head-text { flex: 1; min-width: 0; }
.head-text h2 { margin: 0; font-size: 1rem; font-family: var(--font); }
.head-text p { margin: 0; color: var(--muted); line-height: 1.35; }
.icon-btn {
  display: grid;
  place-items: center;
  flex: none;
  width: 40px;
  height: 40px;
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
}
.icon-btn:hover { background: var(--surface-2); color: var(--text); }

.log {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--s3);
  padding: var(--s4);
  overflow-y: auto;
  overscroll-behavior: contain;
}

.bubble {
  max-width: 92%;
  margin: 0;
  padding: var(--s3) var(--s4);
  border-radius: 16px;
  font-size: 0.92rem;
  line-height: 1.5;
}
.bubble p { margin: 0; }
.bubble p + p, .bubble p + .chips { margin-top: var(--s2); }
.bubble--bot { align-self: flex-start; background: var(--surface); border: 1px solid var(--border); border-bottom-left-radius: 6px; }
.bubble--me {
  align-self: flex-end;
  background: var(--ink);
  color: var(--text-inverse);
  border-bottom-right-radius: 6px;
  white-space: pre-line;
  overflow-wrap: anywhere;
}
.starters-label { margin-top: var(--s3) !important; }
.thinking { display: inline-flex; align-items: center; gap: var(--s2); color: var(--muted); }
.error { border-color: var(--danger); background: var(--danger-bg); color: var(--danger); }
.error .btn { margin-top: var(--s2); }

.reply { display: grid; gap: var(--s3); }
.section-label { display: flex; align-items: center; gap: var(--s2); margin: 0; }
.tools { display: grid; gap: var(--s2); }
.tool {
  display: flex;
  align-items: center;
  gap: var(--s3);
  padding: var(--s3);
  border: 1px solid var(--border);
  border-radius: 12px;
  background: var(--surface);
  color: var(--text);
  font-size: 0.9rem;
}
.tool:hover { text-decoration: none; border-color: var(--border-strong); background: var(--surface-2); }
.tool-text { display: grid; gap: 2px; flex: 1; min-width: 0; line-height: 1.35; }
.tool-text strong { font-weight: 600; overflow-wrap: anywhere; }
.tool :deep(.icon) { flex: none; color: var(--muted); }

/* The router's answer card, sized for a narrow panel. */
.reply .answer-card { padding: var(--s4); border-radius: 12px; box-shadow: none; }
.answer-card :deep(h2) { font-size: 1rem; font-family: var(--font); }
.answer-card :deep(.verdict), .answer-card :deep(.caveat) { font-size: 0.88rem; }
.answer-card :deep(table) { font-size: 0.82rem; }

.chips { display: flex; flex-wrap: wrap; gap: var(--s2); }
.chip-btn {
  min-height: 36px;
  padding: 6px 12px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-pill);
  background: var(--surface);
  color: inherit;
  font: inherit;
  font-size: 0.84rem;
  text-align: left;
  cursor: pointer;
}
.chip-btn:hover { background: var(--surface-2); }

.way-on { display: flex; flex-wrap: wrap; gap: var(--s2) var(--s4); padding: 0 var(--s1); }

.composer {
  display: flex;
  align-items: flex-end;
  gap: var(--s2);
  padding: var(--s3);
  border-top: 1px solid var(--border);
  background: var(--surface);
}
.composer textarea {
  flex: 1;
  min-height: 44px;
  max-height: 120px;
  padding: 11px var(--s4);
  border: 1px solid var(--border-strong);
  border-radius: 22px;
  background: var(--bg);
  color: var(--text);
  font: inherit;
  font-size: 0.95rem;
  line-height: 1.4;
  resize: none;
  field-sizing: content;
}
.composer textarea:focus { outline: none; border-color: var(--blue); box-shadow: 0 0 0 3px var(--blue-50); }
.send {
  display: grid;
  place-items: center;
  flex: none;
  width: 44px;
  height: 44px;
  border: 0;
  border-radius: 50%;
  background: var(--ink);
  color: var(--text-inverse);
  cursor: pointer;
}
.send:disabled { background: var(--border-strong); cursor: default; }

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}

/* The tab bar is at the bottom below 1180px: 56px plus the safe area. */
@media (max-width: 1180px) {
  .assistant { right: var(--s4); bottom: calc(56px + var(--s3) + env(safe-area-inset-bottom)); }
  .fab { min-height: 48px; }
  .panel { height: min(640px, calc(100dvh - var(--header-h) - 56px - 2 * var(--s5))); }
}

/* A phone gets the whole screen, or the answer has no room. */
@media (max-width: 640px) {
  .fab { width: 48px; padding: 0; justify-content: center; }
  .fab-label { display: none; }
  .assistant:has(.panel) { inset: 0; }
  .panel {
    width: 100%;
    height: 100dvh;
    border: 0;
    border-radius: 0;
    padding-bottom: env(safe-area-inset-bottom);
  }
}
</style>

<style>
/* The calculator's summary bar (pages/marks.vue) rides on the tab bar below
   1100px while it is showing, so the button moves up out of its way. Not
   scoped: it reads the page's markup, not this component's. */
@media (max-width: 1100px) {
  body:has(.dock) .site-assistant:not(:has(.panel)) { bottom: calc(56px + 76px + env(safe-area-inset-bottom)); }
}
</style>
