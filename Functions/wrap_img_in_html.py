
def qru(img_b64, url):
    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="icon" type="image/svg+xml" href="https://coludai.cn/data_img/Logo.png" />
        <title>Pcap - {url}</title>
        <style>
            /* 全局样式 */
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }}

            /* 浅色模式 */
            @media (prefers-color-scheme: light) {{
                body {{
                    background-color: #f1f3f4;
                }}
                .browser-window {{
                    background-color: #fff;
                }}
                .toolbar {{
                    background-color: #f8f9fa;
                    border-bottom: 1px solid #e0e0e0;
                }}
                .tab {{
                    background-color: #fff;
                    border: 1px solid #e0e0e0;
                    color: #202124;
                }}
                .tab.active {{
                    background-color: #f8f9fa;
                    border-bottom-color: transparent;
                }}
            }}

            /* 深色模式 */
            @media (prefers-color-scheme: dark) {{
                body {{
                    background-color: #1C1C1C;
                }}
                .browser-window {{
                    background-color: #2d2d2d;
                }}
                .toolbar {{
                    background-color: #333;
                    border-bottom: 1px solid #444;
                }}
                .tab {{
                    background-color: #2d2d2d;
                    border: 1px solid #444;
                    color: #e0e0e0;
                }}
                .tab.active {{
                    background-color: #333;
                    border-bottom-color: transparent;
                }}
            }}

            /* 浏览器窗口容器 - 全屏显示 */
            .browser-window {{
                width: 100vw;
                height: 100vh;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }}

            /* 顶部工具栏 */
            .toolbar {{
                display: flex;
                align-items: center;
                padding: 12px;
                flex-shrink: 0; /* 防止工具栏被压缩 */
            }}

            /* Mac风格的控制按钮 */
            .controls {{
                display: flex;
                gap: 8px;
                margin-right: 12px;
            }}

            .control-btn {{
                width: 12px;
                height: 12px;
                border-radius: 50%;
                border: none;
            }}

            .close {{
                background-color: #ff5f56;
            }}

            .minimize {{
                background-color: #ffbd2e;
            }}

            .maximize {{
                background-color: #27c93f;
            }}

            /* 标签页栏 */
            .tabs {{
                flex: 1;
                display: flex;
                gap: 8px;
                padding: 0 12px;
                overflow-x: auto;
            }}

            .tab {{
                flex: 1;
                max-width: 200px;
                height: 36px;
                border-radius: 8px 8px 0 0;
                display: flex;
                align-items: center;
                padding: 0 12px;
                font-size: 14px;
            }}

            .tab.active {{
                border-bottom-color: transparent;
            }}

            /* 内容区域 - 宽度适配，高度滚动 */
            .content {{
                flex: 1;
                overflow-x: hidden; /* 隐藏水平滚动条 */
                overflow-y: auto; /* 允许垂直滚动 */
                position: relative;
            }}

            /* 图片样式 - 宽度适配，高度按比例 */
            .content img {{
                width: 100%;
                height: auto; /* 高度按比例缩放 */
                display: block;
            }}
        </style>
    </head>
    <body>
        <div class="browser-window">
            <!-- 顶部工具栏 -->
            <div class="toolbar">
                <div class="controls">
                    <div class="control-btn close"></div>
                    <div class="control-btn minimize"></div>
                    <div class="control-btn maximize"></div>
                </div>
                <!-- 标签页 -->
                <div class="tabs">
                    <div class="tab active">{url}</div>
                </div>
            </div>

            <!-- 内容区域 -->
            <div class="content">
                <img src="data:image/png;base64,{img_b64}" alt="网页截图">
            </div>
        </div>
    </body>
    </html>
    """