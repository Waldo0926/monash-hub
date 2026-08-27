<script setup lang="ts">
import { MONASH_SYSTEMS } from '~/data/systems'
</script>

<template>
  <footer class="footer">
    <div class="container inner">
      <div class="about">
        <p class="brand">
          <span class="brand-mark" aria-hidden="true">MH</span>
          <span>
            <strong>Monash Hub</strong>
            <span class="tiny muted block">{{ $t('footer.about') }}</span>
          </span>
        </p>
        <p class="small disclaimer">{{ $t('footer.disclaimer') }}</p>
      </div>

      <nav class="col" :aria-label="$t('footer.explore')">
        <h2 class="tiny muted heading">{{ $t('footer.explore') }}</h2>
        <NuxtLink to="/units">{{ $t('nav.units') }}</NuxtLink>
        <NuxtLink to="/guides">{{ $t('nav.guides') }}</NuxtLink>
        <NuxtLink to="/community">{{ $t('nav.community') }}</NuxtLink>
        <NuxtLink to="/exchange">{{ $t('nav.exchange') }}</NuxtLink>
      </nav>

      <nav class="col" :aria-label="$t('footer.official')">
        <h2 class="tiny muted heading">{{ $t('footer.official') }}</h2>
        <a href="https://handbook.monash.edu" rel="noopener external" target="_blank">
          {{ $t('footer.handbookLink') }} ↗
        </a>
        <a href="https://www.monash.edu/students" rel="noopener external" target="_blank">
          {{ $t('footer.monashStudents') }} ↗
        </a>
        <a href="https://www.monash.edu.my/student-services" rel="noopener external" target="_blank">
          {{ $t('footer.monashMalaysia') }} ↗
        </a>
      </nav>

      <!-- The systems a student logs into. Kept apart from the reference sites
           above because these are things you do, not things you read - and
           split by campus, because half of them are Malaysia's own. -->
      <nav class="col" :aria-label="$t('footer.systems')">
        <h2 class="tiny muted heading">{{ $t('footer.systems') }}</h2>
        <a
          v-for="system in MONASH_SYSTEMS"
          :key="system.url"
          :href="system.url"
          rel="noopener external"
          target="_blank"
          class="system"
        >
          <span>{{ system.name }} ↗</span>
          <CampusNotice
            v-if="system.appliesTo === 'malaysia'"
            :applies-to="system.appliesTo"
            compact
          />
        </a>
      </nav>
    </div>
  </footer>
</template>

<style scoped>
/*
 * Four columns rather than one.
 *
 * The disclaimer is the longest single piece of text on the site and it sits at
 * the bottom of every page, so left on its own it either runs the full window
 * width - unreadable on a wide screen - or gets capped and leaves half the
 * footer visibly empty. Putting the navigation beside it means the measure stays
 * comfortable and the space is actually used.
 */
.footer {
  margin-top: var(--s8);
  padding: var(--s6) 0 var(--s7);
  border-top: 1px solid var(--border);
  background: var(--surface);
}
.inner {
  display: grid;
  /* The four columns are not the same shape. "Browse" is four short words
     and needs the least; the source and system columns carry long names and
     a campus label, so they get the room the browse column gives up. */
  grid-template-columns:
    minmax(0, 2fr) minmax(80px, 0.62fr) minmax(150px, 1.19fr) minmax(160px, 1.19fr);
  gap: var(--s6);
  align-items: start;
}

.brand { display: flex; align-items: center; gap: var(--s3); margin-bottom: var(--s3); }
.brand-mark {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  background: var(--navy);
  color: var(--text-inverse);
  font-size: 0.75rem;
  font-weight: 700;
}
.block { display: block; }
.disclaimer { margin: 0; color: var(--muted); }

.col { display: grid; align-content: start; gap: var(--s2); }
/* The campus label sits against the right edge of the column rather than
   trailing the name, so the four Malaysia ones line up as a block instead of
   stepping in and out with the length of each system's name. */
.system {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--s2);
}
.heading {
  margin: 0 0 var(--s1);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-weight: 600;
}
.col a { font-size: 0.9rem; }

@media (max-width: 900px) {
  .inner { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--s5); }
  /* The disclaimer spans the row on a narrow screen; the three link
     columns pair up under it rather than each taking a half-width
     column of their own and leaving one stranded. */
  .about { grid-column: 1 / -1; }
  .about { grid-column: 1 / -1; }
}
@media (max-width: 980px) {
  .footer { padding-bottom: calc(var(--s7) + 56px); }
}
</style>
