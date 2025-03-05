# 📸Pcap
网页截图获取工具API
<div align="center">
 <img src="https://raw.githubusercontent.com/ColudAI/ColudAI-SAI-L6/refs/heads/main/%E5%AE%B9%E5%99%A8%201%401x%20(7).png" width="50%" alt="ColludAI " />
</div>
<hr>
这是一个基于 FastAPI 和 Playwright 的网页截图 API，支持高并发访问并优化了性能。

## 功能特性

- 支持跨域访问
- 高性能，支持高并发
- 自动验证 URL 合法性
- 返回 PNG 格式的截图

## 安装依赖

### 1. 安装 Python 依赖

确保已安装 Python 3.7+，然后运行以下命令：

```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate
```
# 安装 Python 包
```
pip install fastapi uvicorn playwright
```
## 未来工作
### 这是我们的开源周的第一个产品，它不支持网页操作，但是后续会更新
*   实施验证和测试
*   实现思考链模型的结合等....
