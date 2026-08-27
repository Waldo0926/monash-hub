<script setup lang="ts">
/**
 * Renders the structured blocks the crawler extracted from an official page.
 *
 * The blocks come from `backend/app/knowledge/cleaner.py` and are plain data —
 * headings, paragraphs, lists and tables, with inline spans carrying emphasis
 * and links. Nothing here is injected as HTML: every string arrives as text and
 * is bound as text, so a change on monash.edu can never put markup into this
 * page.
 *
 * `fallback` is the old flat `clean_text`. A page crawled before the structured
 * extractor existed has no blocks, and showing its text is better than showing
 * an empty card while the next crawl catches up.
 */
interface Span { text: string; bold?: boolean; url?: string }
interface Block {
  type: 'heading' | 'paragraph' | 'list' | 'table'
  level?: number
  text?: string
  id?: string
  variant?: string
  spans?: Span[]
  ordered?: boolean
  items?: Span[][]
  caption?: string
  columns?: string[]
  rows?: string[][]
  foot?: string[][]
}

const props = defineProps<{ blocks?: Block[] | null; fallback?: string | null }>()

const blocks = computed(() => props.blocks || [])

/** External links get the same treatment everywhere: new tab, no opener. */
function isExternal(url?: string): boolean {
  return !!url && /^https?:\/\//i.test(url)
}

/**
 * Whether a cell holds a sentence rather than a date or a code.
 *
 * Long enough that keeping it on one line makes the table wider than any phone,
 * and wide enough that wrapping it costs nothing. Measured in characters, so it
 * works the same for Chinese, which has no spaces to wrap at either.
 */
function wraps(cell: string): boolean {
  return (cell || '').trim().length > 28
}

/** A table whose header row is entirely empty is really a layout table. */
function hasHeader(block: Block): boolean {
  return (block.columns || []).some(c => c.trim() !== '')
}
</script>

<template>
  <div v-if="blocks.length" class="blocks">
    <template v-for="(block, i) in blocks" :key="i">
      <component
        :is="`h${block.level || 2}`"
        v-if="block.type === 'heading'"
        :id="block.id"
        :class="['block-heading', { 'block-heading--tab': block.variant === 'tab' }]"
      >
        {{ block.text }}
      </component>

      <p v-else-if="block.type === 'paragraph'" class="block-p">
        <template v-for="(span, j) in block.spans || []" :key="j">
          <a
            v-if="span.url"
            :href="span.url"
            :target="isExternal(span.url) ? '_blank' : undefined"
            :rel="isExternal(span.url) ? 'noopener external' : undefined"
          >{{ span.text }}</a>
          <strong v-else-if="span.bold">{{ span.text }}</strong>
          <template v-else>{{ span.text }}</template>
        </template>
      </p>

      <component
        :is="block.ordered ? 'ol' : 'ul'"
        v-else-if="block.type === 'list'"
        class="block-list"
      >
        <li v-for="(item, j) in block.items || []" :key="j">
          <template v-for="(span, k) in item" :key="k">
            <a
              v-if="span.url"
              :href="span.url"
              :target="isExternal(span.url) ? '_blank' : undefined"
              :rel="isExternal(span.url) ? 'noopener external' : undefined"
            >{{ span.text }}</a>
            <strong v-else-if="span.bold">{{ span.text }}</strong>
            <template v-else>{{ span.text }}</template>
          </template>
        </li>
      </component>

      <figure v-else-if="block.type === 'table'" class="block-table">
        <figcaption v-if="block.caption" class="tiny muted">{{ block.caption }}</figcaption>
        <!-- A six-column table has to be able to scroll sideways inside its own
             box; the page itself must never scroll horizontally. -->
        <div class="scroll-x">
          <table>
            <thead v-if="hasHeader(block)">
              <tr>
                <th
                  v-for="(column, j) in block.columns || []"
                  :key="j"
                  scope="col"
                  :class="{ wraps: wraps(column) }"
                >
                  {{ column }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, j) in block.rows || []" :key="j">
                <td v-for="(cell, k) in row" :key="k" :class="{ wraps: wraps(cell) }">{{ cell }}</td>
              </tr>
            </tbody>
            <tfoot v-if="block.foot?.length">
              <tr v-for="(row, j) in block.foot" :key="j">
                <td v-for="(cell, k) in row" :key="k" :class="{ wraps: wraps(cell) }">{{ cell }}</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </figure>
    </template>
  </div>

  <p v-else-if="fallback" class="fallback">{{ fallback }}</p>
</template>

<style scoped>
/* Prose is held to a readable measure; a table is not prose and gets the whole
   card, because squeezing six columns into 68ch only moves the reading problem
   into a scrollbar. */
.block-heading,
.block-p,
.block-list { max-width: 68ch; }

.block-heading {
  margin: var(--s6) 0 var(--s3);
  scroll-margin-top: calc(var(--header-h) + var(--s4));
}
.blocks > .block-heading:first-child { margin-top: 0; }

/* A tab label is a different kind of heading: it does not describe the section
   below it so much as say which campus or scheme the section applies to, and
   reading it as an ordinary heading is how the Malaysian grading scale ends up
   looking like a continuation of the Australian one. */
.block-heading--tab {
  display: inline-block;
  margin-top: var(--s7);
  padding: var(--s1) var(--s3);
  border-radius: var(--radius-pill);
  background: var(--badge-official-bg);
  color: var(--badge-official);
  font-size: 0.9rem;
  letter-spacing: 0.02em;
}

.block-p { margin: 0 0 var(--s4); white-space: pre-line; }

.block-list { margin: 0 0 var(--s4); padding-left: var(--s5); }
.block-list li + li { margin-top: var(--s2); }

.block-table { margin: 0 0 var(--s5); }
.block-table figcaption { margin-bottom: var(--s2); }
.block-table .scroll-x {
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  /* The property the comment above the markup has always promised. Without it
     a single cell of Chinese prose - 2,547px of it on the Malaysia student pass
     page - widened the table, the card and the page, and every paragraph on a
     phone ran off the right edge. */
  overflow-x: auto;
}
.block-table table { min-width: 100%; }
/* Dates and codes must not be broken across lines, so cells do not wrap by
   default. A cell holding a sentence is a different thing and says so - see
   `wraps` in the script: nowrap there is 2,000px nobody can read. */
.block-table th,
.block-table td { white-space: nowrap; }
.block-table td.wraps,
.block-table th.wraps { white-space: normal; min-width: 22ch; max-width: 46ch; }
/* The first column is usually the label and is the one that may be long. */
.block-table td:first-child,
.block-table th:first-child { white-space: normal; min-width: 12ch; }
.block-table tfoot td {
  border-top: 2px solid var(--border-strong);
  border-bottom: 0;
  font-weight: 600;
}

.fallback { white-space: pre-line; }
</style>
