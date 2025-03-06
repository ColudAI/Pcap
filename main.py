from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse  # 修改为返回HTML
from fastapi.middleware.cors import CORSMiddleware
from playwright.async_api import async_playwright
from urllib.parse import urlparse, quote
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

# 全局浏览器实例和信号量（限制并发数）
_browser = None
_semaphore = asyncio.Semaphore(10)  # 限制最多 10 个并发

def validate_url(url: str) -> bool:
    """验证URL合法性（基础SSRF防护）"""
    parsed = urlparse(url)
    if not re.match(r"^https?://", url, re.IGNORECASE):
        return False
    # 可在此处添加域名白名单过滤
    return True

async def get_browser():
    """获取全局浏览器实例"""
    global _browser
    if not _browser:
        playwright = await async_playwright().start()  # 启动 Playwright
        _browser = await playwright.chromium.launch(headless=True, timeout=30000)
    return _browser

async def take_screenshot_common(url: str, action: Optional[Callable] = None):
    """公共截图函数，执行特定操作后截图"""
    try:
        if not validate_url(url):
            raise HTTPException(status_code=400, detail="Invalid URL format")

        async with _semaphore:
            browser = await get_browser()
            context = None
            page = None
            try:
                context = await browser.new_context(viewport={"width": 1280, "height": 800})
                page = await context.new_page()
                await page.goto(url, wait_until="networkidle", timeout=15000)
                
                if action:
                    await action(page)

                screenshot = await page.screenshot(full_page=True, type="png")
                return screenshot
            finally:
                if page:
                    await page.close()
                if context:
                    await context.close()
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screenshot failed: {str(e)}")

def wrap_screenshot_in_html(screenshot: bytes, url: str) -> str:
    """将截图嵌入到模仿Chrome浏览器标签页的HTML页面中"""
    # 将图片转换为Base64
    screenshot_base64 = base64.b64encode(screenshot).decode("utf-8")
    
    # 构建HTML页面
    html_content = f"""
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
                    <div class="tab active">新标签页</div>
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
    return html_content

@app.get("/screenshot")
async def take_screenshot(url: str):
    """基础截图API"""
    screenshot = await take_screenshot_common(url)
    html_content = wrap_screenshot_in_html(screenshot, url)
    return HTMLResponse(content=html_content)

@app.get("/screenshot_after_click")
async def take_screenshot_after_click(url: str, text: str):
    """点击指定文本元素后截图"""
    async def action(page):
        element = page.get_by_text(text)
        count = await element.count()
        if count == 0:
            raise HTTPException(status_code=404, detail="找不到包含指定文本的元素")
        await element.click()
        try:
            await page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass  # 超时后继续截图
    screenshot = await take_screenshot_common(url, action)
    html_content = wrap_screenshot_in_html(screenshot, url)
    return HTMLResponse(content=html_content)

@app.get("/screenshot_after_scroll")
async def take_screenshot_after_scroll(url: str, delta_y: int):
    """滚动页面后截图"""
    async def action(page):
        await page.evaluate(f"window.scrollBy(0, {delta_y})")
    screenshot = await take_screenshot_common(url, action)
    html_content = wrap_screenshot_in_html(screenshot, url)
    return HTMLResponse(content=html_content)

# 关闭浏览器实例
@app.on_event("shutdown")
async def shutdown_event():
    if _browser:
        await _browser.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)