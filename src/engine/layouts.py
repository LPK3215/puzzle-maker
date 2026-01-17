"""拼图切分布局实现"""

from PIL import Image, ImageDraw
from typing import List, Tuple
import random


def create_jigsaw_mask(w: int, h: int, edges: dict) -> Image.Image:
    """创建拼图形状遮罩

    Args:
        w, h: 拼图块尺寸
        edges: {'top': 0/1/-1, 'right': 0/1/-1, 'bottom': 0/1/-1, 'left': 0/1/-1}
               0=平边, 1=凸起, -1=凹槽
    """
    import math

    tab_size = min(w, h) // 4
    mask = Image.new('L', (w + 2*tab_size, h + 2*tab_size), 0)
    draw = ImageDraw.Draw(mask)

    # 构建拼图轮廓点
    points = []

    # 左上角
    points.append((tab_size, tab_size))

    # 上边
    if edges.get('top') == 1:  # 凸起
        cx, cy = w // 2 + tab_size, tab_size
        for i in range(180, 361, 10):
            angle = math.radians(i)
            x = cx + tab_size * math.cos(angle)
            y = cy + tab_size * math.sin(angle)
            points.append((x, y))
    elif edges.get('top') == -1:  # 凹槽
        cx, cy = w // 2 + tab_size, tab_size
        for i in range(0, 181, 10):
            angle = math.radians(i)
            x = cx + tab_size * math.cos(angle)
            y = cy + tab_size * math.sin(angle)
            points.append((x, y))
    else:  # 平边
        points.append((w + tab_size, tab_size))

    # 右上角
    if edges.get('top') == 0:
        points.append((w + tab_size, tab_size))

    # 右边
    if edges.get('right') == 1:
        cx, cy = w + tab_size, h // 2 + tab_size
        for i in range(270, 451, 10):
            angle = math.radians(i)
            x = cx + tab_size * math.cos(angle)
            y = cy + tab_size * math.sin(angle)
            points.append((x, y))
    elif edges.get('right') == -1:
        cx, cy = w + tab_size, h // 2 + tab_size
        for i in range(90, 271, 10):
            angle = math.radians(i)
            x = cx + tab_size * math.cos(angle)
            y = cy + tab_size * math.sin(angle)
            points.append((x, y))
    else:
        points.append((w + tab_size, h + tab_size))

    # 右下角
    if edges.get('right') == 0:
        points.append((w + tab_size, h + tab_size))

    # 下边
    if edges.get('bottom') == 1:
        cx, cy = w // 2 + tab_size, h + tab_size
        for i in range(0, 181, 10):
            angle = math.radians(i)
            x = cx + tab_size * math.cos(angle)
            y = cy + tab_size * math.sin(angle)
            points.append((x, y))
    elif edges.get('bottom') == -1:
        cx, cy = w // 2 + tab_size, h + tab_size
        for i in range(180, 361, 10):
            angle = math.radians(i)
            x = cx + tab_size * math.cos(angle)
            y = cy + tab_size * math.sin(angle)
            points.append((x, y))
    else:
        points.append((tab_size, h + tab_size))

    # 左下角
    if edges.get('bottom') == 0:
        points.append((tab_size, h + tab_size))

    # 左边
    if edges.get('left') == 1:
        cx, cy = tab_size, h // 2 + tab_size
        for i in range(90, 271, 10):
            angle = math.radians(i)
            x = cx + tab_size * math.cos(angle)
            y = cy + tab_size * math.sin(angle)
            points.append((x, y))
    elif edges.get('left') == -1:
        cx, cy = tab_size, h // 2 + tab_size
        for i in range(270, 451, 10):
            angle = math.radians(i)
            x = cx + tab_size * math.cos(angle)
            y = cy + tab_size * math.sin(angle)
            points.append((x, y))
    else:
        points.append((tab_size, tab_size))

    # 绘制多边形
    draw.polygon(points, fill=255)

    return mask


def split_grid(img: Image.Image, rows: int = 3, cols: int = 3, jigsaw_shape: bool = False) -> List[Tuple[Image.Image, int, int]]:
    """规则网格切分

    Args:
        img: 输入图像
        rows: 行数
        cols: 列数
        jigsaw_shape: 是否使用拼图形状

    Returns:
        List of (piece_image, row_index, col_index)
    """
    w, h = img.size
    piece_w = w // cols
    piece_h = h // rows
    tab_size = min(piece_w, piece_h) // 4

    # 生成边缘模式（确保相邻块互补）
    h_edges = [[random.choice([1, -1]) for _ in range(cols - 1)] for _ in range(rows)]
    v_edges = [[random.choice([1, -1]) for _ in range(cols)] for _ in range(rows - 1)]

    pieces = []
    for row in range(rows):
        for col in range(cols):
            x = col * piece_w
            y = row * piece_h

            if jigsaw_shape:
                # 裁剪扩展区域以容纳凸起
                x1 = max(0, x - tab_size)
                y1 = max(0, y - tab_size)
                x2 = min(w, x + piece_w + tab_size)
                y2 = min(h, y + piece_h + tab_size)
                piece = img.crop((x1, y1, x2, y2))

                # 创建扩展遮罩
                edges = {
                    'top': -v_edges[row - 1][col] if row > 0 else 0,
                    'bottom': v_edges[row][col] if row < rows - 1 else 0,
                    'left': -h_edges[row][col - 1] if col > 0 else 0,
                    'right': h_edges[row][col] if col < cols - 1 else 0,
                }
                mask = create_jigsaw_mask(piece_w, piece_h, edges)

                # 调整遮罩以匹配实际裁剪区域
                if x1 > x - tab_size or y1 > y - tab_size or x2 < x + piece_w + tab_size or y2 < y + piece_h + tab_size:
                    # 边界情况：裁剪遮罩
                    crop_x1 = tab_size - (x - x1)
                    crop_y1 = tab_size - (y - y1)
                    crop_x2 = crop_x1 + (x2 - x1)
                    crop_y2 = crop_y1 + (y2 - y1)
                    mask = mask.crop((crop_x1, crop_y1, crop_x2, crop_y2))

                piece.putalpha(mask)
            else:
                piece = img.crop((x, y, x + piece_w, y + piece_h))

            pieces.append((piece, row, col))

    return pieces


def split_irregular(img: Image.Image, pieces: int = 12) -> List[Tuple[Image.Image, int, int]]:
    """不规则形状切分（使用拼图形状）"""
    import math
    cols = int(math.sqrt(pieces))
    rows = (pieces + cols - 1) // cols
    return split_grid(img, rows, cols, jigsaw_shape=True)


def split_jigsaw(img: Image.Image, pieces: int = 20) -> List[Tuple[Image.Image, int, int]]:
    """传统拼图形状切分（使用拼图形状）"""
    import math
    cols = int(math.sqrt(pieces))
    rows = (pieces + cols - 1) // cols
    return split_grid(img, rows, cols, jigsaw_shape=True)


# 布局注册表
LAYOUT_REGISTRY = {
    "grid": split_grid,
    "irregular": split_irregular,
    "jigsaw": split_jigsaw,
}
