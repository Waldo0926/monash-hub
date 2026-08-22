<template>
  <footer class="footer">
    <div class="container">
      <p class="small">
        <strong>Monash Hub</strong> is an independent student information platform and is not
        affiliated with or endorsed by Monash University. Always confirm enrolment, graduation,
        visa and academic policy decisions through the Monash website, Handbook, Moodle or WES.
      </p>
      <p class="small muted">
        Monash Hub 为独立学生信息平台，与 Monash University 无官方隶属或背书关系。重要决定请以官方最新信息为准。
      </p>
      <p class="tiny muted links">
        <NuxtLink to="/units">Units</NuxtLink> ·
        <NuxtLink to="/guides">Official guides</NuxtLink> ·
        <NuxtLink to="/community">Community</NuxtLink> ·
        <a href="https://handbook.monash.edu" rel="noopener external" target="_blank">Monash Handbook ↗</a>
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
@media (max-width: 900px) {
  .footer { padding-bottom: calc(var(--s8) + 56px); }
}
</style>
