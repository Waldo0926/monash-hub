// npm audit with an allowlist, for CI.
//
// `npm audit --audit-level=high` fails on advisories that have no fixed
// release yet, and npm has no way to accept one with a reason. This runs the
// same audit and ignores only the advisories listed below, each with why it
// is safe to wait. Anything else at high or critical fails the build.
//
// Check the list when Nuxt is upgraded: an entry whose package now has a fix
// should be dropped so the audit can catch it again.
import { execFileSync } from 'node:child_process'

const allowlist = {
  // braces, reached only through nitropack's globby while the server bundle
  // is built. It never runs in the web container: .output/server/node_modules
  // holds neither braces nor micromatch. No fixed release as of 2026-10-19.
  'GHSA-vfj7-8cjw-p6xm': 'build-time glob, not in the production bundle'
}

let report
try {
  report = JSON.parse(execFileSync('npm', ['audit', '--json'], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'inherit'] }))
} catch (error) {
  // npm audit exits non-zero when it finds anything; the report is still on stdout.
  if (!error.stdout) throw error
  report = JSON.parse(error.stdout)
}

const failing = []
for (const [name, entry] of Object.entries(report.vulnerabilities ?? {})) {
  if (!['high', 'critical'].includes(entry.severity)) continue
  // `via` mixes advisory objects (the package itself is vulnerable) with
  // package names (it only depends on a vulnerable one). Only the former
  // carry an advisory id; a package flagged purely through its dependencies
  // is covered by whatever decision was made for those.
  const advisories = entry.via.filter((item) => typeof item === 'object')
  const unexplained = advisories.filter((item) => !(item.url.split('/').pop() in allowlist))
  if (unexplained.length > 0) {
    failing.push(`${name} (${entry.severity}): ${unexplained.map((item) => `${item.title} ${item.url}`).join('; ')}`)
  }
}

const accepted = Object.keys(allowlist).length
if (failing.length > 0) {
  console.error(`npm audit: ${failing.length} high or critical advisories without an entry in scripts/audit.mjs:`)
  for (const line of failing) console.error(`  ${line}`)
  process.exit(1)
}
console.log(`npm audit: no high or critical advisories beyond the ${accepted} accepted in scripts/audit.mjs`)
