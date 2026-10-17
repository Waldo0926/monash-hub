import { describe, expect, it } from 'vitest'
import { MAMO_POSTS } from '../data/mamo'
import { hanPairs, matchMamo, matchTools } from '../utils/assistant'

const ids = (question: string) => matchTools(question).map(tool => tool.id)

describe('matchTools', () => {
  it('finds the calculator in every language', () => {
    expect(ids('How is WAM calculated?')).toContain('marks')
    expect(ids('WAM 怎么算')).toContain('marks')
    expect(ids('ＷＡＭ 怎么算')).toContain('marks')
    expect(ids('GPA計算の方法')).toContain('marks')
    expect(ids('평점 계산은 어떻게 하나요')).toContain('marks')
  })

  it('points planning questions at the course map', () => {
    expect(ids('Where can I plan my units?')).toEqual(['plan'])
    expect(ids('在哪里做选课规划？')).toEqual(['plan'])
  })

  it('matches short English words only as whole words', () => {
    // "gpa" inside another word, "major" inside "majority".
    expect(ids('the majority of students')).toEqual([])
    expect(ids('Does FIT2004 have a final exam?')).toEqual([])
  })

  it('offers nothing for a question that names no tool', () => {
    expect(ids('怎么退课？')).toEqual([])
    expect(ids('')).toEqual([])
  })

  it('puts the longest match first and stops at two', () => {
    const found = matchTools('马莫百科 交换 社区 WAM')
    expect(found).toHaveLength(2)
    expect(found[0]!.id).toBe('mamo')
  })
})

describe('matchMamo', () => {
  it('finds a post by the words in its title', () => {
    const found = matchMamo('入台证怎么申请', MAMO_POSTS)
    expect(found[0]?.title).toContain('入台证')
  })

  it('finds the graduation post', () => {
    const found = matchMamo('毕业要不要申请？自动授予学位', MAMO_POSTS)
    expect(found[0]?.title).toContain('毕业')
  })

  it('does not match on the account name or filler words', () => {
    expect(matchMamo('马莫百科', MAMO_POSTS)).toEqual([])
    expect(matchMamo('怎么办？请问一下', MAMO_POSTS)).toEqual([])
    expect(matchMamo('Taiwan entry permit', MAMO_POSTS)).toEqual([])
  })

  it('counts pairs of Chinese characters only', () => {
    expect([...hanPairs('FIT2004 退课')]).toEqual(['退课'])
  })
})
