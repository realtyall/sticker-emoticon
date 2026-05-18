import io
import mimetypes
import os
import uuid
import zipfile

from dotenv import load_dotenv
from flask import Flask, abort, jsonify, render_template, request, send_file
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20MB

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Vercel은 /tmp에만 쓰기 권한 있음
if os.environ.get('FLASK_ENV') == 'production':
    UPLOAD_DIR = '/tmp/uploads'
    OUTPUT_DIR = '/tmp/output'
else:
    UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
    OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp'}

def generate_sticker_prompt(sticker_count):
    emotions = [
        "최고!", "고마워요", "미안해요", "사랑해요", "헉", "깜짝이야",
        "빵터짐", "축하해요", "멋져!", "힘내세요", "안녕", "OK", "힝", "ㅋㅋㅋ",
        "화났어", "신나요"
    ]
    selected_emotions = emotions[:sticker_count]
    emotion_str = ', '.join(f'"{e}"' for e in selected_emotions)

    return (
        f"사진 속 인물을 참고해 밝고 유쾌한 분위기의 메신저용 리액션 스티커 {sticker_count}종 제작.\n"
        "깨끗한 흰색 배경, 자연스럽고 귀여운 실사 스타일.\n"
        "인물의 분위기와 헤어스타일을 참고하되 과도한 복제 느낌 없이 친근하고 캐릭터스럽게 표현.\n"
        "각 스티커마다 감정이 잘 전달되도록 표정과 손동작을 크게 강조.\n"
        "밝고 선명한 조명, 깔끔한 피부 표현, 유쾌한 밈 느낌의 리액션 스타일.\n"
        "텍스트는 굵고 가독성 좋은 한국어 스타일로 삽입.\n"
        f"사용 문구: {emotion_str}\n"
        f"{sticker_count}개의 스티커를 한 장에 배치.\n"
        "3~4열 그리드 구성, 각 스티커 사이 간격 넓게 유지.\n"
        "충분한 흰 여백과 동일한 마진 적용.\n"
        "전체적으로 깔끔하고 미니멀한 메신저 스티커 미리보기 스타일."
    )


def _session_paths(session_id):
    base = os.path.join(OUTPUT_DIR, session_id)
    return {
        'base': base,
        'grid': os.path.join(base, 'grid.png'),
        'stickers': os.path.join(base, 'stickers'),
    }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/validate-key', methods=['POST'])
def validate_key():
    api_key = request.json.get('api_key', '').strip()
    if not api_key:
        return jsonify({'valid': False, 'error': 'API 키가 입력되지 않았습니다.'}), 400

    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        # 간단한 텍스트 생성으로 API 키 유효성 확인
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents='test'
        )
        return jsonify({'valid': True, 'message': 'API 키가 유효합니다.'})
    except Exception as e:
        error_msg = str(e)
        if 'API key' in error_msg or 'authentication' in error_msg.lower():
            return jsonify({'valid': False, 'error': '유효하지 않은 API 키입니다.'}), 400
        return jsonify({'valid': False, 'error': f'검증 중 오류: {error_msg}'}), 500


@app.route('/api/generate', methods=['POST'])
def generate():
    if 'image' not in request.files:
        return jsonify({'error': '이미지 파일이 없습니다.'}), 400

    file = request.files['image']
    if not file.filename:
        return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400

    ext = os.path.splitext(secure_filename(file.filename))[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({'error': '지원하지 않는 파일 형식입니다. (PNG, JPG, WEBP)'}), 400

    sticker_count = request.form.get('sticker_count', default='14', type=int)
    if sticker_count < 12 or sticker_count > 16:
        sticker_count = 14

    api_key = request.form.get('api_key', '').strip()
    if not api_key:
        api_key = os.environ.get('GEMINI_API_KEY')

    if not api_key:
        return jsonify({'error': 'API 키가 필요합니다.'}), 400

    session_id = uuid.uuid4().hex
    paths = _session_paths(session_id)
    upload_dir = os.path.join(UPLOAD_DIR, session_id)

    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(paths['base'], exist_ok=True)
    os.makedirs(paths['stickers'], exist_ok=True)

    ref_path = os.path.join(upload_dir, f'ref{ext}')
    file.save(ref_path)

    mime_type = mimetypes.guess_type(ref_path)[0] or 'image/jpeg'

    # Gemini 이미지 생성
    try:

        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key, http_options={"api_version": "v1"})

        with open(ref_path, 'rb') as f:
            image_bytes = f.read()

        sticker_prompt = generate_sticker_prompt(sticker_count)
        response = client.models.generate_content(
            model='gemini-2.0-flash-preview-image-generation',
            contents=[
                types.Content(parts=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    types.Part.from_text(text=sticker_prompt),
                ])
            ],
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE', 'TEXT']
            ),
        )

        grid_image_data = None
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                grid_image_data = part.inline_data.data
                break

        if grid_image_data is None:
            return jsonify({'error': 'Gemini API가 이미지를 생성하지 못했습니다. 다시 시도해 주세요.'}), 500

        with open(paths['grid'], 'wb') as f:
            f.write(grid_image_data)

    except Exception as e:
        return jsonify({'error': f'이미지 생성 중 오류: {e}'}), 500

    # 개별 스티커 분할
    try:
        from split import split_image
        output_files = split_image(paths['grid'], paths['stickers'])
    except Exception as e:
        return jsonify({'error': f'이미지 분할 중 오류: {e}'}), 500

    stickers = [
        {
            'name': os.path.basename(f),
            'preview_url': f'/api/preview/sticker/{session_id}/{os.path.basename(f)}',
            'download_url': f'/api/download/sticker/{session_id}/{os.path.basename(f)}',
        }
        for f in output_files
    ]

    return jsonify({
        'session_id': session_id,
        'grid_preview_url': f'/api/preview/grid/{session_id}',
        'grid_download_url': f'/api/download/grid/{session_id}',
        'stickers': stickers,
    })


@app.route('/api/preview/grid/<session_id>')
def preview_grid(session_id):
    grid_path = _session_paths(session_id)['grid']
    if not os.path.exists(grid_path):
        abort(404)
    return send_file(grid_path, mimetype='image/png')


@app.route('/api/preview/sticker/<session_id>/<filename>')
def preview_sticker(session_id, filename):
    sticker_path = os.path.join(_session_paths(session_id)['stickers'], secure_filename(filename))
    if not os.path.exists(sticker_path):
        abort(404)
    return send_file(sticker_path, mimetype='image/png')


@app.route('/api/download/grid/<session_id>')
def download_grid(session_id):
    grid_path = _session_paths(session_id)['grid']
    if not os.path.exists(grid_path):
        abort(404)
    return send_file(grid_path, as_attachment=True, download_name='sticker_grid.png')


@app.route('/api/download/sticker/<session_id>/<filename>')
def download_sticker(session_id, filename):
    sticker_path = os.path.join(_session_paths(session_id)['stickers'], secure_filename(filename))
    if not os.path.exists(sticker_path):
        abort(404)
    return send_file(sticker_path, as_attachment=True, download_name=filename)


@app.route('/api/download/all/<session_id>')
def download_all(session_id):
    stickers_dir = _session_paths(session_id)['stickers']
    if not os.path.exists(stickers_dir):
        abort(404)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fname in sorted(os.listdir(stickers_dir)):
            if fname.endswith('.png'):
                zf.write(os.path.join(stickers_dir, fname), fname)
    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name='stickers.zip',
    )


if __name__ == '__main__':
    import os
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=5000)
