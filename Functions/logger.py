import logging
import sys
from logging.handlers import RotatingFileHandler
from config import LOG_CONFIG

def setup_logger(name: str) -> logging.Logger:
    """设置日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(LOG_CONFIG["LOG_LEVEL"])

    # 创建格式化器
    formatter = logging.Formatter(LOG_CONFIG["LOG_FORMAT"])

    # 添加控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 添加文件处理器
    file_handler = RotatingFileHandler(
        f"logs/{LOG_CONFIG['LOG_FILE']}",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# 创建默认日志记录器
logger = setup_logger("pcap") 