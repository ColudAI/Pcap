from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Functions import ipManage
from Functions.routes import router

app = FastAPI()

# 获取IP地址
ip_list = ipManage.get_ip_address()
for i in ip_list:
    print(f"App is running at http://{i}:8000/  ...")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)