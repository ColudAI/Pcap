from fastapi import HTTPException
from DrissionPage import WebPage
from typing import Optional, Callable
import asyncio

# 并发SB控制
_semaphore = asyncio.Semaphore(10)

async def take_screenshot_common(url: str, action: Optional[Callable] = None):
    """核心截图处理函数"""
    try:
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

def click_element(page: WebPage, text: str):
    """点击元素动作"""
    element = page.ele(f'text:{text}', timeout=5)
    if not element:
        raise ValueError("找不到指定元素")
    element.click()
    page.wait(2)

def scroll_page(page: WebPage, delta_y: int):
    """页面滚动动作"""
    page.run_js(f"window.scrollBy(0, {delta_y})")
    page.wait(0.5)