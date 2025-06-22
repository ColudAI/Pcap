from urllib.parse import urlparse
import re
import socket
import ipaddress

def validate_url(url: str) -> bool:
    """URL验证函数"""
    # 必须以 http/https 开头
    if re.match(r"^https?://", url, re.IGNORECASE) is None:
        return False
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return False
        # 禁止常见本地主机名
        if hostname.lower() in ["localhost", "0.0.0.0", "127.0.0.1", "::1"]:
            return False
        # 解析域名为 IP
        ip = None
        try:
            ip = socket.gethostbyname(hostname)
        except Exception:
            return False
        ip_obj = ipaddress.ip_address(ip)
        if (
            ip_obj.is_private or
            ip_obj.is_loopback or
            ip_obj.is_link_local or
            ip_obj.is_reserved or
            ip_obj.is_multicast
        ):
            return False
        return True
    except Exception:
        return False