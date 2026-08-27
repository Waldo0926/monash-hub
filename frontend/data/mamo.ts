/**
 * 马莫百科 — the WeChat account, and the posts on it.
 *
 * WeChat article URLs are not searchable: mp.weixin.qq.com pages are not
 * indexed, and an invented link is worse than none. So every post below starts
 * with an empty `url`, and the card renders as plain text until a real link is
 * pasted in. Copy the link from WeChat (推文右上角 ⋯ → 复制链接) and paste it
 * between the quotes.
 *
 * Everything else here was read off the account's own pages: the titles and
 * summaries as WeChat shows them, so a title WeChat truncates is truncated
 * here too rather than guessed at.
 */
export interface MamoPost {
  /** Paste the mp.weixin.qq.com link here. Empty means "not linked yet". */
  url: string
  date: string
  title: string
  summary?: string
  reads?: number
  likes?: number
}

export const MAMO_ACCOUNT = {
  name: '马莫百科',
  region: '马来西亚',
  channel: '马莫百科Waldo学长',
  originals: 5,
  /** The account's own description, as written on its profile page. */
  about:
    '由马莫（Monash University Malaysia）在读学生运营，专注分享新生申请、学分减免、' +
    '选课学习、校园生活、国际交换及校园资讯等。内容结合个人真实经历与官方政策整理，' +
    '希望帮你少走弯路、更快适应马莫生活。欢迎关注、交流与咨询～'
}

export const MAMO_POSTS: MamoPost[] = [
  {
    url: '',
    date: '2026-08-26',
    title: '马莫同学专访｜"在意大利上3周课、游玩欧洲6个国家后，我又踩了国际交换的坑"',
    summary:
      'Monash 意大利校区课程、欧洲 6 国旅行、真实花费与国际交换踩坑…内含 16 分钟完整专访视频！',
    reads: 667,
    likes: 20
  },
  {
    url: '',
    date: '2026-08-17',
    title: '马莫百科｜学生签证快到期？续签完整指南：时间、要…',
    summary: '时间・要求・SORS 申请流程・EMGS 节点・注意事项',
    reads: 374,
    likes: 12
  },
  {
    url: '',
    date: '2026-08-06',
    title: '马莫百科｜想去海外交换?Monash Malaysia国际交换完…',
    summary: '资格・选校・学分・费用・流程 一站式整理',
    reads: 1050,
    likes: 23
  },
  {
    url: '',
    date: '2026-07-27',
    title: '马莫百科｜Monash常用网站与系统指南：学习、选课、…',
    summary: '学生邮箱・学习平台・课程选课・课表系统・咨询支持',
    reads: 584,
    likes: 27
  },
  {
    url: '',
    date: '2026-07-20',
    title: '马莫百科｜新生入境、报到、缴费、选课全流程指南',
    summary: '入境指南・校园报到・缴费指南・选课排课',
    reads: 757,
    likes: 32
  }
]
