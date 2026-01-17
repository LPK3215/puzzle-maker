"""图像预处理模块"""

from PIL import Image


def center_crop(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """中心裁剪"""
    w, h = img.size
    crop_ratio = target_w / target_h
    img_ratio = w / h

    if img_ratio > crop_ratio:
        new_w = int(h * crop_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / crop_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))

    return img
