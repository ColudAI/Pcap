#!/bin/bash

# 系统检测函数
detect_system() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        case $ID in
            debian|ubuntu) echo "debian";;
            centos|fedora|rhel) echo "rhel";;
            arch) echo "arch";;
            *) echo "unknown";;
        esac
    elif [[ $(uname) == "Darwin" ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# 安装函数
install_packages() {
    case $1 in
        debian)
            sudo apt update && sudo apt install -y python3 python3-pip
            ;;
        rhel)
            if command -v dnf &> /dev/null; then
                sudo dnf install -y python3 python3-pip
            else
                sudo yum install -y python3 python3-pip
            fi
            ;;
        arch)
            sudo pacman -Sy --noconfirm python python-pip
            ;;
        macos)
            if ! command -v brew &> /dev/null; then
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew install python3
            ;;
        *)
            echo "不支持的系统"
            exit 1
            ;;
    esac
}

# 主执行流程
set -euo pipefail

system_type=$(detect_system)
if [[ $system_type == "unknown" ]]; then
    echo "错误：无法识别的操作系统"
    exit 1
fi

echo "检测到系统类型：$system_type"
echo "开始安装Python和pip..."

if ! install_packages $system_type; then
    echo "安装失败，请检查错误信息"
    exit 1
fi

# 验证安装
if ! command -v python3 --version &> /dev/null || ! command -v pip3 --version &> /dev/null; then
    echo "安装验证失败"
    exit 1
fi

echo "安装成功！"