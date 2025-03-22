# 自动安装依赖文件中的依赖并配置
import subprocess
import sys
from rich.console import Console
from rich.progress import Progress

def install_dependencies():
    with Progress() as progress:
        task = progress.add_task("[cyan]安装依赖...", total=1)
        console = Console()
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                                capture_output=True, text=True)
            console.print(f'[bold green]\n{result.stdout}')
            print("依赖已安装。")
        except subprocess.CalledProcessError:
            console.print("[bold red]安装依赖时发生错误。")

def configure():
    console = Console()
    try:
        console.print("正在安装浏览器驱动(PlayWright环境[Chromium, Microsoft Edge, WebKit等])...")
        subprocess.check_call(["playwright", "install"])
        subprocess.check_call(["playwright", "install", "chromium"])
    except subprocess.CalledProcessError:
        console.print("[bold red]安装浏览器驱动时发生错误。")
    finally:
        console.print("[bold green]✓ 配置完成")

def run():
    install_dependencies()
    configure()

if __name__ == "__main__":
    run()