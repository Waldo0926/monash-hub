/** Check authored UI strings; preserve official text and normal prose punctuation. */
import { readFileSync } from 'node:fs'
const text = readFileSync(new URL('../i18n/index.ts', import.meta.url), 'utf8')
const start = text.indexOf('const zh: Messages = {')
const end = text.indexOf('const ja: Messages')
if (start < 0 || end <= start) throw new Error('Chinese section not found')
const section = text.slice(start, end)
const issues = []
let checked = 0
let narratives = 0
for (const [index, line] of section.split('\n').entries()) {
  const m = line.match(/^\s*'([^']+)':\s*'(.*)',?\s*$/)
  if (!m) continue
  const [, key, value] = m
  checked++
  if (value.includes('。')) narratives++
  const shortUI = /(?:^|\.)(title|label|button|tab|cta|placeholder|submit|save|cancel|back|next|done)$/i.test(key)
  if (shortUI && value.endsWith('。')) issues.push(String(index + 1) + ': ' + key + ' ends with 。')
  if (/[\u3400-\u9fff]\s+[A-Za-z0-9]|[A-Za-z0-9]\s+[\u3400-\u9fff]/.test(value)) {
    issues.push(String(index + 1) + ': ' + key + ' has Chinese/Latin boundary spacing')
  }
}
console.log('Chinese UI copy: ' + checked + ' single-line translations checked, ' + narratives + ' retain narrative punctuation.')
if (issues.length) { console.error(issues.join('\n')); process.exitCode = 1 }
