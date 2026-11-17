<script setup lang="ts">
import type { CommencementRules } from '~/utils/commencementRules'
defineProps<{ evidence: CommencementRules; showStructure?: boolean }>()
const { locale } = useLocale()
const zh = computed(() => locale.value === 'zh')
</script>

<template>
  <section class="commencement-context card" :data-state="evidence.status">
    <h2>{{ zh ? '入学年份的学位资料' : 'Commencement-year degree information' }}</h2>
    <p class="commencement-identity">{{ evidence.code }} · {{ evidence.year }}</p>
    <template v-if="evidence.status === 'available' && evidence.snapshot">
      <p v-if="showStructure && evidence.snapshot.title">{{ evidence.snapshot.title }}</p>
      <template v-if="showStructure">
        <ul v-if="evidence.snapshot.containers?.length">
          <li v-for="(part, i) in evidence.snapshot.containers" :key="i">
            {{ part.title || (zh ? '未命名结构项' : 'Untitled requirement') }}
            <template v-if="part.credit_points != null"> · {{ part.credit_points }} cp</template>
          </li>
        </ul>
        <p v-else>{{ zh ? '未提取到学位结构，不能据此认定没有学位要求。' : 'Degree structure was not extracted; this does not establish an absence of requirements.' }}</p>
      </template>
      <p><a :href="evidence.snapshot.source_url" target="_blank" rel="noopener external">{{ evidence.year }} Monash Handbook ↗</a><template v-if="evidence.snapshot.last_checked"> · <LastChecked :value="evidence.snapshot.last_checked" /></template><span v-else> · {{ zh ? '核对日期未知' : 'Check date unknown' }}</span></p>
      <NuxtLink :to="`/courses/${evidence.code}?year=${evidence.year}`">{{ zh ? '查看该年份完整学位资料' : 'View the full degree record for this year' }} →</NuxtLink>
    </template>
    <p v-else role="status">{{ zh ? '未能核实该入学年份的学位资料。没有使用邻近或最新年份替代；资料缺失不代表学位取消。' : 'This commencement-year degree record could not be verified. No nearby or latest edition was substituted; missing data does not establish discontinuation.' }}</p>
    <p class="small muted">{{ zh ? '课程单元的教学年份与学位入学年份分别核对。这里是资料快照，不是选课、学分认定或毕业资格批准。' : 'Unit teaching years and degree commencement years are checked separately. These snapshots are not enrolment, credit or graduation approvals.' }}</p>
  </section>
</template>

<style scoped>
.commencement-context { margin-block: var(--s4); padding: var(--s4); overflow-wrap: anywhere; }
.commencement-context h2 { font-size: 1rem; }
.commencement-context p, .commencement-context li { margin-block: var(--s2); }
</style>
