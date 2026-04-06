"""
ビズウェル TikTokリール動画 自動生成スクリプト v3
================================================
・縦型 1080x1920 / 30fps / MP4 出力
・BGM を numpy + wave で自動生成（外部サービス不要）
・Pexels API キーがあれば背景に動画素材を使用
・MoviePy 2.x 対応

【事前準備】
  pip install moviepy requests pillow numpy

【実行方法】
  python3 tiktok_bizwell_generator.py

  # Pexels 動画背景を使う場合（任意）
  export PEXELS_API_KEY="your_key_here"
  python3 tiktok_bizwell_generator.py
"""

import os, sys, wave, math, tempfile, struct, requests
import numpy as np
from pathlib import Path
from typing import Optional

try:
    from moviepy import (
        VideoFileClip, ImageClip, CompositeVideoClip,
        concatenate_videoclips, ColorClip, AudioFileClip
    )
    from moviepy import vfx
    from PIL import Image, ImageDraw, ImageFont
    if not hasattr(Image, "ANTIALIAS"):
        Image.ANTIALIAS = Image.LANCZOS
except ImportError as e:
    print(f"[ERROR] パッケージ不足: {e}")
    print("  pip install moviepy requests pillow numpy")
    sys.exit(1)

# ─── 設定 ────────────────────────────────────────────
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
OUTPUT_PATH    = "output_bizwell_tiktok.mp4"
VIDEO_W        = 1080
VIDEO_H        = 1920
FPS            = 30

FONT_CANDIDATES = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W9.ttc",
    "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc",
    "/Library/Fonts/NotoSansJP-Bold.otf",
    "./NotoSansJP-Bold.otf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
]

# ─── シーン定義（就労移行支援事業所PR動画）────────────
SCENES = [
    # ── Scene 1: HOOK ──────────────────────────────────
    {
        "id": 1, "duration": 6.0,
        "pexels_query": "artificial intelligence technology glow",
        "bg_color": (5, 5, 15),
        "texts": [
            {"text": "AIが学べる",               "t": 0.3, "y": 0.35, "size": 80,  "color": (0,230,118),   "align": "center"},
            {"text": "就労移行支援",              "t": 0.9, "y": 0.47, "size": 86,  "color": (255,255,255), "align": "center"},
            {"text": "知ってますか？",            "t": 1.5, "y": 0.59, "size": 86,  "color": (255,255,255), "align": "center"},
            {"text": "障害のある方が無料でAIを学んでIT就職できます", "t": 2.4, "y": 0.73, "size": 34, "color": (140,200,255), "align": "center"},
            {"text": "最後まで見てください",      "t": 3.2, "y": 0.82, "size": 36,  "color": (100,100,100), "align": "center"},
        ],
    },
    # ── Scene 2: PROBLEM ───────────────────────────────
    {
        "id": 2, "duration": 8.0,
        "pexels_query": "person laptop thinking office",
        "bg_color": (10, 20, 40),
        "bg_overlay": 0.55,
        "texts": [
            {"text": "こんなお悩みありませんか？",     "t": 0.4, "y": 0.18, "size": 40, "color": (150,210,255), "align": "center"},
            {"text": "「障害があって",               "t": 0.8, "y": 0.30, "size": 68, "color": (255,255,255), "align": "center"},
            {"text": "働ける気がしない…」",          "t": 0.8, "y": 0.40, "size": 68, "color": (255,255,255), "align": "center"},
            {"text": "「スキルが何もなくて",          "t": 1.5, "y": 0.52, "size": 58, "color": (220,220,220), "align": "center"},
            {"text": "自信がない…」",               "t": 1.5, "y": 0.61, "size": 58, "color": (220,220,220), "align": "center"},
            {"text": "その悩み、ビズウェルが解決します",   "t": 2.8, "y": 0.74, "size": 38, "color": (0,230,118), "align": "center"},
            {"text": "AIスキル × 就職支援 × 給付金活用", "t": 3.4, "y": 0.83, "size": 32, "color": (100,181,246), "align": "center"},
        ],
    },
    # ── Scene 3: SOLUTION ──────────────────────────────
    {
        "id": 3, "duration": 10.0,
        "pexels_query": "learning computer education modern",
        "bg_color": (0, 50, 35),
        "bg_overlay": 0.50,
        "texts": [
            {"text": "ビズウェルが選ばれる理由",                  "t": 0.3, "y": 0.10, "size": 40, "color": (150,255,200), "align": "center"},
            {"text": "AI特化型",                                  "t": 0.7, "y": 0.19, "size": 70, "color": (0,230,118),   "align": "center"},
            {"text": "就労移行支援",                              "t": 0.7, "y": 0.28, "size": 70, "color": (255,255,255), "align": "center"},
            {"text": "[ AI学習 ]  ChatGPT・画像生成・自動化",     "t": 1.2, "y": 0.39, "size": 36, "color": (255,255,255), "align": "left"},
            {"text": "実務で使えるAIスキルをゼロから習得",         "t": 1.2, "y": 0.45, "size": 26, "color": (200,255,230), "align": "left"},
            {"text": "[ IT就職 ]  リモートワーク就職実績あり",     "t": 1.9, "y": 0.53, "size": 36, "color": (255,255,255), "align": "left"},
            {"text": "在宅勤務可のIT企業への転職をフルサポート",   "t": 1.9, "y": 0.59, "size": 26, "color": (200,255,230), "align": "left"},
            {"text": "[ 個別支援 ]  専任スタッフが毎日サポート",   "t": 2.6, "y": 0.67, "size": 36, "color": (255,255,255), "align": "left"},
            {"text": "自分のペースで無理なく続けられる環境",       "t": 2.6, "y": 0.73, "size": 26, "color": (200,255,230), "align": "left"},
            {"text": "[ 給付金 ]  最大月10万円支給の場合あり",     "t": 3.3, "y": 0.81, "size": 36, "color": (255,255,255), "align": "left"},
            {"text": "受講料¥0・交通費支給・給付金活用OK",         "t": 3.3, "y": 0.87, "size": 26, "color": (200,255,230), "align": "left"},
        ],
    },
    # ── Scene 4: カリキュラム紹介 ───────────────────────
    {
        "id": 4, "duration": 8.0,
        "pexels_query": "coding screen laptop workspace dark",
        "bg_color": (12, 10, 30),
        "bg_overlay": 0.60,
        "texts": [
            {"text": "実際に学べるAIスキル",           "t": 0.4, "y": 0.15, "size": 50, "color": (200,180,255), "align": "center"},
            {"text": "カリキュラム例",                 "t": 0.6, "y": 0.23, "size": 32, "color": (120,100,180), "align": "center"},
            {"text": "ChatGPTで文章・メール作成",       "t": 1.0, "y": 0.33, "size": 40, "color": (0,230,118),   "align": "center"},
            {"text": "画像生成AIでデザイン制作",        "t": 1.7, "y": 0.43, "size": 40, "color": (100,181,246), "align": "center"},
            {"text": "業務自動化ツールの操作",          "t": 2.4, "y": 0.53, "size": 40, "color": (255,200,80),  "align": "center"},
            {"text": "AIを活用した就職書類作成",        "t": 3.1, "y": 0.63, "size": 40, "color": (255,130,100), "align": "center"},
            {"text": "プログラミング×AI基礎",          "t": 3.8, "y": 0.73, "size": 40, "color": (150,255,200), "align": "center"},
            {"text": "修了後はIT企業への就職を全力サポート！", "t": 4.8, "y": 0.85, "size": 34, "color": (255,255,255), "align": "center"},
        ],
    },
    # ── Scene 5: CTA ───────────────────────────────────
    {
        "id": 5, "duration": 8.0,
        "pexels_query": "team diversity smile support office",
        "bg_color": (0, 70, 60),
        "bg_overlay": 0.45,
        "texts": [
            {"text": "ビズウェル",                        "t": 0.4, "y": 0.25, "size": 96, "color": (255,255,255), "align": "center"},
            {"text": "株式会社ビズリンクウェルビーイング",  "t": 0.7, "y": 0.36, "size": 30, "color": (200,255,230), "align": "center"},
            {"text": "まずは無料見学から",                  "t": 1.2, "y": 0.48, "size": 66, "color": (0,230,118),   "align": "center"},
            {"text": "相談・見学 完全無料",                 "t": 1.8, "y": 0.58, "size": 44, "color": (255,255,255), "align": "center"},
            {"text": "オンライン相談OK | 全国対応",         "t": 2.1, "y": 0.66, "size": 36, "color": (200,255,230), "align": "center"},
            {"text": "精神・発達障害のある方・ご家族歓迎",  "t": 2.5, "y": 0.74, "size": 32, "color": (200,255,230), "align": "center"},
            {"text": "受講料¥0 | 就職実績あり",            "t": 2.9, "y": 0.81, "size": 38, "color": (255,220,80),  "align": "center"},
            {"text": "プロフィールのリンクから申込み",      "t": 3.5, "y": 0.90, "size": 42, "color": (255,255,255), "align": "center"},
        ],
    },
]


# ─── BGM 生成（numpy + wave）────────────────────────────
def generate_bgm(duration: float, out_path: str = "temp_bgm.wav", style: str = "default") -> str:
    sr = 44100
    n  = int(sr * duration)
    t  = np.linspace(0, duration, n, endpoint=False)

    notes = {
        "C3": 130.81, "D3": 146.83, "E3": 164.81, "F3": 174.61, "G3": 196.00,
        "A3": 220.00, "B3": 246.94,
        "C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23,
        "G4": 392.00, "A4": 440.00, "B4": 493.88,
        "C5": 523.25, "D5": 587.33,
    }

    def note_burst(freq, start_sec, dur_sec, amp=0.25):
        s = int(start_sec * sr)
        e = min(int((start_sec + dur_sec) * sr), n)
        length = e - s
        if length <= 0:
            return np.zeros(n)
        lt = np.linspace(0, dur_sec, length, endpoint=False)
        env = np.minimum(lt / 0.02, 1.0) * np.exp(-lt * 3.0)
        out = np.zeros(n)
        out[s:e] = amp * env * np.sin(2 * np.pi * freq * lt)
        return out

    if style == "calm":
        bpm, pad_amp, mel_amp = 75, 0.07, 0.18
        chord = [notes["A3"], notes["C4"], notes["E4"]]
        pattern = [
            ("A3", 0.0, 0.6), ("C4", 0.6, 0.6), ("E4", 1.2, 1.2),
            ("G3", 2.4, 0.6), ("A3", 3.0, 0.6), ("E3", 3.6, 0.8),
        ]
    elif style == "tech":
        bpm, pad_amp, mel_amp = 128, 0.04, 0.28
        chord = [notes["D3"], notes["F3"], notes["A3"]]
        pattern = [
            ("D4", 0.0, 0.12), ("F4", 0.12, 0.12), ("A4", 0.25, 0.12), ("D5", 0.37, 0.12),
            ("A4", 0.5, 0.12), ("F4", 0.62, 0.12), ("D4", 0.75, 0.25),
            ("E4", 1.0, 0.12), ("G4", 1.12, 0.12), ("A4", 1.25, 0.25),
            ("B4", 1.5, 0.12), ("A4", 1.62, 0.12), ("G4", 1.75, 0.25),
        ]
    elif style == "upbeat":
        bpm, pad_amp, mel_amp = 100, 0.06, 0.24
        chord = [notes["G3"], notes["B3"], notes["D4"]]
        pattern = [
            ("G4", 0.0, 0.3), ("B4", 0.3, 0.3), ("D5", 0.6, 0.6),
            ("B4", 1.2, 0.3), ("G4", 1.5, 0.3), ("D4", 1.8, 0.6),
            ("A4", 2.4, 0.3), ("G4", 2.7, 0.3), ("E4", 3.0, 0.6),
            ("D4", 3.6, 0.3), ("E4", 3.9, 0.3), ("G4", 4.2, 0.6),
        ]
    else:
        bpm, pad_amp, mel_amp = 120, 0.05, 0.22
        chord = [notes["C3"], notes["E3"], notes["G3"], notes["C4"]]
        pattern = [
            ("C4", 0.0, 0.25), ("E4", 0.25, 0.25), ("G4", 0.5, 0.25), ("A4", 0.75, 0.25),
            ("G4", 1.0, 0.5 ), ("E4", 1.5,  0.25), ("C4", 1.75, 0.25),
            ("D4", 2.0, 0.25), ("F4", 2.25, 0.25), ("A4", 2.5,  0.25), ("G4", 2.75, 0.25),
            ("E4", 3.0, 0.5 ), ("C4", 3.5,  0.25), ("E4", 3.75, 0.25),
        ]

    beat_dur   = 60.0 / bpm
    phrase_dur = beat_dur * 4
    loop_sec   = phrase_dur

    pad    = np.zeros(n)
    loop_n = int(loop_sec * sr)
    lt     = np.linspace(0, loop_sec, loop_n, endpoint=False)
    chunk  = sum(pad_amp * np.sin(2 * np.pi * f * lt) for f in chord)
    fade   = np.minimum(lt / 0.3, 1.0) * np.minimum((loop_sec - lt) / 0.3, 1.0)
    chunk *= fade
    for start in range(0, n, loop_n):
        end = min(start + loop_n, n)
        pad[start:end] += chunk[:end - start]

    melody      = np.zeros(n)
    num_phrases = math.ceil(duration / phrase_dur)
    for phrase_i in range(num_phrases):
        phrase_start = phrase_i * phrase_dur
        for note_name, beat_off, note_dur in pattern:
            melody += note_burst(notes[note_name],
                                 phrase_start + beat_off * beat_dur,
                                 note_dur * beat_dur, amp=mel_amp)

    audio = pad + melody
    fade_samples = int(1.5 * sr)
    audio[-fade_samples:] *= np.linspace(1, 0, fade_samples)
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.75

    audio_int = (audio * 32767).astype(np.int16)
    with wave.open(out_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio_int.tobytes())

    print(f"[BGM] 生成完了: {out_path}  ({duration:.1f}秒, style={style})")
    return out_path


# ─── ユーティリティ ──────────────────────────────────────
def find_font() -> Optional[str]:
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            print(f"[FONT] {p}")
            return p
    print("[FONT] 日本語フォントが見つかりません。デフォルトを使用します。")
    return None


def fetch_pexels_video(query: str, min_dur: int = 8) -> Optional[str]:
    if not PEXELS_API_KEY:
        return None
    try:
        print(f"  [Pexels] '{query}' を検索中...")
        r = requests.get(
            "https://api.pexels.com/videos/search",
            headers={"Authorization": PEXELS_API_KEY},
            params={"query": query, "per_page": 10, "orientation": "portrait"},
            timeout=15,
        )
        r.raise_for_status()
        videos = r.json().get("videos", [])
        candidates = [v for v in videos if v.get("duration", 0) >= min_dur] or videos
        if not candidates:
            return None
        files = sorted(
            [f for f in candidates[0].get("video_files", []) if f.get("quality") in ("hd", "sd")],
            key=lambda f: abs(f.get("height", 0) - 1080),
        )
        url = (files or candidates[0].get("video_files", [{}]))[0].get("link")
        if not url:
            return None
        vr  = requests.get(url, timeout=60, stream=True)
        vr.raise_for_status()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        for chunk in vr.iter_content(1024 * 256):
            tmp.write(chunk)
        tmp.close()
        print(f"  [Pexels] 保存: {tmp.name}")
        return tmp.name
    except Exception as e:
        print(f"  [Pexels] エラー: {e}")
        return None


def gradient_bg(color, w=VIDEO_W, h=VIDEO_H) -> np.ndarray:
    r, g, b = color
    frame = np.zeros((h, w, 3), np.uint8)
    for y in range(h):
        ratio = y / h
        frame[y, :] = [
            max(0, int(r * (1 - ratio * 0.45))),
            max(0, int(g * (1 - ratio * 0.45))),
            max(0, int(b * (1 - ratio * 0.45))),
        ]
    return frame


def make_text_img(text: str, font_path: Optional[str], size: int, color: tuple) -> np.ndarray:
    try:
        font = ImageFont.truetype(font_path, size) if font_path else ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    dummy = Image.new("RGBA", (1, 1))
    bbox  = ImageDraw.Draw(dummy).textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad    = 16
    img    = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    d      = ImageDraw.Draw(img)
    for ox, oy in [(3, 3), (-3, 3), (3, -3), (-3, -3)]:
        d.text((pad + ox, pad + oy), text, font=font, fill=(0, 0, 0, 160))
    d.text((pad, pad), text, font=font, fill=(*color, 255))
    return np.array(img)


def build_scene(scene: dict, font_path: Optional[str]) -> CompositeVideoClip:
    dur = scene["duration"]
    print(f"\n[Scene {scene['id']}] {dur}s")

    # 背景
    video_path = fetch_pexels_video(scene["pexels_query"]) if PEXELS_API_KEY else None
    if video_path:
        try:
            raw = VideoFileClip(video_path)
            cw, ch = raw.size
            tr = VIDEO_W / VIDEO_H
            cr = cw / ch
            if cr > tr:
                nw = int(ch * tr)
                raw = raw.cropped(x1=(cw - nw) // 2, y1=0, x2=(cw - nw) // 2 + nw, y2=ch)
            else:
                nh = int(cw / tr)
                raw = raw.cropped(x1=0, y1=(ch - nh) // 2, x2=cw, y2=(ch - nh) // 2 + nh)
            raw = raw.resized((VIDEO_W, VIDEO_H))
            if raw.duration < dur:
                raw = concatenate_videoclips([raw] * math.ceil(dur / raw.duration))
            bg = raw.subclipped(0, dur)
            ov = ColorClip((VIDEO_W, VIDEO_H), color=(0, 0, 0)).with_opacity(scene.get("bg_overlay", 0.4)).with_duration(dur)
            bg = CompositeVideoClip([bg, ov])
        except Exception as e:
            print(f"  [WARN] 動画処理失敗: {e}")
            bg = ImageClip(gradient_bg(scene["bg_color"])).with_duration(dur)
    else:
        bg = ImageClip(gradient_bg(scene["bg_color"])).with_duration(dur)

    # テキストオーバーレイ
    layers = [bg]
    left_margin = 60
    for td in scene.get("texts", []):
        img  = make_text_img(td["text"], font_path, td["size"], td["color"])
        iw, ih = img.shape[1], img.shape[0]
        t_end = dur - 0.3

        if td.get("align") == "left":
            x = left_margin
        else:
            x = (VIDEO_W - iw) // 2

        y = int(VIDEO_H * td["y"]) - ih // 2

        clip = (
            ImageClip(img)
            .with_start(td["t"])
            .with_duration(t_end - td["t"])
            .with_position((x, y))
            .with_effects([vfx.CrossFadeIn(0.35)])
        )
        layers.append(clip)

    return CompositeVideoClip(layers, size=(VIDEO_W, VIDEO_H)).with_duration(dur)


# ─── メイン ──────────────────────────────────────────────
def main():
    print("=" * 52)
    print("  ビズウェル TikTokリール動画 生成スクリプト v3")
    print("=" * 52)

    if not PEXELS_API_KEY:
        print("\n[INFO] PEXELS_API_KEY 未設定 → グラデーション背景で生成")
    font_path = find_font()

    # シーン構築
    clips = [build_scene(s, font_path) for s in SCENES]
    total_dur = sum(s["duration"] for s in SCENES)

    # 結合
    print("\n[COMPOSE] シーンを結合中...")
    final = concatenate_videoclips(clips, method="compose")

    # BGM 生成・合成
    print("[BGM] 音楽を生成中...")
    bgm_path = generate_bgm(total_dur + 1.0)
    bgm_clip = AudioFileClip(bgm_path).subclipped(0, final.duration)
    final    = final.with_audio(bgm_clip)

    # 書き出し
    print(f"\n[EXPORT] {OUTPUT_PATH}")
    print(f"  解像度: {VIDEO_W}x{VIDEO_H} / FPS: {FPS} / 尺: {final.duration:.1f}秒")
    final.write_videofile(
        OUTPUT_PATH,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="fast",
        ffmpeg_params=["-crf", "22"],
        logger="bar",
    )

    try:
        os.remove(bgm_path)
    except Exception:
        pass

    print(f"\n完了 → {OUTPUT_PATH}")
    print("TikTokアプリで動画を選択して投稿してください。")


if __name__ == "__main__":
    main()
