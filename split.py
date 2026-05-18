import os
import sys
import numpy as np
from PIL import Image


def find_splits(size, is_bg_1d, min_gap=20, min_item=200):
    gaps = []
    in_gap = False
    start = 0
    for i in range(size):
        if is_bg_1d[i]:
            if not in_gap:
                start = i
                in_gap = True
        else:
            if in_gap:
                gaps.append((start, i - 1))
                in_gap = False
    if in_gap:
        gaps.append((start, size - 1))

    int_gaps = [g for g in gaps if g[0] > 0 and g[1] < size - 1]

    # 특정 크기(min_gap) 이상의 갭만 1차 구분선으로 인정
    separators = [g for g in int_gaps if g[1] - g[0] >= min_gap]

    # 구분선 사이의 간격(이모티콘 크기)이 너무 작으면(텍스트와 이미지 사이의 간격 등) 무시
    valid_separators = []
    last_end = gaps[0][1] + 1 if gaps and gaps[0][0] == 0 else 0
    for sep in separators:
        if sep[0] - last_end >= min_item:
            valid_separators.append(sep)
            last_end = sep[1] + 1

    bounds = []
    curr = 0
    for sep in valid_separators:
        bounds.append((curr, sep[0]))
        curr = sep[1] + 1
    bounds.append((curr, size - 1))

    if gaps and gaps[0][0] == 0:
        bounds[0] = (gaps[0][1] + 1, bounds[0][1])
    if gaps and gaps[-1][1] == size - 1:
        bounds[-1] = (bounds[-1][0], gaps[-1][0] - 1)

    # 너무 얇은 조각 제거
    return [b for b in bounds if b[1] - b[0] > 10]


def split_image(image_path: str, output_dir: str) -> list:
    """그리드 이미지를 개별 이모티콘으로 분할한다.

    Args:
        image_path: 입력 그리드 이미지 경로
        output_dir: 분할된 이모티콘을 저장할 폴더 경로

    Returns:
        생성된 이모티콘 파일 경로 리스트
    """
    img = Image.open(image_path)
    arr = np.array(img.convert("RGBA"))

    # 배경 조건: 알파값이 0이거나 RGB가 240 이상인 하얀색 여백
    is_bg = (arr[:, :, 3] == 0) | np.all(arr[:, :, :3] >= 240, axis=2)
    col_bg = is_bg.sum(axis=0) >= arr.shape[0] * 0.98

    col_bounds = find_splits(arr.shape[1], col_bg, min_gap=20, min_item=100)

    os.makedirs(output_dir, exist_ok=True)

    output_files = []
    count = 1
    for c_idx, (left, right) in enumerate(col_bounds):
        col_is_bg = is_bg[:, left:right + 1]
        row_bg = col_is_bg.sum(axis=1) >= col_is_bg.shape[1] * 0.98
        row_bounds = find_splits(col_is_bg.shape[0], row_bg, min_gap=20, min_item=200)

        for r_idx, (top, bottom) in enumerate(row_bounds):
            cropped_img = img.crop((left, top, right, bottom))
            out_path = os.path.join(output_dir, f"emoticon_{count:02d}.png")
            cropped_img.save(out_path)
            output_files.append(out_path)
            count += 1

    return output_files


if __name__ == "__main__":
    image_files = [
        f for f in os.listdir('.')
        if f.lower().endswith(('.png', '.jpg', '.jpeg')) and os.path.isfile(f)
    ]
    if not image_files:
        print("현재 폴더에 처리할 이미지 파일(.png, .jpg, .jpeg)이 없습니다.")
        sys.exit()

    image_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    image_path = image_files[0]
    print(f"[{image_path}] 이미지를 사용하여 분할을 시작합니다.")

    files = split_image(image_path, "sliced_emoticons")
    print(f"분할 완료! 'sliced_emoticons' 폴더에 총 {len(files)}개의 이모티콘이 저장되었습니다.")
