<template>
  <footer class="footer">
    <div class="container">
      <p class="small">{{ $t('footer.disclaimer') }}</p>
      <p class="tiny muted links">
        <NuxtLink to="/units">{{ $t('nav.units') }}</NuxtLink> ·
        <NuxtLink to="/guides">{{ $t('nav.guides') }}</NuxtLink> ·
        <NuxtLink to="/community">{{ $t('nav.community') }}</NuxtLink> ·
        <a href="https://handbook.monash.edu" rel="noopener external" target="_blank">
          {{ $t('footer.handbookLink') }} ↗
        </a>
      </p>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  margin-top: var(--s8);
  padding: var(--s6) 0 var(--s8);
  border-top: 1px solid var(--border);
  background: var(--surface);
}
.footer p { max-width: 78ch; }
.links { margin-bottom: 0; }
@media (max-width: 980px) {
  .footer { padding-bottom: calc(var(--s8) + 56px); }
}
</style>
