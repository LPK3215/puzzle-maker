"""拼图切分引擎 - 图片加载、配置管理、切分调度"""

import json
from pathlib import Path
from typing import List, Tuple

from PIL import Image

from .layouts import LAYOUT_REGISTRY


class Config:
    """配置管理器"""

    def __init__(self, config_path: str = None):
        if config_path is None:
            # 默认配置路径：项目根目录/config/layouts.json
            config_path = Path(__file__).parent.parent.parent / "config" / "layouts.json"
        with open(config_path, "r", encoding="utf-8") as f:
            self._data = json.load(f)

    @property
    def defaults(self) -> dict:
        return self._data.get("defaults", {})

    @property
    def layouts(self) -> list:
        return self._data.get("layouts", [])

    def get_layout(self, layout_id: str) -> dict:
        for layout in self.layouts:
            if layout["id"] == layout_id:
                return layout
        return None


class Splitter:
    """拼图切分引擎"""

    def __init__(self, config: Config = None):
        self.config = config or Config()

    def load_image(self, path: str) -> Image.Image:
        """加载图片"""
        return Image.open(path).convert("RGB")

    def prepare_image(self, img: Image.Image, max_size: int = 2000) -> Image.Image:
        """准备图片 - 限制尺寸"""
        w, h = img.size
        if w > max_size or h > max_size:
            if w > h:
                new_w = max_size
                new_h = int(h * max_size / w)
            else:
                new_h = max_size
                new_w = int(w * max_size / h)
            return img.resize((new_w, new_h), Image.LANCZOS)
        return img

    def split(self, img: Image.Image, layout: dict) -> List[Tuple[Image.Image, int, int]]:
        """执行切分"""
        layout_type = layout.get("type", "grid")
        defaults = layout.get("defaults", {})

        split_func = LAYOUT_REGISTRY.get(layout_type)
        if not split_func:
            raise ValueError(f"未知布局类型: {layout_type}")

        return split_func(img, **defaults)
