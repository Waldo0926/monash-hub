<script setup lang="ts">
import { MONASH_SYSTEMS } from '~/data/systems'

const EVERY_CAMPUS_SYSTEMS = MONASH_SYSTEMS.filter(s => s.appliesTo !== 'malaysia')
const MALAYSIA_SYSTEMS = MONASH_SYSTEMS.filter(s => s.appliesTo === 'malaysia')
const sectionLinks = useSectionNavigation()
const { locale } = useLocale()
const { $t } = useNuxtApp()
const route = useRoute()
// The parents page has its own contact section and does not carry the
// student disclaimer.
const showDisclaimer = computed(() => route.path !== '/parents')

// The account name is a link to /mamo, so the sentence is split around it.
// The name stays in Chinese in every language because that is what people
// search for in WeChat.
const wechatParts = computed(() => $t('footer.wechat').split('{name}'))

const standalone = ref(true)
onMounted(() => { standalone.value = isStandalone() })

const featuresHeading = computed(() => {
  if (locale.value === 'zh') return '功能导航'
  if (locale.value === 'en') return 'Features'
  return $t('footer.explore')
})
</script>

<template>
  <footer class="footer">
    <div class="container">
      <div class="top">
        <div class="about">
          <NuxtLink to="/" class="brand">
            <AppLogo :size="28" tone="onLight" />
            <strong>Monash Hub</strong>
          </NuxtLink>
          <p class="tagline small">{{ $t('footer.about') }}</p>
          <p v-if="showDisclaimer" class="disclaimer small">{{ $t('footer.disclaimer') }}</p>
          <!-- Always here, for anyone who closed the hint at the top of the page.
               Not shown inside the installed app, where it has nothing to do. -->
          <ClientOnly>
            <details v-if="!standalone" class="install">
              <summary class="small">{{ $t('pwa.footerTitle') }}</summary>
              <InstallSteps />
            </details>
          </ClientOnly>
        </div>

        <div class="cols">
          <nav class="col" :aria-label="featuresHeading">
            <h2 class="heading">{{ featuresHeading }}</h2>
            <NuxtLink v-for="link in sectionLinks" :key="link.to" :to="link.to">{{ link.label }}</NuxtLink>
          </nav>

          <nav class="col" :aria-label="$t('footer.official')">
            <h2 class="heading">{{ $t('footer.official') }}</h2>
            <a href="https://handbook.monash.edu" rel="noopener external" target="_blank">
              {{ $t('footer.handbookLink') }} <span class="ext" aria-hidden="true">↗</span>
            </a>
            <a href="https://www.monash.edu/students" rel="noopener external" target="_blank">
              {{ $t('footer.monashStudents') }} <span class="ext" aria-hidden="true">↗</span>
            </a>
            <a href="https://www.monash.edu.my/student-services" rel="noopener external" target="_blank">
              {{ $t('footer.monashMalaysia') }} <span class="ext" aria-hidden="true">↗</span>
            </a>
          </nav>

          <!-- The systems a student logs into, apart from the reference sites
               because these are things you do, not things you read. Which campus
               a system belongs to is what a reader checks, so each campus has its
               own column rather than a label on every row. -->
          <nav class="col" :aria-label="$t('footer.systems')">
            <h2 class="heading">{{ $t('footer.systems') }}</h2>
            <a
              v-for="system in EVERY_CAMPUS_SYSTEMS"
              :key="system.url"
              :href="system.url"
              rel="noopener external"
              target="_blank"
            >{{ system.name }} <span class="ext" aria-hidden="true">↗</span></a>
          </nav>

          <nav class="col" :aria-label="$t('footer.systemsMalaysia')">
            <h2 class="heading">{{ $t('footer.systemsMalaysia') }}</h2>
            <a
              v-for="system in MALAYSIA_SYSTEMS"
              :key="system.url"
              :href="system.url"
              rel="noopener external"
              target="_blank"
            >{{ system.name }} <span class="ext" aria-hidden="true">↗</span></a>
          </nav>
        </div>
      </div>

      <!-- Points at the 马莫百科 page rather than only naming the account, so
           someone can see what it posts and scan the QR codes there. A filled
           button, because as plain bold text nobody saw it could be clicked. -->
      <div class="wechat">
        <p class="wechat-text small">
          {{ wechatParts[0] }}<NuxtLink to="/mamo" class="wechat-name">马莫百科</NuxtLink>{{ wechatParts[1] }}
        </p>
        <NuxtLink to="/mamo#follow" class="btn btn--small wechat-cta">
          <svg class="qr-icon" viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
            <path
              d="M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h2v2h-2zM18 14h2v2h-2zM16 16h2v2h-2zM14 18h2v2h-2zM18 18h2v2h-2z"
              fill="none"
              stroke="currentColor"
              stroke-width="1.6"
              stroke-linejoin="round"
            />
          </svg>
          <span>{{ $t('footer.wechatCta') }}</span>
        </NuxtLink>
      </div>

      <div class="bottom tiny">
        <p class="copyright">{{ $t('footer.copyright') }}</p>
        <p class="credits">
          <span>{{ $t('footer.conceptBy') }} <a href="https://github.com/Laceyxinx" rel="noopener external" target="_blank">@Laceyxinx</a></span>
          <span>{{ $t('footer.builtMaintainedBy') }} <a href="https://github.com/Waldo0926" rel="noopener external" target="_blank">@Waldo0926</a></span>
          <NuxtLink to="/privacy">{{ $t('footer.privacy') }}</NuxtLink>
        </p>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  margin-top: var(--s8);
  padding: var(--s7) 0 var(--s5);
  background: var(--footer-bg);
  border-top: 1px solid var(--footer-border);
  color: var(--footer-text);
}

.top {
  display: grid;
  grid-template-columns: minmax(240px, 1fr) minmax(0, 2.4fr);
  gap: var(--s6) var(--s7);
  align-items: start;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: var(--s2);
  font-size: 1.05rem;
}
.footer .brand { color: var(--footer-heading); }
.footer .brand:hover { text-decoration: none; }
.tagline { margin: var(--s2) 0 var(--s3); color: var(--footer-heading); }
.disclaimer { margin: 0; max-width: 32em; line-height: 1.6; }
.install { margin-top: var(--s3); color: var(--footer-heading); }
.install summary {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  font-weight: 600;
  cursor: pointer;
}
.install :deep(.install-steps) { margin-top: var(--s2); }

.cols {
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.3fr) minmax(0, 0.9fr) minmax(0, 1fr);
  gap: var(--s5);
}
.col { display: flex; flex-direction: column; align-items: flex-start; gap: 10px; min-width: 0; }
.heading {
  margin: 0 0 var(--s1);
  font-family: var(--font);
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: var(--muted-2);
}
.col a { font-size: 0.9rem; line-height: 1.4; }
.ext { color: var(--muted-2); font-size: 0.8em; }

.wechat {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--s3) var(--s4);
  margin-top: var(--s6);
  padding: var(--s3) var(--s4);
  border: 1px solid var(--footer-border);
  border-radius: var(--radius);
  background: var(--surface);
}
.wechat-text { margin: 0; color: var(--footer-heading); }
.footer .wechat-name { color: var(--brand); font-weight: 600; }
.footer .wechat-cta { background: var(--brand); color: #fff; font-weight: 600; }
.footer .wechat-cta:hover { background: var(--brand-700); color: #fff; }
.qr-icon { flex: none; }

.bottom {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--s2) var(--s4);
  margin-top: var(--s5);
  padding-top: var(--s4);
  border-top: 1px solid var(--footer-border);
}
.bottom p { margin: 0; }
.credits { display: flex; flex-wrap: wrap; gap: var(--s2) var(--s4); }
.credits a { font-weight: 600; }

@media (max-width: 1000px) {
  .top { grid-template-columns: 1fr; }
  .cols { grid-template-columns: repeat(2, minmax(0, 1fr)); row-gap: var(--s5); }
}
@media (max-width: 640px) {
  .footer { padding-top: var(--s6); }
  .wechat { align-items: flex-start; }
  .wechat .btn { width: 100%; }
  .bottom { flex-direction: column; align-items: flex-start; }
}
@media (max-width: 1180px) {
  .footer { padding-bottom: calc(var(--s5) + 72px); }
}
.footer :deep(a) { color: var(--footer-link); }
.footer :deep(a:hover) { color: var(--footer-link-hover); }
.footer :deep(.muted),
.disclaimer { color: var(--footer-text); }
</style>
