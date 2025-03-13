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

# 允许跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# 并发控制信号量
_semaphore = asyncio.Semaphore(10)

def validate_url(url: str) -> bool:
    """验证URL合法性（基础SSRF防护）"""
    parsed = urlparse(url)
    if not re.match(r"^https?://", url, re.IGNORECASE):
        return False
    return True

async def take_screenshot_common(url: str, action: Optional[Callable] = None):
    """公共截图处理函数"""
    try:
        if not validate_url(url):
            raise HTTPException(status_code=400, detail="Invalid URL format")

        async with _semaphore:
            loop = asyncio.get_event_loop()
            screenshot = await loop.run_in_executor(
                None, _sync_screenshot_handler, url, action
            )
            return screenshot
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screenshot failed: {str(e)}")

def _sync_screenshot_handler(url: str, action: Optional[Callable] = None) -> bytes:
    """同步处理截图逻辑"""
    page = WebPage()
    try:
        # 访问页面并设置超时
        page.get(url, timeout=15000)
        
        # 执行自定义操作（如果有）
        if action:
            action(page)

        # 获取全屏截图，并返回字节数据（移除了 save_path 参数）
        return page.get_screenshot(full_page=True, as_bytes=True)
    
    except Exception as e:
        raise RuntimeError(str(e))
    finally:
        page.quit()

def wrap_screenshot_in_html(screenshot: bytes, url: str) -> str:
    """将截图嵌入HTML页面（与原代码保持一致）"""
    screenshot_base64 = base64.b64encode(screenshot).decode("utf-8")
    # 此处保持原有HTML模板不变
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
                background-color: #f1f3f4;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }}

            /* 浏览器窗口容器 */
            .browser-window {{
                width: 100%;
                height: 100vh;
                background-color: #fff;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                overflow: hidden;
                display: flex;
                flex-direction: column;
            }}

            /* 顶部工具栏 */
            .toolbar {{
                display: flex;
                align-items: center;
                padding: 12px;
                background-color: #f8f9fa;
                border-bottom: 1px solid #e0e0e0;
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
                background-color: #fff;
                border: 1px solid #e0e0e0;
                border-radius: 8px 8px 0 0;
                display: flex;
                align-items: center;
                padding: 0 12px;
                font-size: 14px;
                color: #202124;
            }}

            .tab.active {{
                background-color: #f8f9fa;
                border-bottom-color: transparent;
            }}

            /* 内容区域 */
            .content {{
                flex: 1;
                background-color: #fff;
                padding: 20px;
                overflow: auto;
                text-align: center;
            }}

            .content img {{
                max-width: 100%;
                height: auto;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
async def take_screenshot(url: str):
    """基础截图接口"""
    screenshot = await take_screenshot_common(url)
    return HTMLResponse(content=wrap_screenshot_in_html(screenshot, url))

@app.get("/screenshot_after_click")
async def take_screenshot_after_click(url: str, text: str):
    """点击文本后截图"""
    def action(page: WebPage):
        # 使用更可靠的文本定位方式
        element = page.ele(f'text:{text}', timeout=5)
        if not element:
            raise ValueError("Element not found")
        element.click()
        page.wait(2)  # 等待可能的页面变化

    try:
        screenshot = await take_screenshot_common(url, action)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return HTMLResponse(content=wrap_screenshot_in_html(screenshot, url))

@app.get("/screenshot_after_scroll")
async def take_screenshot_after_scroll(url: str, delta_y: int):
    """滚动页面后截图"""
    def action(page: WebPage):
        page.run_js(f"window.scrollBy(0, {delta_y})")
        page.wait(0.5)  # 等待滚动动画

    screenshot = await take_screenshot_common(url, action)
    return HTMLResponse(content=wrap_screenshot_in_html(screenshot, url))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)