/**
 * Facts on the /parents page, each with the official page it was read from and
 * the day it was checked.
 *
 * Typed in by hand for now. Every page here is an official seed (in
 * crawler/official/seeds.py or seeds_coverage.py), so these can be read from
 * the harvested pages later instead. Collapsed FAQ answers were opened and read
 * in a browser on 2026-10-30.
 */
export interface ParentSource {
  url: string
  checked: string
}

/** About the Malaysia campus, from the campus welcome page. */
export const ABOUT = {
  url: 'https://www.monash.edu.my/about/welcome',
  checked: '2026-10-30',
  facts: [
    { label: '建校', value: '1998 年' },
    { label: '在校学生', value: '约 13,800 人' },
    { label: '学生来自', value: '91 个国家和地区' },
    { label: '海外合作大学', value: '140 所' }
  ]
}

export const SETARA_SOURCE: ParentSource = {
  url: 'https://www.monash.edu.my/about/top-university-in-malaysia',
  checked: '2026-10-30'
}

export const RANKINGS_SOURCE: ParentSource = {
  url: 'https://www.monash.edu/about/our-rankings',
  checked: '2026-10-30'
}

export const RANKINGS = [
  { name: 'QS 世界大学排名', year: '2027', place: '第 31 位' },
  { name: 'U.S. News 全球最佳大学排名', year: '2026-2027', place: '第 38 位' },
  { name: '泰晤士高等教育世界大学排名（THE）', year: '2027', place: '第 61 位' },
  { name: '软科世界大学学术排名（ARWU）', year: '2026', place: '第 76 位' }
]

/** World top 30 subjects that the Malaysia campus also teaches. */
export const SUBJECT_RANKINGS = [
  { name: 'QS 学科排名 药学与药理学', year: '2026', place: '世界第 2 位' },
  { name: '软科学科排名 工商管理', year: '2026', place: '世界第 11 位' },
  { name: '软科学科排名 管理学', year: '2026', place: '世界第 15 位' }
]

export const DEGREE_SOURCE: ParentSource = {
  url: 'https://www.monash.edu.my/about/welcome',
  checked: '2026-10-30'
}

/** The FAQ under "Is a Monash Malaysia degree the same as an Australian Monash degree?" */
export const DEGREE_FAQ_URL = 'https://www.monash.edu.my/about/top-university-in-malaysia'

export const CSCSE_URL = 'https://www.cscse.edu.cn'

export const ENTRY_SOURCE: ParentSource = {
  url: 'https://www.monash.edu.my/study/entry-requirements/academic/undergraduate',
  checked: '2026-10-29'
}

export const SCORE_METHOD_URL =
  'https://www.monash.edu.my/study/entry-requirements/academic/undergraduate/calculating-entry-scores'

export const ENGLISH_SOURCE: ParentSource = {
  url: 'https://www.monash.edu.my/study/entry-requirements/english',
  checked: '2026-10-28'
}

/**
 * Entry scores for the degrees most Chinese students at the Malaysia campus
 * take, from a checked summary of the Monash Malaysia course pages. The
 * official course page is linked for each.
 */
export interface EntryCourse {
  name: string
  /** For the column heading on a phone. */
  short: string
  code: string
  url: string
  years: number
  intakes: string
  gaokao: number
  gaokaoSubjects: string
  scores: Record<EntryKey, string>
}

export type EntryKey = 'aLevel' | 'ib' | 'ap' | 'sat' | 'act' | 'mufy' | 'cimp'

export const ENTRY_ROWS: { key: EntryKey; label: string }[] = [
  { key: 'aLevel', label: 'A-Level' },
  { key: 'ib', label: 'IB 文凭' },
  { key: 'ap', label: 'AP' },
  { key: 'sat', label: 'SAT' },
  { key: 'act', label: 'ACT' },
  { key: 'mufy', label: 'MUFY 预科' },
  { key: 'cimp', label: 'CIMP / OSSD' }
]

export const ENTRY_COURSES: EntryCourse[] = [
  {
    name: '商务和商业学士',
    short: '商科',
    code: 'B2026',
    url: 'https://www.monash.edu.my/study/undergraduate/business/bachelor-business-commerce',
    years: 3,
    intakes: '2、7、10',
    gaokao: 60,
    gaokaoSubjects: '数学 60%，或高二数学及格',
    scores: { aLevel: '7', ib: '25', ap: '6', sat: '1120', act: '22', mufy: '60%', cimp: '75.40%' }
  },
  {
    name: '数字媒体与传播学士',
    short: '传媒',
    code: 'A2011',
    url: 'https://www.monash.edu.my/study/undergraduate/arts-social-sciences/bachelor-of-digital-media-and-communication',
    years: 3,
    intakes: '2、7、10',
    gaokao: 60,
    gaokaoSubjects: '无',
    scores: { aLevel: '7', ib: '25', ap: '6', sat: '1120', act: '22', mufy: '60%', cimp: '75.40%' }
  },
  {
    name: '计算机科学学士',
    short: '计算机',
    code: 'C2001',
    url: 'https://www.monash.edu.my/study/undergraduate/information-technology/bachelor-computer-science/entry-score',
    years: 3,
    intakes: '2、7、10',
    gaokao: 70,
    gaokaoSubjects: '数学 60%',
    scores: { aLevel: '9', ib: '28', ap: '7', sat: '1190', act: '24', mufy: '70%', cimp: '81.60%' }
  },
  {
    name: '工程学士（荣誉）',
    short: '工程',
    code: 'E3001',
    url: 'https://www.monash.edu.my/study/undergraduate/engineering/bachelor-of-engineering-honours-in-mechanical-engineering/entry-score',
    years: 4,
    intakes: '2、7、10',
    gaokao: 75,
    gaokaoSubjects: '数学 60%，物理或化学 60%',
    scores: { aLevel: '10', ib: '30', ap: '7', sat: '1240', act: '26', mufy: '76.25%', cimp: '84.80%' }
  }
]

export const MUFY = {
  url: 'https://www.monash.edu.my/study/diploma-and-pathway/mufy',
  checked: '2026-10-30'
}

export const DIPLOMA = {
  url: 'https://www.monash.edu.my/study/diploma-and-pathway/diploma-higher-education-studies',
  checked: '2026-10-30',
  gaokao: 60,
  fees: { year: 2027, nonScience: 49440, science: 55680 }
}

export const SCHOLARSHIP = {
  url: 'https://www.monash.edu.my/student-services/financial-assistance/undergraduate-scholarships-and-bursaries/merit-scholarships',
  checked: '2026-10-30'
}

export const TRANSFER = {
  url: 'https://www.monash.edu.my/study/apply/internal-course-transfer',
  rulesUrl: 'https://www.monash.edu/admissions/study-options/internal-transfer',
  reasonsUrl: 'https://www.monash.edu.my/about/top-university-in-malaysia/10-reasons-to-choose-monash-university-malaysia',
  checked: '2026-10-30'
}

/** The campus's own page for parents: privacy, transfer fees, support. */
export const PARENTS_INFO = {
  url: 'https://www.monash.edu.my/student-services/new-to-monash/information-for-parents',
  checked: '2026-10-30'
}

export const EXCHANGE = {
  checked: '2026-10-29',
  programs: [
    {
      name: 'Semester Exchange Program',
      text: '到 Monash 的海外合作大学交换一到两个学期，所修学分计入 Monash 学位。',
      url: 'https://www.monash.edu/study-abroad/overseas/monash-partner-programs/exchange'
    },
    {
      name: 'Semester in Australia',
      text: '到澳大利亚的校区读一个学期。学籍仍在马来西亚校区，学费按马来西亚校区标准以马币缴纳，每人限一次。',
      url: 'https://www.monash.edu.my/study-abroad/outbound/Semester-in-Australia'
    },
    {
      name: 'Global Summer Program / Global Winter Program',
      text: '寒暑假期间到合作大学上 2 到 4 周的短期课程，可以计入学分。冬季项目在 6 至 7 月，夏季项目在 11 月至次年 2 月。',
      url: 'https://www.monash.edu.my/study-abroad/outbound/short-term-programs'
    },
    {
      name: 'Prato 中心（意大利）',
      text: 'Monash 在意大利 Prato 设有自己的教学中心。2026 年 6 至 7 月，马来西亚校区的学生在这里参加了为期三周的短期课程。',
      url: 'https://www.monash.edu.my/pages/latest/articles/2026/monash-malaysia-students-expand-global-perspectives-through-mgci-in-italy'
    }
  ]
}

/** 目前以 1 马币兑 1.65 人民币换算，具体以当天汇率为准。 */
export const MYR_TO_CNY = 1.65

/** Malaysian service tax on tuition for international students since 1 July 2025. */
export const SST = {
  rate: 0.06,
  url: 'https://www.monash.edu.my/finance/sst-info',
  checked: '2026-10-30'
}

export const VISA = {
  amount: 2515,
  months: 12,
  url: 'https://www.monash.edu.my/student-services/media/student-services2/homepage/current-students/publications/student-pass/new-international-students',
  checked: '2026-10-28'
}

export const LIVING = {
  url: 'https://www.monash.edu.my/lets-begin/about-uni-life/money-matters',
  checked: '2026-10-28',
  items: [
    { item: '房租', amount: '每月 RM500 起' },
    { item: '租房押金', amount: 'RM1,500 起' },
    { item: '外出吃饭', amount: '每餐 RM7 至 RM15' },
    { item: '超市采购', amount: 'RM30 起' },
    { item: '手机和网络', amount: '每月 RM99 起' }
  ]
}

/**
 * The fee rows shown as examples, matched against the title or the degrees a
 * row covers on /ugfees. Engineering is one row for all its honours degrees.
 */
export const FEE_EXAMPLES = [
  { label: '商务和商业学士', match: 'Bachelor of Business and Commerce' },
  { label: '数字媒体与传播学士', match: 'Bachelor of Digital Media and Communication' },
  { label: '计算机科学学士', match: 'Bachelor of Computer Science' },
  { label: '工程学士（荣誉）', match: 'Bachelor of Civil Engineering (Honours)' }
]

export const CAMPUS = {
  welcomeUrl: 'https://www.monash.edu.my/about/welcome',
  housingUrl: 'https://www.monash.edu.my/student-life/accommodation',
  healthUrl: 'https://www.monash.edu.my/student-services/support-services/health-and-wellness-services',
  insuranceUrl: 'https://www.monash.edu.my/student-services/support-services/insurance',
  securityUrl: 'https://www.monash.edu.my/security/about-us',
  checked: '2026-10-30',
  residences: ['Waterfront Residence', 'Sun-U Residence', 'Sun-U Apartment'],
  securityHotline: '+603 5514 6333'
}
