from pathlib import Path
import pypdfium2

import cv2

# (.venv/lib64/python3.13/site-packages/yomitoku/constants.py)
# models.pyの定義に合わせる　modelsとtoolsで拡張子定義が個別なのを後で修正したい
SUPPORT_INPUT_FORMAT = ["jpg", "png", "bmp", "tif", "pdf"]
# SUPPORT_OUTPUT_FORMAT = ["json", "csv", "html", "markdown", "md", "pdf"]
# MIN_IMAGE_SIZE = 32
# WARNING_IMAGE_SIZE = 720
# filesizeはDjangoのバリデーターで十分であると判断
# /root/Django/RestOCR/.venv/lib64/python3.13/site-packages/yomitoku/data/functions.py を参考にする
# yomitokuにはRGBの入力が必要

def validate_and_analyze(file):
    ext = Path(file.name).suffix.lstrip('.').lower()
    ext = exchange_ext(ext)
    if ext not in SUPPORT_INPUT_FORMAT:
        raise ValueError(
            f"Unsupported file format. Supported formats are {SUPPORT_INPUT_FORMAT}")
    if ext == 'pdf':
       image_list, total_pages = analyze_pdf(file)
    else:
        image_list, total_pages = analyze_img(file)
    return image_list, ext, total_pages

def analyze_pdf(file, type=".png", dpi=300):
    scale = dpi / 72 
    images = []
    pdf = pypdfium2.PdfDocument(file)
    for page in pdf:
        array = page.render(scale=scale, rotation=0).to_numpy() 
        images.append(cv2.imencode(type, array)[1].tobytes())
    return images, len(images)

def analyze_img(file, type=".png"):
    ok, imgs = cv2.imreadmulti(str(file), flags=cv2.IMREAD_UNCHANGED) # 複数枚tiff想定
    if ok and imgs: 
        return [cv2.imencode(type, i)[1].tobytes() for i in imgs], len(imgs)
    img = cv2.imread(str(file), cv2.IMREAD_UNCHANGED)  # png/jpeg/単体tiff想定
    if img is None:
        raise ValueError("failed to read image")
    return [cv2.imencode(type, img)[1].tobytes()], 1

def exchange_ext(ext):
    """
    拡張子の表記ゆれを吸収する関数
        Returns:は3文字(深い理由はない)
    """
    ALIAS = {
        "jpeg": "jpg", "jpg": "jpg",
        "png":  "png",
        "bmp":  "bmp",
        "tiff":  "tif", "tif": "tif",
        "pdf":  "pdf",
    }
    return ALIAS[ext]