<p align="center"><img src="./frontend/public/favicon.svg" alt="Monash Hub Logo" width="120" /></p>

<h1 align="center">Monash Hub</h1>
<p align="center">Monash の情報を、より見つけやすく、理解しやすく</p>

<p align="center">
  <a href="https://monashhub.secureview.tech"><img src="https://img.shields.io/badge/live-monash--hub-1e5eff?style=for-the-badge" alt="公開サイト" /></a>
  <a href="https://github.com/Waldo0926/monash-hub/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/Waldo0926/monash-hub/ci.yml?branch=main&style=for-the-badge&label=CI" alt="CI" /></a>
  <img src="https://img.shields.io/badge/status-in%20production-2ea44f?style=for-the-badge" alt="ステータス：本番運用中" />
  <a href="https://waldo0926.github.io/uptime/history/monash-hub"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2FWaldo0926%2Fuptime%2FHEAD%2Fapi%2Fmonash-hub%2Fuptime.json&style=for-the-badge" alt="稼働率" /></a>
  <img src="https://img.shields.io/badge/unofficial-not%20affiliated%20with%20Monash-black?style=for-the-badge" alt="非公式" />
</p>

<p align="center"><a href="https://monashhub.secureview.tech">Monash Hub を開く</a></p>
<p align="center"><a href="./README.md">English</a> | <a href="./README.zh-CN.md">简体中文</a> | <strong>日本語</strong> | <a href="./README.ko.md">한국어</a></p>

---

<p align="center"><img src="./docs/images/home-en.webp" alt="Monash Hub のトップページ：検索、マレーシアとオーストラリアの重要日程、ユニット・履修計画・ガイドへの入口" width="900" /></p>

## Monash Hub とは？

Monash Hub は、モナシュ大学の学生のための独立した情報プラットフォームです。特に、英語を母語としない学生が、学習やキャンパス生活に関する Monash の情報を検索し、理解し、確認しやすくなるよう設計されています。

Handbook、大学ウェブサイト、規程ページ、学生の議論を行き来しなくても、まず一つの入口から必要な情報を探し、各情報の出所を確認できます。

> Monash Hub は Monash University と提携しておらず、公式に承認されたサービスでもありません。履修、ビザ、評価、学業規程に関する重要な判断は、Monash の公式サイト、Handbook、Moodle または WES で必ず確認してください。

## なぜ新しいサイトを作ったのか

これまで学生が何かを調べるには、三つの場所を回る必要があり、どれも一部しかカバーしていませんでした。

| 場所 | 得意なこと | 足りないこと |
| --- | --- | --- |
| [Monash Handbook](https://handbook.monash.edu) | ユニットとコースの公式記録 | 英語のみで、ユニットとコースだけ。規則、ビザ、重要日程は別のサイト |
| monash.edu と monash.edu.my | キャンパスごとの公式ガイド | 二つのサイトで約 3,100 ページあり、キャンパスによって規則が違う（ビザ、保険、ユニットの変更） |
| 学生のグループチャットや共有ドキュメント | 中国語ですぐ答えが返ってくる | 出典がなく、過去の年度や別キャンパスの情報が多い |

学生が作ったツールは以前にもありました。[MonPlan](https://github.com/MonPlan) は学生が作った履修計画ツールで、公開されているスクレイパー（[MonScrape](https://github.com/MonPlan/MonScrape)）の最終更新は 2017 年、読んでいるのは旧版の Handbook ページです。monashcoding の [TheBetterHandbookAPI](https://github.com/monashcoding/TheBetterHandbookAPI) は Handbook の検索エンドポイントの使い方をまとめています（最終コミットは 2022 年 9 月）。どちらも規則や英語以外の言語は扱っていません。

Monash Hub はそれらの良いところ、つまり Handbook から直接取るデータを残し、足りない部分を加えました。両方のサイトの公式ページをユニットと並べ、すべての結果に出典と最終確認日を付け、マレーシアとオーストラリアで規則が違うときは並べて表示し、中国語訳には英語の原文へのリンクを付けています。サイト内アシスタントはこれらの資料を検索するだけで、生成 AI に回答を書かせることはありません。

## 技術スタック

現在の本番環境の構成：

- **フロントエンド：** Nuxt 4、Vue 3、TypeScript、SSR でレンダリング
- **バックエンド：** FastAPI と Python
- **データベースと検索：** PostgreSQL 17。`tsvector`、GIN インデックス、`pg_trgm` による全文検索とあいまい検索
- **インフラ：** Docker Compose、Nginx、HTTPS
- **テスト：** 実際の PostgreSQL に接続する pytest、Vitest、デスクトップとスマートフォンの画面サイズで動く Playwright のブラウザテスト。どれもデプロイ前に CI で実行
- **データパイプライン：** Python クローラー。内容ハッシュによる差分同期と、失敗時に既存データを守る保存処理
- **本番環境：** [monashhub.secureview.tech](https://monashhub.secureview.tech)

本番のリクエスト経路は、Web 画面が Nginx → Nuxt SSR、`/api/*` が Nginx → FastAPI で、PostgreSQL はプライベートな Docker ネットワーク上で動いています。現在のシステム設計は [architecture](docs/ARCHITECTURE.md) を参照してください。

## 数字で見る（2026 年 10 月 25 日時点）

| | |
| --- | --- |
| ガイドに収録した公式ページ | 二つのサイトの sitemap から約 3,100 ページ（以前は 662 ページ） |
| バックエンドのテスト | 799 個のテスト関数。CI で実際の PostgreSQL に対して実行 |
| フロントエンドとブラウザのテスト | Vitest 48 個、デスクトップとスマホのサイズで Playwright 13 個 |
| 翻訳モデル | 智譜の無料モデル `glm-4.5-flash`。無料の三つのモデルの訳を英語原文と 70 段落分照らし合わせて選んだ（`glm-4-flash` は条件を逆に訳した） |
| デプロイ | `main` にマージするたびに自動デプロイ。毎回本番サイトにスモークチェックを行い、失敗したら前のバージョンに戻す |

出典：[変更履歴](CHANGELOG.md) と `backend/tests`、`frontend`、`e2e` のテストファイル。

## できること

### Unit 情報を調べる

- Unit code または科目名で検索
- 開講キャンパス、学期、評価、試験、履修要件、学習成果、学習時間を確認
- Handbook の原文リンクと最終確認日で情報を確認

<p align="center"><img src="./docs/images/unit-en.webp" alt="FIT2004 のユニットページ：学部からの通知、単位数、キャンパス、評価、開講学期、Handbook へのリンク" width="900" /></p>
<p align="center"><sub>このページのスクリーンショットはブラウザテスト用の環境で撮ったものです。実際のサイトを架空の 3 ユニット（FIT1008、FIT2004、FIT2102）と架空の学位で動かしているため、名前・点数・計画はすべて作り物です。本番サイトは Handbook のデータを表示します。</sub></p>

### Monash の公式情報を調べる

- WAM、Special Consideration、census date、ビザ、交換留学、キャンパスサービスなどを検索
- 出所リンクと最終確認日付きの公式情報を読む
- `Official Handbook` または `Official source` の表示を優先して確認

### 情報を理解しやすくする

- 簡体字中国語、英語、日本語、韓国語でインターフェースを利用
- Handbook と公式ガイドの翻訳補助を閲覧
- 翻訳の出所と原文ページへのリンクを確認

### 学位を計画する

- **学位**：学位が何で構成されているか、各要件グループの単位数と、そのうちどれが自分のキャンパスでは開講されないか
- **履修計画**：ユニットを学期に配置すると、自分のキャンパスで開講されるか、その教育期に開講されるか、必要な科目がより前に置かれているかを一つずつ確認します
- **履修条件マップ**：あるユニットから遡って前提科目を、あるいは先へ進んで解放される科目をたどれます。自分のキャンパスで開講されない科目は隠さず、印を付けて示します

計画はご自身のブラウザーにのみ保存され、アカウントには保存されません。チェックのたびに計画は API に送られて Handbook と照合されますが、結果が返った後は何も保持されません。計画は別の端末には引き継がれないので、移すには「エクスポート」を使ってください。

<p align="center"><img src="./docs/images/plan-en.webp" alt="履修計画：学期に置いた 4 ユニットをキャンパス、開講学期、前提条件で確認し、右側に学位要件に対する進捗を表示" width="900" /></p>

### WAM / GPA を計算する

- ユニットコードを入力すると単位数とレベルが Handbook から入り、レベル係数を覚える必要はありません
- マレーシアキャンパスは CGPA という別の尺度です。切り替えられます
- WES の成績のスクリーンショットを読み込ませる、あるいはテキストを貼り付けて表に取り込むこともできます
- 点数はブラウザー内で計算され、アカウントには保存されません。API に送られるのは入力したユニットコードだけで、単位数とレベルの参照に使われます。点数そのものは端末の外に出ません

<p align="center"><img src="./docs/images/marks-en.webp" alt="WAM / GPA 計算機：3 ユニットをレベルごとにまとめ、右側に WAM と CGPA を表示" width="900" /></p>

### 学生コミュニティに参加する

- 公開質問・ディスカッションの閲覧と検索
- ログイン後の投稿、回答、投票、保存、報告
- 特定 Unit に関する学生の経験を確認
- 勉強仲間、イベントの同行者、共通の興味を持つ学生を探す

コミュニティの内容は学生個人の経験であり、Monash University の公式規程ではありません。

### 馬莫百科

WeChat 公式アカウント「马莫百科」の記事の索引です。検索とトピック別の閲覧ができ、元の投稿へ移動できます。コミュニティと同様、公式の規定ではなく学生によるまとめです。

## 使い方

1. ホームページで Unit code、キーワード、または質問を検索します。
2. 重要な判断では、まず公式情報を読み、原文リンクを開いて確認します。
3. 学生の経験が必要なときは、`Community` と表示された結果を確認します。
4. 質問や回答をするには、メールアドレスで登録してログインします。

## 情報源の表示

| 表示 | 意味 |
| --- | --- |
| `Official Handbook` | Monash Handbook からの構造化された科目情報 |
| `Official source` | Monash 公式ウェブページから整理した情報 |
| `Community` | 学生による質問、議論、個人的な経験 |

## ソースコードとプライバシーの境界

このリポジトリには、アプリケーションのソースコード、スキーマとマイグレーション、デプロイ用テンプレート、テスト、そして小さな合成パーサー用フィクスチャが含まれています。本番の認証情報、データベースダンプ、ユーザーのエクスポート、生のクロール出力は Git に入れません。クローラーは公式ソースへリンクを残すだけで、バイナリをミラーしません。リクエストは一度に一件、数秒おきに送り、自分の名前（`MonashHubBot`）を名乗ります。Monash の公式ページを読む前には `robots.txt` を確認します。詳しくは [クロールについて](docs/CRAWLING.md) を参照してください。

リポジトリのプライバシー、シークレット、第三者コンテンツの境界については [Public release checklist](docs/PUBLIC-RELEASE.md) を参照してください。

## 開発者・コントリビューター向け

この README は製品利用者向けです。プロジェクト作業については、[architecture](docs/ARCHITECTURE.md)、[decision records](docs/adr/README.md)、[deployment](docs/DEPLOYMENT.md)、[crawling](docs/CRAWLING.md)、[public-release checklist](docs/PUBLIC-RELEASE.md)、[roadmap](docs/ROADMAP-STATUS.md)、[contribution rules](AGENTS.md)、[changelog](CHANGELOG.md) を確認してください。

開発の変更は `feat/*`、`fix/*`、`chore/*` ブランチで行い、Pull Request でレビューしてから `main` にマージします。

### ローカルで動かす

ブラウザテストには、実際のスタックを合成データで動かすのに必要なものが揃っています（PostgreSQL、API、フロントエンドの本番ビルド、本番の nginx と同じく同一オリジンにまとめる小さなプロキシ）。

```sh
createdb monashhub_e2e
pip install -r backend/requirements.txt
(cd frontend && npm ci && npm run build)
(cd e2e && npm ci && npx playwright install chromium)
cd e2e && DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/monashhub_e2e npx playwright test
```

Playwright がマイグレーションと `e2e/seed.py` の読み込みを行い、ポート 8100、3101、3100 で 3 つのサーバーを起動してテスト後に停止します。サイトを立ち上げたままにしたい場合は [e2e/README.md](e2e/README.md) のコマンドを手動で実行してください。実際の Handbook と公式ページのデータはクローラーが取得します（[crawling](docs/CRAWLING.md)）。バックエンドのテストは `backend/` で `pytest`、フロントエンドのテストは `frontend/` で `npm test` です。

## ライセンスと著作権

**リポジトリが公開されていることは、このプロジェクトがオープンソースであることを意味しません。**

Copyright © 2026 Waldo. All rights reserved.

このリポジトリのソースコードは、ポートフォリオとしての提示、教育目的のレビュー、コードの検証のために公開されています。著作権者の事前の書面による許可がない限り、本ソフトウェアを複製、改変、配布、再許諾、販売、商用利用、競合サービスとしてデプロイ、または派生物を作成する許可は与えられません。

公開リポジトリの閲覧、クローン、フォークといった GitHub の機能は、著作権者からの追加のソフトウェアライセンスにはなりません。

第三者の名称、商標、素材は、Monash University の名称、マーク、コンテンツを含め、それぞれの権利者に帰属し、このリポジトリによって再許諾されることはありません。

詳しい所有権の境界は [COPYRIGHT.md](COPYRIGHT.md) と [NOTICE.md](NOTICE.md) を参照してください。
