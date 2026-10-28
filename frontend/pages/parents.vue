<script setup lang="ts">
/**
 * A page for parents in China weighing Monash University Malaysia. Chinese
 * only, in a formal register, with no student vocabulary. Every official fact
 * links to the English page it came from.
 *
 * Tuition comes from the same /v1/fees table as /fees; the rest is in
 * data/parents.ts.
 */
import { MAMO_ACCOUNT, MAMO_POSTS } from '~/data/mamo'
import {
  DEGREE_SOURCE, ENGLISH_SOURCE, ENTRY_COURSES, ENTRY_ROWS, ENTRY_SOURCE, EXCHANGE, FEE_EXAMPLES, LIVING, MYR_TO_CNY,
  RANKINGS, RANKINGS_SOURCE, SCORE_METHOD_URL, SUBJECT_RANKING, TRANSFER, VISA
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

const score = (percent: number) => Math.round((750 * percent) / 100)

// The account's own posts on exchange, as further reading under the official programmes.
const exchangePosts = MAMO_POSTS.filter(p => p.topic === 'exchange' && p.url)
  .map(p => ({ ...p, title: p.title.replace(/^马莫百科[｜|]\s*/, '') }))

const MORE = [
  { to: '/courses', title: '专业与学位', text: '每个专业的课程结构、必修课和专业方向' },
  { to: '/fees', title: '马莫学费', text: '马来西亚校区全部专业的每年学费' },
  { to: '/guides', title: '官方指南', text: '学校官网上选课、考试、签证等规定的中文整理' },
  { to: '/mamo', title: '马莫百科', text: '在读学生写的入境报到、签证续签、海外交换等文章' }
]

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
const description = '莫纳什大学马来西亚校区的世界排名、学位证书、高考和国际课程录取要求、转澳洲校区、海外交换和每年费用，内容来自学校官网。'
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
        <a href="#transfer">转澳洲校区</a>
        <a href="#exchange">海外交换</a>
        <a href="#cost">费用</a>
        <a href="#more">更多</a>
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
      <p>
        学校接受多种高中学历直接申请本科，包括中国高考、A-Level、IB、AP 和美国高中等，每个专业有各自的分数线和单科要求。下表是中国学生读得最多的几个专业：
      </p>
      <div class="entry-wrap">
        <table class="entry">
          <thead>
            <tr>
              <th scope="col"><span class="visually-hidden">项目</span></th>
              <th v-for="c in ENTRY_COURSES" :key="c.code" scope="col">
                <span class="long">{{ c.name }}</span><span class="short">{{ c.short }}</span>
                <span class="code mono">{{ c.code }}</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="row">学制</th>
              <td v-for="c in ENTRY_COURSES" :key="c.code">{{ c.years }} 年</td>
            </tr>
            <tr>
              <th scope="row">入学月份</th>
              <td v-for="c in ENTRY_COURSES" :key="c.code">{{ c.intakes }}</td>
            </tr>
            <tr class="group">
              <th scope="row">高考总分</th>
              <td v-for="c in ENTRY_COURSES" :key="c.code">
                <b>{{ c.gaokao }}%</b><span class="sub"><span class="long">750 分制</span>约 {{ score(c.gaokao) }} 分</span>
              </td>
            </tr>
            <tr>
              <th scope="row">高考单科</th>
              <td v-for="c in ENTRY_COURSES" :key="c.code" class="text">{{ c.gaokaoSubjects }}</td>
            </tr>
            <tr v-for="(row, n) in ENTRY_ROWS" :key="row.key" :class="{ group: n === 0 }">
              <th scope="row">{{ row.label }}</th>
              <td v-for="c in ENTRY_COURSES" :key="c.code">{{ c.scores[row.key] }}</td>
            </tr>
            <tr class="group">
              <th scope="row">原文</th>
              <td v-for="c in ENTRY_COURSES" :key="c.code">
                <a :href="c.url" target="_blank" rel="noopener external"><span class="long">查看英文原文</span><span class="short">查看</span></a>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p class="note">
        高考按总分的百分比计算，上海（满分 660 分）、海南（满分 900 分）等省份按本省满分乘以同样的百分比。工程学士下设土木、化学、材料、电气与计算机、机械、机器人与机电、软件等方向，录取要求相同；生物医学工程只在 2 月入学。A-Level、AP、IB 的计分方法见官网计分说明。每年的要求可能调整，最新要求可以直接咨询。
      </p>
      <h3>先读预科再升本科</h3>
      <p>
        没有参加高考，或成绩未达到直接入读要求的学生，可以先在马来西亚校区读一年 Monash 大学预科（MUFY），按预科成绩升读本科。也有学生在其他院校读加拿大国际大学预科（CIMP），取得安大略省高中文凭（OSSD）后申请。两种预科各专业要求的成绩见上表。
      </p>
      <p>此外，所有申请人都需要达到英语要求，雅思等考试的具体分数见英文原文。</p>
      <p class="src">
        <a :href="ENTRY_SOURCE.url" target="_blank" rel="noopener external">查看英文原文（本科学术要求）</a>
        <a :href="SCORE_METHOD_URL" target="_blank" rel="noopener external">查看英文原文（计分说明）</a>
        <a :href="ENGLISH_SOURCE.url" target="_blank" rel="noopener external">查看英文原文（英语要求）</a>
        <span>核对于 {{ ENTRY_SOURCE.checked }}</span>
      </p>
    </section>

    <section id="transfer" class="block">
      <h2>转到澳洲校区</h2>
      <p>
        在读本科生在完成学业前，可以申请转到澳洲的校区，继续读同类学位。各学院对已修学分和平均成绩有各自的要求，由澳洲校区的学院审批。毕业证书同样由莫纳什大学颁发。
      </p>
      <p class="src">
        <a :href="TRANSFER.url" target="_blank" rel="noopener external">查看英文原文（Internal Course Transfer）</a>
        <a :href="TRANSFER.rulesUrl" target="_blank" rel="noopener external">查看英文原文（转校区条件）</a>
        <span>核对于 {{ TRANSFER.checked }}</span>
      </p>
    </section>

    <section id="exchange" class="block">
      <h2>海外交换</h2>
      <p>不转校区的学生，也可以通过以下项目到海外学习一段时间：</p>
      <ul class="programs">
        <li v-for="p in EXCHANGE.programs" :key="p.name">
          <h3>{{ p.name }}</h3>
          <p>{{ p.text }}</p>
          <a :href="p.url" class="src-link" target="_blank" rel="noopener external">查看英文原文</a>
        </li>
      </ul>
      <p class="src"><span>核对于 {{ EXCHANGE.checked }}</span></p>
      <div v-if="exchangePosts.length" class="reading">
        <p class="reading-title">马莫百科写过的交换经历和申请指南：</p>
        <ul>
          <li v-for="p in exchangePosts" :key="p.url">
            <a :href="p.url" target="_blank" rel="noopener external">{{ p.title }}</a>
          </li>
        </ul>
      </div>
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

    <section id="more" class="block">
      <h2>想进一步了解</h2>
      <ul class="more">
        <li v-for="m in MORE" :key="m.to">
          <NuxtLink :to="m.to">
            <b>{{ m.title }}</b>
            <span>{{ m.text }}</span>
          </NuxtLink>
        </li>
      </ul>
    </section>

    <MamoIntro zh class="mamo-block" />

    <section id="contact" class="block">
      <h2>咨询</h2>
      <div class="wechat">
        <img src="/img/mamo/qr-wechat.png" alt="作者微信二维码" width="132" height="132" loading="lazy">
        <div>
          <p>作者是马来西亚校区在读学生，也是莫纳什大学马来西亚校区的授权招生代理。申请和入学的各类问题都可以添加微信咨询。</p>
          <p class="id">
            微信号：<span class="mono">{{ MAMO_ACCOUNT.wechatId }}</span>
            <button type="button" class="copy" @click="copyId">{{ copied ? '已复制' : '复制' }}</button>
          </p>
        </div>
      </div>
      <p class="agent">
        通过作者以学校授权代理渠道办理申请，从选专业、整理材料、递交申请、办理学生签证，到入学报到和在校指引，全程协助，不收取中介费、手续费和押金。
      </p>
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

.entry-wrap { margin: var(--s4) 0; overflow-x: auto; }
.entry { width: 100%; table-layout: fixed; border-collapse: collapse; font-size: 0.9rem; font-variant-numeric: tabular-nums; }
.entry thead th:first-child { width: 7.5em; }
.entry th, .entry td { padding: 8px 6px; border-bottom: 1px solid var(--border); text-align: center; vertical-align: top; }
.entry thead th { padding-bottom: 10px; border-bottom: 1px solid var(--ink); font-weight: 600; line-height: 1.4; }
.entry th { font-size: inherit; letter-spacing: normal; text-transform: none; }
.entry tbody th { color: var(--muted); font-weight: 400; text-align: left; white-space: nowrap; }
.entry .short { display: none; }
.entry .code { display: block; color: var(--muted-2); font-size: 0.75rem; font-weight: 400; }
.entry .sub { display: block; color: var(--muted-2); font-size: 0.75rem; }
.entry td.text { font-size: 0.82rem; line-height: 1.5; }
.entry tr.group th, .entry tr.group td { padding-top: 14px; }
.entry a { color: var(--brand); font-size: 0.78rem; }
.src-link { color: var(--brand); font-size: 0.8rem; }

.programs { margin: 0 0 var(--s3); padding: 0; list-style: none; }
.programs li { padding: var(--s3) 0; border-bottom: 1px solid var(--border); }
.programs h3 { margin: 0 0 var(--s1); font-size: 1rem; }
.programs p { margin: 0 0 var(--s1); }
.reading { margin-top: var(--s4); padding: var(--s4); border-radius: 10px; background: var(--surface-2); }
.reading-title { margin: 0 0 var(--s2) !important; font-weight: 500; }
.reading ul { margin: 0; padding-left: 1.2em; }
.reading li { margin: 4px 0; line-height: 1.6; }
.reading a { color: var(--brand); }

.note { color: var(--muted); font-size: 0.875rem; }
.src { display: flex; flex-wrap: wrap; gap: var(--s1) var(--s4); color: var(--muted-2); font-size: 0.8rem; }
.src a { color: var(--brand); }
.placeholder { padding: var(--s6) var(--s4); border: 1px dashed var(--border-strong); border-radius: 12px; color: var(--muted); text-align: center; }

.more { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--s3); margin: 0; padding: 0; list-style: none; }
.more a {
  display: grid;
  gap: 4px;
  height: 100%;
  padding: var(--s4);
  border: 1px solid var(--border);
  border-radius: 12px;
  background: var(--surface);
  color: inherit;
}
.more a:hover { border-color: var(--brand); text-decoration: none; }
.more a:hover b { color: var(--brand); }
.more span { color: var(--muted); font-size: 0.875rem; line-height: 1.6; }
.mamo-block { margin-block: var(--s6); }
.wechat { display: grid; grid-template-columns: auto minmax(0, 1fr); gap: var(--s4); align-items: center; margin: 0 0 var(--s4); }
.wechat img { border: 1px solid var(--border); border-radius: 8px; background: #fff; }
.wechat p { margin: 0 0 var(--s2); }
.id { font-size: 0.9rem; }
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
  .entry { font-size: 0.8rem; }
  .entry th, .entry td { padding: 7px 3px; }
  .entry thead th:first-child { width: 6.4em; }
  .entry thead th { white-space: normal; }
  .entry td.text { font-size: 0.75rem; }
  .entry .long { display: none; }
  .entry .short { display: inline; }
}
@media (max-width: 520px) {
  .page { padding-top: var(--s4); }
  .ranks li { flex-direction: column; gap: 2px; }
  .table { font-size: 0.875rem; }
  .more { grid-template-columns: 1fr; }
  .wechat img { width: 112px; height: 112px; }
}
</style>
