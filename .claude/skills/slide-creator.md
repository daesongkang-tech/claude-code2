---
name: slide-creator
description: ビズリンクのトンマナに沿ったプレゼンテーションスライドをHTMLで自動生成する。「スライドを作って」「プレゼン資料を作りたい」「〇〇のスライドを生成して」と言ったときに使う。
argument-hint: [スライドのテーマ・タイトル]
---

# スライドクリエイター

ビズリンクのプレゼンテーションスタイルに沿ったHTMLスライドを自動生成する。
引数 `$ARGUMENTS` にテーマが渡された場合はそれを元に直接生成する。

## デザイン仕様（必ず守る）

### カラーパレット
- **プライマリネイビー**: `#1B3A6B`
- **アクセントブルー**: `#4A7EC4`
- **ライトブルー**: `#D6E4F7`
- **オレンジアクセント**: `#E87D2B`（強調・KPI数値に使用）
- **テキスト**: `#1A1A1A`（本文）、`#FFFFFF`（白背景反転）
- **背景**: `#FFFFFF`（コンテンツ）、`#F5F8FC`（セクション背景）

### レイアウト原則
- スライドサイズ: 16:9（1280×720px）
- 左端に `6px` のカラーバー（プライマリネイビー）
- 見出しエリア: プライマリネイビー背景、白文字
- フッター: `Confidential - All Rights Reserved – Bizlink` を全スライドに表示
- ロゴ: 右上に `Bizlink` テキストロゴ（ネイビー）

### タイポグラフィ
- フォント: `'Noto Sans JP', 'Hiragino Kaku Gothic ProN', sans-serif`
- タイトル: 32-40px、Bold
- 見出し: 24-28px、Bold
- 本文: 16-18px、Regular
- 章番号: 120px、Bold、薄いブルーグレー（`#B0C4DE`）

---

## 手順

### 1. 構成確認

`$ARGUMENTS` が空の場合のみ以下を確認する：
- スライドのテーマ・目的
- 想定聴衆（経営者・営業・全社など）
- スライド枚数の目安（未定なら8〜12枚で提案）
- 含めたいセクション・キーメッセージ

### 2. アウトライン提示

以下の構成で提案し、確認を得てから生成する：

```
1. タイトルスライド
2. アジェンダ
3. 章扉（セクション区切り）× 必要数
4. コンテンツスライド × 必要数
5. まとめ / 次のアクション
6. Q&A / ご静聴ありがとうございました
```

### 3. HTMLスライドを生成

以下の完全なHTMLファイルを生成し、`company/slides/slides_YYYYMMDD.html` として保存する。

#### スライドテンプレート構造

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>[タイトル]</title>
  <style>
    /* === リセット & ベース === */
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Noto Sans JP', 'Hiragino Kaku Gothic ProN', 'Yu Gothic', sans-serif;
      background: #E8EDF2;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 20px;
      gap: 20px;
    }

    /* === スライド共通 === */
    .slide {
      width: 1280px;
      height: 720px;
      background: #fff;
      position: relative;
      overflow: hidden;
      box-shadow: 0 4px 20px rgba(0,0,0,0.15);
      display: flex;
      flex-direction: column;
    }

    /* 左カラーバー */
    .slide::before {
      content: '';
      position: absolute;
      left: 0; top: 0; bottom: 0;
      width: 6px;
      background: #1B3A6B;
    }

    /* === フッター === */
    .footer {
      position: absolute;
      bottom: 0; left: 0; right: 0;
      height: 32px;
      background: #1B3A6B;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 32px 0 20px;
      color: #fff;
      font-size: 11px;
    }
    .footer .logo {
      font-weight: 700;
      font-size: 13px;
      letter-spacing: 0.5px;
    }
    .slide-number {
      background: rgba(255,255,255,0.2);
      border-radius: 3px;
      padding: 2px 8px;
      font-size: 11px;
    }

    /* === タイトルスライド === */
    .slide-title {
      background: linear-gradient(135deg, #1B3A6B 0%, #2A5298 60%, #4A7EC4 100%);
    }
    .slide-title::before { background: #E87D2B; }
    .slide-title .content {
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
      padding: 60px 80px 50px;
      color: #fff;
    }
    .slide-title .label {
      font-size: 14px;
      letter-spacing: 3px;
      opacity: 0.8;
      text-transform: uppercase;
      margin-bottom: 20px;
    }
    .slide-title h1 {
      font-size: 48px;
      font-weight: 900;
      line-height: 1.3;
      margin-bottom: 24px;
    }
    .slide-title .subtitle {
      font-size: 20px;
      opacity: 0.85;
      margin-bottom: 40px;
    }
    .slide-title .presenter {
      font-size: 16px;
      opacity: 0.75;
      border-top: 1px solid rgba(255,255,255,0.3);
      padding-top: 20px;
    }
    .slide-title .footer { background: rgba(0,0,0,0.3); }

    /* === 章扉スライド === */
    .slide-section {
      background: #F5F8FC;
    }
    .slide-section .section-num {
      position: absolute;
      right: 60px;
      top: 50%;
      transform: translateY(-60%);
      font-size: 200px;
      font-weight: 900;
      color: #D6E4F7;
      line-height: 1;
      z-index: 0;
    }
    .slide-section .content {
      flex: 1;
      display: flex;
      align-items: center;
      padding: 0 80px;
      position: relative;
      z-index: 1;
    }
    .slide-section h2 {
      font-size: 56px;
      font-weight: 900;
      color: #1A1A1A;
      line-height: 1.3;
    }

    /* === コンテンツスライド === */
    .slide-content .header {
      background: #1B3A6B;
      padding: 20px 32px 18px 28px;
      color: #fff;
    }
    .slide-content .header h2 {
      font-size: 26px;
      font-weight: 700;
    }
    .slide-content .header .sub {
      font-size: 13px;
      opacity: 0.75;
      margin-top: 4px;
    }
    .slide-content .body {
      flex: 1;
      padding: 28px 36px 50px 36px;
      overflow: hidden;
    }

    /* === リスト === */
    .bullet-list { list-style: none; }
    .bullet-list li {
      padding: 8px 0 8px 24px;
      position: relative;
      font-size: 17px;
      border-bottom: 1px solid #F0F4F8;
      line-height: 1.6;
    }
    .bullet-list li::before {
      content: '●';
      color: #4A7EC4;
      position: absolute;
      left: 0;
      font-size: 10px;
      top: 14px;
    }
    .bullet-list li strong { color: #1B3A6B; }

    /* === 2カラムレイアウト === */
    .two-col {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      height: 100%;
    }
    .col-card {
      background: #F5F8FC;
      border-radius: 8px;
      border-left: 4px solid #4A7EC4;
      padding: 20px 20px;
    }
    .col-card h3 {
      font-size: 18px;
      color: #1B3A6B;
      margin-bottom: 12px;
      font-weight: 700;
    }
    .col-card p, .col-card li {
      font-size: 15px;
      color: #444;
      line-height: 1.7;
    }

    /* === KPI・数値強調 === */
    .kpi-row {
      display: flex;
      gap: 20px;
      margin-bottom: 20px;
    }
    .kpi-card {
      flex: 1;
      background: #1B3A6B;
      color: #fff;
      border-radius: 8px;
      padding: 20px 16px;
      text-align: center;
    }
    .kpi-card .num {
      font-size: 44px;
      font-weight: 900;
      color: #E87D2B;
      line-height: 1;
    }
    .kpi-card .unit { font-size: 20px; color: #E87D2B; }
    .kpi-card .label { font-size: 13px; opacity: 0.85; margin-top: 8px; }

    /* === テーブル === */
    .bizlink-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 15px;
    }
    .bizlink-table th {
      background: #1B3A6B;
      color: #fff;
      padding: 10px 16px;
      text-align: left;
      font-weight: 600;
    }
    .bizlink-table td {
      padding: 10px 16px;
      border-bottom: 1px solid #E8EDF2;
    }
    .bizlink-table tr:nth-child(even) td { background: #F5F8FC; }

    /* === まとめスライド === */
    .slide-summary .header { background: #2A5298; }
    .summary-box {
      background: linear-gradient(135deg, #1B3A6B, #2A5298);
      color: #fff;
      border-radius: 10px;
      padding: 20px 24px;
      margin-bottom: 16px;
    }
    .summary-box h3 { font-size: 16px; opacity: 0.8; margin-bottom: 6px; }
    .summary-box p { font-size: 18px; font-weight: 700; line-height: 1.5; }

    /* === Q&A / エンドスライド === */
    .slide-end {
      background: linear-gradient(135deg, #1B3A6B 0%, #2A5298 100%);
      color: #fff;
    }
    .slide-end::before { background: #E87D2B; }
    .slide-end .content {
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      text-align: center;
    }
    .slide-end h2 { font-size: 64px; font-weight: 900; margin-bottom: 24px; }
    .slide-end p { font-size: 18px; opacity: 0.8; }
    .slide-end .footer { background: rgba(0,0,0,0.3); }

    /* === ナビゲーション === */
    .nav {
      position: fixed;
      bottom: 24px;
      right: 24px;
      display: flex;
      gap: 8px;
      z-index: 100;
    }
    .nav button {
      background: #1B3A6B;
      color: #fff;
      border: none;
      padding: 10px 20px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
      font-family: inherit;
    }
    .nav button:hover { background: #2A5298; }

    /* プレゼンモード */
    .slide { display: none; }
    .slide.active { display: flex; }
    body.present-mode {
      background: #000;
      padding: 0;
      justify-content: center;
      align-items: center;
      height: 100vh;
      overflow: hidden;
    }
    body.present-mode .slide.active {
      width: 100vw;
      height: 100vh;
      transform-origin: center;
    }
  </style>
</head>
<body>

  <!-- ============================================
       スライド1: タイトル
  ============================================ -->
  <div class="slide slide-title active" id="slide-1">
    <div class="content">
      <div class="label">Bizlink Presentation</div>
      <h1>[メインタイトル]<br>[サブタイトル]</h1>
      <div class="subtitle">[キャッチコピーや概要文]</div>
      <div class="presenter">
        株式会社ビズリンク　代表取締役　姜 大成
      </div>
    </div>
    <div class="footer">
      <span>Confidential - All Rights Reserved – Bizlink</span>
      <span class="logo">Bizlink</span>
    </div>
  </div>

  <!-- ============================================
       スライド2: アジェンダ
  ============================================ -->
  <div class="slide slide-content" id="slide-2">
    <div class="header">
      <h2>本日のアジェンダ</h2>
    </div>
    <div class="body">
      <table class="bizlink-table">
        <thead>
          <tr><th>セクション</th><th>主な内容</th></tr>
        </thead>
        <tbody>
          <tr><td><strong>1. [セクション名]</strong></td><td>[内容概要]</td></tr>
          <tr><td><strong>2. [セクション名]</strong></td><td>[内容概要]</td></tr>
          <tr><td><strong>3. [セクション名]</strong></td><td>[内容概要]</td></tr>
        </tbody>
      </table>
    </div>
    <div class="footer">
      <span>Confidential - All Rights Reserved – Bizlink</span>
      <span class="logo">Bizlink</span>
      <span class="slide-number">2</span>
    </div>
  </div>

  <!-- ============================================
       スライド3: 章扉
  ============================================ -->
  <div class="slide slide-section" id="slide-3">
    <div class="section-num">1</div>
    <div class="content">
      <h2>[章タイトル]</h2>
    </div>
    <div class="footer">
      <span>Confidential - All Rights Reserved – Bizlink</span>
      <span class="logo">Bizlink</span>
      <span class="slide-number">3</span>
    </div>
  </div>

  <!-- ============================================
       スライド4: KPI数値スライド
  ============================================ -->
  <div class="slide slide-content" id="slide-4">
    <div class="header">
      <h2>[スライドタイトル]</h2>
      <div class="sub">[サブタイトル]</div>
    </div>
    <div class="body">
      <div class="kpi-row">
        <div class="kpi-card">
          <div class="num">XX<span class="unit">億円</span></div>
          <div class="label">[指標名]</div>
        </div>
        <div class="kpi-card">
          <div class="num">XX<span class="unit">%</span></div>
          <div class="label">[指標名]</div>
        </div>
        <div class="kpi-card">
          <div class="num">XX<span class="unit">名</span></div>
          <div class="label">[指標名]</div>
        </div>
      </div>
      <ul class="bullet-list">
        <li><strong>[ポイント1]</strong>：[説明]</li>
        <li><strong>[ポイント2]</strong>：[説明]</li>
        <li><strong>[ポイント3]</strong>：[説明]</li>
      </ul>
    </div>
    <div class="footer">
      <span>Confidential - All Rights Reserved – Bizlink</span>
      <span class="logo">Bizlink</span>
      <span class="slide-number">4</span>
    </div>
  </div>

  <!-- ============================================
       スライド5: 2カラム比較
  ============================================ -->
  <div class="slide slide-content" id="slide-5">
    <div class="header">
      <h2>[スライドタイトル]</h2>
    </div>
    <div class="body">
      <div class="two-col">
        <div class="col-card">
          <h3>[左カラムタイトル]</h3>
          <ul class="bullet-list">
            <li>[項目1]</li>
            <li>[項目2]</li>
            <li>[項目3]</li>
          </ul>
        </div>
        <div class="col-card" style="border-left-color: #E87D2B;">
          <h3>[右カラムタイトル]</h3>
          <ul class="bullet-list">
            <li>[項目1]</li>
            <li>[項目2]</li>
            <li>[項目3]</li>
          </ul>
        </div>
      </div>
    </div>
    <div class="footer">
      <span>Confidential - All Rights Reserved – Bizlink</span>
      <span class="logo">Bizlink</span>
      <span class="slide-number">5</span>
    </div>
  </div>

  <!-- ============================================
       スライドN: まとめ
  ============================================ -->
  <div class="slide slide-content slide-summary" id="slide-n1">
    <div class="header">
      <h2>まとめ</h2>
    </div>
    <div class="body">
      <div class="summary-box">
        <h3>ポイント① </h3>
        <p>[キーメッセージ1]</p>
      </div>
      <div class="summary-box">
        <h3>ポイント②</h3>
        <p>[キーメッセージ2]</p>
      </div>
      <div class="summary-box">
        <h3>ポイント③</h3>
        <p>[キーメッセージ3]</p>
      </div>
    </div>
    <div class="footer">
      <span>Confidential - All Rights Reserved – Bizlink</span>
      <span class="logo">Bizlink</span>
    </div>
  </div>

  <!-- ============================================
       最終スライド: ご静聴ありがとう
  ============================================ -->
  <div class="slide slide-end" id="slide-last">
    <div class="content">
      <h2>ご静聴ありがとうございました</h2>
      <p>些細な疑問でも構いません。皆様のリアルな課題感にお答えします。</p>
    </div>
    <div class="footer">
      <span>Confidential - All Rights Reserved – Bizlink</span>
      <span class="logo">Bizlink</span>
    </div>
  </div>

  <!-- ナビゲーション -->
  <div class="nav">
    <button onclick="prevSlide()">← 前へ</button>
    <button onclick="nextSlide()">次へ →</button>
    <button onclick="togglePresent()">プレゼンモード</button>
  </div>

  <script>
    let current = 0;
    const slides = document.querySelectorAll('.slide');

    function showSlide(n) {
      slides.forEach(s => s.classList.remove('active'));
      current = (n + slides.length) % slides.length;
      slides[current].classList.add('active');
    }
    function nextSlide() { showSlide(current + 1); }
    function prevSlide() { showSlide(current - 1); }
    function togglePresent() { document.body.classList.toggle('present-mode'); }

    document.addEventListener('keydown', e => {
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') nextSlide();
      if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') prevSlide();
      if (e.key === 'Escape') document.body.classList.remove('present-mode');
      if (e.key === 'f' || e.key === 'F') togglePresent();
    });
  </script>
</body>
</html>
```

### 4. ファイル保存とプレビュー案内

- ファイルを `company/slides/slides_YYYYMMDD.html` として保存
- 保存後、以下を伝える：
  - ファイルパス
  - ブラウザで開く方法
  - キー操作: `←→` でスライド移動、`F` でプレゼンモード、`Esc` で終了

### 5. 調整対応

生成後、以下のリクエストに対応する：
- スライドの追加・削除
- 特定スライドの内容変更
- カラーテーマの調整（アクセントカラーのみ変更など）
- 日本語・英語の切り替え

## 注意事項

- ビズリンクのロゴ・実際の数値を使用する場合は `company/` 配下のcontextを参照する
- 機密情報は含めず、公開可能な内容のみ記載する
- スライド枚数は多くなりすぎないよう10〜15枚を目安にする
- 各スライドに必ず `Confidential - All Rights Reserved – Bizlink` フッターを入れる
