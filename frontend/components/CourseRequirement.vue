<script setup lang="ts">
/**
 * One requirement group, and everything under it.
 *
 * Recursive because the data is: a group holds units, or holds groups that
 * hold units, and C2001 nests two deep while other degrees nest deeper. The
 * alternative - rendering two fixed levels - would silently drop the third.
 *
 * A group whose units this campus does not teach carries the count on its own
 * header, so a reader collapsing the outline still sees where the problem is
 * rather than having to open every Part to find it.
 */
const props = defineProps<{
  node: any
  units: Record<string, any>
  campus: string
  depth: number
  open?: boolean
}>()
const emit = defineEmits<{ toggle: [id: number] }>()
const { $t } = useNuxtApp()

const expanded = ref(props.open ?? props.depth === 0)
function toggle() {
  expanded.value = !expanded.value
  emit('toggle', props.node.id)
}

/**
 * How many units under this group the campus does not teach.
 *
 * Computed here rather than passed in, so that it reaches every level. C2001's
 * Part D is "complete one of the following options" and two of the five are
 * entirely untaught at Malaysia - a count on Part D alone tells the reader
 * there is a problem without telling them which option to avoid.
 */
const elsewhere = computed(() => {
  if (!props.campus) return 0
  const codes = unitCodes(props.node)
  return codes.filter((code) => {
    const f = props.units?.[code]
    return f?.in_year && !f.offered_at_campus
  }).length
})

function unitCodes(node: any): string[] {
  const here = (node.items || []).filter((i: any) => i.type === 'unit').map((i: any) => i.code)
  return [...here, ...(node.containers || []).flatMap(unitCodes)]
}

function fact(code: string) {
  return props.units?.[code] || { in_year: false, offered_at_campus: false, periods: [] }
}
function away(code: string) {
  const f = fact(code)
  return Boolean(props.campus) && f.in_year && !f.offered_at_campus
}
</script>

<template>
  <div class="group" :class="`group--d${depth}`">
    <button class="header" type="button" :aria-expanded="expanded" @click="toggle">
      <span class="caret" :class="{ 'caret--open': expanded }">▸</span>
      <span class="title">{{ node.title || $t('courses.unnamedGroup') }}</span>
      <span v-if="node.credit_points" class="points">{{ node.credit_points }} cp</span>
      <span v-if="elsewhere" class="flag">{{ $t('courses.groupNotHere', { n: elsewhere }) }}</span>
    </button>

    <div v-if="expanded" class="body">
      <p v-if="node.description" class="note">{{ node.description }}</p>

      <ul v-if="node.items?.length" class="items">
        <li v-for="item in node.items" :key="item.code" :class="{ away: away(item.code) }">
          <NuxtLink v-if="item.type === 'unit'" class="item" :to="`/units/${item.code}`">
            <span class="code">{{ item.code }}</span>
            <span class="name">{{ fact(item.code).title || item.name }}</span>
            <span class="meta">
              <span v-if="fact(item.code).periods?.length" class="periods">
                {{ fact(item.code).periods.join('·') }}
              </span>
              <span v-if="!fact(item.code).in_year" class="tag tag--gone">{{ $t('courses.notThisYear') }}</span>
              <span v-else-if="away(item.code)" class="tag tag--away">✕ {{ campus }}</span>
            </span>
          </NuxtLink>
          <NuxtLink v-else class="item item--aos" :to="`/courses/aos/${item.code}`">
            <span class="code">{{ item.code }}</span>
            <span class="name">{{ item.name }}</span>
            <span class="meta">
              <span class="tag">{{ item.type }}</span>
              <span v-if="item.credit_points">{{ item.credit_points }} cp</span>
            </span>
          </NuxtLink>
          <NuxtLink
            v-if="item.type === 'unit' && fact(item.code).in_year"
            class="tree"
            :to="`/tree?unit=${item.code}&campus=${campus}`"
            :title="$t('courses.openTree')"
          >⤳</NuxtLink>
        </li>
      </ul>

      <CourseRequirement
        v-for="child in node.containers"
        :key="child.id"
        :node="child"
        :units="units"
        :campus="campus"
        :depth="depth + 1"
      />

      <p v-if="node.footnote" class="note note--foot">{{ node.footnote }}</p>
    </div>
  </div>
</template>

<style scoped>
.group {
  border: 1px solid var(--border); border-radius: var(--radius);
  background: var(--surface); margin-bottom: var(--s2);
}
.group--d1, .group--d2, .group--d3 { background: var(--surface-2); }

.header {
  display: flex; align-items: baseline; gap: var(--s2); width: 100%;
  padding: var(--s3) var(--s4); background: none; border: 0; cursor: pointer;
  font: inherit; text-align: left; color: var(--text);
}
.caret { color: var(--muted); transition: transform 0.12s ease; display: inline-block; }
.caret--open { transform: rotate(90deg); }
.title { font-weight: 600; flex: 1; }
.points {
  background: var(--badge-handbook-bg); color: var(--badge-handbook);
  border-radius: var(--radius-pill); padding: 2px var(--s2);
  font-size: 0.78rem; white-space: nowrap;
}
.flag {
  background: var(--warning-bg); color: var(--warning);
  border-radius: var(--radius-pill); padding: 2px var(--s2);
  font-size: 0.75rem; white-space: nowrap;
}

.body { padding: 0 var(--s4) var(--s3); }
.note { margin: 0 0 var(--s3); color: var(--muted); font-size: 0.85rem; white-space: pre-line; }
.note--foot { margin-top: var(--s3); margin-bottom: 0; font-size: 0.8rem; }

.items { list-style: none; margin: 0 0 var(--s2); padding: 0; display: grid; gap: 2px; }
.items li { display: flex; align-items: center; gap: var(--s1); }
.item {
  display: grid; grid-template-columns: 78px minmax(0, 1fr) auto; gap: var(--s3);
  align-items: baseline; flex: 1; padding: var(--s2) var(--s3);
  border-radius: var(--radius-sm); color: inherit; text-decoration: none;
}
.item:hover { background: var(--blue-50); }
.away .item { opacity: 0.72; }
.code { font: 600 0.8rem var(--font-mono); color: var(--navy); }
.name { font-size: 0.9rem; }
.meta { display: flex; gap: var(--s2); align-items: center; font-size: 0.75rem; color: var(--muted); }
.tag { background: var(--surface-2); border-radius: var(--radius-pill); padding: 1px var(--s2); }
.item--aos .tag { background: var(--badge-community-bg); color: var(--badge-community); }
.tag--away { background: var(--warning-bg); color: var(--warning); }
.tag--gone { background: var(--danger-bg); color: var(--danger); }
.tree {
  color: var(--muted); text-decoration: none; padding: 0 var(--s2);
  font-size: 1rem; line-height: 1;
}
.tree:hover { color: var(--blue); }

@media (max-width: 700px) {
  .item { grid-template-columns: minmax(0, 1fr); gap: 2px; }
}
</style>
