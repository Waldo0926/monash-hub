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
 * Entry scores for every undergraduate degree at the Malaysia campus, typed in
 * from the owner's own summary table. Fees are the 2027 international rate:
 * read live from /v1/fees by `match` (an English title or a degree a fee row
 * covers), with `fee` as the fallback when the API is down.
 */
export type EntryKey =
  | 'mufy' | 'cimp' | 'aLevel' | 'atar' | 'ib' | 'sat' | 'act' | 'ap' | 'dse' | 'unsw' | 'mc'

export const ENTRY_COLUMNS: { key: EntryKey; label: string; sub?: string }[] = [
  { key: 'mufy', label: 'MUFY' },
  { key: 'cimp', label: 'CIMP/OSSD' },
  { key: 'aLevel', label: 'A-Level' },
  { key: 'atar', label: 'ATAR' },
  { key: 'ib', label: 'IB' },
  { key: 'sat', label: 'SAT' },
  { key: 'act', label: 'ACT' },
  { key: 'ap', label: 'AP' },
  { key: 'dse', label: 'DSE' },
  { key: 'unsw', label: 'UNSW', sub: 'Foundation Studies' },
  { key: 'mc', label: 'Monash College', sub: 'Diploma Part 2' }
]

export interface EntryCourse {
  name: string
  years: number
  intakes: string
  /** English fee-table title or covered degree. */
  match: string
  /** 2027 international fee, used when /v1/fees cannot be read. */
  fee: number | string
  /** Percentage of the gaokao total, or null when gaokao is not accepted. */
  gaokao: number | null
  gaokaoSubjects: string
  scores: Record<EntryKey, string>
}

export interface EntrySchool {
  school: string
  courses: EntryCourse[]
}

/** The 11 scores in ENTRY_COLUMNS order. */
type Scores = [string, string, string, string, string, string, string, string, string, string, string]
type Row = [string, number, string, string, number | string, number | null, string, ...Scores]

const row = ([name, years, intakes, match, fee, gaokao, gaokaoSubjects, ...s]: Row): EntryCourse => {
  const [mufy, cimp, aLevel, atar, ib, sat, act, ap, dse, unsw, mc] = s
  return {
    name, years, intakes, match, fee, gaokao, gaokaoSubjects,
    scores: { mufy, cimp, aLevel, atar, ib, sat, act, ap, dse, unsw, mc }
  }
}

const ENG: Scores = ['76.25%', '84.80%', '10', '85', '30', '1240', '26', '7', '19', '8', '60%']
const ENG_GAOKAO = '高考数学 60%，高考物理或化学 60%'
const engineering = (name: string, match: string, intakes = '2、7、10'): Row =>
  [name, 4, intakes, match, 68160, 75, ENG_GAOKAO, ...ENG]

export const ENTRY_SCHOOLS: EntrySchool[] = [
  {
    school: '艺术与社会科学学院',
    courses: ([
      ['文学与社会科学学士（含 5 个方向）', 3, '2、7、10', 'Bachelor of Arts and Social Sciences', 53280, 60, '无高考单科要求',
        '60%', '75.40%', '7', '70', '25', '1120', '22', '6', '13', '6.5', '50%'],
      ['数字媒体与传播学士', 3, '2、7、10', 'Bachelor of Digital Media and Communication', 53280, 60, '无高考单科要求',
        '60%', '75.40%', '7', '70', '25', '1120', '22', '6', '13', '6.5', '50%']
    ] as Row[]).map(row)
  },
  {
    school: '商学院',
    courses: ([
      ['商务和商业学士（含 10 个方向）', 3, '2、7、10', 'Bachelor of Business and Commerce', 54240, 60, '高考数学 60%，或高二数学及格',
        '60%', '75.40%', '7', '70', '25', '1120', '22', '6', '13', '6.5', '50%'],
      ['数字商务学士', 3, '2、7', 'Bachelor of Digital Business', 54240, 65, '高考数学 60%',
        '70%', '78.50%', '8', '75', '26', '1160', '24', '6', '15', '7', '/'],
      ['精算分析学士', 3, '2、7', 'Bachelor in Actuarial Analytics', 57600, 70, '高考数学 60%',
        '72.5%', '81.60%', '9', '80', '28', '1190', '24', '7', '17', '7.5', '/'],
      ['商务学士与计算机科学学士', 4, '2、7、10', 'Bachelor of Business and Commerce and Bachelor of Computer Science', 57600, 70, '高考数学 60%',
        '70%', '81.60%', '9', '80', '28', '1190', '24', '7', '17', '7.5', '60%'],
      ['商务学士与数字媒体与传播学士', 4, '2、7、10', 'Bachelor of Business and Commerce and Bachelor of Digital Media and Communication', 54240, 60, '高考数学 60%，或高二数学及格',
        '60%', '75.40%', '7', '70', '25', '1120', '22', '6', '13', '6.5', '55%']
    ] as Row[]).map(row)
  },
  {
    school: '信息技术学院',
    courses: ([
      ['计算机科学学士（含 3 个方向）', 3, '2、7、10', 'Bachelor of Computer Science', 57600, 70, '高考数学 60%',
        '70%', '81.60%', '9', '80', '28', '1190', '24', '7', '17', '7.5', '60%']
    ] as Row[]).map(row)
  },
  {
    school: '工程学院',
    courses: ([
      engineering('土木工程学士（荣誉）', 'Bachelor of Civil Engineering (Honours)'),
      engineering('生物医学工程学士（荣誉）', 'Bachelor of Biomedical Engineering (Honours)', '2'),
      engineering('化学工程学士（荣誉）', 'Bachelor of Chemical Engineering (Honours)'),
      engineering('材料工程学士（荣誉）', 'Bachelor of Materials Engineering (Honours)'),
      engineering('电气与计算机工程学士（荣誉）', 'Bachelor of Electrical and Computer Systems Engineering (Honours)'),
      engineering('机械工程学士（荣誉）', 'Bachelor of Mechanical Engineering (Honours)'),
      engineering('机器人与机电工程学士（荣誉）', 'Bachelor of Robotics and Mechatronics Engineering (Honours)'),
      engineering('软件工程学士（荣誉）', 'Bachelor of Software Engineering (Honours)')
    ]).map(row)
  },
  {
    school: '医学和健康科学学院',
    courses: ([
      ['心理学学士', 3, '2、7、10', 'Bachelor of Psychology', 53280, 65, '高考数学 60%，高二物理、化学或生物及格',
        '67.50%', '78.50%', '8', '75', '26', '1160', '24', '6', '15', '7', '/'],
      ['医学学士和医学博士', 5, '2、7', 'Bachelor of Medical Science and Doctor of Medicine', 148320, null, '/',
        '91.00%', '85.00%', '14', '95', '36', '1360', '30', '9', '23', '9', '/'],
      ['人类营养学士', 3, '2、7', 'Bachelor of Human Nutrition', 63360, 65, '高考数学 60%，高二物理、化学或生物及格',
        '67.50%', '78.50%', '8', '75', '26', '1160', '24', '6', '15', '/', '/']
    ] as Row[]).map(row)
  },
  {
    school: '药剂学院',
    courses: ([
      ['药学学士（荣誉）', 4, '2', 'Bachelor of Pharmacy (Honours)', 74400, 70, '高考数学 60% 或高考化学 60%',
        '75%', '87.90%', '12', '90', '33', '1290', '27', '8', '21', '8.5', '/'],
      ['制药科学学士', 3, '2', 'Bachelor of Pharmaceutical Science', 63360, 65, '高考数学 60% 或高考化学 60%',
        '72.50%', '83.20%', '9.5', '82.5', '29', '1220', '25', '7', '18', '7.75', '/']
    ] as Row[]).map(row)
  },
  {
    school: '科学学院',
    courses: ([
      ['理学学士', 3, '2、7、10', 'Bachelor of Science', 63360, 65, '高考数学、物理、化学或生物 60%',
        '72.50%', '81.60%', '9', '80', '28', '1190', '24', '7', '17', '7.5', '55%'],
      ['应用数据科学学士', 3, '2、7、10', 'Bachelor of Applied Data Science', 63360, 65, '高考数学 60%',
        '72.50%', '81.60%', '9', '80', '28', '1190', '24', '7', '17', '7.5', '60%'],
      ['食品科学与技术学士', 3, '2、7、10', 'Bachelor of Food Science and Technology', 63360, 65, '高考数学、生物或化学 60%',
        '63.75%', '78.50%', '8', '75', '26', '1160', '24', '6', '15', '7', '50%'],
      ['医学生物科学学士', 3, '2、7、10', 'Bachelor of Medical Bioscience', 64800, 65, '高考数学、生物或化学 60%',
        '67.50%', '78.50%', '8', '75', '26', '1160', '24', '6', '15', '7', '50%']
    ] as Row[]).map(row)
  },
  {
    school: '高等教育文凭（国际大一）',
    courses: ([
      ['文学、商学、理学、信息技术', 1, '2、7、10', '', '49,440 / 55,680', 60, '',
        '60%', '72%', '6', '65', '24', '1090', '21', '6', '12', '6', '/']
    ] as Row[]).map(row)
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
