import os
import json
import time
import base64
from typing import Optional, Dict, Any
from config import APP_CONFIG
from Functions.logger import logger

class ScreenshotCache:
    def __init__(self):
        self.cache_dir = "cache"
        self.cache_file = os.path.join(self.cache_dir, "screenshot_cache.json")
        self._load_cache()

    def _load_cache(self):
        """加载缓存数据"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
            except Exception as e:
                logger.error(f"加载缓存失败: {str(e)}")
                self.cache = {}
        else:
            self.cache = {}

    def _save_cache(self):
        """保存缓存数据"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f)
        except Exception as e:
            logger.error(f"保存缓存失败: {str(e)}")

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """获取缓存数据"""
        if not APP_CONFIG["CACHE_ENABLED"]:
            return None

        if key in self.cache:
            cache_data = self.cache[key]
            if time.time() - cache_data["timestamp"] < APP_CONFIG["CACHE_EXPIRE"]:
                logger.info(f"缓存命中: {key}")
                # 将base64字符串转换回bytes
                if "screenshot" in cache_data["data"]:
                    cache_data["data"]["screenshot"] = base64.b64decode(cache_data["data"]["screenshot"])
                return cache_data["data"]
            else:
                logger.info(f"缓存过期: {key}")
                del self.cache[key]
                self._save_cache()
        return None

    def set(self, key: str, data: Dict[str, Any]):
        """设置缓存数据"""
        if not APP_CONFIG["CACHE_ENABLED"]:
            return

        # 创建数据的副本
        cache_data = data.copy()
        
        # 如果数据中包含bytes类型的screenshot，转换为base64字符串
        if "screenshot" in cache_data and isinstance(cache_data["screenshot"], bytes):
            cache_data["screenshot"] = base64.b64encode(cache_data["screenshot"]).decode('utf-8')

        self.cache[key] = {
            "data": cache_data,
            "timestamp": time.time()
        }
        self._save_cache()
        logger.info(f"缓存已更新: {key}")

    def clear(self):
        """清除所有缓存"""
        self.cache = {}
        self._save_cache()
        logger.info("缓存已清除")

# 创建缓存实例
screenshot_cache = ScreenshotCache() 