# 📸 Pcap

<p align="center">
  <a href="https://raw.githubusercontent.com/ColudAI/Pcap/LICENSE">
    <img src="https://img.shields.io/github/license/ColudAI/Pcap" alt="license">
  </a>
  <img src="https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=edb641" alt="python">
    <a href="https://github.com/ColudAI/Pcap/actions/workflows/auto-package.yml">
  </a>
</p>

一个基于 FastAPI 的智能网页操作和截图服务，为大语言模型提供强大的网页交互和数据采集能力。

![Pcap](https://github.com/user-attachments/assets/0404e841-7be7-4303-924c-95e9692e7074)

## ✨ 主要特性

- 🌐 支持跨域访问和高并发处理
- 🔍 智能网页操作和元素定位
- 📸 高质量页面截图功能
  - 支持完整页面截图
  - 支持元素点击后截图
  - 支持页面滚动后截图
- 🛡️ 内置 URL 安全性验证
- 🖼️ 优化的图片处理
  - 自动输出 PNG 格式
  - 智能图片压缩
- 🚀 高性能设计
  - 异步处理机制
  - 内存优化管理

## 🛠️ 技术栈

- FastAPI
- Python 3.10+
- Nuitka（用于打包）
- GitHub Actions（CI/CD）

## 📦 安装说明

### 环境要求

- Python 3.10 或更高版本
- pip 包管理器
- 支持 Windows/Linux/macOS 系统

### 方式一：直接下载发行版

访问 [Releases](https://github.com/ColudAI/Pcap/releases) 页面，下载对应平台的可执行文件：

- Windows: `main.exe`
- Linux: `main.bin`
- macOS: `Pcap.app.zip`

### 方式二：从源码安装

1. 克隆仓库
```bash
git clone https://github.com/ColudAI/Pcap.git
cd Pcap
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行程序
```bash
python main.py
```

## 🚀 使用方法

1. 启动服务后，访问 `http://localhost:8000/docs` 查看 API 文档
2. API 端点说明：
   - `/screenshot`: 获取网页截图
   - `/click`: 点击元素后截图
   - `/scroll`: 滚动页面后截图

## 🔧 配置说明

主要配置项在 `config` 目录下(由于打包问题所以不会提供配置文件，有需求请自行下载)：

- 服务器配置
- 截图参数设置
- 缓存策略
- 日志级别

## 📝 开发说明

本项目使用 GitHub Actions 进行自动化构建和发布：

- 自动版本管理
- 多平台构建支持
- 自动发布流程

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

[许可证类型]

---

## 🔗 相关链接

- [项目文档](#)
- [问题反馈](https://github.com/ColudAI/Pcap/issues)
- [更新日志](https://github.com/ColudAI/Pcap/commits)
