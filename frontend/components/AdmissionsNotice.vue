<script setup lang="ts">
/** Current programme notices are separate from selected-intake eligibility. */
import type { AdmissionsEvidence } from '~/utils/admissions'
defineProps<{ evidence: AdmissionsEvidence; compact?: boolean }>()
const { locale } = useLocale()
const zh = computed(() => locale.value === 'zh')
const en = { open: 'Explicit open notice', closed: 'Explicit closed notice', suspended: 'Explicit suspension notice', conflict: 'Conflicting notices — review required', not_verified: 'Not verified', not_offered_on_campus: 'Explicitly not offered at this campus' }
const cn = { open: '课程页明确显示开放申请', closed: '课程页明确显示关闭申请', suspended: '课程页明确显示暂停申请', conflict: '来源通知冲突，需人工核对', not_verified: '未核实', not_offered_on_campus: '明确未在该校区开设' }
const periods: Record<string, string> = { february: '2月', july: '7月', october: '10月' }
</script>

<template>
  <span :class="['admissions-notice', { compact }]" role="note">
    <strong>{{ zh ? '当前申请通知' : 'Current application notice' }}：{{ (zh ? cn : en)[evidence.status] }}</strong>
    <span v-if="evidence.intake_year && evidence.intake_period" class="notice-line selected-intake">
      <strong>{{ zh ? '所选批次' : 'Selected intake' }} {{ evidence.intake_year }} {{ zh ? periods[evidence.intake_period] : evidence.intake_period }} · {{ evidence.campus }}：</strong>
      {{ (zh ? cn : en)[evidence.intake_status] }}
      <span v-if="evidence.intake_status === 'not_verified'"> · {{ zh ? '须有明确对应学位、年份和批次的通知，不能从学费、名单或一般截止日期推断' : 'Requires an explicit programme, year and intake notice; fees, listings and general deadlines are insufficient.' }}</span>
    </span>
    <span class="notice-line" v-if="evidence.reason === 'stale_source' || evidence.reason === 'source_unavailable'">
      {{ zh ? '来源已过期或暂不可用，不能继续确认旧状态' : 'The source is stale or unavailable; its earlier status cannot be confirmed.' }}
    </span>
    <span v-if="evidence.fee_link_conflict" class="notice-line">{{ zh ? '收费表的课程链接与已核对的课程页面不一致，请分别核对两个来源。' : 'The fee-table link differs from the reviewed programme page. Check both sources.' }}</span>
    <span v-if="evidence.reason === 'source_identity_mismatch'" class="notice-line">{{ zh ? '课程页标题与收费行的资格名称不一致，不能自动认定是同一学位，请核对原始来源。' : 'The fetched programme title does not match the fee qualification. Verify the original sources before treating them as the same degree.' }}</span>
    <span class="notice-line" v-if="!compact">{{ zh ? '这是课程页面的当前通知，不代表所选未来批次已开放，也不代表个人申请资格。收费表和截止日期不能代替课程通知' : 'This is a current programme-page notice, not confirmation that a future intake is open or that you are eligible. Fees and deadlines do not establish application status.' }}</span>
    <span v-if="evidence.programme_page_verified" class="small notice-line">
      {{ zh ? '课程来源索引有效；申请状态仍以明确通知为准' : 'Current matching programme source indexed; application status still requires an explicit notice.' }}
      <template v-if="evidence.course_code"> · {{ evidence.course_code }}</template>
    </span>
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
