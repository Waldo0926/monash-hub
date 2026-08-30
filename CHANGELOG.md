# Changelog

All notable changes to Monash Hub are documented here.

## Unreleased

### Fixed

- Audited the Simplified-Chinese output of all 45 official guides, with
  page-specific human translations for policy labels, table cells and academic
  result terminology. This replaces misleading literal output such as `Yes` →
  `对`, `Pencil cases` → `笔会案件`, `First Class Honours` → `头等舱荣誉学位`,
  and weekday cells such as `Sat 01` → `卫星1号`; critical exam-rule sentences
  also retain their conditions and disciplinary consequences instead of being
  shortened into a different rule.
- Replaced the inconsistent unit-title output with a complete Simplified-Chinese
  baseline covering all 4,212 distinct titles in the 5,228-record 2026
  catalogue, so the Chinese interface no longer falls back to English names.
  The baseline remains explicitly machine-labelled and is overlaid by exact
  human-reviewed corrections, including `Accounting in business` → `商业会计`,
  `Assurance and audit services` → `鉴证与审计服务`, and high-risk curating,
  assurance, academic-literacy and communication terminology. Degree categories
  now use exact bilingual labels rather than renderings such as `大师研究型` and
  `PG主控制器`; changing the site language also reloads once so the selector
  and every navigation item cannot remain in different languages.
- Audited all 503 active degree records against their 2026 Handbook English
  titles and added 93 exact, human-reviewed Chinese title corrections, covering
  95 course codes. This fixes recurring errors such as *Business and Commerce*
  becoming 工商业, *Digital Media and Communication* becoming 数字媒体和通信,
  *Cardiovascular Perfusion* becoming 心血管输血, and *Aeromedical Retrieval*
  becoming 空中医疗检索, as well as broken partner names and Science Advanced
  subtitles. Curated seed rows now explicitly use human provenance, so they
  reliably override older machine translations and remain searchable.
- Chinese titles are searchable for units, degrees and official guides. The
  unified search did not include degrees at all, so a parent searching `理学学士`
  could not reach *Bachelor of Science*; translated unit and guide titles also
  depended on a separately refreshed index and exact title matches could sit
  below loosely related prose. Exact Chinese titles now rank first, the degree
  picker accepts Chinese too, and deploy/translation jobs refresh the longer
  Chinese content index automatically.
- Search direct answers now refresh when the language changes. The rest of the
  search page switched languages immediately, but a unit answer such as FIT2004
  kept its old translated title until the query itself changed.
- Unit titles whose subject is a list ("Introduction to the history and theory
  of art") are reordered too. Only a subtitle after a colon is left alone now;
  skipping every title with an "and" in it had left ten reading 导论对艺术的历史和理论.
- A double degree whose second subject contains "and" is split correctly.
  *Master of Global Business and Master of Regulation and Compliance* had been
  cut at every "and", so nothing paired up and the whole name went to the
  translator as one subject - producing 大师 in front of 硕士.

- Degree and unit names are now composed rather than translated whole. English
  names a qualification front-to-back and Chinese back-to-front, and a general
  translator handled the words without the order: *Bachelor of Science* had lost
  its subject entirely (学士), *Master of Teaching* read 师傅 (a craftsman),
  *Master of Accounting* 大师会计 (a guru), and *Doctor of Podiatric Medicine*
  had become a paediatrician. 452 of the 502 degrees are now built from an
  award, a subject and any qualifiers; the rest are left to the ordinary path.
  The same reordering fixes unit titles - 65 of 123 "Introduction to X" units
  read 导论到X, and one read 导论改为学术研究, "the introduction was changed to
  academic research".
- A search that matches units no longer opens with "No official answer indexed
  for this yet". Searching *2102* showed that notice above five Handbook
  results, because the answer router looks up FAQs and official pages and never
  sees what the result list found.
- A prerequisite made of nested groups is written out instead of coming up
  blank. FIT2004 needs one of FIT1008/FIT1054/FIT2085 *and* one of
  MAT1830/FIT1058; its outer group names no units of its own, so the planner had
  been showing "需要先修完 。" with nothing after it.
- The WAM/GPA calculator is usable on a phone. Its seven columns had been
  squeezed to about thirty pixels each, so the values could not be read; each
  row is now its own labelled block. The page also stopped scrolling sideways -
  a grid column had been sized to its widest child's minimum, pushing a 375px
  phone to 497px.

### Added

- Mobile navigation now includes a More menu with every destination from the
  desktop header, and the home page shows the same eight destinations directly
  in a responsive quick-access grid.

### Fixed

- Production deploys now apply the curated seed automatically, so
  human-reviewed unit titles such as `FIT2085` (工程师算法基础), `FIT1054`
  (算法基础（进阶）), and `ENG1014` (工程数值分析) cannot remain hidden behind
  older machine translations merely because a separate seed command was
  missed.
- A free elective part of a degree is now credited with the units no other part
  uses, instead of only the handful it happens to list. "Part E. Free elective
  studies" read 0/48 for a student whose plan held twelve units that counted
  towards it. 55 degrees have such a part.
- The plan checker reports what each unit is worth, not only the total, so units
  the degree does not name are no longer scored as zero credit points.
- The degree progress card no longer disappears when /plan is opened directly or
  reloaded. Which degree to load comes from the browser's own storage, so it is
  now fetched in the browser rather than on the server, which had no way to know
  it and was rendering the page against the API's index document.
- "major" and "minor" are translated as the academic senses in the prose
  describing how a degree is assembled, where that is what they always mean, and
  left to the translator elsewhere, where they are usually ordinary adjectives.
  "complete a major or minor from other courses" had been reading as an army
  rank and a child.
- "partner degree" no longer translates as a spouse.

### Documentation

- Added a direct production-site link to every language version of the README.
- Reworked the primary README as a Simplified Chinese, user-facing guide for students who need help finding and understanding Monash information.
- Added English, Japanese and Korean README versions, linked from every README.
- Clarified the separation between official Handbook data, official Monash sources and student community content.
- Documented community participation, including finding study partners, activity companions and students with shared interests, as a supporting feature.
- Moved developer-oriented references to the existing documentation set instead of placing local setup instructions in the user-facing README.

## Pull request history / PR 历史

This index records every pull request, including small fixes that do not need a
long release note. A closed PR that was not merged is labelled explicitly and
is not presented as shipped code.

这里记录每一个 PR，包括不需要单独撰写长篇发布说明的小修复。未合并就关闭的
PR 会明确标注，不会被误写成已经上线的功能。

### 2026-08-31

- [#79](https://github.com/Waldo0926/monash-hub/pull/79) Audit Chinese translations across all official guides / 全面审查 45 篇官方指南的简体中文翻译，修复考试规则、成绩等级、日历日期及其他政策术语误译。

### 2026-08-30

- [#78](https://github.com/Waldo0926/monash-hub/pull/78) Review Chinese unit titles and degree categories / 为 2026 Handbook 全部课程名称提供完整简体中文基线，校正会计课程与高风险错译，并修复学位分类和语言切换不一致。
- [#77](https://github.com/Waldo0926/monash-hub/pull/77) Audit every Chinese degree title / 全面检查 503 条在用学位记录，人工校对 93 个中文名称并确保其覆盖旧机器译文。
- [#76](https://github.com/Waldo0926/monash-hub/pull/76) Make Chinese titles searchable and refresh answers after language changes / 支持用中文搜索课程、学位和官方指南，切换语言后刷新直达答案，并补齐 #68–#75 的 Changelog 记录。

### 2026-08-29

- [#75](https://github.com/Waldo0926/monash-hub/pull/75) Describe the half of the site the README never mentioned / 补全 README 中遗漏的核心功能说明。
- [#74](https://github.com/Waldo0926/monash-hub/pull/74) Do not compose a name around a full stop / 遇到完整句号时不再错误拼接课程名称。
- [#73](https://github.com/Waldo0926/monash-hub/pull/73) Put the brand blue back in the footer mark / 恢复页脚标志的品牌蓝色。
- [#72](https://github.com/Waldo0926/monash-hub/pull/72) Point the footer at the WeChat account, and sign it / 在页脚加入微信公众号说明和作者署名。
- [#71](https://github.com/Waldo0926/monash-hub/pull/71) Finish the degree and title composition / 完善学位名称与课程名称的组合翻译。
- [#70](https://github.com/Waldo0926/monash-hub/pull/70) Build a degree's name instead of translating it / 按中文语序组合学位名称，不再整句直译。
- [#69](https://github.com/Waldo0926/monash-hub/pull/69) A unit code is a request for the unit / 输入课程代码时直接展示对应课程答案。
- [#68](https://github.com/Waldo0926/monash-hub/pull/68) Stop a narrow pass from deleting a wide one / 防止局部翻译修正覆盖更完整的已有结果。
- [#67](https://github.com/Waldo0926/monash-hub/pull/67) Complete mobile navigation and clarify the home page / 补全手机导航，并明确首页主要与次要功能层级。
- [#66](https://github.com/Waldo0926/monash-hub/pull/66) Apply curated translations on every deploy / 每次部署时自动应用人工校对翻译。
- [#65](https://github.com/Waldo0926/monash-hub/pull/65) Fix long degree cards and add a bilingual PR template / 修复长学位卡片被挤成逐字竖排的问题，并新增中英文 PR 模板。
- [#64](https://github.com/Waldo0926/monash-hub/pull/64) Let people sign in with Google / 新增 Google 登录（尚未合并，需配置 OAuth 客户端后才会显示）。
- [#63](https://github.com/Waldo0926/monash-hub/pull/63) Count the units a free elective part is actually free to count / 让自由选修部分正确计算未被其他要求占用的课程。
- [#62](https://github.com/Waldo0926/monash-hub/pull/62) Blue header, black footer, and a mark that is not a monogram / 更新蓝色页眉、黑色页脚及新的品牌标志。
- [#61](https://github.com/Waldo0926/monash-hub/pull/61) Give someone a page of their own / 新增个人主页及相关账户展示。
- [#60](https://github.com/Waldo0926/monash-hub/pull/60) Credit a specialisation to the part that asks for one, and stop computers having buildings / 将专精方向计入正确的学位要求，并修正线上课程被误标为实体地点的问题。
- [#59](https://github.com/Waldo0926/monash-hub/pull/59) Screenshot import, the browser-translation note, and room for Chinese to breathe / 新增成绩截图导入、浏览器翻译提示，并改善中文界面排版空间。
- [#58](https://github.com/Waldo0926/monash-hub/pull/58) Let a Chinese query find something / 让中文关键词可以找到对应的英文官方内容及中文索引。
- [#57](https://github.com/Waldo0926/monash-hub/pull/57) A WAM and GPA calculator, and one row for the planner's filters / 新增 WAM/GPA 计算器，并整理选课规划器筛选栏。
- [#56](https://github.com/Waldo0926/monash-hub/pull/56) A hand-written paragraph was never being read / 修复人工翻译段落未被读取的问题。
- [#55](https://github.com/Waldo0926/monash-hub/pull/55) Let the hand-written sentence win / 让人工翻译句子优先于机器翻译结果。
- [#54](https://github.com/Waldo0926/monash-hub/pull/54) Anonymous posts, threaded replies, and a like button that works / 新增匿名发帖、嵌套回复，并修复点赞功能。
- [#53](https://github.com/Waldo0926/monash-hub/pull/53) Keep the nesting in a requisite rule / 保留先修规则的嵌套结构，避免复杂条件被错误扁平化。
- [#52](https://github.com/Waldo0926/monash-hub/pull/52) Fix the headings the full pass exposed / 修复完整翻译流程暴露出的标题问题。
- [#51](https://github.com/Waldo0926/monash-hub/pull/51) Refetch when the controls change / 在筛选条件变化时重新获取对应数据。

### 2026-08-28

- [#50](https://github.com/Waldo0926/monash-hub/pull/50) Pin the words a degree structure uses for itself / 固定学位结构中的关键术语，避免机器误译。
- [#49](https://github.com/Waldo0926/monash-hub/pull/49) Translate what the page shows, not what it stores / 只翻译页面显示值，不改动数据库中的官方原始值。
- [#48](https://github.com/Waldo0926/monash-hub/pull/48) Add the course map, and check it against the Handbook / 新增学位课程地图，并依据 Handbook 校验结构。
- [#47](https://github.com/Waldo0926/monash-hub/pull/47) Show a degree, in Chinese, marked for your campus / 以中文展示学位结构，并标明课程是否在所选校区开设。
- [#46](https://github.com/Waldo0926/monash-hub/pull/46) Widen `aqf_level`: a double degree carries two of them / 扩展 `aqf_level` 字段以支持双学位的两个 AQF 等级。
- [#45](https://github.com/Waldo0926/monash-hub/pull/45) Crawl what a degree is made of / 抓取并保存学位组成、要求组和专业方向。
- [#44](https://github.com/Waldo0926/monash-hub/pull/44) Write out the unit titles the machine cannot do / 为机器无法可靠处理的课程名称提供人工译文。
- [#43](https://github.com/Waldo0926/monash-hub/pull/43) Draw the prerequisite graph, scoped to a campus / 新增按校区筛选的先修课程关系图。
- [#42](https://github.com/Waldo0926/monash-hub/pull/42) Pin a term in the plural, not only in the singular / 让术语表同时保护单数和复数形式。
- [#41](https://github.com/Waldo0926/monash-hub/pull/41) Make a grade a whole value, not a word inside a sentence / 将成绩等级作为完整字段处理，避免被当成句中普通单词翻译。
- [#40](https://github.com/Waldo0926/monash-hub/pull/40) Scope the guides by category, fix credit, and close the blank-line gaps / 按类别限定指南搜索，修正学分显示并清理多余空行。
- [#39](https://github.com/Waldo0926/monash-hub/pull/39) Put the Malaysia systems in their own column, beside the others / 将马来西亚校区系统入口整理为独立页脚栏。
- [#38](https://github.com/Waldo0926/monash-hub/pull/38) Reject a mask the model repeated instead of copying / 拒绝机器重复占位符而未正确还原术语的翻译结果。

### 2026-08-27

- [#37](https://github.com/Waldo0926/monash-hub/pull/37) Give the footer columns the widths they each need / 根据内容为页脚各栏分配合适宽度。
- [#36](https://github.com/Waldo0926/monash-hub/pull/36) Find a unit by part of its code, and line the footer up / 支持按部分课程代码搜索，并对齐页脚布局。
- [#35](https://github.com/Waldo0926/monash-hub/pull/35) Let every grid column shrink below its content / 允许网格列缩小到内容最小宽度以下，防止页面横向溢出。
- [#34](https://github.com/Waldo0926/monash-hub/pull/34) Stop the page scrolling sideways, and scope the visa answers / 修复移动端横向滚动，并限制签证答案的适用范围。
- [#33](https://github.com/Waldo0926/monash-hub/pull/33) Malaysia pages translated, and the systems students log into / 翻译马来西亚校区页面，并加入学生常用系统入口。
- [#32](https://github.com/Waldo0926/monash-hub/pull/32) Put the campus migration back on the end of the chain / 修正校区数据库迁移的依赖顺序。
- [#31](https://github.com/Waldo0926/monash-hub/pull/31) Say which campus a guide page is for / 在指南页面明确标注适用校区。
- [#30](https://github.com/Waldo0926/monash-hub/pull/30) Give the Mamo Guide page its logo / 为马莫指南页面加入品牌标志。
- [#29](https://github.com/Waldo0926/monash-hub/pull/29) Every guide page written by a person / 为所有指南页面提供人工撰写的中文内容。
- [#28](https://github.com/Waldo0926/monash-hub/pull/28) Hand-written Chinese for the guides, and the Mamo Guide page / 为指南及马莫指南页面加入人工中文翻译。
- [#25](https://github.com/Waldo0926/monash-hub/pull/25) Full Chinese on the Chinese site, and a unit filter that means what it says / 完善中文站内容，并修复课程筛选条件与界面文字不一致的问题。

### 2026-08-26

- [#27](https://github.com/Waldo0926/monash-hub/pull/27) Add the production site link / 在 README 中加入生产网站链接。
- [#26](https://github.com/Waldo0926/monash-hub/pull/26) Add a multilingual user README / 新增面向用户的中、英、日、韩多语言 README。

### 2026-08-24

- [#24](https://github.com/Waldo0926/monash-hub/pull/24) Do not let the model sign its work with the name of a language / 清理机器翻译意外附加的语言名称。
- [#23](https://github.com/Waldo0926/monash-hub/pull/23) Keep the university's own name, and every date, out of the model's hands / 保护大学专名和日期，不交由机器翻译。
- [#22](https://github.com/Waldo0926/monash-hub/pull/22) Write the sentences the machine is not allowed to guess at / 为禁止机器猜测的关键句子提供人工译文。
- [#21](https://github.com/Waldo0926/monash-hub/pull/21) Only let a costly term hold a sentence back / 仅让真正影响学费或学业决定的术语阻止自动翻译。
- [#20](https://github.com/Waldo0926/monash-hub/pull/20) Stop the tidying from closing a paragraph break / 防止翻译清理过程吞掉段落换行。
- [#19](https://github.com/Waldo0926/monash-hub/pull/19) Tidy a string that was all terms and no translation / 正确处理完全由受保护术语组成的文本。
- [#18](https://github.com/Waldo0926/monash-hub/pull/18) Give the translation pass the cores, and take the sharding back out / 让翻译任务使用多核并移除不合适的分片方案。
- [#17](https://github.com/Waldo0926/monash-hub/pull/17) Let the units pass be split across several processes / 支持把课程翻译任务分配到多个进程。
- [#16](https://github.com/Waldo0926/monash-hub/pull/16) Full Chinese on the guide pages, with the codes left alone / 完整翻译指南页面，同时保持课程代码等标识不变。

### 2026-08-23

- [#15](https://github.com/Waldo0926/monash-hub/pull/15) Make switching to English actually show English / 修复切换到英文后仍显示中文内容的问题。
- [#14](https://github.com/Waldo0926/monash-hub/pull/14) Stop showing students the CMS's own comments / 过滤 CMS 内部注释，避免向学生展示维护信息。
- [#13](https://github.com/Waldo0926/monash-hub/pull/13) Say census date the way the reviewed translations already say it / 统一 census date 的人工审核中文译法。
- [#12](https://github.com/Waldo0926/monash-hub/pull/12) Translate the content, with the terms that matter taken off the machine / 在关键术语保护机制下翻译官方内容。
- [#11](https://github.com/Waldo0926/monash-hub/pull/11) Machine-translate official content under a protected glossary / 尝试在术语保护下机器翻译官方内容；此 PR 已关闭且未合并，由 #12 取代。
- [#10](https://github.com/Waldo0926/monash-hub/pull/10) Chinese content, readable guide pages, and an email that always arrives / 加入中文内容和结构化指南页，并修复注册邮件静默不发送的问题。
- [#9](https://github.com/Waldo0926/monash-hub/pull/9) Stop the home page and footer leaving half the width empty / 重排首页和页脚，消除大面积空白并完善社区空状态。
- [#8](https://github.com/Waldo0926/monash-hub/pull/8) Stop `deploy.sh` sourcing `.env` as a shell script / 避免部署脚本把 Compose `.env` 当作 Shell 脚本执行。
- [#7](https://github.com/Waldo0926/monash-hub/pull/7) Verified accounts, answer notifications, and four interface languages / 新增邮箱验证与密码恢复、回答通知、四语言界面及并发计数修复。
- [#6](https://github.com/Waldo0926/monash-hub/pull/6) Crawl every 2026 unit, not just the twenty fixtures / 将 Handbook 抓取从 20 个测试课程扩展到全部 2026 课程。
- [#5](https://github.com/Waldo0926/monash-hub/pull/5) Key API fetches by path so the SSR payload reaches the client / 统一 SSR 与浏览器的 API 缓存键，修复 hydration 丢失数据。
- [#4](https://github.com/Waldo0926/monash-hub/pull/4) Render “last checked” in UTC so the server and browser agree / 使用 UTC 渲染最后检查日期，避免服务端与浏览器 hydration 不一致。
- [#3](https://github.com/Waldo0926/monash-hub/pull/3) Resolve the search answer during SSR so hydration keeps the results / 在 SSR 阶段获取搜索答案，避免 hydration 后结果消失。
- [#2](https://github.com/Waldo0926/monash-hub/pull/2) Correct what the first production deploy exposed / 修复首次生产部署暴露的 nginx、证书、sitemap 和部署文档问题。
- [#1](https://github.com/Waldo0926/monash-hub/pull/1) Resolve the frontend lockfile so `npm ci` can install it / 修复前端 lockfile，使 CI 和 Docker 构建可以正常执行 `npm ci`。

### Foundation / 初始版本

- `81173a4` Stage 0 foundation: Handbook parser, official knowledge seed, zero-AI QA, and community / 建立 Handbook 解析器、官方知识种子、零 AI 问答和学生社区的项目基础。
