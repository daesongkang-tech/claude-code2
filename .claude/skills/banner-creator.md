---
name: banner-creator
description: セミナー集客用のバナーをHTMLで自動生成する。「バナーを作って」「セミナーの集客バナーが欲しい」「SNS用の告知画像を作りたい」と言ったときに使う。
argument-hint: [セミナータイトル]
---

# バナークリエイター

ビズリンクのトンマナに沿ったセミナー集客バナーをHTMLで自動生成する。
引数 `$ARGUMENTS` にテーマが渡された場合はそれを元に直接生成する。

## デザイン仕様（必ず守る）

### カラーパレット
- **プライマリネイビー**: `#1B3A6B`
- **アクセントブルー**: `#4A7EC4`
- **ライトブルー**: `#D6E4F7`
- **オレンジアクセント**: `#E87D2B`（強調・CTA・バッジに使用）
- **グラデーション**: `linear-gradient(135deg, #1B3A6B 0%, #2D5A9E 100%)`
- **テキスト**: `#FFFFFF`（バナー上）、`#1A1A1A`（本文）

### タイポグラフィ
- フォント: `'Noto Sans JP', 'Hiragino Kaku Gothic ProN', sans-serif`
- タグライン: 14-16px、オレンジ背景
- タイトル: 32-48px、Bold、白
- サブタイトル: 16-20px、ライトブルー
- 日時・場所: 16-18px、白
- CTA: 18-22px、Bold、オレンジ背景

---

## 手順

### 1. セミナー情報の確認

`$ARGUMENTS` が空の場合のみ以下を確認する：
- セミナータイトル
- 開催日時（日付・時間）
- 開催形式（オンライン / リアル / ハイブリッド）
- 対象者（経営者・人事担当者・DX推進担当など）
- 参加費（無料 / 有料）
- 登壇者・ゲスト（任意）
- キャッチコピー・訴求ポイント（任意）

`$ARGUMENTS` がある場合はタイトルとして使い、不足情報は適切なデフォルト値で補完する。

### 2. バナーサイズの確認

以下から用途を選ばせる（未指定なら全サイズ生成）：

| サイズ | 用途 |
|---|---|
| 1200×630px | OGP / SNSシェア / Facebook |
| 1200×600px | Twitter / X カード |
| 728×90px | Web横長バナー |
| 300×250px | Web矩形バナー |

### 3. HTMLバナーを生成

以下の仕様でHTMLファイルを生成する。

**ファイル名**: `company/banners/banner_YYYYMMDD.html`（本日の日付を使用）

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>セミナーバナー</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700;900&display=swap" rel="stylesheet">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Noto Sans JP', 'Hiragino Kaku Gothic ProN', sans-serif;
      background: #F0F4F8;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 40px;
      padding: 40px 20px;
    }
    .banner-label {
      font-size: 13px;
      color: #666;
      text-align: center;
      margin-bottom: -30px;
      font-weight: 700;
      letter-spacing: 0.05em;
    }

    /* ===== OGP 1200×630 ===== */
    .banner-ogp {
      width: 1200px;
      height: 630px;
      background: linear-gradient(135deg, #1B3A6B 0%, #2D5A9E 100%);
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: center;
      padding: 60px 80px;
    }
    .banner-ogp .bg-circle {
      position: absolute;
      border-radius: 50%;
      opacity: 0.06;
      background: #FFFFFF;
    }
    .banner-ogp .bg-circle-1 { width: 500px; height: 500px; right: -100px; top: -150px; }
    .banner-ogp .bg-circle-2 { width: 300px; height: 300px; right: 200px; bottom: -80px; }
    .banner-ogp .accent-line {
      position: absolute;
      left: 0; top: 0; bottom: 0;
      width: 8px;
      background: #E87D2B;
    }
    .banner-ogp .logo {
      position: absolute;
      top: 40px;
      right: 60px;
      font-size: 22px;
      font-weight: 900;
      color: rgba(255,255,255,0.9);
      letter-spacing: 0.05em;
    }
    .banner-ogp .tag {
      display: inline-block;
      background: #E87D2B;
      color: #FFFFFF;
      font-size: 14px;
      font-weight: 700;
      padding: 6px 18px;
      border-radius: 4px;
      margin-bottom: 24px;
      letter-spacing: 0.08em;
      width: fit-content;
    }
    .banner-ogp .title {
      font-size: 48px;
      font-weight: 900;
      color: #FFFFFF;
      line-height: 1.25;
      margin-bottom: 20px;
      max-width: 800px;
      text-shadow: 0 2px 12px rgba(0,0,0,0.2);
    }
    .banner-ogp .subtitle {
      font-size: 20px;
      color: #D6E4F7;
      margin-bottom: 36px;
      max-width: 700px;
      line-height: 1.5;
    }
    .banner-ogp .meta {
      display: flex;
      gap: 32px;
      align-items: center;
    }
    .banner-ogp .meta-item {
      display: flex;
      align-items: center;
      gap: 8px;
      color: #FFFFFF;
      font-size: 17px;
      font-weight: 700;
    }
    .banner-ogp .meta-icon {
      width: 28px;
      height: 28px;
      background: rgba(255,255,255,0.15);
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
    }
    .banner-ogp .cta {
      position: absolute;
      right: 80px;
      bottom: 60px;
      background: #E87D2B;
      color: #FFFFFF;
      font-size: 18px;
      font-weight: 700;
      padding: 16px 40px;
      border-radius: 8px;
      letter-spacing: 0.05em;
      box-shadow: 0 4px 16px rgba(232,125,43,0.4);
    }
    .banner-ogp .free-badge {
      position: absolute;
      right: 220px;
      bottom: 50px;
      width: 80px;
      height: 80px;
      background: #E87D2B;
      border-radius: 50%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: #FFFFFF;
      font-weight: 900;
      font-size: 22px;
      line-height: 1;
      box-shadow: 0 4px 16px rgba(232,125,43,0.4);
    }
    .banner-ogp .free-badge span { font-size: 11px; font-weight: 700; }

    /* ===== Twitter 1200×600 ===== */
    .banner-twitter {
      width: 1200px;
      height: 600px;
      background: linear-gradient(135deg, #1B3A6B 0%, #2D5A9E 100%);
      position: relative;
      overflow: hidden;
      display: flex;
      align-items: center;
      padding: 0 80px;
      gap: 60px;
    }
    .banner-twitter .left { flex: 1; }
    .banner-twitter .right {
      width: 340px;
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.15);
      border-radius: 16px;
      padding: 32px;
      backdrop-filter: blur(8px);
    }
    .banner-twitter .accent-line {
      position: absolute;
      left: 0; top: 0; bottom: 0;
      width: 8px;
      background: #E87D2B;
    }
    .banner-twitter .logo {
      position: absolute;
      top: 32px;
      right: 60px;
      font-size: 20px;
      font-weight: 900;
      color: rgba(255,255,255,0.85);
    }
    .banner-twitter .tag {
      display: inline-block;
      background: #E87D2B;
      color: #FFFFFF;
      font-size: 13px;
      font-weight: 700;
      padding: 5px 16px;
      border-radius: 4px;
      margin-bottom: 20px;
      letter-spacing: 0.08em;
    }
    .banner-twitter .title {
      font-size: 40px;
      font-weight: 900;
      color: #FFFFFF;
      line-height: 1.3;
      margin-bottom: 16px;
    }
    .banner-twitter .subtitle {
      font-size: 16px;
      color: #D6E4F7;
      line-height: 1.6;
    }
    .banner-twitter .detail-label {
      font-size: 11px;
      color: #D6E4F7;
      font-weight: 700;
      letter-spacing: 0.1em;
      margin-bottom: 6px;
      opacity: 0.7;
    }
    .banner-twitter .detail-value {
      font-size: 16px;
      color: #FFFFFF;
      font-weight: 700;
      margin-bottom: 20px;
    }
    .banner-twitter .cta-btn {
      display: block;
      background: #E87D2B;
      color: #FFFFFF;
      font-size: 16px;
      font-weight: 700;
      padding: 14px;
      border-radius: 8px;
      text-align: center;
      margin-top: 8px;
      letter-spacing: 0.05em;
    }
    .banner-twitter .bg-circle {
      position: absolute;
      border-radius: 50%;
      opacity: 0.05;
      background: #FFFFFF;
    }
    .banner-twitter .bg-circle-1 { width: 400px; height: 400px; right: -50px; top: -120px; }

    /* ===== Web横長 728×90 ===== */
    .banner-wide {
      width: 728px;
      height: 90px;
      background: linear-gradient(90deg, #1B3A6B 0%, #2D5A9E 60%, #1B3A6B 100%);
      display: flex;
      align-items: center;
      padding: 0 24px;
      gap: 20px;
      position: relative;
      overflow: hidden;
    }
    .banner-wide .accent-line {
      position: absolute;
      left: 0; top: 0; bottom: 0;
      width: 5px;
      background: #E87D2B;
    }
    .banner-wide .logo {
      font-size: 14px;
      font-weight: 900;
      color: rgba(255,255,255,0.85);
      white-space: nowrap;
      padding-left: 8px;
    }
    .banner-wide .divider {
      width: 1px;
      height: 40px;
      background: rgba(255,255,255,0.25);
    }
    .banner-wide .tag {
      background: #E87D2B;
      color: #FFFFFF;
      font-size: 11px;
      font-weight: 700;
      padding: 3px 10px;
      border-radius: 3px;
      white-space: nowrap;
    }
    .banner-wide .title {
      font-size: 16px;
      font-weight: 700;
      color: #FFFFFF;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      flex: 1;
    }
    .banner-wide .date {
      font-size: 13px;
      color: #D6E4F7;
      white-space: nowrap;
      font-weight: 700;
    }
    .banner-wide .cta {
      background: #E87D2B;
      color: #FFFFFF;
      font-size: 13px;
      font-weight: 700;
      padding: 8px 20px;
      border-radius: 6px;
      white-space: nowrap;
    }

    /* ===== 矩形 300×250 ===== */
    .banner-rect {
      width: 300px;
      height: 250px;
      background: linear-gradient(160deg, #1B3A6B 0%, #2D5A9E 100%);
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: center;
      padding: 28px 24px;
    }
    .banner-rect .accent-line {
      position: absolute;
      left: 0; top: 0; bottom: 0;
      width: 5px;
      background: #E87D2B;
    }
    .banner-rect .logo {
      position: absolute;
      top: 18px;
      right: 18px;
      font-size: 13px;
      font-weight: 900;
      color: rgba(255,255,255,0.8);
    }
    .banner-rect .bg-circle {
      position: absolute;
      border-radius: 50%;
      opacity: 0.06;
      background: #FFFFFF;
      width: 200px; height: 200px;
      right: -50px; bottom: -60px;
    }
    .banner-rect .tag {
      display: inline-block;
      background: #E87D2B;
      color: #FFFFFF;
      font-size: 11px;
      font-weight: 700;
      padding: 4px 12px;
      border-radius: 3px;
      margin-bottom: 12px;
      width: fit-content;
      letter-spacing: 0.06em;
    }
    .banner-rect .title {
      font-size: 22px;
      font-weight: 900;
      color: #FFFFFF;
      line-height: 1.35;
      margin-bottom: 12px;
    }
    .banner-rect .date {
      font-size: 13px;
      color: #D6E4F7;
      font-weight: 700;
      margin-bottom: 16px;
    }
    .banner-rect .cta {
      display: inline-block;
      background: #E87D2B;
      color: #FFFFFF;
      font-size: 13px;
      font-weight: 700;
      padding: 10px 20px;
      border-radius: 6px;
      text-align: center;
      letter-spacing: 0.05em;
    }
  </style>
</head>
<body>

  <!-- OGP / SNS -->
  <p class="banner-label">OGP / SNSシェア（1200×630px）</p>
  <div class="banner-ogp">
    <div class="accent-line"></div>
    <div class="bg-circle bg-circle-1"></div>
    <div class="bg-circle bg-circle-2"></div>
    <div class="logo">Bizlink</div>
    <div class="tag">無料セミナー</div>
    <div class="title">【セミナータイトル】<br>をここに入力する</div>
    <div class="subtitle">〜サブタイトルや訴求ポイントをここに記載〜</div>
    <div class="meta">
      <div class="meta-item">
        <div class="meta-icon">📅</div>
        2026年4月15日（水）19:00〜20:30
      </div>
      <div class="meta-item">
        <div class="meta-icon">💻</div>
        オンライン開催（Zoom）
      </div>
      <div class="meta-item">
        <div class="meta-icon">👥</div>
        対象: 経営者・人事担当者
      </div>
    </div>
    <div class="free-badge">無料<span>参加</span></div>
    <div class="cta">今すぐ申込む →</div>
  </div>

  <!-- Twitter / X -->
  <p class="banner-label">Twitter / X（1200×600px）</p>
  <div class="banner-twitter">
    <div class="accent-line"></div>
    <div class="bg-circle bg-circle-1"></div>
    <div class="logo">Bizlink</div>
    <div class="left">
      <div class="tag">無料セミナー</div>
      <div class="title">【セミナータイトル】<br>をここに入力する</div>
      <div class="subtitle">〜サブタイトルや訴求ポイントをここに記載〜</div>
    </div>
    <div class="right">
      <div class="detail-label">開催日時</div>
      <div class="detail-value">2026年4月15日（水）<br>19:00〜20:30</div>
      <div class="detail-label">開催形式</div>
      <div class="detail-value">オンライン（Zoom）</div>
      <div class="detail-label">参加費</div>
      <div class="detail-value">無料</div>
      <div class="cta-btn">今すぐ申込む →</div>
    </div>
  </div>

  <!-- Web横長 -->
  <p class="banner-label">Web横長バナー（728×90px）</p>
  <div class="banner-wide">
    <div class="accent-line"></div>
    <div class="logo">Bizlink</div>
    <div class="divider"></div>
    <div class="tag">無料</div>
    <div class="title">【セミナータイトル】をここに入力する</div>
    <div class="date">4/15（水）19:00〜</div>
    <div class="cta">申込む →</div>
  </div>

  <!-- 矩形 -->
  <p class="banner-label">Web矩形バナー（300×250px）</p>
  <div class="banner-rect">
    <div class="accent-line"></div>
    <div class="bg-circle"></div>
    <div class="logo">Bizlink</div>
    <div class="tag">無料セミナー</div>
    <div class="title">【セミナー<br>タイトル】</div>
    <div class="date">📅 2026年4月15日（水）19:00〜</div>
    <div class="cta">今すぐ申込む →</div>
  </div>

</body>
</html>
```

### 4. ファイルを保存

収集した情報を上記テンプレートの以下の箇所に埋め込んでHTMLファイルを生成する：

| プレースホルダー | 置き換え内容 |
|---|---|
| `【セミナータイトル】をここに入力する` | 実際のセミナータイトル |
| `〜サブタイトルや訴求ポイント〜` | キャッチコピー・訴求ポイント |
| `2026年4月15日（水）19:00〜20:30` | 実際の開催日時 |
| `オンライン開催（Zoom）` | 実際の開催形式 |
| `経営者・人事担当者` | 実際の対象者 |
| `無料セミナー`（タグ） | 有料の場合は金額に変更 |
| `無料`（バッジ） | 有料の場合は非表示 |

ファイル名: `banner_YYYYMMDD.html`（本日の日付）
保存先: `company/banners/`

### 5. 調整対応

生成後、以下のカスタマイズに対応する：
- 登壇者の写真・プロフィール追加
- 特定サイズのみの出力
- コピー文言の修正・差し替え
- カラーテーマの変更（ダーク / オレンジ強調など）
- ダウンロードボタン追加（`window.print()` / Puppeteer案内）
