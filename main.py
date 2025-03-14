from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from DrissionPage import WebPage
from urllib.parse import urlparse
from typing import Optional, Callable
import re
import asyncio
import base64

app = FastAPI()

# 加载页面HTML模板
LOADING_HTML = """
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Pcap-让我思考与执行💡</title>
  <link rel="icon" type="image/svg+xml" href="https://coludai.cn/data_img/Logo.png" />
  <style>
    /* 全局初始化 */
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    /* 居中屏幕并设置背景为深空灰色 */
    body {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100vh;
      background-color: #1C1C1C;
      position: relative;
    }
    /* API 开放平台按钮及其光泽效果，文本更浅灰 */
    .api-btn {
      position: relative;
      display: inline-block;
      overflow: hidden;
      padding-bottom: 0.3rem;
    }
    .api-btn .btn-text {
      display: inline-block;
      background: linear-gradient(90deg, #888 40%, #aaa 50%, #888 60%);
      background-size: 200%;
      -webkit-background-clip: text;
      color: transparent;
      animation: shine 3s linear infinite;
      font-size: 1.2rem;
    }
    @keyframes shine {
      0% { background-position: -200%; }
      100% { background-position: 200%; }
    }
    .api-btn:hover {
      cursor: default;
    }
    /* 底部水印样式 */
    .watermark {
      position: fixed;
      bottom: 10px;
      width: 100%;
      text-align: center;
      color: #999;
      font-size: 0.8rem;
      pointer-events: none;
    }
  </style>
</head>
<body>
  <div class="api-btn">
    <span class="btn-text">让我思考与执行💡</span>
  </div>
  <div class="watermark">Pcap&SAI-Reasoner</div>
  <script>
    window.onload = function() {
      const urlParams = new URLSearchParams(window.location.search);
      const params = { ajax: 'true' };
      
      urlParams.forEach((value, key) => {
        if (key !== 'ajax') params[key] = value;
      });

      fetch(`${window.location.pathname}?${new URLSearchParams(params)}`)
        .then(response => {
          if (!response.ok) return response.text().then(t => { throw t });
          return response.text();
        })
        .then(html => {
          document.documentElement.innerHTML = html;
        })
        .catch(error => {
          document.body.innerHTML = `<div style="color:#ff5555;padding:20px">加载失败: ${error}</div>`;
        });
    };
  </script>
</body>
</html>
"""

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# 并发控制
_semaphore = asyncio.Semaphore(10)

def validate_url(url: str) -> bool:
    """URL验证函数"""
    parsed = urlparse(url)
    return re.match(r"^https?://", url, re.IGNORECASE) is not None

async def take_screenshot_common(url: str, action: Optional[Callable] = None):
    """核心截图处理函数"""
    try:
        if not validate_url(url):
            raise HTTPException(status_code=400, detail="URL格式无效")

        async with _semaphore:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, _sync_screenshot_handler, url, action
            )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"截图失败: {str(e)}")

def _sync_screenshot_handler(url: str, action: Optional[Callable] = None) -> bytes:
    """同步处理逻辑"""
    page = WebPage()
    try:
        page.get(url, timeout=15000)
        if action:
            action(page)
        return page.get_screenshot(full_page=True, as_bytes=True)
    finally:
        page.quit()

def wrap_screenshot_in_html(screenshot: bytes, url: str) -> str:
    """将截图嵌入HTML页面，支持深色和浅色模式"""
    screenshot_base64 = base64.b64encode(screenshot).decode("utf-8")
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
                <img src="data:image/png;base64,{screenshot_base64}" alt="网页截图">
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/screenshot")
async def take_screenshot(url: str, ajax: bool = False):
    """基础截图接口"""
    if not ajax:
        return HTMLResponse(LOADING_HTML)
    screenshot = await take_screenshot_common(url)
    return HTMLResponse(wrap_screenshot_in_html(screenshot, url))

@app.get("/screenshot_after_click")
async def take_screenshot_after_click(url: str, text: str, ajax: bool = False):
    """点击后截图接口"""
    if not ajax:
        return HTMLResponse(LOADING_HTML)
    
    def action(page: WebPage):
        element = page.ele(f'text:{text}', timeout=5)
        if not element:
            raise ValueError("找不到指定元素")
        element.click()
        page.wait(2)

    try:
        screenshot = await take_screenshot_common(url, action)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return HTMLResponse(wrap_screenshot_in_html(screenshot, url))

@app.get("/screenshot_after_scroll")
async def take_screenshot_after_scroll(url: str, delta_y: int, ajax: bool = False):
    """滚动后截图接口"""
    if not ajax:
        return HTMLResponse(LOADING_HTML)
    
    def action(page: WebPage):
        page.run_js(f"window.scrollBy(0, {delta_y})")
        page.wait(0.5)

    screenshot = await take_screenshot_common(url, action)
    return HTMLResponse(wrap_screenshot_in_html(screenshot, url))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)