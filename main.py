from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from playwright.async_api import async_playwright
from urllib.parse import urlparse
from typing import Optional, Callable
import re
import asyncio

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
                return Response(content=screenshot, media_type="image/png")
            finally:
                if page:
                    await page.close()
                if context:
                    await context.close()
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screenshot failed: {str(e)}")

@app.get("/screenshot")
async def take_screenshot(url: str):
    """基础截图API"""
    return await take_screenshot_common(url)

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
    return await take_screenshot_common(url, action)

@app.get("/screenshot_after_scroll")
async def take_screenshot_after_scroll(url: str, delta_y: int):
    """滚动页面后截图"""
    async def action(page):
        await page.evaluate(f"window.scrollBy(0, {delta_y})")
    return await take_screenshot_common(url, action)

# 关闭浏览器实例
@app.on_event("shutdown")
async def shutdown_event():
    if _browser:
        await _browser.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)