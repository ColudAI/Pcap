from urllib.parse import urlparse
import re

def validate_url(url: str) -> bool:
    """URL验证函数"""
    parsed = urlparse(url)
    return re.match(r"^https?://", url, re.IGNORECASE) is not None