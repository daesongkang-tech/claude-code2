import base64
import sys
from pathlib import Path
from google import genai
from google.genai import types

api_key = "AIzaSyBc_Y-ja4EqkvBXTJB5rYUZ6aVUpn9AQHs"
client = genai.Client(api_key=api_key)

# 記事ファイルを読み込む
article_path = sys.argv[1]
article_text = Path(article_path).read_text(encoding='utf-8')[:500]

prompt = f"""以下の就労移行支援施設の記事に合ったサムネイル画像を生成してください。
ダークな背景にオレンジとブルーのグラデーション、IT・AI・プログラミングをイメージするデザイン。
日本語テキストは入れないでください。

記事概要: {article_text}"""

response = client.models.generate_images(
    model="imagen-3.0-generate-002",
    prompt=prompt,
    config=types.GenerateImagesConfig(
        number_of_images=1,
        aspect_ratio="16:9",
    )
)

for img in response.generated_images:
    img_data = img.image.image_bytes
    output_path = article_path.replace('.md', '_サムネイル.png')
    Path(output_path).write_bytes(img_data)
    print(f"画像保存: {output_path}")
    break
