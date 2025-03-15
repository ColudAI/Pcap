from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from DrissionPage import WebPage
from urllib.parse import urlparse
from typing import Optional, Callable
import re
import asyncio
import base64
from Functions import ipManage, wrap_img_in_html

app = FastAPI()

# 加载页面HTML模板
with open('files/template/load.html', 'r', encoding='utf-8') as f:
    LOADING_HTML = f.read()

ip_list = ipManage.get_ip_address()
for i in ip_list:
    print(f"App is running at http://{i}:8000/  ...")

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
    return wrap_img_in_html.qru(screenshot_base64, url)

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