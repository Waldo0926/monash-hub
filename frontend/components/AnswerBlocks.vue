<script setup lang="ts">
/**
 * Renders one zero-AI answer.
 *
 * The API sends typed blocks rather than prose, and this component draws them.
 * Keeping the shapes explicit is what stops a "summary" from quietly becoming
 * something the Handbook never said.
 */
defineProps<{ answer: any }>()
const { $t } = useNuxtApp()
</script>

<template>
  <div class="answer card">
    <div class="head">
      <h2>{{ answer.title }}</h2>
      <SourceBadge v-if="answer.sources?.length" :kind="answer.sources[0].kind" />
    </div>

    <template v-for="(block, index) in answer.blocks || []" :key="index">
      <p v-if="block.type === 'verdict'" class="verdict">{{ block.text }}</p>

      <div v-else-if="block.type === 'text'" class="block">
        <h3 v-if="block.title">{{ block.title }}</h3>
        <p class="pre">{{ block.text }}</p>
      </div>

      <div v-else-if="block.type === 'table'" class="block">
        <div class="scroll-x">
          <table>
            <thead>
              <tr><th v-for="column in block.columns" :key="column">{{ column }}</th></tr>
            </thead>
            <tbody>
              <tr v-for="(row, rowIndex) in block.rows" :key="rowIndex">
                <td v-for="key in block.keys" :key="key">{{ row[key] ?? '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-if="block.caption" class="tiny muted caption">{{ block.caption }}</p>
      </div>

      <div v-else-if="block.type === 'requisite_group'" class="block">
        <h3 class="req-type">{{ block.requisite_type }}</h3>
        <div v-for="(group, groupIndex) in block.groups" :key="groupIndex" class="req-group">
          <p v-if="group.description" class="small">{{ group.description }}</p>
          <ul class="req-items">
            <li v-for="item in group.items" :key="item.code">
              <NuxtLink :to="`/units/${item.code}`" class="mono">{{ item.code }}</NuxtLink>
              <span class="muted"> — {{ item.name }}</span>
            </li>
          </ul>
          <p v-if="group.connector && group.items.length > 1" class="tiny muted">
            Any one of these satisfies the rule ({{ group.connector }}).
          </p>
        </div>
      </div>

      <ul v-else-if="block.type === 'list'" class="block outcomes">
        <li v-for="item in block.items" :key="item.code">
          <strong class="mono">{{ item.code }}</strong> {{ item.text }}
        </li>
      </ul>

      <NuxtLink
        v-else-if="block.type === 'link'"
        :to="block.to"
        class="btn btn--small block-link"
      >{{ $t('answer.openUnit', { code: block.label?.replace(/^Open /, '') }) }}</NuxtLink>

      <ul v-else-if="block.type === 'page_list'" class="block pages">
        <li v-for="page in block.items" :key="page.slug">
          <NuxtLink :to="`/guides/${page.slug}`">{{ page.title }}</NuxtLink>
          <p class="tiny muted">{{ page.summary }}</p>
          <LastChecked :value="page.last_checked" />
        </li>
      </ul>
    </template>

    <p v-if="answer.caveat" class="caveat small">{{ answer.caveat }}</p>

    <div v-if="answer.sources?.length" class="sources tiny">
      <span v-for="source in answer.sources" :key="source.url">
        Source:
        <a :href="source.url" rel="noopener external" target="_blank">{{ source.label }} ↗</a>
        <LastChecked :value="source.last_checked" />
      </span>
    </div>
  </div>
</template>

<style scoped>
.block-link { display: inline-flex; margin-top: var(--s2); }

.answer { padding: var(--s5); }
.head { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--s3); }
.head h2 { margin-bottom: var(--s4); }
.verdict {
  padding: var(--s3) var(--s4);
  border-left: 3px solid var(--blue);
  background: var(--blue-50);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}
.block { margin-bottom: var(--s4); }
.pre { white-space: pre-line; margin: 0; }
.caption { margin: var(--s2) 0 0; }
.req-type { text-transform: capitalize; }
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
</style>
