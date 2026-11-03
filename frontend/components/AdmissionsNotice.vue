<script setup lang="ts">
/** Current programme notices are separate from selected-intake eligibility. */
import type { AdmissionsEvidence } from '~/utils/admissions'
defineProps<{ evidence: AdmissionsEvidence; compact?: boolean }>()
const { locale } = useLocale()
const zh = computed(() => locale.value === 'zh')
const en = { open: 'Explicit open notice', closed: 'Explicit closed notice', suspended: 'Explicit suspension notice', conflict: 'Conflicting notices — review required', not_verified: 'Not verified' }
const cn = { open: '课程页明确显示开放申请', closed: '课程页明确显示关闭申请', suspended: '课程页明确显示暂停申请', conflict: '来源通知冲突，需人工核对', not_verified: '未核实' }
</script>

<template>
  <span :class="['admissions-notice', { compact }]" role="note">
    <strong>{{ zh ? '当前申请通知' : 'Current application notice' }}：{{ (zh ? cn : en)[evidence.status] }}</strong>
    <span class="notice-line" v-if="evidence.reason === 'stale_source' || evidence.reason === 'source_unavailable'">
      {{ zh ? '来源已过期或暂不可用，不能继续确认旧状态' : 'The source is stale or unavailable; its earlier status cannot be confirmed.' }}
    </span>
    <span class="notice-line" v-if="!compact">{{ zh ? '这是课程页面的当前通知，不代表所选未来批次已开放，也不代表个人申请资格。收费表和截止日期不能代替课程通知' : 'This is a current programme-page notice, not confirmation that a future intake is open or that you are eligible. Fees and deadlines do not establish application status.' }}</span>
    <span v-if="evidence.source_url" class="small notice-line">
      <a :href="evidence.source_url" target="_blank" rel="noopener external">{{ zh ? '官方课程页' : 'Official programme page' }} ↗</a>
      <template v-if="evidence.last_checked"> · <LastChecked :value="evidence.last_checked" /></template>
    </span>
  </span>
</template>

<style scoped>
.admissions-notice { display: block; padding: var(--s3); margin-block: var(--s3); border: 1px solid var(--border); border-radius: 8px; overflow-wrap: anywhere; }
.admissions-notice .notice-line { display: block; margin: .5em 0 0; }
.compact { font-size: .8rem; }
</style>
