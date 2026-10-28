<script setup lang="ts">
/**
 * A page for parents in China weighing Monash University Malaysia. Chinese
 * only, in a formal register, with no student vocabulary. Every official fact
 * links to the English page it came from.
 *
 * Tuition comes from the same /v1/fees table as /fees; the rest is in
 * data/parents.ts.
 */
import { MAMO_ACCOUNT } from '~/data/mamo'
import {
  DEGREE_SOURCE, ENGLISH_SOURCE, ENTRY_SOURCE, FEE_EXAMPLES, GAOKAO, LIVING, MYR_TO_CNY,
  RANKINGS, RANKINGS_SOURCE, SUBJECT_RANKING, TRANSFER, VISA
} from '~/data/parents'
import type { FeeRow } from '~/utils/tuition'

const config = useRuntimeConfig()
const site = config.public.siteUrl.replace(/\/$/, '')

type Table = { year: number | null; sections: { source: string; schools: { rows: FeeRow[] }[] }[] }
const { data: fees } = await useApiFetch<Table>('/v1/fees')

const norm = (s: string) => s.trim().toLowerCase()
const feeRows = computed(() => {
  const rows = (fees.value?.sections ?? [])
    .filter(s => s.source === 'malaysia-ugfees')
    .flatMap(s => s.schools.flatMap(g => g.rows))
  return FEE_EXAMPLES.flatMap(({ label, match }) => {
    const row = rows.find(r => norm(r.title) === norm(match) || r.covers.some(c => norm(c) === norm(match)))
    const amount = row?.international[0]?.value
    if (!row || amount == null) return []
    const years = Number(row.duration)
    return [{ label, amount, years: Number.isFinite(years) && years > 0 ? years : null }]
  })
})

const group = (n: number) => String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
const rm = (n: number) => `RM${group(n)}`
const cny = (n: number) => `约 ${(n * MYR_TO_CNY / 10000).toFixed(1)} 万元`
const cnyPlain = (n: number) => `约 ${group(Math.round(n * MYR_TO_CNY / 10) * 10)} 元`

const score = (percent: number) => {
  const n = (750 * percent) / 100
  return Number.isInteger(n) ? `${n} 分` : `约 ${Math.round(n)} 分`
}

const copied = ref(false)
async function copyId() {
  try {
    await navigator.clipboard.writeText(MAMO_ACCOUNT.wechatId)
    copied.value = true
    setTimeout(() => (copied.value = false), 2000)
  } catch {
    copied.value = false
  }
}

const title = 'Monash 马来西亚校区：给家长的介绍'
const description = '莫纳什大学马来西亚校区的世界排名、学位证书、高考录取要求、2+2 转澳洲本部和每年费用，内容来自学校官网。'
useSeoMeta({
  title,
  description,
  ogTitle: title,
  ogDescription: description,
  ogImage: `${site}/og-parents.png`,
  ogImageSecureUrl: `${site}/og-parents.png`,
  ogImageAlt: '莫纳什大学马来西亚校区，给家长的介绍',
  ogLocale: 'zh_CN',
  twitterTitle: title,
  twitterDescription: description,
  twitterImage: `${site}/og-parents.png`
})
useHead({
  htmlAttrs: { lang: 'zh-Hans' },
  link: [{ rel: 'canonical', href: `${site}/parents` }]
})
</script>

<template>
  <div class="page" lang="zh-Hans">
    <header class="intro">
      <h1>莫纳什大学马来西亚校区</h1>
      <p class="lead">
        莫纳什大学（Monash University）是澳大利亚八校联盟成员，总部在墨尔本。马来西亚校区位于吉隆坡附近的双威城。以下内容整理自学校官网，每一项下面附有英文原文链接。
      </p>
      <nav class="toc" aria-label="本页目录">
        <a href="#rankings">学校排名</a>
        <a href="#degree">毕业证书</a>
        <a href="#entry">录取要求</a>
        <a href="#transfer">转澳洲本部</a>
        <a href="#cost">费用</a>
        <a href="#contact">咨询</a>
      </nav>
    </header>

    <section id="rankings" class="block">
      <h2>学校排名</h2>
      <ul class="ranks">
        <li v-for="r in RANKINGS" :key="r.name">
          <span class="rank-name">{{ r.name }} {{ r.year }}</span>
          <b>{{ r.place }}</b>
        </li>
        <li>
          <span class="rank-name">{{ SUBJECT_RANKING.name }} {{ SUBJECT_RANKING.year }}</span>
          <b>{{ SUBJECT_RANKING.place }}</b>
        </li>
      </ul>
      <p class="src">
        <a :href="RANKINGS_SOURCE.url" target="_blank" rel="noopener external">查看英文原文</a>
        <span>核对于 {{ RANKINGS_SOURCE.checked }}</span>
      </p>
    </section>

    <section id="degree" class="block">
      <h2>毕业证书</h2>
      <p>
        在马来西亚校区完成学业，获得的毕业证书和学位证书由莫纳什大学颁发，与澳洲本部毕业生相同。回国后可以在教育部留学服务中心办理国（境）外学历学位认证。
      </p>
      <p class="src">
        <a :href="DEGREE_SOURCE.url" target="_blank" rel="noopener external">查看英文原文</a>
        <span>核对于 {{ DEGREE_SOURCE.checked }}</span>
      </p>
    </section>

    <section id="entry" class="block">
      <h2>录取要求</h2>
      <p>学校接受高考成绩直接申请本科。下表是官网列出的最低要求，按高考总分的百分比计算：</p>
      <table class="table">
        <thead>
          <tr><th>专业</th><th>高考总分要求</th><th>满分 750 分时</th></tr>
        </thead>
        <tbody>
          <tr v-for="g in GAOKAO" :key="g.course">
            <td>{{ g.course }}</td>
            <td>{{ g.percent }}%</td>
            <td>{{ score(g.percent) }}</td>
          </tr>
        </tbody>
      </table>
      <p class="note">
        上海（满分 660 分）、海南（满分 900 分）等总分不同的省份，按本省满分乘以同样的百分比计算。每年的要求可能调整，以录取当年官网为准。此外还需要达到英语要求，雅思等考试的具体分数见英文原文。
      </p>
      <p class="src">
        <a :href="ENTRY_SOURCE.url" target="_blank" rel="noopener external">查看英文原文（学术要求）</a>
        <a :href="ENGLISH_SOURCE.url" target="_blank" rel="noopener external">查看英文原文（英语要求）</a>
        <span>核对于 {{ ENTRY_SOURCE.checked }}</span>
      </p>
    </section>

    <section id="transfer" class="block">
      <h2>2+2 转澳洲本部</h2>
      <p>
        部分工程专业可以前两年在马来西亚校区就读，后两年转到墨尔本的 Clayton 校区完成学业，例如{{ TRANSFER.course }}。转校区需要前两年的加权平均成绩达到 55 分以上，并且在澳洲还有至少 48 学分的课程要修。毕业证书同样由莫纳什大学颁发。
      </p>
      <p class="src">
        <a :href="TRANSFER.courseUrl" target="_blank" rel="noopener external">查看英文原文（专业介绍）</a>
        <a :href="TRANSFER.ruleUrl" target="_blank" rel="noopener external">查看英文原文（转校区条件）</a>
        <span>核对于 {{ TRANSFER.checked }}</span>
      </p>
    </section>

    <section id="cost" class="block">
      <h2>费用</h2>
      <h3>学费</h3>
      <table v-if="feeRows.length" class="table">
        <thead>
          <tr><th>专业</th><th>每年学费</th><th>折合人民币</th></tr>
        </thead>
        <tbody>
          <tr v-for="f in feeRows" :key="f.label">
            <td>{{ f.label }}<span v-if="f.years" class="years">{{ f.years }} 年制</span></td>
            <td class="num">{{ rm(f.amount) }}</td>
            <td class="num">{{ cny(f.amount) }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="note">学费数据暂时无法读取，请查看各专业学费页。</p>
      <p class="note">
        以上为{{ fees?.year ? ` ${fees.year} 年` : '' }}国际学生学费。目前以 1 马币兑 {{ MYR_TO_CNY }} 人民币汇率换算，具体以当天汇率为准。
        <NuxtLink to="/fees">全部专业的学费</NuxtLink>
      </p>

      <h3>学生签证</h3>
      <p>
        新生办理马来西亚学生签证，费用约 {{ rm(VISA.amount) }}（{{ cnyPlain(VISA.amount) }}），有效期 {{ VISA.months }} 个月。
      </p>
      <p class="src">
        <a :href="VISA.url" target="_blank" rel="noopener external">查看英文原文</a>
        <span>核对于 {{ VISA.checked }}</span>
      </p>

      <h3>生活费</h3>
      <p>学校官网给出的参考价格：</p>
      <ul class="living">
        <li v-for="l in LIVING.items" :key="l.item"><span>{{ l.item }}</span><b>{{ l.amount }}</b></li>
      </ul>
      <p class="note">官网说明以上均为估算，实际花费与住宿选择和个人习惯有关。</p>
      <p class="src">
        <a :href="LIVING.url" target="_blank" rel="noopener external">查看英文原文</a>
        <span>核对于 {{ LIVING.checked }}</span>
      </p>
    </section>

    <section id="campus" class="block">
      <h2>校园与生活</h2>
      <p class="placeholder">校园照片正在整理，稍后补充。</p>
    </section>

    <section id="contact" class="block">
      <h2>咨询</h2>
      <p>
        如有疑问，可以关注微信公众号“{{ MAMO_ACCOUNT.name }}”，或添加作者微信咨询。作者是马来西亚校区在读学生。
      </p>
      <div class="qrs">
        <figure>
          <img src="/img/mamo/qr-official-account.png" alt="马莫百科公众号二维码" width="140" height="140" loading="lazy">
          <figcaption>公众号：{{ MAMO_ACCOUNT.name }}</figcaption>
        </figure>
        <figure>
          <img src="/img/mamo/qr-wechat.png" alt="作者微信二维码" width="140" height="140" loading="lazy">
          <figcaption>
            微信号：<span class="mono">{{ MAMO_ACCOUNT.wechatId }}</span>
            <button type="button" class="copy" @click="copyId">{{ copied ? '已复制' : '复制' }}</button>
          </figcaption>
        </figure>
      </div>
      <p class="agent">
        可通过作者以学校授权代理渠道递交申请，不收取中介费，不收取押金。
      </p>
      <p class="note">本站由学生自建，并非莫纳什大学官方网站。招生、费用和签证事宜以学校官网和录取通知为准。</p>
    </section>
  </div>
</template>

<style scoped>
.page { max-width: 760px; margin: 0 auto; padding: var(--s6) var(--s4) var(--s8); }
.intro h1 { margin: 0 0 var(--s4); font-size: clamp(1.7rem, 1.3rem + 1.6vw, 2.3rem); line-height: 1.25; }
.lead { margin: 0 0 var(--s5); color: var(--muted); font-size: 1rem; line-height: 1.8; }
.toc { display: flex; flex-wrap: wrap; gap: var(--s2); }
.toc a {
  padding: 6px 14px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-pill);
  color: var(--text);
  font-size: 0.875rem;
}
.toc a:hover { border-color: var(--brand); color: var(--brand); text-decoration: none; }

.block { padding-block: var(--s6); border-top: 1px solid var(--border); scroll-margin-top: calc(var(--header-h) + 8px); }
.intro + .block { margin-top: var(--s6); }
.block h2 { margin: 0 0 var(--s4); font-size: 1.35rem; }
.block h3 { margin: var(--s5) 0 var(--s3); font-size: 1.05rem; }
.block h2 + h3 { margin-top: 0; }
.block p { margin: 0 0 var(--s3); line-height: 1.85; }

.ranks { margin: 0 0 var(--s3); padding: 0; list-style: none; }
.ranks li {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: var(--s4);
  padding: var(--s3) 0;
  border-bottom: 1px solid var(--border);
}
.ranks b { color: var(--brand-700); font-size: 1.05rem; white-space: nowrap; }

.table { width: 100%; margin: 0 0 var(--s3); border-collapse: collapse; font-size: 0.95rem; }
.table th, .table td { padding: 10px 8px 10px 0; border-bottom: 1px solid var(--border); text-align: left; vertical-align: baseline; }
.table th { color: var(--muted); font-size: 0.82rem; font-weight: 500; }
.table .num { font-variant-numeric: tabular-nums; white-space: nowrap; }
.years { display: block; color: var(--muted-2); font-size: 0.8rem; }

.living { margin: 0 0 var(--s3); padding: 0; list-style: none; }
.living li { display: flex; justify-content: space-between; gap: var(--s4); padding: 8px 0; border-bottom: 1px solid var(--border); }
.living b { font-weight: 500; white-space: nowrap; }

.note { color: var(--muted); font-size: 0.875rem; }
.src { display: flex; flex-wrap: wrap; gap: var(--s1) var(--s4); color: var(--muted-2); font-size: 0.8rem; }
.src a { color: var(--brand); }
.placeholder { padding: var(--s6) var(--s4); border: 1px dashed var(--border-strong); border-radius: 12px; color: var(--muted); text-align: center; }

.qrs { display: flex; flex-wrap: wrap; gap: var(--s5); margin: var(--s4) 0; }
.qrs figure { margin: 0; text-align: center; }
.qrs img { display: block; margin: 0 auto var(--s2); border: 1px solid var(--border); border-radius: 8px; background: #fff; }
.qrs figcaption { font-size: 0.875rem; }
.copy {
  margin-left: 6px;
  padding: 2px 10px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-pill);
  background: none;
  color: var(--brand);
  font: inherit;
  font-size: 0.8rem;
  cursor: pointer;
}
.agent { padding: var(--s3) var(--s4); border-radius: 10px; background: var(--surface-2); }

@media (max-width: 520px) {
  .page { padding-top: var(--s4); }
  .ranks li { flex-direction: column; gap: 2px; }
  .table { font-size: 0.875rem; }
  .qrs { justify-content: center; }
}
</style>
