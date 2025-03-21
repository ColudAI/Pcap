from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from Functions.screenshot_handler import take_screenshot_common, click_element, scroll_page
from Functions.html_wrapper import wrap_screenshot_in_html
from Functions.url_validator import validate_url

router = APIRouter()

# 加载页面HTML模板
with open('files/template/load.html', 'r', encoding='utf-8') as f:
    LOADING_HTML = f.read()

@router.get("/screenshot")
async def take_screenshot(url: str, ajax: bool = False):
    """基础截图接口"""
    if not ajax:
        return HTMLResponse(LOADING_HTML)
    if not validate_url(url):
        raise HTTPException(status_code=400, detail="URL格式无效")
    screenshot = await take_screenshot_common(url)
    return HTMLResponse(wrap_screenshot_in_html(screenshot, url))

@router.get("/screenshot_after_click")
async def take_screenshot_after_click(url: str, text: str, ajax: bool = False):
    """点击后截图接口"""
    if not ajax:
        return HTMLResponse(LOADING_HTML)
    if not validate_url(url):
        raise HTTPException(status_code=400, detail="URL格式无效")
    
    try:
        screenshot = await take_screenshot_common(url, lambda page: click_element(page, text))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return HTMLResponse(wrap_screenshot_in_html(screenshot, url))

@router.get("/screenshot_after_scroll")
async def take_screenshot_after_scroll(url: str, delta_y: int, ajax: bool = False):
    """滚动后截图接口"""
    if not ajax:
        return HTMLResponse(LOADING_HTML)
    if not validate_url(url):
        raise HTTPException(status_code=400, detail="URL格式无效")
    
    screenshot = await take_screenshot_common(url, lambda page: scroll_page(page, delta_y))
    return HTMLResponse(wrap_screenshot_in_html(screenshot, url))