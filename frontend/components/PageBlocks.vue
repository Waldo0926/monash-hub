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
  head?: string[][]
  /** [part, row, column, rowspan, colspan]; part is head, body or foot. */
  merged?: [string, number, number, number, number][]
  links?: Span[][]
}

type Part = 'head' | 'body' | 'foot'
interface Cell { text: string; rowspan?: number; colspan?: number }

/**
 * One section of a table as the cells to draw. The rows arrive as a regular
 * grid with blanks where a merged cell reaches; those blanks are left out
 * and the merged cell carries its rowspan and colspan, so the table looks as
 * it does on monash.edu instead of a grid of half-empty rows.
 */
function cellsOf(block: Block, part: Part, rows: string[][]): Cell[][] {
  const starts = new Map<string, [number, number]>()
  const covered = new Set<string>()
  for (const [where, row, column, rowspan, colspan] of block.merged || []) {
    if (where !== part) continue
    starts.set(`${row}:${column}`, [rowspan, colspan])
    for (let r = row; r < row + rowspan; r++) {
      for (let c = column; c < column + colspan; c++) {
        if (r !== row || c !== column) covered.add(`${r}:${c}`)
      }
    }
  }
  return rows.map((row, r) => row.flatMap((text, c) => {
    if (covered.has(`${r}:${c}`)) return []
    const span = starts.get(`${r}:${c}`)
    return [span ? { text, rowspan: span[0], colspan: span[1] } : { text }]
  }))
}

function headRows(block: Block): Cell[][] {
  const rows = hasHeader(block) ? [block.columns || [], ...(block.head || [])] : []
  return cellsOf(block, 'head', rows)
}

const props = defineProps<{ blocks?: Block[] | null; fallback?: string | null }>()

const blocks = computed(() => props.blocks || [])

/** External links get the same treatment everywhere: new tab, no opener. */
function isExternal(url?: string): boolean {
  return !!url && /^https?:\/\//i.test(url)
}

/**
 * Drop the blank lines a source page uses as spacing.
 *
 * Paragraphs render with `white-space: pre-line`, because a heading and the
 * sentence under it arrive in one string and the break between them is real.
 * The runs of empty lines around them are not: monash.edu writes
 * "Indigenous PhD scholarships now open\n \n\n\n \n Monash University is
 * proud ..." and pre-line turns each of those into a gap, so the page reads as
 * a column of white with sentences adrift in it.
 *
 * One break survives; a run of them becomes one. The strings themselves are
 * left alone - they are the keys every hand-written translation is matched on.
 */
function spaced(text: string): string {
  return (text || '').replace(/[ \t]*\n(?:[ \t]*\n)+/g, '\n')
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

/**
 * Mark the tables that are wider than their box.
 *
 * On a phone the fee table's last two columns - the fees - start off the right
 * edge, and nothing said there was more to see: the table looked like a list
 * of courses. A wide table gets a shadow at the edge it continues past and a
 * line under it saying to swipe. Measured, not guessed from the column count,
 * because a three-column table of dates fits and a two-column one of
 * sentences may not.
 */
const root = ref<HTMLElement | null>(null)
let watcher: ResizeObserver | null = null

function measure() {
  for (const box of root.value?.querySelectorAll<HTMLElement>('.scroll-x') || []) {
    box.toggleAttribute('data-wide', box.scrollWidth > box.clientWidth + 1)
  }
}

onMounted(() => {
  measure()
  if (typeof ResizeObserver === 'undefined' || !root.value) return
  watcher = new ResizeObserver(measure)
  watcher.observe(root.value)
})
onBeforeUnmount(() => watcher?.disconnect())
watch(blocks, () => nextTick(measure))
</script>

<template>
  <div v-if="blocks.length" ref="root" class="blocks">
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
          >{{ spaced(span.text) }}</a>
          <strong v-else-if="span.bold">{{ spaced(span.text) }}</strong>
          <template v-else>{{ spaced(span.text) }}</template>
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
            >{{ spaced(span.text) }}</a>
            <strong v-else-if="span.bold">{{ spaced(span.text) }}</strong>
            <template v-else>{{ spaced(span.text) }}</template>
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
              <tr v-for="(row, j) in headRows(block)" :key="j">
                <th
                  v-for="(cell, k) in row"
                  :key="k"
                  :scope="cell.colspan && cell.colspan > 1 ? 'colgroup' : 'col'"
                  :rowspan="cell.rowspan"
                  :colspan="cell.colspan"
                  :class="{ wraps: wraps(cell.text) }"
                >
                  {{ cell.text }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, j) in cellsOf(block, 'body', block.rows || [])" :key="j">
                <td
                  v-for="(cell, k) in row"
                  :key="k"
                  :rowspan="cell.rowspan"
                  :colspan="cell.colspan"
                  :class="{ wraps: wraps(cell.text), lines: cell.text.includes('\n') }"
                >{{ cell.text }}</td>
              </tr>
            </tbody>
            <tfoot v-if="block.foot?.length">
              <tr v-for="(row, j) in cellsOf(block, 'foot', block.foot)" :key="j">
                <td
                  v-for="(cell, k) in row"
                  :key="k"
                  :rowspan="cell.rowspan"
                  :colspan="cell.colspan"
                  :class="{ wraps: wraps(cell.text), lines: cell.text.includes('\n') }"
                >{{ cell.text }}</td>
              </tr>
            </tfoot>
          </table>
        </div>
        <p class="scroll-hint tiny muted" aria-hidden="true">{{ $t('guides.tableScroll') }}</p>
        <ul v-if="block.links?.length" class="block-list table-links">
          <li v-for="(link, j) in block.links" :key="j">
            <template v-for="(span, k) in link" :key="k">
              <a v-if="span.url" :href="span.url" target="_blank" rel="noopener external">{{ spaced(span.text) }}</a>
              <template v-else>{{ spaced(span.text) }}</template>
            </template>
          </li>
        </ul>
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
.block-list { max-width: var(--measure); }

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
.table-links { margin-top: var(--s3); }
.block-table .scroll-x {
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  /* The property the comment above the markup has always promised. Without it
     a single cell of Chinese prose - 2,547px of it on the Malaysia student pass
     page - widened the table, the card and the page, and every paragraph on a
     phone ran off the right edge. */
  overflow-x: auto;
  /* Shadows that say the table goes on: the covers scroll with the table and
     hide a shadow once its edge is reached. */
  background:
    linear-gradient(to right, var(--surface) 40%, transparent) left / 32px 100% no-repeat local,
    linear-gradient(to left, var(--surface) 40%, transparent) right / 32px 100% no-repeat local,
    radial-gradient(farthest-side at 0 50%, rgb(15 23 42 / 0.16), transparent) left / 12px 100% no-repeat scroll,
    radial-gradient(farthest-side at 100% 50%, rgb(15 23 42 / 0.16), transparent) right / 12px 100% no-repeat scroll,
    var(--surface);
}
.block-table table { min-width: 100%; }
.scroll-hint { display: none; margin: var(--s2) 0 0; }
.scroll-x[data-wide] + .scroll-hint { display: block; }
/* Dates and codes must not be broken across lines, so cells do not wrap by
   default. A cell holding a sentence is a different thing and says so - see
   `wraps` in the script: nowrap there is 2,000px nobody can read. */
.block-table th,
.block-table td { white-space: nowrap; }
.block-table td.wraps,
.block-table th.wraps { white-space: normal; min-width: 22ch; max-width: 46ch; }
/* A cell with its own line breaks (two paragraphs, a short list) keeps them. */
.block-table tr td.lines { white-space: pre; }
.block-table tr td.wraps.lines,
.block-table tr td.lines:first-child { white-space: pre-line; }
/* A merged cell sits at the top of the rows it spans, as it does on monash.edu. */
.block-table td[rowspan],
.block-table th[rowspan] { vertical-align: top; }
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
