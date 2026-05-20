from google import genai
from google.genai import types
import os

api_key = "AIzaSyC8gSxwX7-6lfU8WwBU5a9ko51D8PHhYMQ"
models = ['gemini-2.5-flash-image', 'gemini-3-pro-image-preview', 'gemini-3.1-flash-image-preview']

prompt = "A cute cat sticker with white background. Simple and clean style."

client = genai.Client(api_key=api_key, http_options={"api_version": "v1beta"})

for model_name in models:
    print(f"\n[{model_name}] 테스트 중...")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[types.Content(parts=[types.Part.from_text(text=prompt)])],
        )
        image_data = None
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                image_data = part.inline_data.data
                break

        if image_data:
            out_path = f"test_output_{model_name.replace('/', '_')}.png"
            with open(out_path, 'wb') as f:
                f.write(image_data)
            print(f"  성공! 저장: {out_path} ({len(image_data):,} bytes)")
        else:
            text_parts = [p.text for p in response.candidates[0].content.parts if hasattr(p, 'text') and p.text]
            print(f"  이미지 없음. 텍스트 응답: {' '.join(text_parts)[:200]}")
    except Exception as e:
        print(f"  오류: {e}")
