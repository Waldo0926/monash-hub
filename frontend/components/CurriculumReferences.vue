<script setup lang="ts">
const props = defineProps<{ links?: { url: string; label: string }[] }>()
const { locale } = useLocale()
const links = computed(() => (props.links || []).filter(link => {
  try { return ['https:', 'http:'].includes(new URL(link.url).protocol) } catch { return false }
}))
</script>

<template>
  <aside v-if="links.length" class="references">
    <h3>{{ locale === 'zh' ? '原文中的相关链接' : 'References from the original source' }}</h3>
    <ul>
      <li v-for="link in links" :key="link.url">
        <a :href="link.url" target="_blank" rel="noopener noreferrer">{{ link.label }} ↗</a>
      </li>
    </ul>
  </aside>
</template>

<style scoped>
.references { margin-block: var(--s3); overflow-wrap: anywhere; }
h3 { font-size: .9rem; margin-bottom: var(--s2); }
ul { padding-left: var(--s4); }
a { display: inline-block; padding-block: var(--s2); }
</style>
