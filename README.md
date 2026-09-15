<p align="center"><img src="./frontend/public/favicon.svg" alt="Monash Hub Logo" width="120" /></p>

<h1 align="center">Monash Hub</h1>
<p align="center">Making Monash information easier to find and understand</p>

<p align="center">
  <a href="https://monashhub.secureview.tech"><img src="https://img.shields.io/badge/live-monash--hub-1e5eff" alt="Live site" /></a>
  <img src="https://img.shields.io/badge/status-in%20production-2ea44f" alt="Status: in production" />
  <img src="https://img.shields.io/badge/unofficial-not%20affiliated%20with%20Monash-black" alt="Unofficial" />
</p>

<p align="center"><a href="https://monashhub.secureview.tech">Visit Monash Hub</a></p>
<p align="center"><strong>English</strong> | <a href="./README.zh-CN.md">简体中文</a> | <a href="./README.ja.md">日本語</a> | <a href="./README.ko.md">한국어</a></p>

---

## What is Monash Hub?

Monash Hub is an independent information platform for Monash University students. It is designed especially to help non-native English speakers search for, understand and verify information about study and campus life.

Instead of switching between the Handbook, university websites, policy pages and student discussions, students can begin in one place and see clearly where each result comes from.

> Monash Hub is not affiliated with or endorsed by Monash University. For enrolment, visas, assessment and academic-policy decisions, always confirm details through Monash websites, the Handbook, Moodle or WES.

## What can you do here?

### Find unit information

- Search by unit code or title
- Check campuses, teaching periods, assessments, exams, requisites, learning outcomes and workload
- Verify details through the Handbook link and last-checked date

### Find official Monash information

- Search WAM, Special Consideration, census dates, visas, exchange and campus services
- Read curated official content with its source link and last-checked date
- Prioritise results labelled `Official Handbook` or `Official source`

### Understand information more easily

- Use the interface in Simplified Chinese, English, Japanese or Korean
- Read translated support for Handbook and official-guide content
- See translation provenance and links to the original page

### Plan your degree

- **Degrees**: what a degree is made of — how many credit points each group of requirements is worth, and which of its units your campus does not actually teach
- **Course map**: put units into semesters and have each one checked for you — whether your campus offers it, whether that teaching period offers it, and whether what it requires is sitting earlier in the plan
- **Unit tree**: follow a unit back to what it needs, or forward to what it unlocks; units your campus does not teach are marked rather than hidden

A plan lives only in your own browser. It is not uploaded and does not follow you to another device — use Export to move it.

### Work out your WAM / GPA

- Type a unit code and the credit points and level come from the Handbook; you do not have to remember the level weighting
- Malaysia uses CGPA, which is a different scale — switch between them
- You can also upload a screenshot of your WES results or paste the text, and have it read into the table
- Marks are worked out in your browser. They are not sent to a server and not stored on your account

### Join the student community

- Browse and search public questions and discussions
- Sign in to post, answer, vote, bookmark or report
- Read student experience linked to a particular unit
- Find study partners, activity companions or people with shared interests

Community content is student experience, not Monash University policy.

### MUM Guide

An index of the articles from the 马莫百科 WeChat account: searchable, grouped by topic, and linked back to the original post. Like the community, it is a student's write-up rather than official policy.

## How to use it

1. Search from the home page with a unit code, keyword or question.
2. Start with official results and open source links for important decisions.
3. Read results labelled `Community` when you need student experience.
4. Register with an email address to ask or answer questions.

## Source labels

| Label | Meaning |
| --- | --- |
| `Official Handbook` | Structured information from the Monash Handbook |
| `Official source` | Curated information from official Monash web pages |
| `Community` | Student questions, discussions and personal experience |

## Source and privacy boundary

The repository contains application source code, schema/migrations, deployment templates, tests and small synthetic parser fixtures. Production credentials, database dumps, user exports and raw crawl output do not belong in Git. The crawler links back to official sources rather than mirroring binary content.

See [Public release checklist](docs/PUBLIC-RELEASE.md) for the repository's privacy, secret and third-party-content boundary.

## For developers and contributors

This README is for product users. See [architecture](docs/ARCHITECTURE.md), [deployment](docs/DEPLOYMENT.md), [crawling](docs/CRAWLING.md), [public-release checklist](docs/PUBLIC-RELEASE.md), [roadmap](docs/ROADMAP-STATUS.md), [contribution rules](AGENTS.md) and the [changelog](CHANGELOG.md) for project work.

Development changes should use `feat/*`, `fix/*` or `chore/*` branches, with a Pull Request reviewed before merging into `main`.

## License and copyright

**Public visibility does not make this project open source.**

Copyright © 2026 Shuoxun Wen. All rights reserved.

The source code in this repository is made publicly visible for portfolio presentation, educational review and code inspection. Unless you have prior written permission from the copyright holder, no permission is granted to copy, modify, distribute, sublicense, sell, commercially use, deploy as a competing service, or create derivative products from this software.

GitHub features such as viewing, cloning or forking a public repository do not constitute an additional software licence from the copyright holder.

Third-party names, trademarks and source material — including Monash University names, marks and source content — remain the property of their respective rights holders and are not relicensed by this repository.

See [COPYRIGHT.md](COPYRIGHT.md) and [NOTICE.md](NOTICE.md) for the detailed ownership boundary.
