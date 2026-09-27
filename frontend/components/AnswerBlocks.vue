<script setup lang="ts">
/**
 * Renders one zero-AI answer.
 *
 * The API sends typed blocks rather than prose, and this component draws them.
 * Keeping the shapes explicit is what stops a "summary" from quietly becoming
 * something the Handbook never said.
 *
 * Language: every sentence the router writes arrives with a ``key`` and
 * ``params`` as well as its English ``text``, and is drawn in the reader's
 * language from ``i18n``. The data inside - Handbook values, official text -
 * is translated only through ``$term``'s closed dictionary, or not at all.
 */
import type { TermKind } from '~/i18n/handbook-terms'

const props = withDefaults(defineProps<{
  answer: any
  /** Draw the follow-up question chips. */
  suggest?: boolean
  /** Ask a follow-up in place; without it a chip opens the search page. */
  onAsk?: (question: string) => void
}>(), { suggest: true, onAsk: undefined })
const { $t, $term, $assessmentName } = useNuxtApp()

/** One of our sentences in the reader's language, English if the key is unknown. */
function say(key: string | null | undefined, text: string | null | undefined, params?: any, terms?: Record<string, TermKind>) {
  if (!key) return text || ''
  const resolved: Record<string, string | number> = { ...(params || {}) }
  for (const [name, kind] of Object.entries(terms || {})) {
    if (resolved[name] != null) resolved[name] = $term(kind, String(resolved[name])) ?? resolved[name]!
  }
  const translated = $t(key, resolved)
  // translate() hands back the key itself when no locale knows it.
  return translated === key ? text || '' : translated
}

function cell(block: any, row: any, key: string) {
  const value = row[key]
  if (value == null || value === '') return '—'
  const kind = block.terms?.[key]
  if (kind === 'assessmentName') return $assessmentName(String(value)) ?? value
  if (kind) return $term(kind as TermKind, String(value)) ?? value
  return value
}

const title = computed(() =>
  say(props.answer.title_key, props.answer.title, props.answer.title_params)
)

function ask(question: string) {
  if (props.onAsk) props.onAsk(question)
  else navigateTo({ path: '/search', query: { q: question } })
}
</script>

<template>
  <div class="answer card">
    <div class="head">
      <h2>{{ title }}</h2>
      <div class="head-badges">
        <CampusNotice v-if="answer.applies_to" :applies-to="answer.applies_to" compact />
        <SourceBadge v-if="answer.sources?.length" :kind="answer.sources[0].kind" />
      </div>
    </div>

    <TranslationNotice
      v-if="answer.translation"
      :translation="answer.translation"
      :source-url="answer.sources?.[0]?.url"
      class="block"
    />

    <template v-for="(block, index) in answer.blocks || []" :key="index">
      <p v-if="block.type === 'verdict'" class="verdict">
        {{ say(block.key, block.text, block.params, block.terms) }}
      </p>

      <div v-else-if="block.type === 'text'" class="block">
        <h3 v-if="block.title">{{ say(block.title_key, block.title) }}</h3>
        <p class="pre">{{ block.text }}</p>
      </div>

      <div v-else-if="block.type === 'table'" class="block">
        <div class="scroll-x">
          <table>
            <thead>
              <tr>
                <th v-for="(column, columnIndex) in block.columns" :key="column" scope="col">
                  {{ say(block.column_keys?.[columnIndex], column) }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, rowIndex) in block.rows" :key="rowIndex">
                <td v-for="key in block.keys" :key="key">{{ cell(block, row, key) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-if="block.caption" class="tiny muted caption">
          {{ say(block.caption_key, block.caption, block.caption_params) }}
        </p>
      </div>

      <div v-else-if="block.type === 'requisite_group'" class="block">
        <h3 class="req-type">{{ $term('requisiteType', block.requisite_type) }}</h3>
        <div v-for="(group, groupIndex) in block.groups" :key="groupIndex" class="req-group">
          <p v-if="group.description" class="small">{{ group.description }}</p>
          <ul class="req-items">
            <li v-for="item in group.items" :key="item.code">
              <NuxtLink :to="`/units/${item.code}`" class="mono">{{ item.code }}</NuxtLink>
              <span v-if="item.name" class="muted"> — {{ item.name }}</span>
            </li>
          </ul>
          <p v-if="group.connector && group.items.length > 1" class="tiny muted">
            {{ $t(group.connector === 'AND' ? 'answer.connector.and' : 'answer.connector.or', { connector: $term('connector', group.connector) || group.connector }) }}
          </p>
        </div>
      </div>

      <div v-else-if="block.type === 'list'" class="block">
        <h3 v-if="block.title">{{ say(block.title_key, block.title) }}</h3>
        <ul class="outcomes">
          <li v-for="item in block.items" :key="item.code">
            <strong class="mono">{{ item.code }}</strong> {{ item.text }}
          </li>
        </ul>
      </div>

      <NuxtLink
        v-else-if="block.type === 'link'"
        :to="block.to"
        class="btn btn--small block-link"
      >{{ $t('answer.openUnit', { code: block.label }) }}</NuxtLink>

      <ul v-else-if="block.type === 'page_list'" class="block pages">
        <li v-for="page in block.items" :key="page.slug">
          <NuxtLink :to="`/guides/${page.slug}`">{{ page.title }}</NuxtLink>
          <CampusNotice v-if="page.applies_to" :applies-to="page.applies_to" compact />
          <p v-if="page.summary" class="tiny muted">{{ page.summary }}</p>
          <LastChecked :value="page.last_checked" />
        </li>
      </ul>
    </template>

    <p v-if="answer.caveat" class="caveat small">{{ say(answer.caveat_key, answer.caveat) }}</p>

    <div v-if="answer.sources?.length" class="sources tiny">
      <span v-for="source in answer.sources" :key="source.url">
        {{ $t('answer.source') }}
        <a :href="source.url" rel="noopener external" target="_blank">{{ source.label }} ↗</a>
        <LastChecked :value="source.last_checked" />
      </span>
    </div>

    <div v-if="suggest && answer.suggestions?.length" class="related">
      <p class="tiny muted">
        {{ answer.answer_type?.startsWith('handbook') || answer.answer_type === 'subjective'
          ? $t('answer.alsoAsk') : $t('answer.related') }}
      </p>
      <div class="chips">
        <button
          v-for="suggestion in answer.suggestions"
          :key="suggestion"
          type="button"
          class="chip-btn"
          @click="ask(suggestion)"
        >{{ suggestion }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.block-link { display: inline-flex; margin-top: var(--s2); }

.answer { padding: var(--s5); }
.head { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--s3); }
.head h2 { margin-bottom: var(--s4); overflow-wrap: anywhere; }
.head-badges { display: flex; flex-wrap: wrap; gap: var(--s2); justify-content: flex-end; }
.verdict {
  padding: var(--s3) var(--s4);
  border-left: 3px solid var(--blue);
  background: var(--blue-50);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}
.block { margin-bottom: var(--s4); }
.pre { white-space: pre-line; margin: 0; }
.caption { margin: var(--s2) 0 0; }
.req-group + .req-group { margin-top: var(--s4); }
.req-items { margin: 0; padding-left: var(--s5); }
.outcomes { padding-left: var(--s5); }
.outcomes li + li { margin-top: var(--s2); }
.pages { list-style: none; padding: 0; }
.pages li + li { margin-top: var(--s4); }
.pages p { margin: var(--s1) 0; }
.caveat {
  padding: var(--s3) var(--s4);
  border-radius: var(--radius-sm);
  background: var(--warning-bg);
  color: var(--warning);
}
.sources { display: grid; gap: var(--s1); color: var(--muted); }
.related { margin-top: var(--s4); }
.related p { margin: 0 0 var(--s2); }
.chips { display: flex; flex-wrap: wrap; gap: var(--s2); }
.chip-btn {
  min-height: 36px;
  padding: 6px 12px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-pill);
  background: var(--surface);
  color: inherit;
  font: inherit;
  font-size: 0.82rem;
  text-align: left;
  cursor: pointer;
}
.chip-btn:hover { background: var(--surface-2); }
</style>
