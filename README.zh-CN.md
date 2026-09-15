<p align="center"><img src="./frontend/public/favicon.svg" alt="Monash Hub Logo" width="120" /></p>

<h1 align="center">Monash Hub</h1>
<p align="center">帮助学生更轻松地查找和理解 Monash 信息</p>
<p align="center"><a href="https://monashhub.secureview.tech">进入 Monash Hub 网站</a></p>
<p align="center"><a href="./README.md">English</a> | <strong>简体中文</strong> | <a href="./README.ja.md">日本語</a> | <a href="./README.ko.md">한국어</a></p>

---

## Monash Hub 是什么？

Monash Hub 是一个面向蒙纳士大学学生的独立信息平台。它尤其帮助非英语母语学生更轻松地搜索、理解和核实与 Monash 学习和校园生活相关的信息。

你不必在 Handbook、官网、政策页面和学生讨论之间反复切换。Monash Hub 将常用信息整理到同一个入口，并清楚说明每一条内容来自哪里。

> Monash Hub 不隶属于，也未获 Monash University 官方认可。选课、签证、评估、学术政策等重要事项，请始终以 Monash 官网、Handbook、Moodle 或 WES 为准。

## 你可以做什么？

### 查课程信息

- 按 Unit code 或课程名称搜索
- 查看开课校区、教学期、考核、考试、先修/同修要求、学习成果和预期工作量
- 通过 Handbook 原始链接和最近检查时间核实信息

### 查 Monash 官方信息

- 搜索 WAM、Special Consideration、Census Date、签证、交换和校园服务等常见主题
- 查看经过整理的官方内容、来源链接和最近检查时间
- 优先阅读带有 `Official Handbook` 或 `Official source` 标识的结果

### 更容易理解信息

- 使用简体中文、英语、日语或韩语界面
- 阅读 Handbook 与官方指南的翻译辅助内容
- 查看清楚标示的翻译来源与原始页面链接

### 规划你的学位

- **学位**：一个学位由什么构成——每一组要求各占多少学分，以及其中哪些课你所在的校区其实不开
- **选课规划**：把课排进各个学期，每一门都替你核对本校区开不开、那个学期开不开、它要求的课有没有排在更早的位置
- **先修图**：沿着一门课往回看它需要先修哪些课，或者往前看它能解锁哪些课；本校区不开的课不会被隐藏，而是标出来

规划只存在你自己的浏览器里，不会上传，也不会跟着你到别的设备——要转移请用「导出」。

### 算 WAM / GPA

- 输入课程代码，学分和课程级别直接从 Handbook 带出来，级别权重不用自己记
- 马来西亚校区用的是 CGPA，那是另一套刻度，可以切换
- 也可以上传 WES 成绩截图或粘贴文本，自动识别成表格
- 分数只在你的浏览器里计算，不会发到服务器，也不会存进账号

### 参与学生社区

- 浏览和搜索公开问题与讨论
- 登录后提问、回答、投票、收藏和举报
- 查看与特定 Unit 相关的学生经验
- 在社区中寻找学习搭子、活动同伴或兴趣相近的同学

社区内容代表学生个人经验，不代表 Monash University 的官方规定。

### 马莫百科

「马莫百科」微信公众号的文章索引，可以直接搜索、按主题浏览，并跳转到公众号原文阅读。公众号内容同样是学生视角的整理，不是官方规定。

## 如何使用

1. 在首页输入 Unit code、关键词或问题。
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

仓库可以公开应用源码、数据结构/迁移、部署模板、测试以及用于测试解析逻辑的小型合成 fixture。生产环境密码、API key、SSH 私钥、数据库备份、用户导出以及真实抓取输出不应进入 Git。

抓取器保留官方来源链接，并只提取产品需要的结构化字段和文本，不把第三方页面当作镜像保存。公开前检查项目边界可查看 [Public release checklist](docs/PUBLIC-RELEASE.md)。

## 给开发者与贡献者

本 README 面向产品使用者。架构、部署、抓取和本地开发说明请查看：

- [架构说明](docs/ARCHITECTURE.md)
- [部署说明](docs/DEPLOYMENT.md)
- [抓取说明](docs/CRAWLING.md)
- [公开发布检查清单](docs/PUBLIC-RELEASE.md)
- [产品路线图](docs/ROADMAP-STATUS.md)
- [贡献规则](AGENTS.md)
- [更新日志](CHANGELOG.md)

开发改动请使用 `feat/*`、`fix/*` 或 `chore/*` 分支，发起 Pull Request 审查后再合并到 `main`。
