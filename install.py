# 自动安装依赖文件中的依赖并配置
import subprocess
import sys

def install_dependencies():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("依赖已安装。")
    except subprocess.CalledProcessError:
        print("安装依赖时发生错误。")

def configure():
    # 在这里添加配置代码
    try:
        print("正在安装浏览器驱动(PlayWright环境[Chromium, Microsoft Edge, WebKit等])...")
        subprocess.check_call(["playwright", "install"])
        subprocess.check_call(["playwright", "install", "chromium"])
    except subprocess.CalledProcessError:
        print("安装浏览器驱动时发生错误。")
    finally:
        print("配置完成。")

def run():
    install_dependencies()
    configure()

if __name__ == "__main__":
    run()