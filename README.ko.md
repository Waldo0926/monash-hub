<p align="center"><img src="./frontend/public/favicon.svg" alt="Monash Hub Logo" width="120" /></p>

<h1 align="center">Monash Hub</h1>
<p align="center">Monash 정보를 더 쉽게 찾고 이해할 수 있도록</p>

<p align="center">
  <a href="https://monashhub.secureview.tech"><img src="https://img.shields.io/badge/live-monash--hub-1e5eff?style=for-the-badge" alt="운영 사이트" /></a>
  <a href="https://github.com/Waldo0926/monash-hub/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/Waldo0926/monash-hub/ci.yml?branch=main&style=for-the-badge&label=CI" alt="CI" /></a>
  <img src="https://img.shields.io/badge/status-in%20production-2ea44f?style=for-the-badge" alt="상태: 운영 중" />
  <img src="https://img.shields.io/badge/unofficial-not%20affiliated%20with%20Monash-black?style=for-the-badge" alt="비공식" />
</p>

<p align="center"><a href="https://monashhub.secureview.tech">Monash Hub 열기</a></p>
<p align="center"><a href="./README.md">English</a> | <a href="./README.zh-CN.md">简体中文</a> | <a href="./README.ja.md">日本語</a> | <strong>한국어</strong></p>

---

<p align="center"><img src="./docs/images/home-en.webp" alt="Monash Hub 홈 화면: 검색, 말레이시아와 호주의 주요 일정, 유닛·수강 계획·가이드 바로가기" width="900" /></p>

## Monash Hub이란?

Monash Hub은 모나쉬 대학교 학생을 위한 독립 정보 플랫폼입니다. 특히 영어가 모국어가 아닌 학생이 학업 및 캠퍼스 생활과 관련된 Monash 정보를 더 쉽게 검색하고, 이해하고, 확인할 수 있도록 설계되었습니다.

Handbook, 대학 웹사이트, 규정 페이지, 학생 토론을 오갈 필요 없이 한 곳에서 필요한 정보를 찾고 각 결과의 출처를 확인할 수 있습니다.

> Monash Hub은 Monash University와 제휴하거나 공식 승인을 받은 서비스가 아닙니다. 수강 신청, 비자, 평가 및 학사 규정과 관련된 중요한 사항은 Monash 공식 웹사이트, Handbook, Moodle 또는 WES에서 반드시 확인하세요.

## 왜 사이트를 하나 더 만들었나요?

전에는 학생이 궁금한 것이 생기면 세 곳을 찾아봐야 했고, 어느 곳도 전부를 다루지는 않았습니다.

| 어디서 | 잘하는 것 | 부족한 것 |
| --- | --- | --- |
| [Monash Handbook](https://handbook.monash.edu) | 유닛과 과정의 공식 기록 | 영어만 있고 유닛과 과정만 다룸. 규정, 비자, 주요 일정은 다른 사이트에 있음 |
| monash.edu와 monash.edu.my | 캠퍼스별 공식 가이드 | 두 사이트를 합치면 약 3,100페이지이고, 캠퍼스마다 규정이 다름(비자, 보험, 유닛 변경) |
| 학생 단체 채팅방과 공유 문서 | 중국어로 빠르게 답을 얻음 | 출처가 없고, 지난 학년도나 다른 캠퍼스 정보인 경우가 많음 |

학생이 만든 도구는 전에도 있었습니다. [MonPlan](https://github.com/MonPlan)은 학생이 만든 수강 계획 도구로, 공개된 크롤러([MonScrape](https://github.com/MonPlan/MonScrape))는 2017년에 마지막으로 업데이트되었고 예전 Handbook 페이지를 읽습니다. monashcoding의 [TheBetterHandbookAPI](https://github.com/monashcoding/TheBetterHandbookAPI)는 Handbook 검색 엔드포인트 사용법을 정리해 두었습니다(마지막 커밋 2022년 9월). 둘 다 규정이나 다른 언어는 다루지 않습니다.

Monash Hub는 이들이 잘한 점, 즉 Handbook에서 바로 가져온 데이터는 그대로 두고 나머지를 더했습니다. 두 사이트의 공식 페이지를 유닛과 함께 보여 주고, 모든 결과에 출처와 마지막 확인 날짜를 표시하며, 말레이시아와 호주의 규정이 다르면 나란히 보여 주고, 중국어 번역에는 영어 원문 링크를 붙였습니다. 사이트 도우미는 이 자료들을 검색할 뿐, 생성형 모델로 답을 쓰지 않습니다.

## 기술 스택

현재 운영 환경 구성:

- **프론트엔드:** Nuxt 4, Vue 3, TypeScript, SSR 렌더링
- **백엔드:** FastAPI와 Python
- **데이터베이스와 검색:** PostgreSQL 17. `tsvector`, GIN 인덱스, `pg_trgm`으로 전문 검색과 유사 검색
- **인프라:** Docker Compose, Nginx, HTTPS
- **테스트:** 실제 PostgreSQL에 연결하는 pytest, Vitest, 데스크톱과 휴대폰 화면 크기에서 도는 Playwright 브라우저 테스트. 모두 배포 전에 CI에서 실행
- **데이터 파이프라인:** Python 크롤러. 내용 해시 기반 증분 동기화와, 실패 시 기존 데이터를 지키는 저장 처리
- **운영 환경:** [monashhub.secureview.tech](https://monashhub.secureview.tech)

운영 요청 경로는 웹 화면이 Nginx → Nuxt SSR, `/api/*`가 Nginx → FastAPI이며, PostgreSQL은 비공개 Docker 네트워크에서 동작합니다. 현재 시스템 설계는 [architecture](docs/ARCHITECTURE.md)를 참고하세요.

## 숫자로 보기 (2026년 10월 25일 기준)

| | |
| --- | --- |
| 가이드에 수록한 공식 페이지 | 두 사이트의 sitemap에서 약 3,100페이지 (이전 662페이지) |
| 백엔드 테스트 | 테스트 함수 799개, CI에서 실제 PostgreSQL로 실행 |
| 프런트엔드와 브라우저 테스트 | Vitest 48개, 데스크톱과 휴대폰 크기에서 Playwright 13개 |
| 번역 모델 | Zhipu의 무료 모델 `glm-4.5-flash`. 무료 모델 세 개의 번역을 영어 원문과 70단락 비교한 뒤 선택 (`glm-4-flash`는 조건을 반대로 번역함) |
| 배포 | `main`에 병합할 때마다 자동 배포. 배포 후 실제 사이트에 스모크 검사를 하고, 실패하면 이전 버전으로 되돌림 |

출처: [변경 기록](CHANGELOG.md)과 `backend/tests`, `frontend`, `e2e`의 테스트 파일.

## 할 수 있는 일

### Unit 정보 찾기

- Unit code 또는 과목명으로 검색
- 개설 캠퍼스, 수업 기간, 평가, 시험, 선수/동시 이수 요건, 학습 성과 및 학습량 확인
- Handbook 원문 링크와 최종 확인일로 정보 검증

### Monash 공식 정보 찾기

- WAM, Special Consideration, census date, 비자, 교환학생, 캠퍼스 서비스 등의 주제 검색
- 출처 링크와 최종 확인일이 포함된 공식 정보 읽기
- `Official Handbook` 또는 `Official source` 표시가 있는 결과 우선 확인

### 정보를 더 쉽게 이해하기

- 중국어 간체, 영어, 일본어, 한국어 인터페이스 사용
- Handbook 및 공식 가이드의 번역 보조 내용 확인
- 번역 출처와 원문 페이지 링크 확인

### 학위 계획하기

- **학위**: 학위가 무엇으로 이루어져 있는지, 각 요건 그룹의 학점과, 그중 어떤 과목이 내 캠퍼스에서는 열리지 않는지
- **수강 계획**: 과목을 학기에 배치하면 내 캠퍼스에서 열리는지, 그 교육 기간에 열리는지, 선수 과목이 더 앞에 놓여 있는지를 하나씩 확인해 줍니다
- **선수과목 지도**: 한 과목에서 거슬러 올라가 선수 과목을, 또는 앞으로 나아가 열리는 과목을 따라갈 수 있습니다. 내 캠퍼스에서 열리지 않는 과목은 숨기지 않고 표시합니다

계획은 본인 브라우저에만 저장되며 계정에는 저장되지 않습니다. 확인할 때마다 계획이 API로 전송되어 Handbook과 대조되지만, 결과가 돌아온 뒤에는 아무것도 보관하지 않습니다. 계획은 다른 기기로 따라가지 않으니 옮기려면 '내보내기'를 쓰세요.

### WAM / GPA 계산하기

- 과목 코드를 입력하면 학점과 레벨이 Handbook에서 채워지며, 레벨 가중치를 외울 필요가 없습니다
- 말레이시아 캠퍼스는 CGPA라는 다른 척도를 씁니다. 전환할 수 있습니다
- WES 성적 스크린샷을 올리거나 텍스트를 붙여 넣어 표로 읽어들일 수도 있습니다
- 점수는 브라우저에서 계산되며 계정에는 저장되지 않습니다. API로 전송되는 것은 입력한 과목 코드뿐이며 학점과 레벨을 조회하는 데 쓰입니다. 점수 자체는 기기 밖으로 나가지 않습니다

### 학생 커뮤니티 참여하기

- 공개 질문과 토론 탐색 및 검색
- 로그인 후 게시, 답변, 투표, 북마크, 신고
- 특정 Unit과 관련된 학생 경험 확인
- 스터디 파트너, 활동 동행 또는 공통 관심사를 가진 학생 찾기

커뮤니티 콘텐츠는 학생 개인의 경험이며 Monash University의 공식 규정이 아닙니다.

### 마모 백과

WeChat 공식 계정 「马莫百科」 글의 색인입니다. 검색과 주제별 보기가 가능하며 원문으로 이동할 수 있습니다. 커뮤니티와 마찬가지로 공식 규정이 아니라 학생이 정리한 내용입니다.

## 사용 방법

1. 홈페이지에서 Unit code, 키워드 또는 질문을 검색합니다.
2. 중요한 결정은 공식 결과부터 확인하고 원문 링크를 열어 검증합니다.
3. 학생 경험이 필요할 때는 `Community` 표시가 있는 결과를 읽습니다.
4. 질문이나 답변을 하려면 이메일 주소로 가입하고 로그인합니다.

## 정보 출처 표시

| 표시 | 의미 |
| --- | --- |
| `Official Handbook` | Monash Handbook에서 가져온 구조화된 과목 정보 |
| `Official source` | Monash 공식 웹페이지에서 정리한 정보 |
| `Community` | 학생이 작성한 질문, 토론 및 개인 경험 |

## 소스 코드와 개인정보의 경계

이 저장소에는 애플리케이션 소스 코드, 스키마와 마이그레이션, 배포 템플릿, 테스트, 그리고 작은 합성 파서 픽스처가 들어 있습니다. 운영 자격 증명, 데이터베이스 덤프, 사용자 내보내기, 원본 크롤링 결과는 Git에 넣지 않습니다. 크롤러는 공식 출처로 링크를 남길 뿐 바이너리를 미러링하지 않습니다. 요청은 한 번에 하나씩 몇 초 간격으로 보내고, 자기 이름(`MonashHubBot`)을 밝히며, Monash 공식 페이지를 읽기 전에 `robots.txt`를 확인합니다. 자세한 내용은 [크롤링 정책](docs/CRAWLING.md)을 참고하세요.

저장소의 개인정보, 비밀 값, 제3자 콘텐츠 경계는 [Public release checklist](docs/PUBLIC-RELEASE.md)를 참고하세요.

## 개발자 및 기여자 안내

이 README는 제품 사용자를 위한 문서입니다. 프로젝트 작업은 [architecture](docs/ARCHITECTURE.md), [decision records](docs/adr/README.md), [deployment](docs/DEPLOYMENT.md), [crawling](docs/CRAWLING.md), [public-release checklist](docs/PUBLIC-RELEASE.md), [roadmap](docs/ROADMAP-STATUS.md), [contribution rules](AGENTS.md), [changelog](CHANGELOG.md)를 참고하세요.

개발 변경은 `feat/*`, `fix/*`, `chore/*` 브랜치에서 하고, Pull Request로 리뷰한 뒤 `main`에 병합합니다.

## 라이선스와 저작권

**저장소가 공개되어 있다고 해서 이 프로젝트가 오픈 소스인 것은 아닙니다.**

Copyright © 2026 Waldo. All rights reserved.

이 저장소의 소스 코드는 포트폴리오 제시, 교육 목적의 검토, 코드 검사를 위해 공개되어 있습니다. 저작권자의 사전 서면 허가가 없는 한 이 소프트웨어를 복제, 수정, 배포, 재허가, 판매, 상업적 이용, 경쟁 서비스로 배포하거나 파생 제품을 만드는 것은 허용되지 않습니다.

공개 저장소를 보거나 클론하거나 포크하는 GitHub 기능은 저작권자가 추가로 소프트웨어 라이선스를 부여한 것이 아닙니다.

제3자의 이름, 상표, 자료는 Monash University의 이름, 마크, 콘텐츠를 포함해 각 권리자에게 귀속되며, 이 저장소가 이를 재허가하지 않습니다.

자세한 소유권 경계는 [COPYRIGHT.md](COPYRIGHT.md)와 [NOTICE.md](NOTICE.md)를 참고하세요.
