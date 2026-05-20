# 이모티콘 스티커 생성기 (Sticker Emoticon Generator) 🎨

Google Gemini AI를 사용하여 업로드한 사진에서 메신저용(카카오톡, 라인 등) 개인화 스티커를 자동으로 생성하고 개별 이미지로 분할해주는 웹 애플리케이션입니다.

## 주요 기능

- 📸 **사진 기반 생성**: 업로드한 인물 사진의 분위기, 헤어스타일, 특징을 반영한 캐릭터 스타일 스티커 생성
- 🤖 **최신 AI 모델 지원**: Google Gemini 2.0/3.0/3.1 시리즈 이미지 생성 모델 활용
  - `gemini-2.5-flash-image`
  - `gemini-3-pro-image-preview`
  - `gemini-3.1-flash-image-preview`
- 🎯 **스마트 이미지 분할**: 생성된 그리드 이미지를 개별 스티커로 자동 감지 및 추출 (`split.py`)
- 💾 **다양한 다운로드 옵션**: 개별 스티커 저장, 그리드 원본 저장, 또는 전체 스티커를 ZIP 파일로 압축 다운로드
- 🔐 **보안 및 편의성**: API 키 유효성 검증 기능 및 브라우저 로컬 저장 지원
- ☁️ **클라우드 배포 최적화**: Vercel 환경 지원 및 `/tmp` 디렉토리 활용 설계

## 설치 및 실행 방법

### 요구사항
- Python 3.8 이상
- [Google AI Studio](https://aistudio.google.com/apikey)에서 발급받은 Gemini API 키

### 로컬 환경 설정

```bash
# 1. 저장소 클론
git clone https://github.com/realtyall/sticker-emoticon.git
cd sticker-emoticon

# 2. 가상 환경 생성 및 활성화 (uv 권장)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 GEMINI_API_KEY를 입력하거나 웹 UI에서 직접 설정 가능합니다.

# 5. 애플리케이션 실행
python app.py
```

실행 후 브라우저에서 `http://localhost:5000`에 접속하세요.

## 사용 방법

1. **API 키 설정**: 우측 상단의 "⚙️ API 설정" 버튼을 눌러 발급받은 API 키를 입력하고 검증합니다. 사용할 Gemini 모델도 여기서 선택할 수 있습니다.
2. **사진 업로드**: 메인이 되는 사진을 드래그 앤 드롭하거나 클릭하여 업로드합니다.
3. **옵션 선택**: 생성할 스티커 개수(12~16개)를 슬라이더로 조절합니다.
4. **생성**: "스티커 생성하기" 버튼을 클릭합니다. (AI 생성 및 분할 작업에 약 10~20초 소요)
5. **저장**: 생성된 개별 스티커를 확인하고 필요한 이미지를 다운로드하거나 "ZIP으로 모두 받기"를 클릭합니다.

## 기술 스택

- **Backend**: Python, Flask
- **AI**: Google Generative AI (Gemini API)
- **Image Processing**: Pillow (PIL), NumPy
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Deployment**: Vercel (Optional)

## 프로젝트 구조

```
├── app.py              # Flask 서버 및 API 엔드포인트
├── split.py            # 그리드 이미지 분석 및 개별 스티커 분할 로직
├── check_models.py     # 사용 가능한 Gemini 모델 목록 확인 스크립트
├── test_image_gen.py   # Gemini 이미지 생성 기능 단독 테스트 스크립트
├── requirements.txt    # 의존성 패키지 목록
├── vercel.json         # Vercel 배포 설정
├── static/
│   ├── css/style.css   # 웹 UI 스타일
│   └── js/app.js       # 프론트엔드 비즈니스 로직 및 API 연동
├── templates/
│   └── index.html      # 메인 HTML 템플릿
├── uploads/            # (Local) 사용자가 업로드한 원본 이미지 저장소
└── output/             # (Local) AI가 생성한 결과물 및 분할된 이미지 저장소
```

## 핵심 알고리즘: 스마트 분할

`split.py`는 생성된 이미지의 픽셀 데이터를 분석하여 배경(흰색 또는 투명)을 감지하고, 유효한 이미지 영역을 계산하여 스티커를 자동으로 추출합니다. 3~4열 그리드 형태의 레이아웃을 정확하게 인식하도록 최적화되어 있습니다.

## 배포 (Vercel)

본 프로젝트는 Vercel을 통한 배포를 지원합니다.
- `vercel.json` 설정이 포함되어 있습니다.
- 생산 환경에서는 서버리스 함수의 특성에 따라 `/tmp` 디렉토리를 임시 저장소로 사용하도록 설계되었습니다.

## 라이선스

MIT License

## 문제 해결

- **API 키 오류**: [Google AI Studio](https://aistudio.google.com/app/apikey)에서 API 키가 활성 상태인지, `Generative Language API` 권한이 있는지 확인하세요.
- **이미지 생성 실패**: 입력 사진이 너무 어둡거나 복잡할 경우 AI가 인식을 못 할 수 있습니다. 밝고 선명한 인물 사진을 권장합니다.
- **분할 결과가 부정확함**: AI가 생성한 이미지의 간격이 너무 좁을 경우 `split.py`의 `min_gap` 파라미터 조정이 필요할 수 있습니다.
