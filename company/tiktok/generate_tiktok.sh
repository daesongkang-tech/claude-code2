#!/bin/bash
# ビズウェル TikTok動画 自動生成スクリプト
# 使い方: ./generate_tiktok.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# ~/.zshrc から環境変数を読み込む（Pexels等）
if [ -f "$HOME/.zshrc" ]; then
  source "$HOME/.zshrc" 2>/dev/null || true
fi

echo "======================================"
echo "  ビズウェル TikTok動画 生成開始"
echo "======================================"

# Step 1: BGM生成（Pythonで合成）
echo ""
echo "[1/2] BGMを生成中..."
python3 -c "
import sys
sys.path.insert(0, '.')
from tiktok_bizwell_generator import generate_bgm
generate_bgm(24.0, 'temp_bgm.wav', 'default')
"

# Step 2: HTMLをPuppeteerで録画 → BGM合成 → MP4出力
echo ""
echo "[2/2] HTMLを録画中（約5〜10分かかります）..."
node record_tiktok.js

echo ""
echo "動画を開いています..."
open output_bizwell_tiktok.mp4
