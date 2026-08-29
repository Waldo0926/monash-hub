<script setup lang="ts">
/**
 * The Monash Hub mark.
 *
 * A branching path: one node opening into two. That is literally what the
 * product does — the unit tree answers "what does this unlock", the planner
 * answers "what has to come first" — so the mark says what the site is for
 * rather than spelling its initials.
 *
 * What it deliberately is not: a shield, a crest, a serif monogram, or an M.
 * The palette moved closer to the university's after a deliberate decision, and
 * that makes the mark the thing carrying the distinction. A student glancing at
 * a tab has to be able to tell this apart from an official Monash page, and the
 * footer disclaimer cannot do that job on its own.
 *
 * `tone` picks how it sits on its background: `onDark` for the header, `onLight`
 * anywhere the page is white.
 */
withDefaults(
  defineProps<{
    size?: number
    tone?: 'onDark' | 'onLight'
    /** Draw the rounded tile behind the mark. Off gives just the glyph. */
    tile?: boolean
  }>(),
  { size: 32, tone: 'onDark', tile: true }
)
</script>

<template>
  <svg
    :width="size" :height="size" viewBox="0 0 64 64"
    role="img" aria-label="Monash Hub" class="logo" :class="`logo--${tone}`"
  >
    <rect v-if="tile" class="tile" width="64" height="64" rx="15" />
    <!-- One node opening into two: the shape of a prerequisite. -->
    <g class="mark" fill="none" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M20 44 L32 32" />
      <path d="M32 32 L44 20" />
      <path d="M32 32 L44 44" />
    </g>
    <g class="nodes">
      <circle cx="20" cy="44" r="6.5" />
      <circle cx="44" cy="20" r="5" />
      <circle cx="44" cy="44" r="5" />
    </g>
  </svg>
</template>

<style scoped>
.logo { display: block; flex: none; }

.logo--onDark .tile { fill: rgba(255, 255, 255, 0.14); }
.logo--onDark .mark { stroke: #fff; }
.logo--onDark .nodes { fill: #fff; }

.logo--onLight .tile { fill: var(--brand); }
.logo--onLight .mark { stroke: #fff; }
.logo--onLight .nodes { fill: #fff; }
</style>
