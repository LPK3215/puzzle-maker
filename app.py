#!/usr/bin/env python3
"""拼图生成器 - Web 入口"""

from pathlib import Path
import gradio as gr
from src.puzzle_app import create_app

if __name__ == "__main__":
    # 确保使用正确的配置路径
    config_path = Path(__file__).parent / "config" / "layouts.json"
    
    # 自定义CSS - 清新青绿色主题
    custom_css = """
    /* 全局样式 - 清新青绿色主题 */
    .gradio-container {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* 标题居中 - 青绿渐变 */
    .main-header {
        text-align: center;
        padding: 30px 20px;
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        border-radius: 16px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(17, 153, 142, 0.3);
    }
    .main-header h1 {
        color: white !important;
        font-size: 36px !important;
        font-weight: 700 !important;
        margin: 0 0 10px 0 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        letter-spacing: 2px;
    }
    .main-header p {
        color: rgba(255,255,255,0.95) !important;
        font-size: 16px !important;
        margin: 0 !important;
        font-weight: 300;
    }
    
    /* 按钮样式 - 青绿色系 */
    .primary-btn {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(17, 153, 142, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    .primary-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(17, 153, 142, 0.5) !important;
    }
    
    /* 导出按钮 - 橙色渐变 */
    button[size="sm"] {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    button[size="sm"]:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 4px 12px rgba(250, 112, 154, 0.4) !important;
    }
    
    /* 下载区域固定高度 - 淡青色背景 */
    .download-area {
        min-height: 180px !important;
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border-radius: 12px;
        padding: 15px;
    }
    .download-area .file-preview {
        min-height: 52px !important;
        margin-bottom: 4px !important;
        background: white;
        border-radius: 8px;
        border: 2px solid #11998e;
    }
    
    /* 预览区域 */
    .preview-panel {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    /* 输入框样式 */
    .gr-box {
        border-radius: 10px !important;
        border: 2px solid #e0e0e0 !important;
    }
    .gr-box:focus-within {
        border-color: #11998e !important;
        box-shadow: 0 0 0 3px rgba(17, 153, 142, 0.1) !important;
    }
    
    /* 下拉框样式 */
    select {
        border-radius: 8px !important;
        border: 2px solid #e0e0e0 !important;
    }
    select:focus {
        border-color: #11998e !important;
        outline: none !important;
    }
    """
    
    demo = create_app(config_path)
    demo.launch(
        server_name="0.0.0.0",
        server_port=7862,  # 拼图生成器专属端口
        max_threads=2,  # 限制并发，防止内存耗尽
        css=custom_css  # 应用自定义CSS
    )
