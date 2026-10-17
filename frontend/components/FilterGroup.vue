<script setup lang="ts">
/**
 * One filter heading that opens and closes, with + or − on the right.
 *
 * Campus alone is thirty-odd options, so with every filter open the subject
 * and exam filters sat a long scroll below the year picker. Closed groups
 * keep every heading on one screen and show how many values are ticked.
 */
const props = withDefaults(defineProps<{ title: string; open?: boolean; selected?: number }>(), {
  open: false,
  selected: 0
})

const isOpen = ref(props.open)
const id = useId()
</script>

<template>
  <section class="group">
    <h3 class="group-head">
      <button
        type="button"
        class="group-toggle"
        :aria-expanded="isOpen"
        :aria-controls="id"
        @click="isOpen = !isOpen"
      >
        <span class="group-title">{{ title }}</span>
        <span v-if="selected && !isOpen" class="group-count">{{ selected }}</span>
        <span class="group-sign" aria-hidden="true">{{ isOpen ? '−' : '+' }}</span>
      </button>
    </h3>
    <div v-show="isOpen" :id="id" class="group-body">
      <slot />
    </div>
  </section>
</template>

<style scoped>
.group { border-top: 1px solid var(--border); }
.group-head { margin: 0; font-size: inherit; }
.group-toggle {
  display: flex; align-items: center; gap: var(--s2); width: 100%; min-height: 44px; padding: 0;
  border: 0; background: none; color: var(--text); font: inherit; font-weight: 600; font-size: 0.92rem;
  text-align: left; cursor: pointer;
}
.group-toggle:focus-visible { outline: 2px solid var(--brand); outline-offset: 2px; border-radius: 4px; }
.group-title { flex: 1; }
.group-count {
  display: inline-grid; place-items: center; min-width: 20px; height: 20px; padding: 0 6px;
  border-radius: var(--radius-pill); background: var(--navy); color: var(--text-inverse);
  font-size: 0.72rem; font-weight: 600;
}
.group-sign { width: 16px; text-align: center; color: var(--muted); font-size: 1.1rem; font-weight: 400; }
.group-body { padding-bottom: var(--s3); }
</style>
