from typing import Dict, Any
import os

# 应用配置
APP_CONFIG: Dict[str, Any] = {
    "HOST": "0.0.0.0",
    "PORT": 8000,
    "DEBUG": False,
    "TIMEOUT": 30,  # 截图超时时间（秒）
    "CACHE_ENABLED": True,
    "CACHE_EXPIRE": 3600,  # 缓存过期时间（秒）
    "MAX_CONCURRENT_REQUESTS": 5,  # 最大并发请求数
    "SCREENSHOT_QUALITY": 80,  # 截图质量（0-100）
}

# 日志配置
LOG_CONFIG: Dict[str, Any] = {
    "LOG_LEVEL": "INFO",
    "LOG_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "LOG_FILE": "app.log"
}

# 创建必要的目录
os.makedirs("logs", exist_ok=True)
os.makedirs("cache", exist_ok=True) 