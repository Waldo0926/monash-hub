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
  ABOUT, CAMPUS, CSCSE_URL, DEGREE_FAQ_URL, DEGREE_SOURCE, DIPLOMA, ENGLISH_SOURCE, ENTRY_COLUMNS, ENTRY_SCHOOLS,
  ENTRY_SOURCE, EXCHANGE, FEE_EXAMPLES, LIVING, MUFY, MYR_TO_CNY, PARENTS_INFO, RANKINGS, RANKINGS_SOURCE,
  SCHOLARSHIP, SCORE_METHOD_URL, SETARA_SOURCE, SST, SUBJECT_RANKINGS, TRANSFER, VISA
} from '~/data/parents'
import type { FeeRow } from '~/utils/tuition'

const config = useRuntimeConfig()
const site = config.public.siteUrl.replace(/\/$/, '')

type Table = { year: number | null; sections: { source: string; schools: { rows: FeeRow[] }[] }[] }
const { data: fees } = await useApiFetch<Table>('/v1/fees')

const norm = (s: string) => s.trim().toLowerCase()
const ugRows = computed(() => (fees.value?.sections ?? [])
  .filter(s => s.source === 'malaysia-ugfees')
  .flatMap(s => s.schools.flatMap(g => g.rows)))
const findFeeRow = (match: string) => match
  ? ugRows.value.find(r => norm(r.title) === norm(match) || r.covers.some(c => norm(c) === norm(match)))
  : undefined
const feeRows = computed(() => {
  return FEE_EXAMPLES.flatMap(({ label, match }) => {
    const row = findFeeRow(match)
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
const feeYear = computed(() => fees.value?.year ?? 2027)

// The table scrolls both ways inside its own box. Parents did not see that
// there was more to the right (A-Level, IB and the rest) or further down, so
// each edge with more behind it gets a fade and a button, and the hint above
// names only the directions that actually scroll.
const entryWrap = ref<HTMLElement | null>(null)
const entryMore = reactive({ right: false, down: false })
const entryWide = ref(false)
const entryTall = ref(false)
let entryObserver: ResizeObserver | null = null
const checkEntryScroll = () => {
  const el = entryWrap.value
  if (!el) return
  entryWide.value = el.scrollWidth > el.clientWidth + 1
  entryTall.value = el.scrollHeight > el.clientHeight + 1
  entryMore.right = el.scrollLeft + el.clientWidth < el.scrollWidth - 1
  entryMore.down = el.scrollTop + el.clientHeight < el.scrollHeight - 1
}
const entryHint = computed(() => {
  if (entryWide.value && entryTall.value) return '表格可以上下、左右滑动：往右看 A-Level、IB 等其他学历的要求，往下看更多专业'
  if (entryWide.value) return '表格可以左右滑动：往右看 A-Level、IB 等其他学历的要求'
  if (entryTall.value) return '表格可以上下滑动，往下看更多专业'
  return ''
})
const scrollEntry = (dx: number, dy: number) => {
  const el = entryWrap.value
  el?.scrollBy({ left: dx * el.clientWidth * 0.7, top: dy * el.clientHeight * 0.7, behavior: 'smooth' })
}

// Jump straight to the column for the child's qualification, scrolled to
// sit just right of the frozen course names.
const activeCol = ref('gaokao')
const jumpToCol = (key: string) => {
  const el = entryWrap.value
  const th = el?.querySelector<HTMLElement>(`thead th[data-col="${key}"]`)
  const frozen = el?.querySelector<HTMLElement>('thead th.sticky')
  if (!el || !th || !frozen) return
  activeCol.value = key
  const offset = th.getBoundingClientRect().left - el.getBoundingClientRect().left
  el.scrollTo({ left: el.scrollLeft + offset - frozen.offsetWidth, behavior: 'smooth' })
}

onMounted(() => {
  checkEntryScroll()
  if (entryWrap.value && 'ResizeObserver' in window) {
    entryObserver = new ResizeObserver(checkEntryScroll)
    entryObserver.observe(entryWrap.value)
  }
})
onBeforeUnmount(() => entryObserver?.disconnect())
// The live /fees table first, so the page moves with it; the typed 2027
// figure only when the API cannot be read.
const courseFee = (match: string, fallback: number | string) => {
  const live = findFeeRow(match)?.international[0]?.value
  const n = live ?? fallback
  return typeof n === 'number' ? group(n) : n
}
const withTax = (n: number) => n * (1 + SST.rate)
const taxPercent = Math.round(SST.rate * 100)

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
const description = '莫纳什大学马来西亚校区的学校概况、世界排名、学位证书、高考和国际课程录取要求、奖学金、转澳大利亚校区、海外交换、每年费用和校园生活，内容来自学校官网'
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
        莫纳什大学（Monash University）是澳大利亚八校联盟成员，总部在墨尔本，马来西亚校区位于吉隆坡附近的双威城
      </p>
      <p class="lead">
        以下内容整理自学校官网，每一项下面都附有英文原文链接
      </p>
      <nav class="toc" aria-label="本页目录">
        <a href="#about">学校概况</a>
        <a href="#rankings">学校排名</a>
        <a href="#degree">毕业证书</a>
        <a href="#entry">录取要求</a>
        <a href="#scholarship">奖学金</a>
        <a href="#transfer">转澳大利亚校区</a>
        <a href="#exchange">海外交换</a>
        <a href="#cost">费用</a>
        <a href="#campus">校园生活</a>
        <a href="#parents-note">家长须知</a>
        <a href="#contact">咨询</a>
      </nav>
    </header>

    <section id="about" class="block">
      <h2>学校概况</h2>
      <p>
        马来西亚校区建于 1998 年，是马来西亚第一个外国大学校区，也是莫纳什大学第三大的校区
      </p>
      <p>
        莫纳什大学在澳大利亚有四个校区，另外在马来西亚、印度尼西亚、中国和印度设有校区，在意大利 Prato 设有教学中心
      </p>
      <ul class="facts">
        <li v-for="f in ABOUT.facts" :key="f.label"><span>{{ f.label }}</span><b>{{ f.value }}</b></li>
      </ul>
      <p>
        马来西亚校区有自行审核课程的资格
      </p>
      <p>
        在马来西亚高等教育部的 SETARA 大学评级中，学校获评 Competitive（Berdaya Saing），是这项评级的最高一级
      </p>
      <p class="src">
        <a :href="ABOUT.url" target="_blank" rel="noopener external">查看英文原文（校区介绍）</a>
        <a :href="SETARA_SOURCE.url" target="_blank" rel="noopener external">查看英文原文（SETARA 评级）</a>
        <span>核对于 {{ ABOUT.checked }}</span>
      </p>
    </section>

    <section id="rankings" class="block">
      <h2>学校排名</h2>
      <ul class="ranks">
        <li v-for="r in RANKINGS" :key="r.name">
          <span class="rank-name">{{ r.name }} {{ r.year }}</span>
          <b>{{ r.place }}</b>
        </li>
      </ul>
      <h3>学科排名</h3>
      <p>下面是排进世界前 30、马来西亚校区也开设的学科：</p>
      <ul class="ranks">
        <li v-for="r in SUBJECT_RANKINGS" :key="r.name">
          <span class="rank-name">{{ r.name }} {{ r.year }}</span>
          <b>{{ r.place }}</b>
        </li>
      </ul>
      <p class="note">排名是莫纳什大学整体的排名，各校区共用</p>
      <p class="src">
        <a :href="RANKINGS_SOURCE.url" target="_blank" rel="noopener external">查看英文原文</a>
        <span>核对于 {{ RANKINGS_SOURCE.checked }}</span>
      </p>
    </section>

    <section id="degree" class="block">
      <h2>毕业证书</h2>
      <p>
        不论在哪个校区完成学业，毕业证书都由莫纳什大学颁发，与澳大利亚校区的毕业生相同
      </p>
      <p>
        所有校区执行同一套教学质量标准，由学校的学术委员会统一监督
      </p>
      <p>
        证书上写的是 Monash University，不写 Monash University Malaysia
      </p>
      <p>
        学位由澳大利亚高等教育质量与标准署（TEQSA）做质量保证，同时获得马来西亚学术资格鉴定机构（MQA）认可
      </p>
      <p>
        回国后办理国（境）外学历学位认证，所需材料和流程以<a :href="CSCSE_URL" target="_blank" rel="noopener external">中国留学服务中心</a>官网为准
      </p>
      <p class="src">
        <a :href="DEGREE_SOURCE.url" target="_blank" rel="noopener external">查看英文原文（校区介绍）</a>
        <a :href="DEGREE_FAQ_URL" target="_blank" rel="noopener external">查看英文原文（常见问题）</a>
        <span>核对于 {{ DEGREE_SOURCE.checked }}</span>
      </p>
    </section>

    <section id="entry" class="block">
      <h2>录取要求</h2>
      <p>
        学校接受多种高中学历直接申请本科，包括中国高考、A-Level、IB、AP、香港 DSE 和美国高中等，每个专业有各自的分数线和单科要求
      </p>
      <p>
        下表列出马来西亚校区全部本科专业，可以先对照孩子的成绩，看看能选哪些专业
      </p>
      <div class="entry-frame">
        <div class="entry-jump">
          <span class="entry-jump-label">按孩子的学历查看</span>
          <button
            v-for="col in [{ key: 'gaokao', label: '高考' }, ...ENTRY_COLUMNS]"
            :key="col.key"
            type="button"
            :class="{ on: activeCol === col.key }"
            @click="jumpToCol(col.key)"
          >
            {{ col.label }}
          </button>
        </div>
        <p v-if="entryHint" class="swipe-hint">{{ entryHint }}</p>
        <div class="entry-box">
          <div
            ref="entryWrap"
            class="entry-wrap"
            role="region"
            aria-label="各专业录取要求"
            tabindex="0"
            @scroll.passive="checkEntryScroll"
          >
            <table class="entry">
              <thead>
                <tr>
                  <th scope="col" class="sticky">专业</th>
                  <th scope="col">年限</th>
                  <th scope="col">开课月份</th>
                  <th scope="col">年学费<span class="sub">{{ feeYear }} 年，马币</span></th>
                  <th scope="col" class="gaokao" data-col="gaokao" :class="{ on: activeCol === 'gaokao' }">
                    高考<span class="sub">括号内为单科要求</span>
                  </th>
                  <th v-for="col in ENTRY_COLUMNS" :key="col.key" scope="col" :data-col="col.key" :class="{ on: activeCol === col.key }">
                    {{ col.label }}<span v-if="col.sub" class="sub">{{ col.sub }}</span>
                  </th>
                </tr>
              </thead>
              <tbody v-for="g in ENTRY_SCHOOLS" :key="g.school">
                <tr class="school">
                  <th scope="rowgroup" class="sticky">{{ g.school }}</th>
                  <td :colspan="4 + ENTRY_COLUMNS.length" />
                </tr>
                <tr v-for="c in g.courses" :key="c.name">
                  <th scope="row" class="sticky">{{ c.name }}</th>
                  <td>{{ c.years }} 年</td>
                  <td>{{ c.intakes }}</td>
                  <td class="num">{{ courseFee(c.match, c.fee) }}</td>
                  <td class="gaokao">
                    <template v-if="c.gaokao != null">
                      <b>{{ c.gaokao }}%</b><span v-if="c.gaokaoSubjects">（{{ c.gaokaoSubjects }}）</span>
                      <span class="sub">750 分制约 {{ score(c.gaokao) }} 分</span>
                    </template>
                    <template v-else>/</template>
                  </td>
                  <td v-for="col in ENTRY_COLUMNS" :key="col.key">{{ c.scores[col.key] }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <span class="edge edge-right" :class="{ show: entryMore.right }" aria-hidden="true" />
          <span class="edge edge-bottom" :class="{ show: entryMore.down }" aria-hidden="true" />
          <button
            v-show="entryMore.right"
            type="button"
            class="nudge nudge-right"
            aria-label="向右滑动表格，查看其他学历的要求"
            @click="scrollEntry(1, 0)"
          >
            →
          </button>
          <button
            v-show="entryMore.down"
            type="button"
            class="nudge-down"
            @click="scrollEntry(0, 1)"
          >
            往下还有更多专业 ↓
          </button>
        </div>
      </div>
      <ul class="note-list">
        <li>高考按总分的百分比计算，上海（满分 660 分）、海南（满分 900 分）等省份按本省满分乘以同样的百分比</li>
        <li>学费是国际学生每年的学费，另加 6% 服务税</li>
        <li>表中是斜杠的项目可以直接咨询</li>
        <li>每年的要求可能调整，以学校最新公布为准</li>
      </ul>
      <p class="entry-links">
        <NuxtLink to="/courses">看各专业的课程介绍 →</NuxtLink>
        <NuxtLink to="/fees">看全部专业学费 →</NuxtLink>
      </p>
      <p>此外，所有申请人都需要达到英语要求，雅思等考试的具体分数见英文原文</p>
      <p class="src">
        <a :href="ENTRY_SOURCE.url" target="_blank" rel="noopener external">查看英文原文（本科学术要求）</a>
        <a :href="SCORE_METHOD_URL" target="_blank" rel="noopener external">查看英文原文（计分说明）</a>
        <a :href="ENGLISH_SOURCE.url" target="_blank" rel="noopener external">查看英文原文（英语要求）</a>
        <span>核对于 {{ ENTRY_SOURCE.checked }}</span>
      </p>

      <h3>没有高考成绩或分数不够时</h3>
      <ul class="programs">
        <li>
          <h4>Monash 大学预科（MUFY）</h4>
          <p>
            由学校选定的院校开设，马来西亚境内在双威学院（Sunway College）吉隆坡和新山两个校区，中国境内在成都也有开设点
          </p>
          <p>
            课程相当于澳大利亚 12 年级，一般分两个学期，9 到 11 个月读完，按预科成绩升读本科，各专业要求的预科成绩见上表
          </p>
          <a :href="MUFY.url" class="src-link" target="_blank" rel="noopener external">查看英文原文</a>
        </li>
        <li>
          <h4>高等教育文凭（Diploma of Higher Education Studies）</h4>
          <p>
            在马来西亚校区读一年，修读本科一年级的课程，成绩达到要求后进入对应本科专业的二年级，可选的方向在文科与社会科学、商科、信息技术和理科四个学院，工程不在其中
          </p>
          <p>
            高考要求为总分的 {{ DIPLOMA.gaokao }}%，{{ DIPLOMA.fees.year }} 年国际学生学费每年 {{ rm(DIPLOMA.fees.nonScience) }}，理科方向 {{ rm(DIPLOMA.fees.science) }}
          </p>
          <a :href="DIPLOMA.url" class="src-link" target="_blank" rel="noopener external">查看英文原文</a>
        </li>
      </ul>
      <p>也有学生在其他院校读加拿大国际大学预科（CIMP），取得安大略省高中文凭（OSSD）后申请，各专业要求的成绩同样见上表</p>
      <p class="src"><span>核对于 {{ MUFY.checked }}</span></p>
    </section>

    <section id="scholarship" class="block">
      <h2>奖学金</h2>
      <p>
        国际新生可以申请的本科奖学金主要有下面几项，前两项不用单独申请，学校审核入学申请时会一起评估，符合条件的会在录取通知书里一并告知
      </p>
      <ul class="programs">
        <li>
          <h3>Monash High Achiever Award</h3>
          <p>面向高中成绩优秀的新生，每年减免学费 RM10,000，分两个学期各减 RM5,000，医学和药学专业不适用</p>
        </li>
        <li>
          <h3>Female in Engineering Scholarship</h3>
          <p>面向读工程学士的女生，第一年减免学费 RM6,000，每个入学批次名额有限，2 月和 7 月各 7 名，10 月 6 名</p>
        </li>
        <li>
          <h3>Monash Pharmacy Excellence Scholarship</h3>
          <p>面向药学学士（荣誉）新生，四年学费减免 50% 或 25%，这一项要另外申请，每年 1 月 31 日截止</p>
        </li>
      </ul>
      <p>
        入学后成绩优秀的学生，还可以获得在读生版的 Monash High Achiever Award，条件是连续读满两个学期、平均分 80 分以上，并且排在所在学院的前 1%，每学期由学校自动提名
      </p>
      <p>
        拿到奖学金后，要保持录取通知书里写明的成绩要求，每学期修满 24 学分，按正常年限毕业，期间不能再领取其他资助，才能继续享受减免
      </p>
      <p>
        奖学金减免的部分照样按全额学费计算 {{ taxPercent }}% 服务税，详见下方费用部分
      </p>
      <p class="src">
        <a :href="SCHOLARSHIP.url" target="_blank" rel="noopener external">查看英文原文</a>
        <span>核对于 {{ SCHOLARSHIP.checked }}</span>
      </p>
    </section>

    <section id="transfer" class="block">
      <h2>转到澳大利亚校区</h2>
      <p>
        在读本科生在马来西亚校区读满至少一年后，可以申请转到澳大利亚的校区，继续读同类学位，各学院对已修学分和平均成绩有各自的要求，由澳大利亚校区的学院审批，毕业证书同样由莫纳什大学颁发
      </p>
      <p>
        转过去以后就成为澳大利亚校区的学生，学费和其他费用改按澳大利亚校区转入当年的标准，用澳元缴纳
      </p>
      <p>
        先去交换再申请转校区的，也从转入那年开始按澳大利亚的标准交费
      </p>
      <table class="table compare">
        <thead>
          <tr><th scope="col"><span class="visually-hidden">对比项</span></th><th scope="col">去澳大利亚交换</th><th scope="col">转到澳大利亚校区</th></tr>
        </thead>
        <tbody>
          <tr><th scope="row">学籍</th><td>仍是马来西亚校区学生</td><td>转为澳大利亚校区学生</td></tr>
          <tr><th scope="row">学费</th><td>按马币缴纳</td><td>按澳元缴纳</td></tr>
          <tr><th scope="row">毕业</th><td>一般回马来西亚校区读完最后一个学期</td><td>在澳大利亚读完</td></tr>
        </tbody>
      </table>
      <p class="src">
        <a :href="TRANSFER.url" target="_blank" rel="noopener external">查看英文原文（Internal Course Transfer）</a>
        <a :href="TRANSFER.rulesUrl" target="_blank" rel="noopener external">查看英文原文（转校区条件）</a>
        <a :href="PARENTS_INFO.url" target="_blank" rel="noopener external">查看英文原文（家长常见问题）</a>
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
        <p class="reading-title">微信公众号「马莫百科」写过的交换经历和申请指南：</p>
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
          <tr><th>专业</th><th>每年学费</th><th>加 {{ taxPercent }}% 服务税</th><th>折合人民币</th></tr>
        </thead>
        <tbody>
          <tr v-for="f in feeRows" :key="f.label">
            <td>{{ f.label }}<span v-if="f.years" class="years">{{ f.years }} 年制</span></td>
            <td class="num">{{ rm(f.amount) }}</td>
            <td class="num">{{ rm(withTax(f.amount)) }}</td>
            <td class="num">{{ cny(withTax(f.amount)) }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="note">学费数据暂时无法读取，请查看各专业学费页</p>
      <ul class="note-list">
        <li>以上为{{ fees?.year ? ` ${fees.year} 年` : '' }}国际学生学费</li>
        <li>2025 年 7 月 1 日起，马来西亚政府对国际学生的学费、报名费、注册费等教育相关费用征收 {{ taxPercent }}% 服务税，由学校代收，学生签证和保险不收</li>
        <li>人民币按加税后的金额、以 1 马币兑 {{ MYR_TO_CNY }} 人民币换算，具体以当天汇率为准</li>
        <li><NuxtLink to="/fees">看全部专业的学费 →</NuxtLink></li>
      </ul>
      <p class="src">
        <a :href="SST.url" target="_blank" rel="noopener external">查看英文原文（服务税）</a>
        <span>核对于 {{ SST.checked }}</span>
      </p>

      <h3>学生签证</h3>
      <p>
        新生办理马来西亚学生签证，费用约 {{ rm(VISA.amount) }}（{{ cnyPlain(VISA.amount) }}），有效期 {{ VISA.months }} 个月
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
      <p class="note">官网说明以上均为估算，实际花费与住宿选择和个人习惯有关</p>
      <p class="src">
        <a :href="LIVING.url" target="_blank" rel="noopener external">查看英文原文</a>
        <span>核对于 {{ LIVING.checked }}</span>
      </p>
    </section>

    <section id="campus" class="block">
      <h2>校园与生活</h2>
      <p>
        校园里有餐厅和食堂、健身房和室外游泳池，学生社团经常办市集、比赛、文化节和音乐节，学校所在的双威城有商场和休闲场所，走路就能到
      </p>
      <h3>住宿</h3>
      <p>
        学校附近有多处走路可到的学生公寓，其中由双威集团管理的有 {{ CAMPUS.residences.join('、') }}，可以选单人间或合住，在双威的住宿管理处（Sunway House）申请
      </p>
      <p>
        学校官网说明，列出的住宿仅供参考，学校不对房源作担保，房租等生活费见上方费用部分
      </p>
      <h3>健康与保险</h3>
      <p>
        校内健康中心有注册护士，周一至周五 8:30 到 17:30 开放，可以处理小病小伤，也能做急救
      </p>
      <p>
        学校还有专业的心理咨询师，咨询服务免费并且保密
      </p>
      <p>
        所有学生都在学校统一投保的团体意外险范围内，持学生签证的国际学生另有学校指定的医疗保险
      </p>
      <h3>校园安全</h3>
      <p>学校有自己的保安团队，紧急求助电话 <span class="mono">{{ CAMPUS.securityHotline }}</span></p>
      <p class="src">
        <a :href="CAMPUS.welcomeUrl" target="_blank" rel="noopener external">查看英文原文（校园）</a>
        <a :href="CAMPUS.housingUrl" target="_blank" rel="noopener external">查看英文原文（住宿）</a>
        <a :href="CAMPUS.healthUrl" target="_blank" rel="noopener external">查看英文原文（健康中心）</a>
        <a :href="CAMPUS.insuranceUrl" target="_blank" rel="noopener external">查看英文原文（保险）</a>
        <a :href="CAMPUS.securityUrl" target="_blank" rel="noopener external">查看英文原文（校园安全）</a>
        <span>核对于 {{ CAMPUS.checked }}</span>
      </p>
    </section>

    <section id="parents-note" class="block">
      <h2>家长须知</h2>
      <p>
        根据马来西亚《2010 年个人资料保护法》，未经学生本人同意，学校不能向任何第三方透露学生的信息，家长也包括在内
      </p>
      <p>
        家长如果想直接向学校了解孩子的学业进度，需要孩子提交一份个人信息披露授权（Authorisation to Release Personal Information），授权范围限于学业进度、代领成绩单和学校信件，以及学费明细
      </p>
      <p>
        这些信息也可以直接问孩子
      </p>
      <p>
        遇到紧急情况，学校会联系学生登记的紧急联系人
      </p>
      <p class="src">
        <a :href="PARENTS_INFO.url" target="_blank" rel="noopener external">查看英文原文</a>
        <span>核对于 {{ PARENTS_INFO.checked }}</span>
      </p>
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

    <MamoIntro parents class="mamo-block" />

    <section id="contact" class="block">
      <h2>咨询</h2>
      <div class="wechat">
        <img src="/img/mamo/qr-wechat.png" alt="作者微信二维码" width="132" height="132" loading="lazy">
        <div>
          <p>作者是马来西亚校区在读学生，也是莫纳什大学马来西亚校区的授权招生代理，申请和入学的各类问题都可以添加微信咨询</p>
          <p class="id">
            微信号：<span class="mono">{{ MAMO_ACCOUNT.wechatId }}</span>
            <button type="button" class="copy" @click="copyId">{{ copied ? '已复制' : '复制' }}</button>
          </p>
        </div>
      </div>
      <p class="agent">
        通过作者以学校授权代理渠道办理申请，从选专业、整理材料、递交申请、办理学生签证，到入学报到和在校指引，全程协助，不收取中介费、手续费和押金
      </p>
    </section>
  </div>
</template>

<style scoped>
/* As wide as the entry table needs, so the table and the text around it
   share one edge instead of the table jutting out of a narrow column. */
.page { max-width: 1240px; margin: 0 auto; padding: var(--s6) var(--s5) var(--s8); }
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

/* Lists that were full-width rows in the narrow column are cards on the
   wide page, so a label and its figure never sit a screen apart. */
.ranks { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: var(--s3); margin: 0 0 var(--s4); padding: 0; list-style: none; }
.ranks li { display: grid; gap: 4px; align-content: start; padding: var(--s3) var(--s4); border-radius: 10px; background: var(--surface-2); }
.rank-name { color: var(--muted); font-size: 0.875rem; line-height: 1.5; }
.ranks b { color: var(--brand-700); font-size: 1.2rem; white-space: nowrap; }

.table { width: 100%; margin: 0 0 var(--s3); border-collapse: collapse; font-size: 0.95rem; }
.table th, .table td { padding: 10px 8px 10px 0; border-bottom: 1px solid var(--border); text-align: left; vertical-align: baseline; }
.table th { color: var(--muted); font-size: 0.82rem; font-weight: 500; }
.table .num { font-variant-numeric: tabular-nums; white-space: nowrap; }
.years { display: block; color: var(--muted-2); font-size: 0.8rem; }

.living { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(280px, 100%), 1fr)); column-gap: var(--s6); margin: 0 0 var(--s3); padding: 0; list-style: none; }
.living li { display: flex; justify-content: space-between; gap: var(--s4); padding: 8px 0; border-bottom: 1px solid var(--border); }
.living b { font-weight: 500; white-space: nowrap; }

.entry-frame { margin: var(--s4) 0; }
.entry-jump { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin-bottom: var(--s3); }
.entry-jump-label { margin-right: 4px; color: var(--text); font-size: 0.875rem; font-weight: 500; }
.entry-jump button {
  padding: 3px 11px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-pill);
  background: var(--surface);
  color: var(--text);
  font: inherit;
  font-size: 0.8rem;
  cursor: pointer;
}
.entry-jump button:hover { border-color: var(--brand); color: var(--brand); }
.entry-jump button.on { border-color: var(--brand); background: var(--brand); color: #fff; }
.swipe-hint {
  margin: 0 0 var(--s2) !important;
  padding: 8px 12px;
  border-left: 3px solid var(--brand);
  border-radius: 6px;
  background: var(--blue-50);
  color: var(--brand-700);
  font-size: 0.9rem;
  font-weight: 500;
  line-height: 1.6 !important;
}
.entry-box { position: relative; }
.entry-wrap {
  max-height: 72vh;
  overflow: auto;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--surface);
  -webkit-overflow-scrolling: touch;
}
/* Fades over the edges that have more behind them, inside the border. */
.edge { position: absolute; z-index: 4; pointer-events: none; opacity: 0; transition: opacity 0.2s; }
.edge.show { opacity: 1; }
.edge-right { top: 1px; right: 1px; bottom: 1px; width: 56px; border-radius: 0 10px 10px 0; background: linear-gradient(to right, rgb(255 255 255 / 0), rgb(255 255 255 / 0.95)); }
.edge-bottom { right: 1px; bottom: 1px; left: 1px; height: 56px; border-radius: 0 0 10px 10px; background: linear-gradient(to bottom, rgb(255 255 255 / 0), rgb(255 255 255 / 0.95)); }
.nudge {
  position: absolute;
  top: 50%;
  z-index: 5;
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border: 0;
  border-radius: 50%;
  background: var(--brand);
  box-shadow: 0 2px 8px rgb(0 0 0 / 0.18);
  color: #fff;
  font-size: 1.1rem;
  cursor: pointer;
  transform: translateY(-50%);
}
.nudge-right { right: 8px; animation: nudge 1.6s ease-in-out 3; }
.nudge-down {
  position: absolute;
  bottom: 10px;
  left: 50%;
  z-index: 5;
  padding: 5px 14px;
  border: 0;
  border-radius: var(--radius-pill);
  background: var(--brand);
  box-shadow: 0 2px 8px rgb(0 0 0 / 0.18);
  color: #fff;
  font: inherit;
  font-size: 0.8rem;
  cursor: pointer;
  transform: translateX(-50%);
}
@keyframes nudge { 50% { transform: translate(5px, -50%); } }
@media (prefers-reduced-motion: reduce) { .nudge-right { animation: none; } }
.entry-wrap:focus-visible { outline: 2px solid var(--brand); outline-offset: 2px; }
.entry { width: max-content; min-width: 100%; border-collapse: separate; border-spacing: 0; font-size: 0.85rem; font-variant-numeric: tabular-nums; }
.entry th, .entry td { padding: 8px 10px; border-bottom: 1px solid var(--border); text-align: center; white-space: nowrap; vertical-align: top; }
.entry th { font-size: inherit; letter-spacing: normal; text-transform: none; }
.entry thead th {
  position: sticky;
  top: 0;
  z-index: 2;
  background: var(--surface-2);
  border-bottom: 1px solid var(--border-strong);
  font-weight: 600;
  line-height: 1.35;
}
.entry .sticky { position: sticky; left: 0; z-index: 1; background: var(--surface); text-align: left; box-shadow: 1px 0 0 var(--border); }
.entry thead .sticky { z-index: 3; background: var(--surface-2); }
.entry tbody th.sticky { min-width: 13em; max-width: 16em; white-space: normal; font-weight: 500; }
.entry .sub { display: block; color: var(--muted-2); font-size: 0.72rem; font-weight: 400; }
.entry .gaokao { min-width: 14em; white-space: normal; line-height: 1.5; text-align: left; }
.entry .num { text-align: right; }
.entry thead th.on { background: var(--blue-50); color: var(--brand-700); box-shadow: inset 0 -2px 0 var(--brand); }
.entry tr.school th, .entry tr.school td { padding-top: 12px; background: var(--surface); color: var(--brand); font-weight: 600; }
.entry-links { display: flex; flex-wrap: wrap; gap: var(--s2) var(--s4); }
.entry-links a { color: var(--brand); font-weight: 500; }
.src-link { color: var(--brand); font-size: 0.8rem; }

.programs { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(300px, 100%), 1fr)); gap: var(--s3); margin: 0 0 var(--s4); padding: 0; list-style: none; }
/* Four cards go two by two rather than three and a lone one. */
.programs:has(> li:nth-child(4):last-child) { grid-template-columns: repeat(auto-fit, minmax(min(420px, 100%), 1fr)); }
.programs li { display: flex; flex-direction: column; padding: var(--s4) var(--s5); border: 1px solid var(--border); border-radius: 12px; background: var(--surface); }
.programs h3, .programs h4 { margin: 0 0 var(--s2); font-size: 1rem; line-height: 1.5; }
.programs .src-link { margin-top: auto; padding-top: var(--s2); }
.programs p { margin: 0 0 var(--s1); }
.reading { margin-top: var(--s4); padding: var(--s4); border-radius: 10px; background: var(--surface-2); }
.reading-title { margin: 0 0 var(--s2) !important; font-weight: 500; }
.reading ul { margin: 0; padding-left: 1.2em; }
.reading li { margin: 4px 0; line-height: 1.6; }
.reading a { color: var(--brand); }

.note { color: var(--muted); font-size: 0.875rem; }
.note-list { margin: 0 0 var(--s3); padding-left: 1.2em; color: var(--muted); font-size: 0.875rem; line-height: 1.7; }
.note-list a { color: var(--brand); }
.src { display: flex; flex-wrap: wrap; gap: var(--s1) var(--s4); color: var(--muted-2); font-size: 0.8rem; }
.src a { color: var(--brand); }
.facts { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: var(--s3); margin: 0 0 var(--s4); padding: 0; list-style: none; }
.facts li { display: grid; gap: 2px; padding: var(--s3); border-radius: 10px; background: var(--surface-2); }
.facts span { color: var(--muted); font-size: 0.8rem; }
.facts b { color: var(--brand-700); font-size: 1.05rem; }
.compare th[scope='row'] { color: var(--muted); font-weight: 400; white-space: nowrap; }
.compare td { line-height: 1.6; }

.more { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: var(--s3); margin: 0; padding: 0; list-style: none; }
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
  .entry tbody th.sticky { min-width: 9em; max-width: 10em; }
}
@media (max-width: 520px) {
  .page { padding: var(--s4) var(--s4) var(--s8); }
  .ranks { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .table { font-size: 0.875rem; }
  .more { grid-template-columns: 1fr; }
  .facts { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .wechat img { width: 112px; height: 112px; }
}
</style>
