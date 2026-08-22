<template>
  <div class="shell">
    <a href="#main" class="skip">Skip to content</a>
    <AppHeader />
    <main id="main" class="main">
      <slot />
    </main>
    <AppFooter />
    <MobileNav />
  </div>
</template>

<style scoped>
.shell { min-height: 100vh; display: flex; flex-direction: column; }
.main { flex: 1; padding: var(--s6) 0 var(--s7); }
.skip {
  position: absolute;
  left: -9999px;
  z-index: 40;
  padding: var(--s3) var(--s4);
  background: var(--surface);
}
.skip:focus { left: var(--s4); top: var(--s2); }
</style>
