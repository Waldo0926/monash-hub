<script setup lang="ts">
/**
 * The label that says where an answer came from.
 *
 * This is the single most important component on the site. Official Handbook
 * data, official Monash pages and student experience are three different kinds
 * of claim, and a reader has to be able to tell them apart without reading the
 * fine print. Colour alone never carries the meaning - the text is always
 * there too, which is also what keeps it usable for colour-blind readers.
 */
const props = defineProps<{ kind: string }>()

const { $t } = useNuxtApp()

const KEYS: Record<string, string> = {
  handbook: 'badge.handbook',
  'official-handbook': 'badge.handbook',
  official: 'badge.official',
  'official-source': 'badge.official',
  faq: 'badge.official',
  community: 'badge.community',
  mumguide: 'badge.mumguide',
  sponsored: 'badge.sponsored'
}

const label = computed(() => (KEYS[props.kind] ? $t(KEYS[props.kind]!) : props.kind))
const tone = computed(() => {
  if (props.kind.includes('handbook')) return 'handbook'
  if (props.kind === 'community') return 'community'
  if (props.kind === 'sponsored') return 'sponsored'
  if (props.kind === 'mumguide') return 'mumguide'
  return 'official'
})
</script>

<template>
  <span class="badge" :class="`badge--${tone}`">{{ label }}</span>
</template>

<style scoped>
.badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: var(--radius-pill);
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.01em;
  white-space: nowrap;
}
.badge--handbook { background: var(--badge-handbook-bg); color: var(--badge-handbook); }
.badge--official { background: var(--badge-official-bg); color: var(--badge-official); }
.badge--community { background: var(--badge-community-bg); color: var(--badge-community); }
.badge--sponsored { background: var(--badge-sponsored-bg); color: var(--badge-sponsored); }
.badge--mumguide { background: var(--surface-2); color: var(--text); }
</style>
