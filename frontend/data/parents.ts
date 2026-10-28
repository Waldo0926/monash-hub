/**
 * Facts on the /parents page, each with the official page it was read from and
 * the day it was checked.
 *
 * Typed in by hand for now. The pages are already official seeds
 * (malaysia-reputation, malaysia-academic-entry, malaysia-english-entry,
 * malaysia-student-pass in crawler/official/seeds.py), so these can be read
 * from the harvested pages later instead.
 */
export interface ParentSource {
  url: string
  checked: string
}

export const RANKINGS_SOURCE: ParentSource = {
  url: 'https://www.monash.edu/about/our-rankings',
  checked: '2026-10-28'
}

export const RANKINGS = [
  { name: 'QS 世界大学排名', year: '2027', place: '第 31 位' },
  { name: 'U.S. News 全球最佳大学排名', year: '2026-2027', place: '第 38 位' },
  { name: '泰晤士高等教育世界大学排名（THE）', year: '2026', place: '并列第 58 位' },
  { name: '软科世界大学学术排名（ARWU）', year: '2025', place: '第 76 位' }
]

export const SUBJECT_RANKING = { name: 'QS 世界大学学科排名 药学与药理学', year: '2026', place: '世界第 2 位' }

export const DEGREE_SOURCE: ParentSource = {
  url: 'https://www.monash.edu.my/about/top-university-in-malaysia',
  checked: '2026-10-28'
}

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
 * Each degree's published entry scores. The course pages say the figures are
 * for students who started MUFY in 2024. A null is a score the page did not
 * show when it was read, not a degree that refuses the qualification.
 */
export interface EntryScores {
  course: string
  code: string
  url: string
  gaokao: number
  aLevel: number | null
  ib: number | null
  mufy: string | null
  prerequisite: string
}

export const ENTRY_SCORES: EntryScores[] = [
  {
    course: '商业与贸易学士',
    code: 'B2026',
    url: 'https://www.monash.edu.my/study/undergraduate/business/bachelor-business-commerce',
    gaokao: 60,
    aLevel: null,
    ib: null,
    mufy: null,
    prerequisite: '数学'
  },
  {
    course: '数字媒体与传播学士',
    code: 'A2011',
    url: 'https://www.monash.edu.my/study/undergraduate/arts-social-sciences/bachelor-of-digital-media-and-communication',
    gaokao: 60,
    aLevel: 7,
    ib: null,
    mufy: '60%',
    prerequisite: '无'
  },
  {
    course: '计算机科学学士',
    code: 'C2001',
    url: 'https://www.monash.edu.my/study/undergraduate/information-technology/bachelor-computer-science/entry-score',
    gaokao: 70,
    aLevel: 9,
    ib: 28,
    mufy: '70%',
    prerequisite: '数学'
  },
  {
    course: '工程学士（荣誉）',
    code: 'E3001',
    url: 'https://www.monash.edu.my/study/undergraduate/engineering/bachelor-of-engineering-honours-in-mechanical-engineering/entry-score',
    gaokao: 75,
    aLevel: 10,
    ib: null,
    mufy: '76.25%',
    prerequisite: '数学，以及化学或物理其中一门'
  }
]

export const TRANSFER = {
  url: 'https://www.monash.edu.my/study/apply/internal-course-transfer',
  rulesUrl: 'https://www.monash.edu/admissions/study-options/internal-transfer',
  checked: '2026-10-29'
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
      text: '到澳洲的校区读一个学期。学籍仍在马来西亚校区，学费按马来西亚校区标准以马币缴纳，每人限一次。',
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
  { label: '商业与贸易学士', match: 'Bachelor of Business and Commerce' },
  { label: '数字媒体与传播学士', match: 'Bachelor of Digital Media and Communication' },
  { label: '计算机科学学士', match: 'Bachelor of Computer Science' },
  { label: '工程学士（荣誉）', match: 'Bachelor of Civil Engineering (Honours)' }
]
