/**
 * ビズウェル TikTok動画 Puppeteer録画スクリプト
 *
 * HTMLをヘッドレスChromeで内部レンダリングし、
 * フレームごとにPNGキャプチャ → FFmpegでMP4化(1080x1920) → BGM合成
 */

const puppeteer = require('puppeteer');
const fs        = require('fs');
const path      = require('path');
const ffmpegStatic = require('ffmpeg-static');
const ffmpeg    = require('fluent-ffmpeg');

ffmpeg.setFfmpegPath(ffmpegStatic);

// ─── 設定（環境変数で上書き可能）────────────────────────
const HTML_PATH    = process.env.HTML_PATH    || path.resolve(__dirname, 'tiktok_bizwell_20260324.html');
const BGM_PATH     = process.env.BGM_PATH     || path.resolve(__dirname, 'temp_bgm.wav');
const OUTPUT_PATH  = process.env.OUTPUT_PATH  || path.resolve(__dirname, 'output_bizwell_tiktok.mp4');
const FRAMES_DIR   = path.resolve(__dirname, '.frames_tmp');
const VIDEO_SILENT = path.resolve(__dirname, '.video_silent.mp4');

const FPS          = 30;
const DURATION     = parseInt(process.env.DURATION || '22');  // 秒
// HTMLの .video 要素のネイティブサイズ
const NATIVE_W     = 390;
const NATIVE_H     = 844;
// 出力サイズ（TikTok 縦型）
const OUT_W        = 1080;
const OUT_H        = 1920;
// ──────────────────────────────────────────────────────

async function captureFrames(page) {
  const totalFrames = Math.ceil(DURATION * FPS);
  console.log(`[CAPTURE] ${totalFrames} フレームをキャプチャします...`);

  if (fs.existsSync(FRAMES_DIR)) fs.rmSync(FRAMES_DIR, { recursive: true });
  fs.mkdirSync(FRAMES_DIR);

  // .video 要素の位置を取得
  const clip = await page.evaluate(() => {
    const el = document.querySelector('.video');
    const r  = el.getBoundingClientRect();
    return { x: r.left, y: r.top, width: r.width, height: r.height };
  });
  console.log(`[CLIP]    .video 要素: ${clip.width}x${clip.height} @ (${clip.x}, ${clip.y})`);

  // アニメーションを一時停止
  await page.evaluate(() => {
    document.getAnimations().forEach(a => a.pause());
  });

  for (let i = 0; i < totalFrames; i++) {
    const pageTimeMs = (i / FPS) * 1000;

    // 各アニメーションをページ時刻 T に合わせてセット
    await page.evaluate((t) => {
      document.getAnimations().forEach(anim => {
        const delay = anim.effect ? (anim.effect.getTiming().delay || 0) : 0;
        anim.currentTime = t - delay;
      });
    }, pageTimeMs);

    const framePath = path.join(FRAMES_DIR, `frame_${String(i).padStart(5, '0')}.png`);
    // .video 要素だけをクリップしてキャプチャ
    await page.screenshot({ path: framePath, type: 'png', clip });

    if (i % FPS === 0) {
      const pct = Math.round((i / totalFrames) * 100);
      process.stdout.write(`\r  進捗: ${pct}% (${i}/${totalFrames})`);
    }
  }
  process.stdout.write('\n');
}

function framesToVideo() {
  return new Promise((resolve, reject) => {
    console.log('[VIDEO]  フレームを動画に変換中 (スケール→パッド 1080x1920)...');

    // スケール: clip サイズを高さ基準で 1920 にフィット
    // 例: 390x844 → scale=-2:1920 → 887x1920 → pad 1080x1920
    const scaleFilter = `scale=-2:${OUT_H},pad=${OUT_W}:${OUT_H}:(ow-iw)/2:0:black`;

    ffmpeg()
      .input(path.join(FRAMES_DIR, 'frame_%05d.png'))
      .inputOptions([`-framerate ${FPS}`])
      .videoCodec('libx264')
      .outputOptions([
        '-preset fast',
        '-crf 18',
        '-pix_fmt yuv420p',
        `-vf ${scaleFilter}`,
      ])
      .save(VIDEO_SILENT)
      .on('end', resolve)
      .on('error', reject);
  });
}

function mergeAudio() {
  return new Promise((resolve, reject) => {
    if (!fs.existsSync(BGM_PATH)) {
      console.log('[AUDIO]  BGMファイルが見つかりません。映像のみで出力します。');
      fs.copyFileSync(VIDEO_SILENT, OUTPUT_PATH);
      return resolve();
    }
    console.log('[AUDIO]  BGMを合成中...');
    ffmpeg()
      .input(VIDEO_SILENT)
      .input(BGM_PATH)
      .videoCodec('copy')
      .audioCodec('aac')
      .outputOptions(['-shortest'])
      .save(OUTPUT_PATH)
      .on('end', resolve)
      .on('error', reject);
  });
}

function cleanup() {
  if (fs.existsSync(FRAMES_DIR))   fs.rmSync(FRAMES_DIR, { recursive: true });
  if (fs.existsSync(VIDEO_SILENT)) fs.unlinkSync(VIDEO_SILENT);
  if (fs.existsSync(BGM_PATH))     fs.unlinkSync(BGM_PATH);
}

async function main() {
  console.log('='.repeat(52));
  console.log('  ビズウェル TikTok 録画スクリプト (Puppeteer)');
  console.log('='.repeat(52));
  console.log(`  HTML   : ${path.basename(HTML_PATH)}`);
  console.log(`  出力   : ${OUT_W}x${OUT_H} / ${FPS}fps / ${DURATION}秒`);
  console.log('');

  const browser = await puppeteer.launch({
    headless: true,
    args: [
      `--window-size=${NATIVE_W},${NATIVE_H}`,
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-gpu',
    ],
  });

  const page = await browser.newPage();
  // ネイティブサイズでレンダリング（.video がちょうど画面を埋める）
  await page.setViewport({ width: NATIVE_W, height: NATIVE_H, deviceScaleFactor: 1 });
  await page.goto(`file://${HTML_PATH}`, { waitUntil: 'networkidle0' });

  // リプレイボタンは不要なので非表示
  await page.addStyleTag({ content: '.replay { display: none !important; }' });

  await captureFrames(page);
  await browser.close();

  await framesToVideo();
  await mergeAudio();
  cleanup();

  console.log('');
  console.log(`完了 → ${OUTPUT_PATH}`);
}

main().catch(err => {
  console.error('\n[ERROR]', err.message);
  process.exit(1);
});
