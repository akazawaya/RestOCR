import cv2
from pathlib import Path
from yomitoku.ocr import OCR

def init_engine():
    # いずれ外部から初期化できるようにしたい
    return OCR(visualize=False, device="auto")

# 1ページずつ処理する方針
def test_ocr(img_path):
    words = []
    ocr = init_engine()
    arr_bgr = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
    if arr_bgr is None:
        raise ValueError(f"failed to read")
    img_rgb = cv2.cvtColor(arr_bgr, cv2.COLOR_BGR2RGB) # yomitokuはrgb入力想定    

    results, _ = ocr(img_rgb)
    for w in results.words:
        content = {
            "points": w.points,
            "content": w.content,
            "direction": w.direction,
            "det_score": w.det_score,
            "rec_score": w.rec_score,
        }
        words.append(content)
    return words



#test_ocr(r"/root/Django/RestOCR/input/f12d2251-ec34-4495-9da7-2c5a901c02df/")