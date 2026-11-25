<script setup lang="ts">
/**
 * What the site keeps about the people who use it, in plain words.
 *
 * Written from what the code actually stores, so it has to change when that
 * does: the User model, the throttle table, the browser's localStorage, the
 * Google sign-in cookie, and the services a request is passed on to (email,
 * the 马莫百科 bot, Google) and the locale cookie. Chinese and English; Japanese and Korean readers
 * get the English text rather than an unreviewed translation.
 */
const { $t } = useNuxtApp()
const { cnReadonly } = useSiteMode()
const { locale } = useLocale()
const zh = computed(() => locale.value === 'zh')

const UPDATED = computed(() => (cnReadonly.value ? '2026-11-25' : '2026-10-31'))
const CONTACT = 'wensx0926@gmail.com'

useSeoMeta({ title: () => $t('privacy.title') })
</script>

<template>
  <div class="container narrow page">
    <article class="card section prose">
      <h1>{{ $t('privacy.title') }}</h1>
      <p class="tiny muted">{{ $t('privacy.updated', { date: UPDATED }) }}</p>

      <template v-if="cnReadonly && zh">
        <p>Monash Hub 是学生自建的非官方学习资料与选课查询工具，不隶属于 Monash University。国内只读版仅提供公开课程、学位、官方指南与本地计算功能，以下说明网站的数据处理方式。</p>

        <h2>不收集账号与个人发布内容</h2>
        <ul>
          <li>本站点为纯只读信息查询站，不开放注册登录、社区发帖、课程评价、头像或文件上传，也不提供在线 AI 对话</li>
          <li>不收集你的邮箱、密码、昵称、真实姓名、学号或手机号</li>
        </ul>

        <h2>仅保存在你浏览器本地的数据</h2>
        <ul>
          <li>选课计划保存在你的浏览器 <code>localStorage</code> 中；点击“检查计划”时会临时发送到服务器核对先修规则，但服务器不保存任何记录</li>
          <li>WAM/GPA 计算器输入的成绩仅在你的浏览器本地计算，不会上传至服务器</li>
          <li>界面语言偏好（<code>mh_locale</code>）和首页默认校区（<code>mh_home_campus</code>）保存在浏览器 Cookie 中，仅用于记住你的展示偏好</li>
        </ul>

        <h2>服务器访问日志与第三方资源</h2>
        <ul>
          <li>服务器仅保留常规 Web 访问日志（包含访问时间、请求路径、状态码及 IP 地址），仅用于故障排查与基本安全防护</li>
          <li>本站点不投放广告，不接入第三方统计追踪脚本，也不加载海外字体外链</li>
        </ul>

        <h2>联系我们</h2>
        <p>
          如对资料准确性、版权或隐私说明有任何疑问，请发邮件至
          <a :href="`mailto:${CONTACT}`">{{ CONTACT }}</a>。
        </p>
      </template>

      <template v-else-if="cnReadonly">
        <p>Monash Hub is an independent, unofficial student information and planning tool, not affiliated with Monash University. This read-only edition provides public Handbook, degree, official guide lookup and local calculators.</p>

        <h2>No accounts or user uploads</h2>
        <ul>
          <li>This edition is strictly read-only: account registration, sign-in, community posting, unit reviews, file/avatar uploads and interactive chat are disabled.</li>
          <li>We do not collect your email address, password, nickname, real name, student ID or phone number.</li>
        </ul>

        <h2>Data stored only in your browser</h2>
        <ul>
          <li>Study plans stay in your browser's <code>localStorage</code>. Checking a plan sends unit codes to the server to validate Handbook rules without storing them.</li>
          <li>WAM/GPA marks are calculated entirely in your browser and are never uploaded.</li>
          <li>Your language choice (<code>mh_locale</code>) and preferred campus (<code>mh_home_campus</code>) are stored in browser cookies purely to remember your display settings.</li>
        </ul>

        <h2>Server logs and third-party requests</h2>
        <ul>
          <li>The web server keeps standard access logs (timestamp, path, status code and IP address) solely for troubleshooting and abuse protection.</li>
          <li>This edition uses no advertising, no third-party analytics trackers and no external webfont CDNs.</li>
        </ul>

        <h2>Contact</h2>
        <p>
          For questions about data accuracy, copyright or this notice, email
          <a :href="`mailto:${CONTACT}`">{{ CONTACT }}</a>.
        </p>
      </template>

      <template v-else-if="zh">
        <p>Monash Hub是学生做的非官方网站，不隶属于Monash University。这里说明网站保存了你的哪些信息、用来做什么</p>

        <h2>账号</h2>
        <ul>
          <li>注册时只收集邮箱、昵称和密码。密码只保存bcrypt哈希，任何人都看不到原文</li>
          <li>你可以选择上传头像、填写个人简介</li>
          <li>网站会记录账号的创建时间和最近一次登录时间</li>
          <li>不收集真实姓名、学号或电话</li>
        </ul>

        <h2>使用Google登录</h2>
        <ul>
          <li>只向Google请求openid、email和profile，用来读取你的邮箱、邮箱是否已验证，以及显示名称</li>
          <li>邮箱用来找到或创建你的账号；显示名称只在第一次登录时用来生成昵称，之后可以自己改</li>
          <li>不读取你的Gmail、云端硬盘、联系人或其他Google数据，也不保存Google的访问令牌</li>
          <li>登录过程中会设置一个10分钟有效的cookie，用来确认回调来自发起登录的同一个浏览器，登录结束即删除</li>
        </ul>

        <h2>你发布的内容</h2>
        <ul>
          <li>社区帖子、回答和课程评分会公开显示，并标注你的昵称</li>
          <li>未登录也可以评分：浏览器会生成一个随机标识，用来让你之后修改或删除自己的评分</li>
          <li>有人回答你的帖子时，网站会给你生成站内通知</li>
        </ul>

        <h2>邮件</h2>
        <p>注册和重置密码时，验证码通过邮件发送服务送到你的邮箱。验证码只保存哈希，过期后失效</p>

        <h2>防滥用记录</h2>
        <p>为了限制猜密码和刷请求，网站会短时间记录登录失败、索取验证码、举报和评分的次数，按邮箱或网络地址计数，过期后自动清理。服务器访问日志也会记录网络地址</p>

        <h2>提问面板</h2>
        <p>你在提问面板输入的问题会同时发给马莫百科的微信机器人，用来补充回答。随问题一起发送的只有浏览器生成的随机标识，不包括你的账号信息</p>

        <h2>存在你浏览器里的数据</h2>
        <ul>
          <li>登录状态（会话令牌）保存在浏览器的localStorage里，退出登录即清除</li>
          <li>选课计划只保存在你的浏览器里；检查计划时会发给服务器核对，但不保存</li>
          <li>界面语言保存在一个名为mh_locale的cookie里</li>
          <li>网站不使用广告或第三方统计追踪</li>
        </ul>

        <h2>我们不会做的事</h2>
        <p>不出售、不出租你的个人信息，也不用于广告</p>

        <h2>删除账号与联系</h2>
        <p>
          想删除账号或导出数据，或对本政策有疑问，请发邮件到
          <a :href="`mailto:${CONTACT}`">{{ CONTACT }}</a>
        </p>
      </template>

      <template v-else>
        <p>Monash Hub is an unofficial site made by students and is not affiliated with Monash University. This page says what it keeps about you and why.</p>

        <h2>Your account</h2>
        <ul>
          <li>Signing up asks for an email address, a nickname and a password. Only a bcrypt hash of the password is stored; nobody can read the password itself.</li>
          <li>You can choose to add a profile picture and a short bio.</li>
          <li>The site records when the account was created and when it last signed in.</li>
          <li>No real name, student ID or phone number is collected.</li>
        </ul>

        <h2>Signing in with Google</h2>
        <ul>
          <li>Only the openid, email and profile scopes are requested, to read your email address, whether Google has verified it, and your display name.</li>
          <li>The email address finds or creates your account. The display name is used once, to suggest a nickname you can change later.</li>
          <li>Nothing else from your Google account is read (no Gmail, Drive or contacts), and no Google access token is kept.</li>
          <li>A cookie lasting at most ten minutes confirms that the sign-in finishes in the browser that started it, and is deleted when it does.</li>
        </ul>

        <h2>What you post</h2>
        <ul>
          <li>Community posts, answers and unit ratings are public and shown with your nickname.</li>
          <li>You can rate without an account: your browser makes up a random key so you can edit or remove that rating later.</li>
          <li>When someone answers your post, the site creates a notification for you.</li>
        </ul>

        <h2>Email</h2>
        <p>Codes for signing up and resetting a password are sent to your address through an email delivery service. Only a hash of each code is stored, and codes expire.</p>

        <h2>Abuse protection</h2>
        <p>To limit password guessing and request floods, the site briefly counts failed sign-ins, code requests, reports and ratings by email address or network address, and deletes the counts when they expire. The web server's access log also records network addresses.</p>

        <h2>The Ask panel</h2>
        <p>A question typed into the Ask panel is also sent to the 马莫百科 WeChat bot to add to the answer, together with a random key your browser makes up. Your account details are not sent.</p>

        <h2>Stored in your browser</h2>
        <ul>
          <li>Your signed-in session token is kept in the browser's localStorage and cleared when you sign out.</li>
          <li>Study plans are kept only in your browser. Checking a plan sends it to the server, which does not store it.</li>
          <li>Your interface language is kept in a cookie called mh_locale.</li>
          <li>The site uses no advertising or third-party analytics trackers.</li>
        </ul>

        <h2>What we do not do</h2>
        <p>Your personal information is not sold, rented or used for advertising.</p>

        <h2>Deleting your account and contact</h2>
        <p>
          To delete your account, get a copy of your data, or ask about this policy, email
          <a :href="`mailto:${CONTACT}`">{{ CONTACT }}</a>.
        </p>
      </template>
    </article>
  </div>
</template>

<style scoped>
.narrow { max-width: 760px; }
.page { padding: var(--s7) var(--s4); }
.section { padding: var(--s5); }
.prose h2 { margin-top: var(--s5); font-size: 1.1rem; }
.prose ul { padding-left: 1.2em; display: grid; gap: var(--s2); }
.prose p, .prose li { line-height: 1.7; }
</style>
