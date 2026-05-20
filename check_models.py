from google import genai
import os

api_key = os.environ.get('GEMINI_API_KEY')
if not api_key:
    print("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
    print("웹 인터페이스에서 API 키를 확인하고 다시 시도하세요.")
else:
    try:
        client = genai.Client(api_key=api_key)
        models = list(client.models.list())
        print("사용 가능한 모델들:")
        for model in models:
            print(f"\n모델: {model.name}")
            if hasattr(model, 'supported_generation_methods'):
                print(f"  지원 메서드: {model.supported_generation_methods}")
    except Exception as e:
        print(f"에러: {e}")
