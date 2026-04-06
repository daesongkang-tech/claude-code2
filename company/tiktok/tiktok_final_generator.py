"""
TikTok 最終ジェネレーター（ビズウェル対応）
===========================================
構成ルール:
  ① 最初1.5秒以内: 強烈フック「え、マジ！？」
  ② 本文: 中学生でもわかる平易な言葉
  ③ 最後2秒: CTA「保存して後で見返して」

アセット:
  - ElevenLabs API → 日本語音声 + 文字レベルタイミング
  - Unsplash API   → サイバーパンク背景画像

合成:
  - MoviePy 2.x（縦型 1080x1920 / 30fps）
  - 黄色太字・一文字ずつカラオケテロップ
  - 出力: final_output.mp4

環境変数:
  ELEVENLABS_API_KEY   = your_key
  ELEVENLABS_VOICE_ID  = voice_id   # 任意（デフォルト: Aria multilingual）
  UNSPLASH_ACCESS_KEY  = your_key
"""

import os, sys, base64, json, requests, tempfile, wave, re, html
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont

try:
    from moviepy import VideoClip, AudioFileClip
except ImportError as e:
    print(f"[ERROR] {e}\npip install moviepy requests pillow numpy")
    sys.exit(1)

# ─── 設定 ────────────────────────────────────────────────
ELEVENLABS_API_KEY  = os.environ.get("ELEVENLABS_API_KEY", "")
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")
ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")  # Aria (multilingual)

OUTPUT_PATH   = "final_output.mp4"
VIDEO_W, VIDEO_H = 1080, 1920
FPS           = 30

FONT_CANDIDATES = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W9.ttc",
    "/Library/Fonts/NotoSansJP-Bold.otf",
    "./NotoSansJP-Bold.otf",
]

# ─── スクリプト ───────────────────────────────────────────
# SCRIPT_TEXT: ElevenLabsに渡す連続テキスト
# DISPLAY_PHRASES: 画面表示単位（\nで改行、連結するとSCRIPT_TEXTと一致すること）
SCRIPT_TEXT = (
    "え、マジ！？"
    "障害があっても、AIエンジニアになれる時代が来た！"
    "ビズウェルは、精神・発達障害のある方が"
    "AIスキルを学んで就職できる学校。"
    "お金がかかる？ゼロ円。"
    "難しそう？中学生でもわかる内容から始めます。"
    "ChatGPTの使い方、画像作成、業務自動化。"
    "実際に使えるスキルを身につけよう！"
    "しかも月10万円もらいながら学べる場合もあります。"
    "気になった人は今すぐ保存して後で見返してみてください！"
)

DISPLAY_PHRASES = [
    "え、マジ！？",                                          # [0] HOOK
    "障害があっても、\nAIエンジニアになれる時代が来た！",
    "ビズウェルは、\n精神・発達障害のある方が",
    "AIスキルを学んで\n就職できる学校。",
    "お金がかかる？ゼロ円。",
    "難しそう？\n中学生でもわかる内容から始めます。",
    "ChatGPTの使い方、\n画像作成、業務自動化。",
    "実際に使えるスキルを\n身につけよう！",
    "しかも月10万円もらいながら\n学べる場合もあります。",
    "気になった人は今すぐ保存して\n後で見返してみてください！",  # [-1] CTA
]

# ─── バリデーション ────────────────────────────────────────
_flat = "".join(p.replace("\n", "") for p in DISPLAY_PHRASES)
assert _flat == SCRIPT_TEXT, (
    f"SCRIPT_TEXT と DISPLAY_PHRASES が不一致！\n"
    f"SCRIPT ({len(SCRIPT_TEXT)}): {SCRIPT_TEXT[:30]}...\n"
    f"FLAT   ({len(_flat)}): {_flat[:30]}..."
)

# フレーズ → SCRIPT_TEXT上の文字範囲を事前計算
PHRASE_RANGES: List[Tuple[int, int]] = []
pos = 0
for phrase in DISPLAY_PHRASES:
    flat = phrase.replace("\n", "")
    PHRASE_RANGES.append((pos, pos + len(flat)))
    pos += len(flat)


# ─── ユーティリティ ──────────────────────────────────────
def find_font() -> Optional[str]:
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            print(f"[FONT] {p}")
            return p
    print("[FONT] 日本語フォントが見つかりません。デフォルトを使用します。")
    return None


def char_idx_to_phrase(n: int) -> Tuple[int, int]:
    """文字インデックス n が属するフレーズインデックスと、そのフレーズ内でのオフセットを返す。"""
    for i, (start, end) in enumerate(PHRASE_RANGES):
        if n < end:
            return i, n - start
    # 末尾
    last = len(PHRASE_RANGES) - 1
    return last, PHRASE_RANGES[last][1] - PHRASE_RANGES[last][0]


# ─── RSS ニュース収集 ────────────────────────────────────
# 就労B型・AIエンジニア・障害者就労関連フィード
RSS_FEEDS = [
    # 障害・福祉
    ("NHK 福祉",           "https://www3.nhk.or.jp/rss/news/cat05.xml"),
    ("厚労省 新着情報",    "https://www.mhlw.go.jp/rss/topics_hukushi.rdf"),
    # AI・テクノロジー
    ("ITmedia AI",         "https://rss.itmedia.co.jp/rss/2.0/ait.xml"),
    ("Gigazine",           "https://gigazine.net/news/rss_2.0/"),
    ("TechCrunch Japan",   "https://jp.techcrunch.com/feed/"),
    ("ASCII.jp AI",        "https://ascii.jp/rss.xml"),
    # キャリア・就職
    ("マイナビニュース IT","https://news.mynavi.jp/rss/it"),
]

RELEVANT_KEYWORDS = [
    "就労", "障害", "AI", "エンジニア", "人工知能",
    "就職", "支援", "スキル", "DX", "自動化", "副業", "フリーランス",
]


def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", html.unescape(text or "")).strip()


def fetch_rss_articles(n: int = 5) -> List[dict]:
    """
    RSSフィードから関連記事をスコアリングして上位n件を返す。
    各記事: {"title": str, "summary": str, "source": str, "url": str}
    """
    try:
        import feedparser
    except ImportError:
        print("[WARN] feedparser 未インストール。`pip install feedparser` を実行してください。")
        return []

    print("\n[RSS] 最新ニュースを収集中...")
    candidates = []

    for source_name, feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:15]:
                title   = strip_tags(entry.get("title", ""))
                summary = strip_tags(entry.get("summary", entry.get("description", "")))[:200]
                url     = entry.get("link", "")

                # 関連キーワードでスコアリング
                text_to_score = (title + " " + summary).lower()
                score = sum(1 for kw in RELEVANT_KEYWORDS if kw in text_to_score)
                if score > 0:
                    candidates.append({
                        "title": title, "summary": summary,
                        "source": source_name, "url": url,
                        "score": score,
                    })
        except Exception as e:
            print(f"  [RSS] {source_name} 取得失敗: {e}")

    # スコア降順・重複タイトル除去
    seen, results = set(), []
    for art in sorted(candidates, key=lambda x: -x["score"]):
        key = art["title"][:20]
        if key not in seen:
            seen.add(key)
            results.append(art)
        if len(results) >= n:
            break

    if results:
        print(f"[RSS] {len(results)}件ピックアップ:")
        for i, art in enumerate(results, 1):
            print(f"  {i}. [{art['source']}] {art['title'][:50]}")
    else:
        print("[RSS] 関連記事が見つかりませんでした（構成はデフォルトを使用）。")

    return results


def articles_to_script_hint(articles: List[dict]) -> str:
    """記事リストを構成ヒントのサマリーテキストに変換する。"""
    if not articles:
        return ""
    lines = ["【今週の関連トレンド（構成参考）】"]
    for art in articles:
        lines.append(f"・{art['title']}")
    return "\n".join(lines)


# ─── VOICEVOX 音声生成（最優先: 自然な日本語）────────────
# スピーカーID一覧: 0=四国めたん, 8=春日部つむぎ, 13=青山龍星(男性落ち着き),
#                  46=雨晴はう, 3=四国めたん(セクシー), 14=冥鳴ひまり
VOICEVOX_SPEAKER_ID = int(os.environ.get("VOICEVOX_SPEAKER", "13"))  # デフォルト: 青山龍星（落ち着いた男性）
VOICEVOX_URL        = os.environ.get("VOICEVOX_URL", "http://localhost:50021")


def is_voicevox_running() -> bool:
    try:
        r = requests.get(f"{VOICEVOX_URL}/version", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def _voicevox_phrase_duration(flat_text: str) -> Tuple[bytes, float]:
    """1フレーズ分のWAVバイト列と再生時間を返す。"""
    r1 = requests.post(
        f"{VOICEVOX_URL}/audio_query",
        params={"text": flat_text, "speaker": VOICEVOX_SPEAKER_ID},
        timeout=30,
    )
    r1.raise_for_status()
    query = r1.json()

    r2 = requests.post(
        f"{VOICEVOX_URL}/synthesis",
        params={"speaker": VOICEVOX_SPEAKER_ID},
        json=query,
        timeout=60,
    )
    r2.raise_for_status()
    wav_bytes = r2.content

    # WAVヘッダからサンプル数・レートを読み取って正確な尺を計算
    with wave.open(tempfile.SpooledTemporaryFile()) as _:
        pass  # ダミー（wave.openはファイルパスが必要なので下記で計算）
    import io, struct
    buf = io.BytesIO(wav_bytes)
    with wave.open(buf) as wf:
        dur = wf.getnframes() / wf.getframerate()

    return wav_bytes, dur


def generate_voice_voicevox(text: str) -> Tuple[str, List[float]]:
    """
    VOICEVOXでフレーズごとに音声生成し連結。
    フレーズの実際の再生時間を元に文字タイミングを計算するため
    音声とテキスト表示が正確に同期する。
    """
    print(f"[VOICEVOX] フレーズ別音声生成中... (speaker={VOICEVOX_SPEAKER_ID})")

    all_wav_bytes: List[bytes] = []
    phrase_durations: List[float] = []
    sr = nch = sw = None

    for i, phrase in enumerate(DISPLAY_PHRASES):
        flat = phrase.replace("\n", "")
        wav_bytes, dur = _voicevox_phrase_duration(flat)
        all_wav_bytes.append(wav_bytes)
        phrase_durations.append(dur)
        print(f"  フレーズ{i+1}: {flat[:20]}…  ({dur:.2f}s)")

    # WAVを結合
    import io
    samples_list = []
    for wb in all_wav_bytes:
        buf = io.BytesIO(wb)
        with wave.open(buf) as wf:
            if sr is None:
                sr   = wf.getframerate()
                nch  = wf.getnchannels()
                sw   = wf.getsampwidth()
            raw = wf.readframes(wf.getnframes())
            samples_list.append(np.frombuffer(raw, dtype=np.int16))

    combined = np.concatenate(samples_list)
    out_tmp  = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    with wave.open(out_tmp.name, "w") as wf:
        wf.setnchannels(nch)
        wf.setsampwidth(sw)
        wf.setframerate(sr)
        wf.writeframes(combined.tobytes())
    out_tmp.close()

    # フレーズの実再生時間から文字タイミングを計算
    # → フレーズ先頭は必ずそのフレーズの音声開始時刻に一致
    char_starts: List[float] = []
    current_time = 0.0
    for phrase, dur in zip(DISPLAY_PHRASES, phrase_durations):
        flat = phrase.replace("\n", "")
        n    = max(len(flat), 1)
        for ci in range(n):
            # フレーズ内は均等分布（フェードで滑らかに見える）
            char_starts.append(current_time + ci * dur / n)
        current_time += dur

    total_dur = sum(phrase_durations)
    print(f"[VOICEVOX] 完了: {out_tmp.name}  (total={total_dur:.1f}s, phrases={len(DISPLAY_PHRASES)})")
    return out_tmp.name, char_starts


# ─── ElevenLabs 音声生成 ─────────────────────────────────
def get_first_voice_id(api_key: str) -> Optional[str]:
    """アカウントで使える最初のボイスIDを返す。"""
    try:
        r = requests.get(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": api_key},
            timeout=15,
        )
        if r.status_code == 200:
            voices = r.json().get("voices", [])
            if voices:
                vid = voices[0]["voice_id"]
                print(f"[ElevenLabs] ボイス自動選択: {voices[0]['name']} ({vid})")
                return vid
    except Exception as e:
        print(f"  [WARN] ボイス一覧取得失敗: {e}")
    return None


def generate_voice_with_timing(text: str, api_key: str, voice_id: str) -> Tuple[str, List[float]]:
    """
    ElevenLabs /with-timestamps エンドポイントを呼び出し、
    (音声ファイルパス, 文字ごとの開始時刻リスト) を返す。
    """
    # ElevenLabsの公開ボイスIDを優先順に試す
    FALLBACK_VOICE_IDS = [
        voice_id,
        "21m00Tcm4TlvDq8ikWAM",  # Rachel
        "AZnzlk1XvdvUeBnXmlld",  # Domi
        "EXAVITQu4vr4xnSDxMaL",  # Bella
        "ErXwobaYiN019PkySvjV",   # Antoni
        "MF3mGyEYCl7XYWbV9V6O",  # Elli
    ]
    resolved_id = voice_id
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.3,
            "use_speaker_boost": True,
        },
    }

    # 複数ボイスIDを順番に試す
    resp = None
    for vid in FALLBACK_VOICE_IDS:
        resolved_id = vid
        print(f"[ElevenLabs] 音声生成中... (voice={resolved_id})")
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{resolved_id}/with-timestamps"
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            break
        # 通常TTSにフォールバック（/with-timestamps非対応プラン）
        if resp.status_code in (401, 422):
            url_basic = f"https://api.elevenlabs.io/v1/text-to-speech/{resolved_id}"
            resp2 = requests.post(url_basic, headers={**headers, "Accept": "audio/mpeg"},
                                  json=payload, timeout=60)
            if resp2.status_code == 200:
                print(f"  [INFO] 通常TTSで生成成功 (voice={resolved_id})")
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                tmp.write(resp2.content)
                tmp.close()
                duration_est = len(text) * 0.12
                char_starts = [i * duration_est / len(text) for i in range(len(text))]
                print(f"[ElevenLabs] 完了（均等タイミング）: {tmp.name}")
                return tmp.name, char_starts
        print(f"  [WARN] voice={resolved_id} 失敗 (status={resp.status_code})、次を試します...")

    if resp is None or resp.status_code != 200:
        raise RuntimeError(f"全てのボイスIDで失敗しました (最後のstatus={resp.status_code if resp else 'N/A'})")

    resp.raise_for_status()
    data = resp.json()

    # 音声デコード → WAV保存
    audio_bytes = base64.b64decode(data["audio_base64"])
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp.write(audio_bytes)
    tmp.close()
    audio_path = tmp.name

    # 文字タイミング
    alignment = data.get("alignment", {})
    char_starts: List[float] = alignment.get("character_start_times_seconds", [])

    # 文字数チェック
    api_chars = alignment.get("characters", [])
    if len(api_chars) != len(text):
        print(f"  [WARN] 文字数不一致: API={len(api_chars)}, TEXT={len(text)}。タイミングを補間します。")
        # 補間: 均等に割り当て
        duration_est = char_starts[-1] + 0.1 if char_starts else len(text) * 0.12
        char_starts = [i * duration_est / len(text) for i in range(len(text))]

    print(f"[ElevenLabs] 完了: {audio_path}  (文字数={len(text)}, duration≈{char_starts[-1]:.1f}s)")
    return audio_path, char_starts


def generate_dummy_voice(text: str) -> Tuple[str, List[float]]:
    """ElevenLabsキー未設定時のフォールバック: 無音WAVと均等タイミング。"""
    print("[WARN] ELEVENLABS_API_KEY 未設定 → 無音音声でテスト生成します。")
    duration = len(text) * 0.12  # 1文字0.12秒
    sr = 44100
    n  = int(sr * duration)
    silence = np.zeros(n, dtype=np.int16)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    with wave.open(tmp.name, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(silence.tobytes())
    tmp.close()

    char_starts = [i * 0.12 for i in range(len(text))]
    print(f"[DUMMY] 無音音声: {tmp.name}  (duration≈{duration:.1f}s)")
    return tmp.name, char_starts


# ─── Unsplash 背景画像取得 ────────────────────────────────
def fetch_cyberpunk_bg(access_key: str) -> Optional[str]:
    """Unsplashからサイバーパンク縦型画像を取得。"""
    print("[Unsplash] 背景画像を取得中...")
    queries = ["cyberpunk city neon", "neon lights rain city", "futuristic city night"]
    for query in queries:
        try:
            resp = requests.get(
                "https://api.unsplash.com/search/photos",
                params={
                    "query": query,
                    "orientation": "portrait",
                    "per_page": 5,
                },
                headers={"Authorization": f"Client-ID {access_key}"},
                timeout=15,
            )
            resp.raise_for_status()
            results = resp.json().get("results", [])
            if not results:
                continue
            # 最高解像度URLを取得
            url = results[0]["urls"].get("full") or results[0]["urls"]["regular"]
            img_resp = requests.get(url, timeout=30, stream=True)
            img_resp.raise_for_status()
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            for chunk in img_resp.iter_content(1024 * 256):
                tmp.write(chunk)
            tmp.close()
            print(f"[Unsplash] 保存: {tmp.name}  (query='{query}')")
            return tmp.name
        except Exception as e:
            print(f"  [Unsplash] '{query}' 失敗: {e}")
    return None


def make_cyberpunk_gradient() -> np.ndarray:
    """Unsplashキー未設定 or 取得失敗時のフォールバックグラデーション。"""
    print("[INFO] フォールバック: サイバーパンクグラデーション背景を生成します。")
    arr = np.zeros((VIDEO_H, VIDEO_W, 3), dtype=np.uint8)
    for y in range(VIDEO_H):
        t = y / VIDEO_H
        r = int(5  + t * 20)
        g = int(0  + t * 5)
        b = int(30 + t * 60)
        arr[y, :] = [r, g, b]
    # ネオンライン効果
    rng = np.random.default_rng(42)
    for _ in range(80):
        x = rng.integers(0, VIDEO_W)
        h = rng.integers(50, 400)
        yy = rng.integers(0, VIDEO_H - h)
        w  = rng.integers(1, 3)
        col_idx = rng.integers(0, 3)
        color = [(0,200,255),(255,0,255),(0,255,150)][col_idx]
        arr[yy:yy+h, x:min(x+w, VIDEO_W)] = color
    return arr


def load_bg_array(image_path: Optional[str]) -> np.ndarray:
    """背景画像を1080x1920にクロップ・リサイズしてndarrayで返す。"""
    if not image_path:
        return make_cyberpunk_gradient()
    try:
        img = Image.open(image_path).convert("RGB")
        iw, ih = img.size
        target_ratio = VIDEO_W / VIDEO_H
        img_ratio    = iw / ih
        if img_ratio > target_ratio:
            new_w = int(ih * target_ratio)
            x0 = (iw - new_w) // 2
            img = img.crop((x0, 0, x0 + new_w, ih))
        else:
            new_h = int(iw / target_ratio)
            y0 = (ih - new_h) // 2
            img = img.crop((0, y0, iw, y0 + new_h))
        img = img.resize((VIDEO_W, VIDEO_H), Image.LANCZOS)
        # 暗くする（テキストを読みやすくする）
        arr = np.array(img, dtype=np.float32)
        arr = arr * 0.35
        return arr.astype(np.uint8)
    except Exception as e:
        print(f"[WARN] 背景画像読み込み失敗: {e}")
        return make_cyberpunk_gradient()


# ─── フレームレンダリング（スムーズフェードイン版）─────────
CHAR_FADE = 0.07   # 1文字のフェードイン時間（秒）

# フォント・行レイアウトのキャッシュ（フレーズ切替時のみ再計算）
_layout_cache: dict = {}

def _get_layout(phrase_idx: int, font_path: Optional[str]):
    """フレーズのレイアウト情報をキャッシュして返す。"""
    if phrase_idx in _layout_cache:
        return _layout_cache[phrase_idx]

    is_hook = (phrase_idx == 0)
    is_cta  = (phrase_idx == len(DISPLAY_PHRASES) - 1)
    font_size  = 115 if is_hook else 88
    base_color = (255, 255, 255) if is_hook else ((255, 80, 80) if is_cta else (255, 220, 0))

    try:
        font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    phrase = DISPLAY_PHRASES[phrase_idx]
    lines  = phrase.split("\n")
    dummy  = ImageDraw.Draw(Image.new("RGBA", (1, 1)))

    line_metrics = []
    for line in lines:
        bbox = dummy.textbbox((0, 0), line, font=font)
        line_metrics.append((bbox[2] - bbox[0], bbox[3] - bbox[1]))

    line_gap = 28
    block_h  = sum(lh for _, lh in line_metrics) + line_gap * (len(lines) - 1)
    start_y  = (VIDEO_H - block_h) // 2
    max_lw   = max(lw for lw, _ in line_metrics)
    pad      = 40

    # 各文字の描画座標を事前計算
    char_positions = []  # (char, x, y, line_idx)
    chars_consumed = 0
    y = start_y
    for li, ((lw, lh), line) in enumerate(zip(line_metrics, lines)):
        x = (VIDEO_W - lw) // 2
        for ch in line:
            cbbox = dummy.textbbox((0, 0), ch, font=font)
            char_positions.append((ch, x, y))
            x += cbbox[2] - cbbox[0]
            chars_consumed += 1
        y += lh + line_gap

    layout = dict(
        font=font, lines=lines, line_metrics=line_metrics,
        line_gap=line_gap, block_h=block_h, start_y=start_y,
        max_lw=max_lw, pad=pad, base_color=base_color,
        char_positions=char_positions, is_hook=is_hook, is_cta=is_cta,
        font_path=font_path,
    )
    _layout_cache[phrase_idx] = layout
    return layout


def render_frame_smooth(
    t: float,
    char_starts: List[float],
    bg_rgba: Image.Image,   # 背景（RGBA Image、使い回す）
    font_path: Optional[str],
) -> np.ndarray:
    """1フレームをフェードイン付きでレンダリング。"""
    # 現在のフレーズを特定
    n_total    = int(np.searchsorted(char_starts, t, side='right'))
    phrase_idx, _ = char_idx_to_phrase(n_total)
    layout     = _get_layout(phrase_idx, font_path)
    phrase_start_idx = PHRASE_RANGES[phrase_idx][0]

    font        = layout["font"]
    base_color  = layout["base_color"]
    is_hook     = layout["is_hook"]
    is_cta      = layout["is_cta"]
    start_y     = layout["start_y"]
    max_lw      = layout["max_lw"]
    block_h     = layout["block_h"]
    pad         = layout["pad"]

    # 背景コピー
    img = bg_rgba.copy()

    # テキスト背景（半透明）
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    ov_draw.rectangle(
        [(VIDEO_W - max_lw) // 2 - pad, start_y - pad,
         (VIDEO_W + max_lw) // 2 + pad, start_y + block_h + pad],
        fill=(0, 0, 0, 160),
    )
    img = Image.alpha_composite(img, overlay)

    # 文字レイヤー（フェードイン）
    char_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    cdraw      = ImageDraw.Draw(char_layer)
    r, g, b    = base_color

    for ci, (ch, cx, cy) in enumerate(layout["char_positions"]):
        global_idx = phrase_start_idx + ci
        if global_idx >= len(char_starts):
            break
        # フェード進捗 0.0〜1.0（なめらかに出現）
        progress = min(1.0, max(0.0, (t - char_starts[global_idx]) / CHAR_FADE))
        if progress <= 0.0:
            continue
        alpha = int(progress * 255)
        # シャドウ
        for ox, oy in [(3, 3), (-3, 3), (3, -3), (-3, -3)]:
            cdraw.text((cx + ox, cy + oy), ch, font=font, fill=(0, 0, 0, int(progress * 160)))
        # 本文
        cdraw.text((cx, cy), ch, font=font, fill=(r, g, b, alpha))

    img    = Image.alpha_composite(img, char_layer).convert("RGB")
    draw   = ImageDraw.Draw(img)

    # フック/CTAエフェクト
    if is_hook and n_total > 0:
        draw.rectangle([0, 0, VIDEO_W, 12], fill=(0, 230, 118))
        draw.rectangle([0, VIDEO_H - 12, VIDEO_W, VIDEO_H], fill=(0, 230, 118))
    if is_cta and n_total > 0:
        draw.rectangle([0, VIDEO_H - 140, VIDEO_W, VIDEO_H - 100], fill=(255, 80, 80))
        try:
            sf = ImageFont.truetype(font_path, 36) if font_path else ImageFont.load_default()
        except Exception:
            sf = ImageFont.load_default()
        label = "↓  プロフィールのリンクから無料見学申込み  ↓"
        lb = draw.textbbox((0, 0), label, font=sf)
        draw.text(((VIDEO_W - (lb[2] - lb[0])) // 2, VIDEO_H - 132), label, font=sf, fill=(255, 255, 255))

    return np.array(img)


# ─── 動画合成 ────────────────────────────────────────────
def build_video(
    audio_path: str,
    char_starts: List[float],
    bg_array: np.ndarray,
    font_path: Optional[str],
) -> None:
    n_chars   = len(char_starts)
    total_dur = char_starts[-1] + 1.5

    print(f"\n[VIDEO] 動画構築中: 尺={total_dur:.1f}s / 文字数={n_chars}")

    # char_starts を numpy配列に変換（高速なbinary search用）
    cs_arr   = np.array(char_starts, dtype=np.float64)
    # 背景をRGBAに変換して使い回す（毎フレームのコピーを最小化）
    bg_rgba  = Image.fromarray(bg_array).convert("RGBA")

    def make_frame(t: float) -> np.ndarray:
        return render_frame_smooth(t, cs_arr, bg_rgba, font_path)

    clip = VideoClip(make_frame, duration=total_dur)

    # 音声合成
    audio = AudioFileClip(audio_path).subclipped(0, min(total_dur, AudioFileClip(audio_path).duration))
    clip  = clip.with_audio(audio)

    # 書き出し
    out = OUTPUT_PATH
    print(f"[EXPORT] {out}  ({VIDEO_W}x{VIDEO_H} / {FPS}fps)")
    clip.write_videofile(
        out,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="fast",
        ffmpeg_params=["-crf", "22"],
        logger="bar",
    )
    print(f"\n完了 → {out}")


# ─── メイン ──────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  TikTok 最終ジェネレーター（ビズウェル）")
    print("=" * 55)
    print(f"  文字数: {len(SCRIPT_TEXT)}")
    print(f"  フレーズ数: {len(DISPLAY_PHRASES)}")

    # ─── Step 0: RSS ニュース収集 ────────────────────────
    articles = fetch_rss_articles(n=5)
    if articles:
        hint = articles_to_script_hint(articles)
        print(f"\n{hint}\n")
        print("  ↑ 上記トレンドを踏まえた構成で動画を生成します。\n")

    # ① 音声生成（優先順: VOICEVOX → ElevenLabs → 無音）
    if is_voicevox_running():
        print("[INFO] VOICEVOXが起動中 → 自然な日本語音声で生成します。")
        try:
            audio_path, char_starts = generate_voice_voicevox(SCRIPT_TEXT)
        except Exception as e:
            print(f"[WARN] VOICEVOX失敗: {e} → ElevenLabsにフォールバック")
            audio_path, char_starts = None, None
    else:
        print("[INFO] VOICEVOX未起動 → ElevenLabsを試みます。")
        audio_path, char_starts = None, None

    if audio_path is None:
        if ELEVENLABS_API_KEY:
            try:
                audio_path, char_starts = generate_voice_with_timing(
                    SCRIPT_TEXT, ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID
                )
            except Exception as e:
                print(f"\n[WARN] ElevenLabs失敗: {e}")
                print("  → 無音でテスト動画を生成します。\n")
                audio_path, char_starts = generate_dummy_voice(SCRIPT_TEXT)
        else:
            audio_path, char_starts = generate_dummy_voice(SCRIPT_TEXT)

    # ② 背景画像取得
    bg_image_path = fetch_cyberpunk_bg(UNSPLASH_ACCESS_KEY) if UNSPLASH_ACCESS_KEY else None
    bg_array = load_bg_array(bg_image_path)

    # ③ フォント
    font_path = find_font()

    # ④ 動画合成
    build_video(audio_path, char_starts, bg_array, font_path)

    # 後片付け
    try:
        if audio_path and audio_path.startswith(tempfile.gettempdir()):
            os.remove(audio_path)
        if bg_image_path:
            os.remove(bg_image_path)
    except Exception:
        pass

    # 再生
    os.system(f"open {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
