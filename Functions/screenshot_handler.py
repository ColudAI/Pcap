from fastapi import HTTPException
from DrissionPage import ChromiumPage
from typing import Optional, Callable
import asyncio
from config import APP_CONFIG
from PIL import Image
import io
import base64
import re
from Functions.logger import logger
import os
import tempfile
import time

# 并发控制
_semaphore = asyncio.Semaphore(10)

async def take_screenshot_common(
    url: str,
    action: Optional[Callable] = None,
    timeout: Optional[int] = None,
    quality: Optional[int] = None,
    max_retries: int = 3
):
    """核心截图处理函数，带有重试机制"""
    last_error = None
    for attempt in range(max_retries):
        try:
            async with _semaphore:
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(
                    None, _sync_screenshot_handler, url, action, timeout, quality
                )
        except HTTPException as he:
            raise he
        except Exception as e:
            last_error = e
            logger.warning(f"截图尝试 {attempt + 1}/{max_retries} 失败: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1)  # 等待1秒后重试
            continue
    
    raise HTTPException(status_code=500, detail=f"截图失败，已重试{max_retries}次: {str(last_error)}")

def _clean_base64(base64_str: str) -> str:
    """清理base64字符串，只保留有效的base64字符"""
    # 移除可能的data:image前缀
    if ',' in base64_str:
        base64_str = base64_str.split(',')[1]
    
    # 只保留base64有效字符
    base64_str = re.sub(r'[^A-Za-z0-9+/=]', '', base64_str)
    
    # 确保长度是4的倍数
    padding = len(base64_str) % 4
    if padding:
        base64_str += '=' * (4 - padding)
    
    return base64_str

def _sync_screenshot_handler(
    url: str,
    action: Optional[Callable] = None,
    timeout: Optional[int] = None,
    quality: Optional[int] = None
) -> bytes:
    """同步处理逻辑"""
    # 创建页面对象，使用默认窗口大小
    page = ChromiumPage()
    try:
        # 1. 访问页面前
        logger.info(f"开始访问页面: {url}")
        page.set.timeouts(
            page_load=timeout or APP_CONFIG["TIMEOUT"] * 1000,
            script=timeout or APP_CONFIG["TIMEOUT"] * 1000
        )
        page.set.window.size(1366, 768)
        
        # 确保页面完全加载
        page.get(url)
        time.sleep(2)  # 等待页面完全渲染

        # 2. 页面加载后
        logger.info("页面加载完成，准备截图")

        if action:
            action(page)

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # 3. 截图前
            logger.info("准备调用截图方法")
            page.get_screenshot(path=temp_path)
            logger.info(f"截图保存到: {temp_path}")

            with open(temp_path, 'rb') as f:
                screenshot_bytes = f.read()
            logger.info(f"图片数据长度: {len(screenshot_bytes)}")

            # 4. 截图后
            img = Image.open(io.BytesIO(screenshot_bytes))
            logger.info(f"图片格式: {img.format}, 模式: {img.mode}, 大小: {img.size}")

            os.unlink(temp_path)

        except Exception as e:
            # 5. 异常捕获
            logger.error(f"截图失败: {str(e)}")
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise HTTPException(status_code=500, detail=f"截图失败: {str(e)}")

        if quality is not None:
            try:
                img = Image.open(io.BytesIO(screenshot_bytes))
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    img = img.convert('RGB')
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=quality)
                screenshot_bytes = output.getvalue()
            except Exception as e:
                logger.error(f"图片质量处理失败: {str(e)}")
                return screenshot_bytes
        return screenshot_bytes
    finally:
        try:
            page.quit()
        except Exception as e:
            logger.error(f"关闭浏览器页面失败: {str(e)}")

def click_element(page: ChromiumPage, text: str):
    """点击元素动作"""
    element = page.ele(f'text="{text}"')
    if not element:
        raise ValueError("找不到指定元素")
    element.click()
    time.sleep(1)  # 等待点击后的页面变化

def scroll_page(page: ChromiumPage, delta_y: int):
    """页面滚动动作"""
    page.scroll.to_location(0, delta_y)
    time.sleep(1)  # 等待滚动后的页面变化