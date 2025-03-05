from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from playwright.async_api import async_playwright
from urllib.parse import urlparse
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

@app.get("/screenshot")
async def take_screenshot(url: str):
    try:
        # 验证URL合法性
        if not validate_url(url):
            raise HTTPException(status_code=400, detail="Invalid URL format")

        # 限制并发数
        async with _semaphore:
            # 获取浏览器实例
            browser = await get_browser()
            context = await browser.new_context(viewport={"width": 1280, "height": 800})
            page = await context.new_page()

            # 访问页面（配置网络空闲检测）
            await page.goto(url, wait_until="networkidle", timeout=15000)
            
            # 截取完整页面
            screenshot = await page.screenshot(full_page=True, type="png")
            
            # 关闭页面和上下文
            await page.close()
            await context.close()

            # 返回二进制图片数据
            return Response(content=screenshot, media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screenshot failed: {str(e)}")

# 关闭浏览器实例
@app.on_event("shutdown")
async def shutdown_event():
    if _browser:
        await _browser.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)