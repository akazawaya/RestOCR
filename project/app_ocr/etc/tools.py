from pathlib import Path
from PIL import Image, ImageOps
import pypdfium2
import io

# (.venv/lib64/python3.13/site-packages/yomitoku/constants.py)
# models.pyの定義に合わせる　modelsとtoolsで拡張子定義が個別なのを後で修正したい
SUPPORT_INPUT_FORMAT = ["jpg", "png", "bmp", "tif", "pdf"]
# SUPPORT_OUTPUT_FORMAT = ["json", "csv", "html", "markdown", "md", "pdf"]
# MIN_IMAGE_SIZE = 32
# WARNING_IMAGE_SIZE = 720
# filesizeはDjangoのバリデーターで十分であると判断
# /root/Django/RestOCR/.venv/lib64/python3.13/site-packages/yomitoku/data/functions.py を参考にする

def validate_and_analyze(file):
    """
    名称に対してではなく、解析でファイルタイプを区分する関数 画像はpillow読み込みだが
    Djangoのバリデーターにpillowが使われているので冗長かもしれない
    """
    ext = Path(file.name).suffix.lstrip('.').lower()
    ext = exchange_ext(ext)
    if ext not in SUPPORT_INPUT_FORMAT:
        raise ValueError(
            f"Unsupported file format. Supported formats are {SUPPORT_INPUT_FORMAT}"
        )
    if ext == 'pdf':
       image_list, total_pages = analyze_pdf(file)
    elif ext in ('tif', 'tiff'):
        image_list, total_pages = analyze_tiff(file)
    else:
        image_list, total_pages = analyze_img(file)
    image_byte_list = pillow_to_bytes(image_list, format="png")
    return image_byte_list, ext, total_pages


def analyze_pdf(pdf):
    images = []
    pdf = pypdfium2.PdfDocument(pdf)
    for page in pdf:
        image = page.render(
            scale=1,rotation=0,
            crop=(0, 0, 0, 0),
            ).to_pil()
        images.append(image)
    return images, int(len(images))

def analyze_tiff(tif):
    images = []
    with Image.open(tif) as image:
        for i in range(getattr(image, "n_frames", 1)):
            image.seek(i)
            images.append(ImageOps.exif_transpose(image).convert("RGB").copy())
    return images, int(len(images))

def analyze_img(image):
    image = Image.open(image)
    return [image], int(1)

def exchange_ext(ext):
    """
    拡張子の表記ゆれを吸収する関数
        Returns:は3文字(深い理由はない)
    """
    ALIAS = {
        "jpeg": "jpg", "jpg": "jpg",
        "png":  "png",
        "bmp":  "bmp",
        "tif":  "tiff", "tiff": "tif",
        "pdf":  "pdf",
    }
    return ALIAS[ext]

def pillow_to_bytes(img_list, format="png"):
    """
    Django のImageFieldがbyteじゃないと受け入れてくれないので
    bytefileとして保存しなおす関数
    """
    img_bytes_list = []
    for img in img_list:
        img_bytes = io.BytesIO()
        img.save(img_bytes, format=format)
        img_bytes = img_bytes.getvalue() 
        img_bytes_list.append(img_bytes)
    return img_bytes_list


