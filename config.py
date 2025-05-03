from typing import Dict, Any
import os

# 应用配置
APP_CONFIG: Dict[str, Any] = {
    "HOST": "0.0.0.0", # 监听地址
    "PORT": 8000, # 监听端口
    "DEBUG": False, # 是否开启调试模式
    "TIMEOUT": 30,  # 截图超时时间（秒）
    "CACHE_ENABLED": True, # 是否开启缓存
    "CACHE_EXPIRE": 3600,  # 缓存过期时间（秒）
    "MAX_CONCURRENT_REQUESTS": 5,  # 最大并发请求数
    "SCREENSHOT_QUALITY": 80,  # 截图质量（0-100）
}

# 日志配置
LOG_CONFIG: Dict[str, Any] = {
    "LOG_LEVEL": "INFO", # 日志级别
    "LOG_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s", # 日志格式
    "LOG_FILE": "app.log" # 日志文件
}

# LOGO
ART_LOGO = """
Pcap
ColudAI
"""


# 创建必要的目录
os.makedirs("logs", exist_ok=True) # 创建日志目录
os.makedirs("cache", exist_ok=True) # 创建缓存目录