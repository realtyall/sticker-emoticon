# 이모티콘 스티커 생성기 🎨

Google Gemini AI를 사용하여 사진에서 카카오톡 메신저용 개인화 스티커를 자동으로 생성하는 웹 애플리케이션입니다.

## 기능

- 📸 **사진 업로드**: PNG, JPG, WEBP 형식 지원 (최대 20MB)
- 🤖 **AI 스티커 생성**: Gemini 2.0 Flash로 12-16개 커스텀 스티커 생성
- 🎯 **자동 분할**: 그리드 이미지를 개별 스티커로 자동 추출
- 💾 **다운로드**: 개별 스티커 또는 ZIP으로 전체 다운로드
- 🔐 **API 키 관리**: 브라우저 저장 또는 1회성 입력

## 설치

### 요구사항
- Python 3.8+
- Google Gemini API 키 ([Google AI Studio](https://aistudio.google.com/apikey)에서 발급)

### 셋업

```bash
# 저장소 클론
git clone https://github.com/realtyall/sticker-emoticon.git
cd sticker-emoticon

# 가상 환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 실행
python app.py
```

브라우저에서 `http://localhost:5000` 접속

## 사용 방법

1. **API 키 설정**: 상단 우측 "⚙️ API 설정" 버튼 클릭
2. **사진 업로드**: 사진을 드래그하거나 클릭하여 업로드
3. **스티커 개수 선택**: 슬라이더로 12-16개 중 선택
4. **생성 및 다운로드**: "스티커 생성하기" 버튼 클릭

## 기술 스택

- **백엔드**: Flask (Python)
- **AI**: Google Gemini 2.0 Flash Image Generation
- **이미지 처리**: PIL, NumPy
- **프론트엔드**: Vanilla JavaScript, HTML, CSS

## 프로젝트 구조

```
├── app.py              # Flask 메인 애플리케이션
├── split.py            # 이미지 분할 알고리즘
├── requirements.txt    # Python 의존성
├── .env.example        # 환경 변수 예시
├── templates/
│   └── index.html      # 메인 페이지
├── static/
│   ├── css/style.css   # 스타일시트
│   └── js/app.js       # 클라이언트 로직
├── uploads/            # 임시 업로드 디렉토리
└── output/             # 생성된 스티커 저장소
```

## 주요 기능

### API 키 검증
- 사용자가 입력한 Gemini API 키를 Gemini API로 검증
- 유효한 키만 저장 가능
- 1회성 저장 또는 브라우저 저장 선택 가능

### 동적 프롬프트 생성
- 선택한 스티커 개수에 맞춰 프롬프트 자동 조정
- 감정 표현 다양화로 자연스러운 스티커 생성

### 스마트 이미지 분할
- 배경 감지를 통한 자동 분할
- 개별 스티커 추출 및 정렬

## 라이선스

MIT License

## 지원

문제가 발생하면 GitHub Issues에 등록해주세요.
