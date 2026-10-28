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
  url: 'https://www.monash.edu.my/study/entry-requirements/academic',
  checked: '2026-10-28'
}

export const ENGLISH_SOURCE: ParentSource = {
  url: 'https://www.monash.edu.my/study/entry-requirements/english',
  checked: '2026-10-28'
}

/** 高考总分的最低百分比，按满分 750 换算成分数。 */
export const GAOKAO = [
  { course: '计算机科学学士', percent: 70 },
  { course: '土木工程学士（荣誉）', percent: 75 },
  { course: '理学学士', percent: 65 }
]

export const TRANSFER = {
  course: '材料工程学士（荣誉）',
  courseUrl: 'https://www.monash.edu.my/study/undergraduate/engineering/bachelor-of-materials-engineering-honours',
  ruleUrl: 'https://www.monash.edu/engineering/current-students/enrolment-and-re-enrolment/course-information/malaysia-clayton-transfer',
  checked: '2026-10-28'
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
  { label: '计算机科学学士', match: 'Bachelor of Computer Science' },
  { label: '工程学士（荣誉）', match: 'Bachelor of Civil Engineering (Honours)' },
  { label: '理学学士', match: 'Bachelor of Science' }
]
