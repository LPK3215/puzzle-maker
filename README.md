# 拼图生成器

将图片切分为拼图块的 Python 工具，支持多种切分布局和导出格式。

## 功能特性

- 多种切分密度（3x3 到 8x8）
- 两种拼图形状：经典拼图形状（圆形凹凸）/ 直线切分
- Web 界面，响应式设计，支持移动端
- 导出功能：PNG / HTML / SVG
- 自动清除缓存

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

### Web 模式

```bash
python app.py
# 访问 http://localhost:7862
```

## 切分选项

### 切分密度

| 选项 | 说明 | 拼图块数 |
|------|------|----------|
| 3x3 | 简单模式 | 9 块 |
| 4x4 | 标准模式 | 16 块 |
| 5x5 | 中等难度 | 25 块 |
| 6x6 | 较难模式 | 36 块 |
| 8x8 | 困难模式 | 64 块 |

### 拼图形状

| 形状 | 说明 |
|------|------|
| 经典拼图形状 | 带圆形凹凸的传统拼图 |
| 直线切分 | 规则网格切分，无凹凸 |

## 导出格式

| 格式 | 说明 |
|------|------|
| PNG | 图片格式，可直接打印 |
| HTML | 网页格式，包含拼图信息，支持浏览器打印 |
| SVG | 矢量图格式，可无损缩放 |

## 使用方法

1. 上传图片
2. 选择切分密度（块数）
3. 选择拼图形状
4. 点击"生成拼图模板"预览
5. 点击导出按钮下载对应格式

## 项目结构

```
puzzle-maker/
├── app.py               # Web 入口
├── src/
│   ├── puzzle_app.py    # Gradio Web 应用
│   └── engine/          # 拼图切分引擎
│       ├── preprocess.py# 图像预处理
│       ├── layouts.py   # 切分布局实现
│       └── splitter.py  # 配置管理与切分调度
├── config/
│   └── layouts.json     # 布局配置
├── data/
│   └── bg2.jpg          # 示例图片
├── deploy/              # 部署配置
└── requirements.txt
```

## 部署

### Docker 部署（推荐）

```bash
docker build -t puzzle-maker -f deploy/Dockerfile .
docker run -d -p 7862:7862 --name puzzle-maker --restart unless-stopped puzzle-maker
```

详见 `deploy/README.md` 和 `deploy/服务器操作指南.md`

## 依赖

- Python 3.8+
- Pillow >= 9.0.0
- Gradio >= 4.0.0

## Git 脚本

项目包含两个便捷的 Git 脚本：

- `1-git-push-日常推送.bat` - 一键推送代码到 GitHub
- `2-git-clone-从云端拉取.bat` - 一键克隆仓库

## 许可

MIT License
