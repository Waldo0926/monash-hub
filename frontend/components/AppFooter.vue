<script setup lang="ts">
import { MONASH_SYSTEMS } from '~/data/systems'

const EVERY_CAMPUS_SYSTEMS = MONASH_SYSTEMS.filter(s => s.appliesTo !== 'malaysia')
const MALAYSIA_SYSTEMS = MONASH_SYSTEMS.filter(s => s.appliesTo === 'malaysia')
const sectionLinks = useSectionNavigation()
const { locale } = useLocale()
const { $t } = useNuxtApp()

const featuresHeading = computed(() => {
  if (locale.value === 'zh') return '功能导航'
  if (locale.value === 'en') return 'Features'
  return $t('footer.explore')
})
</script>

<template>
  <footer class="footer">
    <div class="container inner">
      <div class="about">
        <p class="brand">
          <AppLogo :size="32" tone="onDeep" />
          <span>
            <strong>Monash Hub</strong>
            <span class="tiny muted block">{{ $t('footer.about') }}</span>
            <span class="tiny muted block credit">
              {{ $t('footer.conceptBy') }}
              <a href="https://github.com/Laceyxinx" rel="noopener external" target="_blank">@Laceyxinx</a>
            </span>
            <span class="tiny muted block credit">
              {{ $t('footer.builtMaintainedBy') }}
              <a href="https://github.com/Waldo0926" rel="noopener external" target="_blank">@Waldo0926</a>
            </span>
          </span>
        </p>
        <p class="small disclaimer">{{ $t('footer.disclaimer') }}</p>
      </div>

      <nav class="col explore-col" :aria-label="featuresHeading">
        <h2 class="tiny muted heading">{{ featuresHeading }}</h2>
        <div class="explore-links">
          <NuxtLink v-for="link in sectionLinks" :key="link.to" :to="link.to">
            {{ link.label }}
          </NuxtLink>
        </div>
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
           above because these are things you do, not things you read, and in two
           columns rather than one list: which campus a system belongs to is the
           thing a reader is checking, and side by side that is one glance rather
           than a label to read on every row. -->
      <nav class="col" :aria-label="$t('footer.systems')">
        <h2 class="tiny muted heading">{{ $t('footer.systems') }}</h2>
        <a
          v-for="system in EVERY_CAMPUS_SYSTEMS"
          :key="system.url"
          :href="system.url"
          rel="noopener external"
          target="_blank"
        >{{ system.name }} ↗</a>
      </nav>

      <nav class="col" :aria-label="$t('footer.systemsMalaysia')">
        <h2 class="tiny muted heading">{{ $t('footer.systemsMalaysia') }}</h2>
        <a
          v-for="system in MALAYSIA_SYSTEMS"
          :key="system.url"
          :href="system.url"
          rel="noopener external"
          target="_blank"
        >{{ system.name }} ↗</a>
      </nav>

      <div class="footer-bottom">
        <p class="small wechat">{{ $t('footer.wechat') }}</p>
        <p class="tiny copyright">© 2026 Shuoxun Wen. All rights reserved.</p>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  margin-top: var(--s8);
  padding: var(--s6) 0 var(--s7);
  background: var(--footer-bg);
  color: var(--footer-text);
}
.inner {
  display: grid;
  width: 100%;
  max-width: 1540px;
  padding-inline: clamp(24px, 3vw, 56px);
  /* The feature navigation gets enough room for two balanced columns while the
     product description and external-resource groups keep comfortable widths. */
  grid-template-columns:
    minmax(280px, 1.45fr) minmax(320px, 1.35fr) minmax(190px, 1.05fr)
    minmax(150px, 0.8fr) minmax(165px, 0.85fr);
  column-gap: clamp(28px, 2.8vw, 52px);
  row-gap: var(--s5);
  align-items: start;
}

.brand { display: flex; align-items: center; gap: var(--s3); margin-bottom: var(--s3); }
.block { display: block; }
.credit { line-height: 1.45; }
.credit :deep(a) { font-weight: 600; }
.disclaimer { margin: 0; color: var(--muted); }
.footer-bottom {
  grid-column: 1 / -1;
  display: grid;
  gap: var(--s3);
}
.wechat {
  margin: 0;
  padding-left: var(--s3);
  border-left: 2px solid var(--footer-accent);
  color: var(--footer-heading);
}
.copyright {
  margin: 0;
  color: var(--footer-text);
  opacity: 0.85;
}

.col { display: grid; align-content: start; gap: var(--s2); }
.explore-col { grid-template-rows: auto 1fr; }
.explore-links {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  column-gap: var(--s5);
  row-gap: var(--s2);
  align-content: start;
}
.explore-links a { white-space: nowrap; }

.heading {
  margin: 0 0 var(--s1);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-weight: 600;
}
.col a { font-size: 0.9rem; }

@media (max-width: 1280px) {
  .inner {
    max-width: var(--container);
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: var(--s5);
  }
  .about { grid-column: 1 / -1; }
}
@media (max-width: 640px) {
  .inner { grid-template-columns: 1fr; }
  .about { grid-column: auto; }
  .explore-links { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .explore-links a { white-space: normal; }
}
@media (max-width: 420px) {
  .explore-links { grid-template-columns: 1fr; }
}
@media (max-width: 1180px) {
  .footer { padding-bottom: calc(var(--s7) + 56px); }
}
.footer :deep(h2),
.footer :deep(.foot-heading) { color: var(--footer-heading); }
.footer :deep(a) { color: #dbeafe; }
.footer :deep(a:hover) { color: #fff; }
.footer :deep(.muted),
.disclaimer { color: var(--footer-text); }
.footer :deep(.brand-name) { color: var(--footer-heading); }
</style>
