<p align="center"><img src="./frontend/public/favicon.svg" alt="Monash Hub Logo" width="120" /></p>

<h1 align="center">Monash Hub</h1>
<p align="center">Monash の情報を、より見つけやすく、理解しやすく</p>

<p align="center">
  <a href="https://monashhub.secureview.tech"><img src="https://img.shields.io/badge/live-monash--hub-1e5eff?style=for-the-badge" alt="公開サイト" /></a>
  <a href="https://github.com/Waldo0926/monash-hub/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/Waldo0926/monash-hub/ci.yml?branch=main&style=for-the-badge&label=CI" alt="CI" /></a>
  <img src="https://img.shields.io/badge/status-in%20production-2ea44f?style=for-the-badge" alt="ステータス：本番運用中" />
  <img src="https://img.shields.io/badge/unofficial-not%20affiliated%20with%20Monash-black?style=for-the-badge" alt="非公式" />
</p>

<p align="center"><a href="https://monashhub.secureview.tech">Monash Hub を開く</a></p>
<p align="center"><a href="./README.md">English</a> | <a href="./README.zh-CN.md">简体中文</a> | <strong>日本語</strong> | <a href="./README.ko.md">한국어</a></p>

---

## Monash Hub とは？

Monash Hub は、モナシュ大学の学生のための独立した情報プラットフォームです。特に、英語を母語としない学生が、学習やキャンパス生活に関する Monash の情報を検索し、理解し、確認しやすくなるよう設計されています。

Handbook、大学ウェブサイト、規程ページ、学生の議論を行き来しなくても、まず一つの入口から必要な情報を探し、各情報の出所を確認できます。

> Monash Hub は Monash University と提携しておらず、公式に承認されたサービスでもありません。履修、ビザ、評価、学業規程に関する重要な判断は、Monash の公式サイト、Handbook、Moodle または WES で必ず確認してください。

## 技術スタック

現在の本番環境の構成：

- **フロントエンド：** Nuxt 4、Vue 3、TypeScript、SSR でレンダリング
- **バックエンド：** FastAPI と Python
- **データベースと検索：** PostgreSQL 17。`tsvector`、GIN インデックス、`pg_trgm` による全文検索とあいまい検索
- **インフラ：** Docker Compose、Nginx、HTTPS
- **データパイプライン：** Python クローラー。内容ハッシュによる差分同期と、失敗時に既存データを守る保存処理
- **本番環境：** [monashhub.secureview.tech](https://monashhub.secureview.tech)

本番のリクエスト経路は、Web 画面が Nginx → Nuxt SSR、`/api/*` が Nginx → FastAPI で、PostgreSQL はプライベートな Docker ネットワーク上で動いています。現在のシステム設計は [architecture](docs/ARCHITECTURE.md) を参照してください。

## できること

### Unit 情報を調べる

- Unit code または科目名で検索
- 開講キャンパス、学期、評価、試験、履修要件、学習成果、学習時間を確認
- Handbook の原文リンクと最終確認日で情報を確認

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

### WAM / GPA を計算する

- ユニットコードを入力すると単位数とレベルが Handbook から入り、レベル係数を覚える必要はありません
- マレーシアキャンパスは CGPA という別の尺度です。切り替えられます
- WES の成績のスクリーンショットを読み込ませる、あるいはテキストを貼り付けて表に取り込むこともできます
- 点数はブラウザー内で計算され、アカウントには保存されません。API に送られるのは入力したユニットコードだけで、単位数とレベルの参照に使われます。点数そのものは端末の外に出ません

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

この README は製品利用者向けです。プロジェクト作業については、[architecture](docs/ARCHITECTURE.md)、[deployment](docs/DEPLOYMENT.md)、[crawling](docs/CRAWLING.md)、[public-release checklist](docs/PUBLIC-RELEASE.md)、[roadmap](docs/ROADMAP-STATUS.md)、[contribution rules](AGENTS.md)、[changelog](CHANGELOG.md) を確認してください。

開発の変更は `feat/*`、`fix/*`、`chore/*` ブランチで行い、Pull Request でレビューしてから `main` にマージします。

## ライセンスと著作権

**リポジトリが公開されていることは、このプロジェクトがオープンソースであることを意味しません。**

Copyright © 2026 Shuoxun Wen. All rights reserved.

このリポジトリのソースコードは、ポートフォリオとしての提示、教育目的のレビュー、コードの検証のために公開されています。著作権者の事前の書面による許可がない限り、本ソフトウェアを複製、改変、配布、再許諾、販売、商用利用、競合サービスとしてデプロイ、または派生物を作成する許可は与えられません。

公開リポジトリの閲覧、クローン、フォークといった GitHub の機能は、著作権者からの追加のソフトウェアライセンスにはなりません。

第三者の名称、商標、素材は、Monash University の名称、マーク、コンテンツを含め、それぞれの権利者に帰属し、このリポジトリによって再許諾されることはありません。

詳しい所有権の境界は [COPYRIGHT.md](COPYRIGHT.md) と [NOTICE.md](NOTICE.md) を参照してください。
