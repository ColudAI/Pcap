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
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, timeout=15000)
            if action:
                action(page)
            return page.screenshot(full_page=True, type='jpeg')
        finally:
            browser.close()

def click_element(page: any, text: str):
    """点击元素动作"""
    element = page.get_by_text(text).first
    if not element:
        raise ValueError("找不到指定元素")
    element.click()
    page.wait_for_timeout(2000)

def scroll_page(page: any, delta_y: int):
    """页面滚动动作"""
    page.mouse.wheel(0, delta_y)
    page.wait_for_timeout(500)