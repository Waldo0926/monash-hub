/**
 * What the assistant adds on top of /v1/ask.
 *
 * The router answers from the Handbook, the FAQ and the official pages, but it
 * knows nothing about the site itself. "How do I work out my WAM?" has a FAQ
 * answer, and the student also wants to hear that there is a calculator one
 * click away. Same for the 马莫百科 posts, which live in frontend/data/mamo.ts
 * and are not in the search index at all.
 *
 * Both are plain word matching, like the router. Nothing here guesses: a tool
 * or a post is offered only when the question names it.
 */
import type { MamoPost } from '~/data/mamo'

export type SiteToolId =
  | 'marks' | 'plan' | 'tree' | 'courses' | 'units' | 'exchange' | 'guides' | 'community' | 'mamo' | 'dates'

export interface SiteTool {
  id: SiteToolId
  to: string
  /** Lower case. ASCII words match whole words only, everything else as a substring. */
  words: string[]
}

export const SITE_TOOLS: SiteTool[] = [
  {
    id: 'marks',
    to: '/marks',
    words: [
      'wam', 'gpa', 'grade point', 'average mark', 'weighted average', 'calculator',
      '均分', '平均分', '绩点', '算分', '计算器', '算成绩',
      '平均点', 'gpa計算',
      '평점', '학점 계산', '계산기'
    ]
  },
  {
    id: 'plan',
    to: '/plan',
    words: [
      'study plan', 'course plan', 'course map', 'plan my degree', 'plan my course', 'plan my units',
      'planner', 'which units should i take',
      '选课规划', '学习计划', '选课计划', '排课', '规划', '课表规划',
      '履修計画', '履修プラン',
      '수강 계획', '학습 계획'
    ]
  },
  {
    id: 'tree',
    to: '/tree',
    words: [
      'unit tree', 'prerequisite tree', 'prereq tree', 'prerequisite map', 'unlocks',
      '先修图', '先修树', '课程树', '解锁',
      '前提科目マップ', '科目ツリー',
      '선수과목 지도', '과목 트리'
    ]
  },
  {
    id: 'courses',
    to: '/courses',
    words: [
      'degree structure', 'degree requirements', 'course structure', 'major', 'majors',
      'specialisation', 'specialization', 'minor',
      '学位结构', '学位要求', '专业方向', '主修', '辅修',
      '学位プログラム', '専攻',
      '학위 구조', '전공'
    ]
  },
  {
    id: 'units',
    to: '/units',
    words: [
      'browse units', 'all units', 'unit list', 'find a unit', 'elective', 'electives',
      '找课', '课程列表', '选修课', '选修',
      '選択科目', '科目一覧',
      '선택 과목', '과목 목록'
    ]
  },
  {
    id: 'exchange',
    to: '/guides?category=exchange',
    words: [
      'exchange', 'study abroad',
      '交换', '海外交换', '出国交换', '交換',
      '交換留学',
      '교환학생', '교환'
    ]
  },
  {
    id: 'guides',
    to: '/guides',
    words: [
      'guide', 'guides', 'official guide',
      '指南', '攻略',
      'ガイド',
      '가이드'
    ]
  },
  {
    id: 'community',
    to: '/community',
    words: [
      'community', 'forum', 'ask students', 'ask other students', 'post a question', 'seniors',
      '社区', '论坛', '发帖', '问学长', '问学姐', '学长', '学姐',
      'コミュニティ', '先輩',
      '커뮤니티', '선배'
    ]
  },
  {
    id: 'dates',
    to: '/dates',
    words: [
      'key dates', 'important dates', 'academic calendar', 'census date', 'swot vac',
      'exam period', 'results release', 'public holiday',
      '重要日期', '校历', '学校日历', '考试周', '复习周', '出成绩', '公布成绩', '公共假期', '放假',
      '重要な日程', '学年暦', '試験期間', '成績発表',
      '주요 일정', '학사 일정', '시험 기간', '성적 발표'
    ]
  },
  {
    id: 'mamo',
    to: '/mamo',
    words: ['mamo', 'mum guide', 'wechat', '马莫百科', '马莫', '公众号', '微信']
  }
]

/** Full-width to half-width and lower case, so "ＷＡＭ" is "wam". */
export function normaliseQuestion(text: string): string {
  return (text || '').normalize('NFKC').toLowerCase().replace(/\s+/g, ' ').trim()
}

const ASCII = /^[\x20-\x7e]+$/

function escape(text: string): string {
  return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function hits(question: string, word: string): boolean {
  if (ASCII.test(word)) return new RegExp(`(^|[^a-z0-9])${escape(word)}($|[^a-z0-9])`).test(question)
  return question.includes(word)
}

/**
 * The site tools a question names, best match first, at most `limit`.
 *
 * The longest matching word decides the order, so "WAM 计算器" puts the
 * calculator ahead of anything that only matched a two-letter word.
 */
export function matchTools(question: string, limit = 2): SiteTool[] {
  const q = normaliseQuestion(question)
  if (!q) return []
  const scored: { tool: SiteTool; score: number }[] = []
  for (const tool of SITE_TOOLS) {
    const best = tool.words.reduce((max, word) => (hits(q, word) ? Math.max(max, word.length) : max), 0)
    if (best > 0) scored.push({ tool, score: best })
  }
  return scored.sort((a, b) => b.score - a.score).slice(0, limit).map(entry => entry.tool)
}

// Words that turn up in any question and say nothing about which post it is.
const FILLER = new Set([
  '怎么', '什么', '如何', '可以', '需要', '哪些', '哪里', '是否', '一下', '请问', '有没',
  '没有', '我们', '我的', '马莫', '莫百', '百科', '吗？', '的话', '时候', '要怎', '么办',
  '怎样', '多少', '为什', '应该', '能不', '不能', '可不', '不可', '现在', '知道'
])

const HAN = /[㐀-鿿]/

/** Pairs of neighbouring Chinese characters, the unit the post matching counts in. */
export function hanPairs(text: string): Set<string> {
  const pairs = new Set<string>()
  const chars = Array.from(normaliseQuestion(text))
  for (let i = 0; i + 1 < chars.length; i++) {
    const a = chars[i]!
    const b = chars[i + 1]!
    if (!HAN.test(a) || !HAN.test(b)) continue
    const pair = a + b
    if (!FILLER.has(pair)) pairs.add(pair)
  }
  return pairs
}

/**
 * 马莫百科 posts that share at least two character pairs with the question.
 *
 * One pair is not enough: "签证" alone would bring up every visa post for a
 * question about something else entirely. The account name at the front of
 * every title is dropped first, or "马莫百科" would match all of them.
 */
export function matchMamo(question: string, posts: MamoPost[], limit = 2): MamoPost[] {
  const asked = hanPairs(question)
  if (asked.size < 2) return []
  const scored: { post: MamoPost; score: number }[] = []
  for (const post of posts) {
    const title = post.title.replace(/^马莫百科\s*[｜|]\s*/, '')
    const own = hanPairs(`${title} ${post.summary || ''}`)
    let score = 0
    for (const pair of asked) if (own.has(pair)) score++
    if (score >= 2) scored.push({ post, score })
  }
  return scored.sort((a, b) => b.score - a.score).slice(0, limit).map(entry => entry.post)
}
