"""拼图生成器 - Gradio Web 应用核心"""

import tempfile
from pathlib import Path
from PIL import Image, ImageDraw

import gradio as gr

from .engine.splitter import Config, Splitter


class PuzzleMakerApp:
    """拼图生成器应用"""

    def __init__(self, config_path: Path = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "layouts.json"
        self.config = Config(str(config_path))
        self.splitter = Splitter(self.config)

    def get_layout_choices(self):
        """获取布局下拉选项"""
        return [(f"{layout['name']} - {layout['desc']}", layout['id'])
                for layout in self.config.layouts]

    def do_split(self, img, layout_id: str):
        """切分拼图并生成预览"""
        if img is None:
            gr.Warning("请先上传图片")
            return None, "请上传图片"

        try:
            img = self.splitter.prepare_image(img)
            layout = self.config.get_layout(layout_id)
            if not layout:
                return None, "无效的布局"

            pieces = self.splitter.split(img, layout)
            preview = self._create_puzzle_template(img, pieces, layout)

            return preview, f"成功生成 {len(pieces)} 块拼图模板"

        except Exception as e:
            return None, f"切分失败: {str(e)}"

    def _draw_dashed_line(self, draw, points, color=(0, 0, 0), width=2, dash_length=5, gap_length=10):
        """绘制虚线"""
        if len(points) < 2:
            return

        total_length = 0
        segments = []
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
            segments.append((points[i], points[i + 1], length))
            total_length += length

        current_pos = 0
        is_dash = True

        for start_pt, end_pt, seg_length in segments:
            x1, y1 = start_pt
            x2, y2 = end_pt

            if seg_length == 0:
                continue

            dx = (x2 - x1) / seg_length
            dy = (y2 - y1) / seg_length

            seg_pos = 0
            while seg_pos < seg_length:
                if is_dash:
                    dash_end = min(seg_pos + dash_length, seg_length)
                    sx = x1 + dx * seg_pos
                    sy = y1 + dy * seg_pos
                    ex = x1 + dx * dash_end
                    ey = y1 + dy * dash_end
                    draw.line([(sx, sy), (ex, ey)], fill=color, width=width)
                    seg_pos = dash_end
                    is_dash = False
                else:
                    seg_pos += gap_length
                    is_dash = True

    def _create_puzzle_template(self, original_img, pieces, layout):
        """创建拼图模板图（半圆不封口）"""
        if not pieces:
            return None

        # 获取布局参数
        defaults = layout.get("defaults", {})
        rows = defaults.get("rows", 3)
        cols = defaults.get("cols", 3)
        jigsaw_shape = defaults.get("jigsaw_shape", True)

        # 创建模板图
        w, h = original_img.size
        template = original_img.copy().convert('RGB')
        draw = ImageDraw.Draw(template)

        piece_w = w // cols
        piece_h = h // rows

        if not jigsaw_shape:
            # 直线切分：只绘制网格线
            for i in range(1, rows):
                y = i * piece_h
                self._draw_dashed_line(draw, [(0, y), (w, y)], color=(0, 0, 0), width=2)
            for j in range(1, cols):
                x = j * piece_w
                self._draw_dashed_line(draw, [(x, 0), (x, h)], color=(0, 0, 0), width=2)
            return template

        # 生成边缘模式（1=凸起，-1=凹陷）
        import random
        import math
        random.seed(42)
        h_edges = [[random.choice([1, -1]) for _ in range(cols - 1)] for _ in range(rows)]
        v_edges = [[random.choice([1, -1]) for _ in range(cols)] for _ in range(rows - 1)]

        tab_size = min(piece_w, piece_h) // 4

        # 绘制每条边（分段绘制，半圆不封口）
        for row in range(rows):
            for col in range(cols):
                x0 = col * piece_w
                y0 = row * piece_h
                x1 = x0 + piece_w
                y1 = y0 + piece_h

                # 上边
                if row == 0:
                    # 顶部边界，直线
                    self._draw_dashed_line(draw, [(x0, y0), (x1, y0)], color=(0, 0, 0), width=2)
                else:
                    # 有相邻块，绘制带半圆的边
                    edge_type = -v_edges[row - 1][col]
                    cx = x0 + piece_w // 2
                    
                    # 左侧直线
                    self._draw_dashed_line(draw, [(x0, y0), (cx - tab_size, y0)], color=(0, 0, 0), width=2)
                    
                    # 半圆弧线（不封口）
                    arc_points = []
                    if edge_type == 1:
                        # 向上凸起
                        for i in range(11):
                            angle = math.pi - i * math.pi / 10
                            px = cx + tab_size * math.cos(angle)
                            py = y0 - tab_size * math.sin(angle)
                            arc_points.append((int(px), int(py)))
                    else:
                        # 向上凹陷
                        for i in range(11):
                            angle = i * math.pi / 10
                            px = cx + tab_size * math.cos(angle)
                            py = y0 + tab_size * math.sin(angle)
                            arc_points.append((int(px), int(py)))
                    self._draw_dashed_line(draw, arc_points, color=(0, 0, 0), width=2)
                    
                    # 右侧直线
                    self._draw_dashed_line(draw, [(cx + tab_size, y0), (x1, y0)], color=(0, 0, 0), width=2)

                # 右边
                if col == cols - 1:
                    # 右侧边界，直线
                    self._draw_dashed_line(draw, [(x1, y0), (x1, y1)], color=(0, 0, 0), width=2)
                else:
                    edge_type = h_edges[row][col]
                    cy = y0 + piece_h // 2
                    
                    # 上侧直线
                    self._draw_dashed_line(draw, [(x1, y0), (x1, cy - tab_size)], color=(0, 0, 0), width=2)
                    
                    # 半圆弧线（不封口）
                    arc_points = []
                    if edge_type == 1:
                        # 向右凸起
                        for i in range(11):
                            angle = -math.pi / 2 - i * math.pi / 10
                            px = x1 - tab_size * math.cos(angle)
                            py = cy + tab_size * math.sin(angle)
                            arc_points.append((int(px), int(py)))
                    else:
                        # 向右凹陷
                        for i in range(11):
                            angle = math.pi / 2 - i * math.pi / 10
                            px = x1 + tab_size * math.cos(angle)
                            py = cy + tab_size * math.sin(angle)
                            arc_points.append((int(px), int(py)))
                    self._draw_dashed_line(draw, arc_points, color=(0, 0, 0), width=2)
                    
                    # 下侧直线
                    self._draw_dashed_line(draw, [(x1, cy + tab_size), (x1, y1)], color=(0, 0, 0), width=2)

                # 下边
                if row == rows - 1:
                    # 底部边界，直线
                    self._draw_dashed_line(draw, [(x1, y1), (x0, y1)], color=(0, 0, 0), width=2)
                else:
                    edge_type = v_edges[row][col]
                    cx = x0 + piece_w // 2
                    
                    # 右侧直线
                    self._draw_dashed_line(draw, [(x1, y1), (cx + tab_size, y1)], color=(0, 0, 0), width=2)
                    
                    # 半圆弧线（不封口）
                    arc_points = []
                    if edge_type == 1:
                        # 向下凸起
                        for i in range(11):
                            angle = i * math.pi / 10
                            px = cx + tab_size * math.cos(angle)
                            py = y1 + tab_size * math.sin(angle)
                            arc_points.append((int(px), int(py)))
                    else:
                        # 向下凹陷
                        for i in range(11):
                            angle = math.pi - i * math.pi / 10
                            px = cx + tab_size * math.cos(angle)
                            py = y1 - tab_size * math.sin(angle)
                            arc_points.append((int(px), int(py)))
                    self._draw_dashed_line(draw, arc_points, color=(0, 0, 0), width=2)
                    
                    # 左侧直线
                    self._draw_dashed_line(draw, [(cx - tab_size, y1), (x0, y1)], color=(0, 0, 0), width=2)

                # 左边
                if col == 0:
                    # 左侧边界，直线
                    self._draw_dashed_line(draw, [(x0, y1), (x0, y0)], color=(0, 0, 0), width=2)
                else:
                    edge_type = -h_edges[row][col - 1]
                    cy = y0 + piece_h // 2
                    
                    # 下侧直线
                    self._draw_dashed_line(draw, [(x0, y1), (x0, cy + tab_size)], color=(0, 0, 0), width=2)
                    
                    # 半圆弧线（不封口）
                    arc_points = []
                    if edge_type == 1:
                        # 向左凸起
                        for i in range(11):
                            angle = math.pi / 2 - i * math.pi / 10
                            px = x0 + tab_size * math.cos(angle)
                            py = cy + tab_size * math.sin(angle)
                            arc_points.append((int(px), int(py)))
                    else:
                        # 向左凹陷
                        for i in range(11):
                            angle = -math.pi / 2 + i * math.pi / 10
                            px = x0 + tab_size * math.cos(angle)
                            py = cy + tab_size * math.sin(angle)
                            arc_points.append((int(px), int(py)))
                    self._draw_dashed_line(draw, arc_points, color=(0, 0, 0), width=2)
                    
                    # 上侧直线
                    self._draw_dashed_line(draw, [(x0, cy - tab_size), (x0, y0)], color=(0, 0, 0), width=2)

        return template

    def do_export_png(self, img, layout_id: str):
        """导出拼图模板图（PNG格式）"""
        if img is None:
            gr.Warning("请先上传图片")
            return None

        try:
            img = self.splitter.prepare_image(img)
            layout = self.config.get_layout(layout_id)
            if not layout:
                gr.Warning("无效的布局")
                return None

            pieces = self.splitter.split(img, layout)
            template = self._create_puzzle_template(img, pieces, layout)

            # 保存为PNG
            template_path = Path(tempfile.gettempdir()) / f"puzzle_template_{layout_id}.png"
            template.save(template_path, "PNG")

            return str(template_path)

        except Exception as e:
            gr.Warning(f"导出失败: {str(e)}")
            return None

    def do_export_html(self, img, layout_id: str):
        """导出拼图模板（HTML格式，可在浏览器查看）"""
        if img is None:
            gr.Warning("请先上传图片")
            return None

        try:
            img = self.splitter.prepare_image(img)
            layout = self.config.get_layout(layout_id)
            if not layout:
                gr.Warning("无效的布局")
                return None

            pieces = self.splitter.split(img, layout)
            template = self._create_puzzle_template(img, pieces, layout)

            # 转换为base64
            import io
            import base64
            buffered = io.BytesIO()
            template.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            # 生成HTML
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>拼图模板 - {layout_id}</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            display: flex;
            flex-direction: column;
            align-items: center;
            font-family: Arial, sans-serif;
        }}
        h1 {{
            color: #333;
            margin-bottom: 20px;
        }}
        .container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
        }}
        .info {{
            margin-top: 20px;
            padding: 15px;
            background: #e3f2fd;
            border-radius: 4px;
            color: #1976d2;
        }}
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
                padding: 0;
            }}
            .info {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <h1>🧩 拼图模板</h1>
    <div class="container">
        <img src="data:image/png;base64,{img_str}" alt="拼图模板">
    </div>
    <div class="info">
        <p><strong>布局：</strong>{layout_id}</p>
        <p><strong>提示：</strong>可以直接打印此页面，或右键保存图片</p>
    </div>
</body>
</html>"""

            # 保存HTML
            html_path = Path(tempfile.gettempdir()) / f"puzzle_template_{layout_id}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            return str(html_path)

        except Exception as e:
            gr.Warning(f"导出失败: {str(e)}")
            return None

    def do_export_svg(self, img, layout_id: str):
        """导出拼图模板（SVG格式，矢量图）"""
        if img is None:
            gr.Warning("请先上传图片")
            return None

        try:
            img = self.splitter.prepare_image(img)
            layout = self.config.get_layout(layout_id)
            if not layout:
                gr.Warning("无效的布局")
                return None

            # 获取布局参数
            defaults = layout.get("defaults", {})
            rows = defaults.get("rows", 3)
            cols = defaults.get("cols", 3)
            jigsaw_shape = defaults.get("jigsaw_shape", True)

            w, h = img.size
            piece_w = w // cols
            piece_h = h // rows

            # 转换图片为base64
            import io
            import base64
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            # 生成SVG路径
            svg_paths = []

            if not jigsaw_shape:
                # 直线切分
                for i in range(1, rows):
                    y = i * piece_h
                    svg_paths.append(f'<line x1="0" y1="{y}" x2="{w}" y2="{y}" stroke="black" stroke-width="2" stroke-dasharray="5,10"/>')
                for j in range(1, cols):
                    x = j * piece_w
                    svg_paths.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{h}" stroke="black" stroke-width="2" stroke-dasharray="5,10"/>')
            else:
                # 拼图形状（简化版，只画网格）
                for i in range(1, rows):
                    y = i * piece_h
                    svg_paths.append(f'<line x1="0" y1="{y}" x2="{w}" y2="{y}" stroke="black" stroke-width="2" stroke-dasharray="5,10"/>')
                for j in range(1, cols):
                    x = j * piece_w
                    svg_paths.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{h}" stroke="black" stroke-width="2" stroke-dasharray="5,10"/>')

            svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <image href="data:image/png;base64,{img_str}" width="{w}" height="{h}"/>
    {chr(10).join(svg_paths)}
</svg>"""

            # 保存SVG
            svg_path = Path(tempfile.gettempdir()) / f"puzzle_template_{layout_id}.svg"
            with open(svg_path, "w", encoding="utf-8") as f:
                f.write(svg_content)

            return str(svg_path)

        except Exception as e:
            gr.Warning(f"导出失败: {str(e)}")
            return None


def create_app(config_path: Path = None) -> gr.Blocks:
    """创建 Gradio 应用"""
    app = PuzzleMakerApp(config_path)

    with gr.Blocks(title="拼图生成器") as demo:
        # 标题区域
        gr.HTML("""
            <div class="main-header">
                <h1>🧩 拼图生成器</h1>
                <p>上传图片，一键生成独特的拼图模板</p>
            </div>
        """)

        with gr.Row():
            with gr.Column(scale=1):
                img_input = gr.Image(type="pil", label="📷 上传图片")

                # 第一个选项：切分密度
                density_dropdown = gr.Dropdown(
                    choices=[
                        ("3x3 (9块)", "3x3"),
                        ("4x4 (16块)", "4x4"),
                        ("5x5 (25块)", "5x5"),
                        ("6x6 (36块)", "6x6"),
                        ("8x8 (64块)", "8x8"),
                    ],
                    value="4x4",
                    label="🎯 切分密度（块数）"
                )

                # 第二个选项：切分形状
                shape_dropdown = gr.Dropdown(
                    choices=[
                        ("经典拼图形状（圆形凹凸）", "classic"),
                        ("直线切分（无凹凸）", "straight"),
                    ],
                    value="classic",
                    label="✨ 拼图形状"
                )

                split_btn = gr.Button("✂️ 生成拼图模板", variant="primary", size="lg", elem_classes="primary-btn")
                
                with gr.Row():
                    export_png_btn = gr.Button("💾 导出PNG", size="sm")
                    export_html_btn = gr.Button("🌐 导出HTML", size="sm")
                
                with gr.Row():
                    export_svg_btn = gr.Button("📐 导出SVG", size="sm")
                    clear_btn = gr.Button("🗑️ 清除缓存", size="sm")

                status_text = gr.Textbox(label="状态", interactive=False)
                
                # 下载文件区域
                gr.Markdown("### 下载文件")
                with gr.Column(elem_classes="download-area"):
                    png_download = gr.File(label="PNG", show_label=True, elem_classes="file-preview")
                    html_download = gr.File(label="HTML", show_label=True, elem_classes="file-preview")
                    svg_download = gr.File(label="SVG", show_label=True, elem_classes="file-preview")

            with gr.Column(scale=2, elem_classes="preview-panel"):
                preview_output = gr.Image(label="拼图模板预览", type="pil", height=600)

        def do_split_with_options(img, density, shape):
            """根据密度和形状选项切分"""
            if img is None:
                gr.Warning("请先上传图片")
                return None, "请上传图片"

            try:
                # 解析密度
                rows, cols = map(int, density.split('x'))

                # 创建临时布局配置
                layout = {
                    "id": f"GRID_{density}",
                    "type": "grid",
                    "defaults": {"rows": rows, "cols": cols, "jigsaw_shape": shape == "classic"}
                }

                img = app.splitter.prepare_image(img)
                pieces = app.splitter.split(img, layout)
                preview = app._create_puzzle_template(img, pieces, layout)

                return preview, f"成功生成 {len(pieces)} 块拼图模板（{density}，{shape}形状）"

            except Exception as e:
                return None, f"切分失败: {str(e)}"

        def do_export_png_with_options(img, density, shape):
            """导出PNG格式"""
            if img is None:
                gr.Warning("请先上传图片")
                return None

            try:
                rows, cols = map(int, density.split('x'))
                layout = {
                    "id": f"GRID_{density}_{shape}",
                    "type": "grid",
                    "defaults": {"rows": rows, "cols": cols, "jigsaw_shape": shape == "classic"}
                }

                img = app.splitter.prepare_image(img)
                pieces = app.splitter.split(img, layout)
                template = app._create_puzzle_template(img, pieces, layout)

                template_path = Path(tempfile.gettempdir()) / f"puzzle_{density}_{shape}.png"
                template.save(template_path, "PNG")

                return str(template_path)

            except Exception as e:
                gr.Warning(f"导出失败: {str(e)}")
                return None

        def do_export_html_with_options(img, density, shape):
            """导出HTML格式"""
            if img is None:
                gr.Warning("请先上传图片")
                return None

            try:
                rows, cols = map(int, density.split('x'))
                layout_id = f"{density}_{shape}"
                layout = {
                    "id": layout_id,
                    "type": "grid",
                    "defaults": {"rows": rows, "cols": cols, "jigsaw_shape": shape == "classic"}
                }

                img = app.splitter.prepare_image(img)
                pieces = app.splitter.split(img, layout)
                template = app._create_puzzle_template(img, pieces, layout)

                # 转换为base64
                import io
                import base64
                buffered = io.BytesIO()
                template.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()

                # 生成HTML
                shape_name = "经典拼图" if shape == "classic" else "直线切分"
                html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>拼图模板 - {density} {shape_name}</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            display: flex;
            flex-direction: column;
            align-items: center;
            font-family: Arial, sans-serif;
        }}
        h1 {{
            color: #333;
            margin-bottom: 20px;
        }}
        .container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
        }}
        .info {{
            margin-top: 20px;
            padding: 15px;
            background: #e3f2fd;
            border-radius: 4px;
            color: #1976d2;
        }}
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
                padding: 0;
            }}
            .info {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <h1>🧩 拼图模板</h1>
    <div class="container">
        <img src="data:image/png;base64,{img_str}" alt="拼图模板">
    </div>
    <div class="info">
        <p><strong>切分密度：</strong>{density} ({rows * cols}块)</p>
        <p><strong>拼图形状：</strong>{shape_name}</p>
        <p><strong>提示：</strong>可以直接打印此页面（Ctrl+P），或右键保存图片</p>
    </div>
</body>
</html>"""

                html_path = Path(tempfile.gettempdir()) / f"puzzle_{density}_{shape}.html"
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(html_content)

                return str(html_path)

            except Exception as e:
                gr.Warning(f"导出失败: {str(e)}")
                return None

        def do_export_svg_with_options(img, density, shape):
            """导出SVG格式（矢量图）"""
            if img is None:
                gr.Warning("请先上传图片")
                return None

            try:
                rows, cols = map(int, density.split('x'))
                img = app.splitter.prepare_image(img)
                
                w, h = img.size
                piece_w = w // cols
                piece_h = h // rows

                # 转换图片为base64
                import io
                import base64
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()

                # 生成SVG（简化版，只画网格线）
                svg_paths = []
                for i in range(1, rows):
                    y = i * piece_h
                    svg_paths.append(f'<line x1="0" y1="{y}" x2="{w}" y2="{y}" stroke="black" stroke-width="2" stroke-dasharray="5,10"/>')
                for j in range(1, cols):
                    x = j * piece_w
                    svg_paths.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{h}" stroke="black" stroke-width="2" stroke-dasharray="5,10"/>')

                svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <image href="data:image/png;base64,{img_str}" width="{w}" height="{h}"/>
    {chr(10).join(svg_paths)}
</svg>"""

                svg_path = Path(tempfile.gettempdir()) / f"puzzle_{density}_{shape}.svg"
                with open(svg_path, "w", encoding="utf-8") as f:
                    f.write(svg_content)

                return str(svg_path)

            except Exception as e:
                gr.Warning(f"导出失败: {str(e)}")
                return None

        def do_clear_cache():
            """清除缓存（清空预览和下载文件）"""
            import glob
            import os
            
            try:
                # 清除临时目录中的拼图相关文件
                temp_dir = Path(tempfile.gettempdir())
                patterns = [
                    "puzzle_*.png",
                    "puzzle_*.html", 
                    "puzzle_*.svg",
                    "puzzle_pieces_*.zip"
                ]
                
                deleted_count = 0
                for pattern in patterns:
                    for file_path in glob.glob(str(temp_dir / pattern)):
                        try:
                            os.remove(file_path)
                            deleted_count += 1
                        except:
                            pass
                
                return (
                    None,  # 清空图片输入
                    None,  # 清空预览
                    None,  # 清空PNG下载
                    None,  # 清空HTML下载
                    None,  # 清空SVG下载
                    f"✅ 已清除缓存（删除 {deleted_count} 个临时文件）"  # 状态信息
                )
            except Exception as e:
                return (None, None, None, None, None, f"❌ 清除失败: {str(e)}")

        def on_image_upload(img):
            """上传新图片时自动清除旧缓存"""
            if img is None:
                return None, None, None, "请上传图片"
            
            # 清除旧的下载文件
            return (
                None,  # 清空PNG下载
                None,  # 清空HTML下载
                None,  # 清空SVG下载
                "图片已上传，请选择参数后生成模板"  # 状态信息
            )

        # 上传图片时自动清除旧缓存
        img_input.upload(
            fn=on_image_upload,
            inputs=[img_input],
            outputs=[png_download, html_download, svg_download, status_text]
        )

        split_btn.click(
            fn=do_split_with_options,
            inputs=[img_input, density_dropdown, shape_dropdown],
            outputs=[preview_output, status_text]
        )

        export_png_btn.click(
            fn=do_export_png_with_options,
            inputs=[img_input, density_dropdown, shape_dropdown],
            outputs=[png_download]
        )

        export_html_btn.click(
            fn=do_export_html_with_options,
            inputs=[img_input, density_dropdown, shape_dropdown],
            outputs=[html_download]
        )

        export_svg_btn.click(
            fn=do_export_svg_with_options,
            inputs=[img_input, density_dropdown, shape_dropdown],
            outputs=[svg_download]
        )

        clear_btn.click(
            fn=do_clear_cache,
            inputs=[],
            outputs=[img_input, preview_output, png_download, html_download, svg_download, status_text]
        )

    return demo
