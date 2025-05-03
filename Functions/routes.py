from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, Response
from Functions.screenshot_handler import take_screenshot_common, click_element, scroll_page
from Functions.html_wrapper import wrap_screenshot_in_html
from Functions.url_validator import validate_url
from Functions.logger import logger
from Functions.cache import screenshot_cache
from config import APP_CONFIG
import asyncio
from typing import Optional

router = APIRouter()

# 加载页面HTML模板
with open('files/template/load.html', 'r', encoding='utf-8') as f:
    LOADING_HTML = f.read()

# 并发请求限制
request_semaphore = asyncio.Semaphore(APP_CONFIG["MAX_CONCURRENT_REQUESTS"])

@router.get("/health")
async def health_check():
    """健康检查接口"""
    return JSONResponse({"status": "healthy"})

@router.get("/screenshot")
async def take_screenshot(
    url: str,
    ajax: bool = False,
    quality: Optional[int] = None,
    timeout: Optional[int] = None
):
    """基础截图接口"""
    if not ajax:
        return HTMLResponse(LOADING_HTML)
    
    if not validate_url(url):
        raise HTTPException(status_code=400, detail="URL格式无效")
    
    try:
        async with request_semaphore:
            screenshot = await take_screenshot_common(
                url,
                timeout=timeout or APP_CONFIG["TIMEOUT"],
                quality=quality or APP_CONFIG["SCREENSHOT_QUALITY"]
            )
            return HTMLResponse(wrap_screenshot_in_html(screenshot, url))
    except Exception as e:
        logger.error(f"截图失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"截图失败: {str(e)}")

@router.get("/screenshot_after_click")
async def take_screenshot_after_click(
    url: str,
    text: str,
    ajax: bool = False,
    quality: Optional[int] = None,
    timeout: Optional[int] = None
):
    """点击后截图接口"""
    if not ajax:
        return HTMLResponse(LOADING_HTML)
    
    if not validate_url(url):
        raise HTTPException(status_code=400, detail="URL格式无效")
    
    try:
        async with request_semaphore:
            screenshot = await take_screenshot_common(
                url,
                lambda page: click_element(page, text),
                timeout=timeout or APP_CONFIG["TIMEOUT"],
                quality=quality or APP_CONFIG["SCREENSHOT_QUALITY"]
            )
            return HTMLResponse(wrap_screenshot_in_html(screenshot, url))
    except ValueError as e:
        logger.error(f"点击元素失败: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"截图失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"截图失败: {str(e)}")

@router.get("/screenshot_after_scroll")
async def take_screenshot_after_scroll(
    url: str,
    delta_y: int,
    ajax: bool = False,
    quality: Optional[int] = None,
    timeout: Optional[int] = None
):
    """滚动后截图接口"""
    if not ajax:
        return HTMLResponse(LOADING_HTML)
    
    if not validate_url(url):
        raise HTTPException(status_code=400, detail="URL格式无效")
    
    try:
        async with request_semaphore:
            screenshot = await take_screenshot_common(
                url,
                lambda page: scroll_page(page, delta_y),
                timeout=timeout or APP_CONFIG["TIMEOUT"],
                quality=quality or APP_CONFIG["SCREENSHOT_QUALITY"]
            )
            return HTMLResponse(wrap_screenshot_in_html(screenshot, url))
    except Exception as e:
        logger.error(f"截图失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"截图失败: {str(e)}")

@router.post("/clear_cache")
async def clear_cache():
    """清除缓存接口"""
    screenshot_cache.clear()
    return JSONResponse({"status": "success", "message": "缓存已清除"})