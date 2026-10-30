/**
 * 马莫百科 — the WeChat account, and the posts on it.
 *
 * Everything here was read off the account's own pages or given by its author:
 * the titles in full, and the article links, which are not searchable (WeChat's
 * mp.weixin.qq.com pages are not indexed) and so cannot be recovered any other
 * way. A post with an empty `url` renders as plain text rather than a dead link.
 *
 * Covers are the account's own cover images, resized and kept in
 * frontend/public/img/mamo/. WeChat's image CDN refuses hotlinks from other
 * sites, so linking to it directly would show a placeholder instead. Not
 * public/mamo/: a folder named like the page makes /mamo redirect to /mamo/.
 * A post without a cover gets a plain tile with its topic on it.
 */
export type MamoTopic = 'arrival' | 'visa' | 'exchange' | 'policy' | 'tools'

/** The order the filter chips appear in. */
export const MAMO_TOPICS: MamoTopic[] = ['policy', 'arrival', 'visa', 'exchange', 'tools']

export interface MamoPost {
  url: string
  date: string
  title: string
  topic: MamoTopic
  summary?: string
  /** Path under public/, e.g. /img/mamo/foo.jpg. */
  cover?: string
}

export const MAMO_ACCOUNT = {
  name: '马莫百科',
  region: '马来西亚',
  channel: '马莫百科Waldo学长',
  /** Personal WeChat ID the author gave for readers who want to ask something. */
  wechatId: 'MonashGuide',
  /** The account's own description, as written on its profile page. */
  about:
    '由马莫（Monash University Malaysia）在读学生运营，专注分享新生申请、学分减免、' +
    '选课学习、校园生活、国际交换及校园资讯等，内容结合个人真实经历与官方政策整理，' +
    '希望帮你少走弯路、更快适应马莫生活，欢迎关注、交流与咨询～'
}

/** Newest first, the way the account itself lists them. */
export const MAMO_POSTS: MamoPost[] = [
  {
    url: 'https://mp.weixin.qq.com/s/DXwDRcdt0dtNzjMVlY0sgQ',
    date: '2026-10-17',
    title: '马莫百科｜重磅！Monash毕业制度大改革：免申请、每月自动授予学位！',
    topic: 'policy',
    summary: '2026 年 12 月起・毕业免申请・每月授予学位・先毕业再参加典礼',
    cover: '/img/mamo/graduation-conferral.jpg'
  },
  {
    url: 'https://mp.weixin.qq.com/s/gUhzWBd5Q66N2rSf7auLnw',
    date: '2026-09-01',
    title: '马莫百科｜赴台必看：入台证申请条件、材料清单与完整办理指南',
    topic: 'visa',
    summary: '入台证申请条件・材料清单・完整办理流程',
    cover: '/img/mamo/taiwan-entry-permit.jpg'
  },
  {
    url: 'https://mp.weixin.qq.com/s/r_QD2P-dLUYyl0pQi2cgJw',
    date: '2026-08-26',
    title: '马莫同学专访｜"在意大利上3周课、游玩欧洲6个国家后，我又踩了国际交换的坑"',
    topic: 'exchange',
    summary:
      'Monash 意大利校区课程、欧洲 6 国旅行、真实花费与国际交换踩坑…内含 16 分钟完整专访视频！',
    cover: '/img/mamo/italy-exchange-interview.jpg'
  },
  {
    url: 'https://mp.weixin.qq.com/s/L_eLXcW_0MSQcpWlUCesTg',
    date: '2026-08-17',
    title: '马莫百科｜学生签证快到期？续签完整指南：时间、要求、SORS申请流程、EMGS节点及注意事项',
    topic: 'visa',
    summary: '时间・要求・SORS 申请流程・EMGS 节点・注意事项',
    cover: '/img/mamo/student-visa-renewal.jpg'
  },
  {
    url: 'https://mp.weixin.qq.com/s/gj3m9RCLm2GGcRa5a1lszQ',
    date: '2026-08-06',
    title:
      '马莫百科｜想去海外交换?Monash Malaysia国际交换完整指南：申请资格、时间线、选校志愿、学分与申请流程',
    topic: 'exchange',
    summary: '资格・选校・学分・费用・流程 一站式整理',
    cover: '/img/mamo/exchange-guide.jpg'
  },
  {
    url: 'https://mp.weixin.qq.com/s/_E4j7ldLXni5RJLtgp_uwg',
    date: '2026-07-27',
    title: '马莫百科｜Monash常用网站与系统指南：学习、选课、行政、支持',
    topic: 'tools',
    summary: '学生邮箱・学习平台・课程选课・课表系统・咨询支持',
    cover: '/img/mamo/systems-guide.jpg'
  },
  {
    url: 'https://mp.weixin.qq.com/s/8TqQOmR9EMHwwtfFiHX-Dw',
    date: '2026-07-20',
    title: '马莫百科｜新生入境、报到、缴费、选课全流程指南',
    topic: 'arrival',
    summary: '入境指南・校园报到・缴费指南・选课排课',
    cover: '/img/mamo/new-student-guide.jpg'
  }
]
