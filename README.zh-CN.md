<p align="center"><img src="./frontend/public/favicon.svg" alt="Monash Hub Logo" width="120" /></p>

<h1 align="center">Monash Hub</h1>
<p align="center">帮助学生更轻松地查找和理解 Monash 信息</p>

<p align="center">
  <a href="https://monashhub.secureview.tech"><img src="https://img.shields.io/badge/live-monash--hub-1e5eff?style=for-the-badge" alt="线上站点" /></a>
  <a href="https://github.com/Waldo0926/monash-hub/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/Waldo0926/monash-hub/ci.yml?branch=main&style=for-the-badge&label=CI" alt="CI" /></a>
  <img src="https://img.shields.io/badge/status-in%20production-2ea44f?style=for-the-badge" alt="状态：正式运行" />
  <a href="https://waldo0926.github.io/uptime/history/monash-hub"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2FWaldo0926%2Fuptime%2FHEAD%2Fapi%2Fmonash-hub%2Fuptime.json&style=for-the-badge" alt="在线率" /></a>
  <img src="https://img.shields.io/badge/unofficial-not%20affiliated%20with%20Monash-black?style=for-the-badge" alt="非官方" />
</p>

<p align="center"><a href="https://monashhub.secureview.tech">进入 Monash Hub 网站</a></p>
<p align="center"><a href="./README.md">English</a> | <strong>简体中文</strong></p>

---

<p align="center"><img src="./docs/images/home-zh.webp" alt="Monash Hub 首页：搜索框和下面的 8 个入口、重要日期、当季指南和马莫百科" width="900" /></p>

## Monash Hub 是什么？

Monash Hub 把课程、学位、选课规划、WAM/GPA、重要日期、马来西亚学费、官方指南和学生社区都集中在一个地方，Monash 学习生活一站查清。它尤其帮助非英语母语学生更轻松地搜索、理解和核实与 Monash 学习和校园生活相关的信息。

你不必在 Handbook、官网、政策页面和学生讨论之间反复切换。Monash Hub 将常用信息整理到同一个入口，并清楚说明每一条内容来自哪里。

> Monash Hub 不隶属于，也未获 Monash University 官方认可。选课、签证、评估、学术政策等重要事项，请始终以 Monash 官网、Handbook、Moodle 或 WES 为准。

## 为什么还要做一个网站？

以前学生有问题，要去三个地方找，每个地方只管一部分：

| 去哪找 | 擅长 | 缺什么 |
| --- | --- | --- |
| [Monash Handbook](https://handbook.monash.edu) | 课程和学位的官方记录 | 只有英文，也只有课程和学位；政策、签证、重要日期在别的网站 |
| monash.edu 和 monash.edu.my | 两个校区各自的官方指南 | 两个网站加起来约 3,100 页，而且两边规则不一样（签证、保险、课程变动） |
| 学生群和共享文档 | 中文，回得快 | 没有出处，经常是往年的或另一个校区的 |

之前也有学生做过工具。[MonPlan](https://github.com/MonPlan) 是学生做的选课规划工具，它公开的爬虫（[MonScrape](https://github.com/MonPlan/MonScrape)）最后一次更新是 2017 年，读的还是旧版 Handbook 页面。monashcoding 的 [TheBetterHandbookAPI](https://github.com/monashcoding/TheBetterHandbookAPI) 记录了 Handbook 搜索接口的用法（最后提交是 2022 年 9 月）。这两个都不管政策，也没有中文。

Monash Hub 保留了它们做对的地方，数据直接来自 Handbook，再补上其余部分：两个校区的官方页面和课程放在一起，每条结果都标出处和最后核对的日期，马来西亚和澳洲规则不同时并排显示，中文翻译附英文原文链接。网站的提问面板只在这些资料里搜，不用生成式模型写答案。它同时会把问题转给马莫百科的微信机器人，机器人先用公众号主人教过的回答和公众号文章来答；这些都没有的话，可能会让一个免费语言模型从官方页面里挑句子，每句发出前都会和原页面逐字核对。机器人的回答单独放一块，标着「来自马莫百科」。

## 技术栈

当前生产环境技术栈：

- **前端：** Nuxt 4、Vue 3、TypeScript，采用 SSR 服务端渲染
- **后端：** FastAPI、Python
- **数据库与搜索：** PostgreSQL 17，使用 `tsvector`、GIN 索引和 `pg_trgm` 实现全文检索与模糊匹配
- **基础设施：** Docker Compose、Nginx、HTTPS
- **测试：** pytest（连真实 PostgreSQL）、Vitest，以及在桌面和手机尺寸下跑的 Playwright 浏览器测试，部署前都在 CI 里跑
- **数据同步：** Python 爬虫，采用基于内容哈希的增量同步与失败保护机制
- **生产环境：** [monashhub.secureview.tech](https://monashhub.secureview.tech)

当前生产请求链路为：Nginx → Nuxt SSR 提供网页界面，Nginx → FastAPI 处理 `/api/*` 请求，PostgreSQL 运行在私有 Docker 网络中。完整系统设计见 [架构说明](docs/ARCHITECTURE.md)。

## 一些数字（2026 年 10 月 29 日）

| | |
| --- | --- |
| 官方指南登记的页面 | 2,917 页，来自两个网站的 sitemap，之前是 662 页 |
| 后端测试 | 891 个测试函数，CI 里连真实 PostgreSQL 跑 |
| 前端和浏览器测试 | 77 个 Vitest 测试；22 个 Playwright 测试，桌面和手机尺寸都跑 |
| 翻译模型 | 智谱免费的 `glm-4.5-flash`。对照英文读了三个免费模型翻的 70 段后选的（`glm-4-flash` 会把条件句译反） |
| 部署 | 每次合并到 `main` 自动部署，部署后对线上网站跑冒烟检查，不通过就退回上一版 |

出处：[更新日志](CHANGELOG.md)，以及 `backend/tests`、`frontend`、`e2e` 里的测试文件。

## 你可以做什么？

### 查课程信息

- 按 Unit code 或课程名称搜索
- 查看开课校区、教学期、考核、考试、先修/同修要求、学习成果和预期工作量
- 通过 Handbook 原始链接和最近检查时间核实信息

<p align="center"><img src="./docs/images/unit-en.webp" alt="FIT2004 课程页：院系通知、学分、校区、考核、开课学期和 Handbook 来源链接" width="900" /></p>
<p align="center"><sub>首页截图来自线上站点。其余截图来自浏览器测试用的整套环境：真实站点跑在三门虚构课程（FIT1008、FIT2004、FIT2102）和一个虚构学位上，课程名、分数和规划都是编的，线上显示的是 Handbook 数据。</sub></p>

### 查 Monash 官方信息

- 搜索 WAM、Special Consideration、Census Date、签证、交换和校园服务等常见主题
- 查看经过整理的官方内容、来源链接和最近检查时间
- 优先阅读带有 `Official Handbook` 或 `Official source` 标识的结果

### 更容易理解信息

- 使用简体中文或英语界面
- 阅读 Handbook 与官方指南的翻译辅助内容
- 查看清楚标示的翻译来源与原始页面链接

### 规划你的学位

- **学位**：一个学位由什么构成，每一组要求各占多少学分，以及其中哪些课你所在的校区其实不开
- **选课规划**：把课排进各个学期，每一门都替你核对本校区开不开、那个学期开不开、它要求的课有没有排在更早的位置
- **先修图**：沿着一门课往回看它需要先修哪些课，或者往前看它能解锁哪些课；本校区不开的课不会被隐藏，而是标出来

这三个工具在顶部导航的「选课工具」菜单里。

规划只保存在你自己的浏览器里，不会存进账号。每次核对时会把规划发给接口和 Handbook 比对，核对完不会保留。想在另一台设备上打开，就在选课规划的「更多」菜单里点「复制规划码」：它会复制一个链接，规划写在 `#` 后面，浏览器不会把这部分发给服务器。在另一台设备上打开这个链接，或者把它粘贴到「粘贴规划码」里就行。想留一份文件的话，「导出」也还能用。

<p align="center"><img src="./docs/images/plan-en.webp" alt="课程地图：四门课排进学期，每门按校区、教学期和先修逐一检查，右侧是对照学位要求的进度" width="900" /></p>

### 算 WAM / GPA

- 输入课程代码，学分和课程级别直接从 Handbook 带出来，级别权重不用自己记
- 马来西亚校区用的是 CGPA，那是另一套刻度，可以切换
- 也可以上传 WES 成绩截图或粘贴文本，自动识别成表格
- 分数只在你的浏览器里计算，不会存进账号。只有你输入的课程代码会发给接口查学分和级别，分数本身不离开你的设备

<p align="center"><img src="./docs/images/marks-en.webp" alt="WAM / GPA 计算器：三门课按年级分组，右侧显示 WAM 和 CGPA" width="900" /></p>

### 查马来西亚校区学费

- `/fees` 列出马来西亚校区本科和研究生学费页上的每一行，按层次和学院分组，可以按课程名筛选
- 每项学费都写明是按年还是整个课程，以及和 2026 年比涨了多少（例如「vs 2026: +RM 2,880 (+5.3%)」）
- 按马来西亚校区查看学位页时，会显示这个学位自己的学费
- 金额直接读自网站已经收录的学费页，这两页每两天重新读一次，所以 monash.edu.my 上改了价，这里不用手动录入也会跟着变。读不成数字的金额会按 Monash 原样显示，并加一条提醒

### 重要日期

- 首页显示你所在校区接下来的几个学术日期：census、退课截止、SWOT vac、考试和出成绩
- `/dates` 按月份列出所有即将到来的日期，包括 Allocate+ 和 WES 续注册的时间段，公共假期可以隐藏

### 给家长的页面

`/parents` 是写给考虑马来西亚校区的家长看的中文页面：学校概况和 SETARA 评级、世界排名、毕业证书、按高考、A-Level、IB、AP、SAT、ACT、MUFY 和 CIMP 列出的录取分数、预科和文凭两条路线、奖学金、转去澳洲校区、交换项目、含 6% 服务税的学费和人民币估算、签证费、生活费、校园生活，以及学校能告诉家长哪些信息。每条官方信息都附英文原页链接，并写明核对日期。

### 直接提问

除了搜索页，每个页面右下角都有「提问」按钮。面板会从 Handbook、官方页面和马莫百科文章里找答案，也会显示马莫百科机器人知道的内容（见[为什么还要做一个网站？](#为什么还要做一个网站)）。两边都答不上来时，会显示公众号二维码，可以把问题发到公众号，之后再回复。

### 参与学生社区

- 浏览和搜索公开问题与讨论
- 登录后提问、回答、投票、收藏和举报
- 查看与特定 Unit 相关的学生经验
- 在社区中寻找学习搭子、活动同伴或兴趣相近的同学

社区内容代表学生个人经验，不代表 Monash University 的官方规定。

### 马莫百科

「马莫百科」微信公众号的文章索引，可以直接搜索、按主题浏览，并跳转到公众号原文阅读。公众号内容同样是学生视角的整理，不是官方规定。

## 如何使用

1. 在首页输入 Unit code、关键词或问题，或者点搜索框下面的 8 个入口之一。
2. 优先查看官方来源的结果；重要事项请打开原始链接确认。
3. 需要真实学习体验时，再阅读带有 `Community` 标识的讨论。
4. 需要提问或回答时，用邮箱注册并登录。

## 信息来源说明

| 标识 | 含义 |
| --- | --- |
| `Official Handbook` | 来自 Monash Handbook 的结构化课程信息 |
| `Official source` | 来自 Monash 官方网页的已整理信息 |
| `Community` | 由学生发布的个人经验、问题或讨论 |

三类内容会明确区分展示。学生经验有助于了解实际情况，但不能替代官方政策。

## 源码与隐私边界

仓库可以公开应用源码、数据结构/迁移、部署模板、测试以及用于测试解析逻辑的小型合成 fixture。生产环境密码、API key、SSH 私钥、数据库备份、用户导出以及真实抓取输出不应进入 Git。爬虫只保留指向官方来源的链接，不镜像图片、PDF 等二进制文件；它一次只发一个请求、每次间隔几秒，请求里写明自己的名字（`MonashHubBot`），抓 Monash 官方页面前先读 `robots.txt`。详见 [抓取说明](docs/CRAWLING.md)。

抓取器保留官方来源链接，并只提取产品需要的结构化字段和文本，不把第三方页面当作镜像保存。公开前检查项目边界可查看 [Public release checklist](docs/PUBLIC-RELEASE.md)。

## 给开发者与贡献者

本 README 面向产品使用者。架构、部署、抓取和本地开发说明请查看：

- [架构说明](docs/ARCHITECTURE.md)
- [架构决策记录](docs/adr/README.md)
- [部署说明](docs/DEPLOYMENT.md)
- [抓取说明](docs/CRAWLING.md)
- [公开发布检查清单](docs/PUBLIC-RELEASE.md)
- [产品路线图](docs/ROADMAP-STATUS.md)
- [贡献规则](AGENTS.md)
- [更新日志](CHANGELOG.md)

开发改动请使用 `feat/*`、`fix/*` 或 `chore/*` 分支，发起 Pull Request 审查后再合并到 `main`。

### 本地运行

浏览器测试自带了整套运行环境：PostgreSQL、API、前端的生产构建，以及一个把它们放到同一来源的小代理（线上由 nginx 做这件事），数据是合成的。

```sh
createdb monashhub_e2e
pip install -r backend/requirements.txt
(cd frontend && npm ci && npm run build)
(cd e2e && npm ci && npx playwright install chromium)
cd e2e && DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/monashhub_e2e npx playwright test
```

Playwright 会跑迁移、载入 `e2e/seed.py`、在 8100、3101、3100 端口起三个服务，跑完测试再停掉。想留着站点自己看，就按 [e2e/README.md](e2e/README.md) 里列的命令手动启动。真实的 Handbook 和官方页面数据由爬虫抓取，见[抓取说明](docs/CRAWLING.md)。后端测试在 `backend/` 下跑 `pytest`，前端测试在 `frontend/` 下跑 `npm test`。

## 版权与使用许可

**仓库公开可见，并不意味着本项目属于开源软件。**

Copyright © 2026 Waldo. All rights reserved.

本仓库源码公开用于作品展示、教育性审阅和代码检查。除非事先取得版权所有者的书面许可，否则不授予复制、修改、分发、再授权、出售、商业使用、部署为竞争性服务，或基于本软件制作衍生产品的权利。

GitHub 对公开仓库提供的查看、Clone 或 Fork 等功能，不代表版权所有者额外授予了软件使用许可。

第三方名称、商标及来源内容，包括 Monash University 的名称、标识和来源材料，其权利仍归各自权利人所有，本仓库不会对这些第三方内容重新授权。

详细的所有权边界请查看 [COPYRIGHT.md](COPYRIGHT.md) 和 [NOTICE.md](NOTICE.md)。
