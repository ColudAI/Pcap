from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Functions import ipManage
from Functions.routes import router
from Functions.logger import logger
from config import APP_CONFIG
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("应用启动")
    yield
    logger.info("应用关闭")

app = FastAPI(
    title="网页截图服务",
    description="提供网页截图、点击后截图和滚动后截图功能",
    version="1.0.0",
    lifespan=lifespan
)

# 获取IP地址
ip_list = ipManage.get_ip_address()
for i in ip_list:
    logger.info(f"应用运行在 http://{i}:{APP_CONFIG['PORT']}/")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)


# 取消不受到支持的启动和关闭事件
"""@app.on_event("startup")
async def startup_event():
    logger.info("应用启动")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("应用关闭")"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=APP_CONFIG["HOST"],
        port=APP_CONFIG["PORT"],
        log_level="info"
    )