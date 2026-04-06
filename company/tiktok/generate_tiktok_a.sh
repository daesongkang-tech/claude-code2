#!/bin/bash
# Pattern A: 給付金強調版 (calm BGM / amber)
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f "$HOME/.zshrc" ]; then source "$HOME/.zshrc" 2>/dev/null || true; fi

echo "======================================"
echo "  Pattern A 給付金版 - TikTok動画生成"
echo "======================================"

echo ""
echo "[1/2] BGMを生成中 (calm style)..."
python3 -c "
import sys
sys.path.insert(0, '.')
from tiktok_bizwell_generator import generate_bgm
generate_bgm(24.0, 'temp_bgm.wav', 'calm')
"

echo ""
echo "[2/2] HTMLを録画中..."
HTML_PATH="$SCRIPT_DIR/tiktok_bizwell_pattern_a.html" \
OUTPUT_PATH="$SCRIPT_DIR/output_pattern_a.mp4" \
DURATION=22 \
node record_tiktok.js

echo ""
echo "動画を開いています..."
open "$SCRIPT_DIR/output_pattern_a.mp4"
