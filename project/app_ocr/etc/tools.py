from pathlib import Path

import cv2
from PIL import Image, ImageOps, ImageSequence
import numpy as np
import torch
import pypdfium2

SUPPORT_INPUT_FORMAT = ["jpg", "jpeg", "png", "bmp", "tiff", "tif", "pdf"]
SUPPORT_OUTPUT_FORMAT = ["json", "csv", "html", "markdown", "md", "pdf"]
MIN_IMAGE_SIZE = 32
WARNING_IMAGE_SIZE = 720

# (.venv/lib64/python3.13/site-packages/yomitoku/constants.py)

# 単に名称に対してではなく、解析でファイルタイプを区分する関数　画像はpillow読み込みか
# pdfに対してそのページ数を判別する関数
# pdfをimgのlistに変換する関数
# filesizeはDjangoのバリデーターで十分であると判断
# /root/Django/RestOCR/.venv/lib64/python3.13/site-packages/yomitoku/data/functions.py を参考にする


def validate_and_analyze(file):
    ext = Path(file.name).suffix.lstrip('.').lower()
    if ext not in SUPPORT_INPUT_FORMAT:
        raise ValueError(
            f"Unsupported file format. Supported formats are {SUPPORT_INPUT_FORMAT}"
        )
    if ext == 'pdf':
       ext ='1'
       image_list, total_pages = analyze_pdf(file)
    elif ext in ('tif', 'tiff'):
        ext ='0'
        image_list, total_pages = analyze_tiff(file)
    else:
        ext ='0'
        image_list, total_pages = analyze_img(file)
    return image_list, ext, total_pages


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

def analyze_tiff(tiff):
    images = []
    with Image.open(tiff) as image:
        for i in range(getattr(image, "n_frames", 1)):
            image.seek(i)
            images.append(ImageOps.exif_transpose(image).convert("RGB").copy())
    return images, int(len(images))

def analyze_img(image):
    images = Image.open(image)
    return images, int(1)