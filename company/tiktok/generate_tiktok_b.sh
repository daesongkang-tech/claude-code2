#!/bin/bash
# Pattern B: AIスキル体験版 (tech BGM / purple-cyan)
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f "$HOME/.zshrc" ]; then source "$HOME/.zshrc" 2>/dev/null || true; fi

echo "======================================"
echo "  Pattern B AIスキル版 - TikTok動画生成"
echo "======================================"

echo ""
echo "[1/2] BGMを生成中 (tech style)..."
python3 -c "
import sys
sys.path.insert(0, '.')
from tiktok_bizwell_generator import generate_bgm
generate_bgm(24.0, 'temp_bgm.wav', 'tech')
"

echo ""
echo "[2/2] HTMLを録画中..."
HTML_PATH="$SCRIPT_DIR/tiktok_bizwell_pattern_b.html" \
OUTPUT_PATH="$SCRIPT_DIR/output_pattern_b.mp4" \
DURATION=22 \
node record_tiktok.js

echo ""
echo "動画を開いています..."
open "$SCRIPT_DIR/output_pattern_b.mp4"
