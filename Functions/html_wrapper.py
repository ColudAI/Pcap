import base64

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" type="image/svg+xml" href="https://coludai.cn/data_img/Logo.png" />
    <title>Pcap - {url}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f5f5f7;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .browser-window {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.08), 0 6px 6px rgba(0, 0, 0, 0.12);
            overflow: hidden;
            max-width: 1200px;
            width: 100%;
            margin: 0 auto;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .browser-window:hover {{
            transform: translateY(-2px);
            box-shadow: 0 14px 28px rgba(0, 0, 0, 0.12), 0 10px 10px rgba(0, 0, 0, 0.14);
        }}
        .browser-header {{
            background: #f1f3f4;
            padding: 12px 16px;
            border-bottom: 1px solid rgba(0, 0, 0, 0.1);
        }}
        .browser-controls {{
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }}
        .control-button {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            position: relative;
            border: none;
        }}
        .control-button::after {{
            content: '';
            position: absolute;
            top: -4px;
            left: -4px;
            right: -4px;
            bottom: -4px;
            border-radius: 50%;
            background: currentColor;
            opacity: 0;
            transition: opacity 0.2s ease;
        }}
        .control-button:hover::after {{
            opacity: 0.1;
        }}
        .close {{ background: #ff5f56; color: #ff5f56; }}
        .minimize {{ background: #ffbd2e; color: #ffbd2e; }}
        .maximize {{ background: #27c93f; color: #27c93f; }}
        .address-bar {{
            background: white;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
            color: #5f6368;
            border: 1px solid rgba(0, 0, 0, 0.1);
            transition: border-color 0.2s ease;
        }}
        .address-bar:hover {{
            border-color: rgba(0, 0, 0, 0.2);
        }}
        .browser-content {{
            padding: 0;
            position: relative;
        }}
        .screenshot {{
            display: block;
            width: 100%;
            height: auto;
            transition: transform 0.2s ease;
        }}
        @media (prefers-color-scheme: dark) {{
            body {{ background: #1a1a1c; }}
            .browser-window {{ 
                background: #2a2a2c; 
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2), 0 6px 6px rgba(0, 0, 0, 0.25);
            }}
            .browser-window:hover {{
                box-shadow: 0 14px 28px rgba(0, 0, 0, 0.25), 0 10px 10px rgba(0, 0, 0, 0.3);
            }}
            .browser-header {{ 
                background: #323234; 
                border-color: rgba(255, 255, 255, 0.1);
            }}
            .address-bar {{ 
                background: #323234; 
                border-color: rgba(255, 255, 255, 0.1); 
                color: #e0e0e0;
            }}
            .address-bar:hover {{
                border-color: rgba(255, 255, 255, 0.2);
            }}
        }}
    </style>
    <script>
        window.onload = function() {
            const width = window.innerWidth;
            const height = window.innerHeight;
            fetch('/api/set-window-size', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ width, height })
            });
        }
    </script>
</head>
<body>
    <div class="browser-window">
        <div class="browser-header">
            <div class="browser-controls">
                <div class="control-button close" onclick="window.close()"></div>
                <div class="control-button minimize"></div>
                <div class="control-button maximize"></div>
            </div>
            <div class="address-bar">{url}</div>
        </div>
        <div class="browser-content">
            <img class="screenshot" src="data:image/png;base64,{img_b64}" alt="Screenshot">
        </div>
    </div>
</body>
</html>
"""

def wrap_screenshot_in_html(screenshot: bytes, url: str) -> str:
    """将截图嵌入HTML页面，支持深色和浅色模式"""
    screenshot_base64 = base64.b64encode(screenshot).decode("utf-8")
    return HTML_TEMPLATE.format(url=url, img_b64=screenshot_base64)