# Good-GYM: AI健身助手 💪

<div align="center">

<img src="assets/Logo-ch.png" width="200px" alt="Good-GYM 标志">

[![GitHub stars](https://img.shields.io/github/stars/yo-WASSUP/Good-GYM?style=social)](https://github.com/yo-WASSUP/Good-GYM/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/yo-WASSUP/Good-GYM?style=social)](https://github.com/yo-WASSUP/Good-GYM/network/members)
[![GitHub license](https://img.shields.io/github/license/yo-WASSUP/Good-GYM)](https://github.com/yo-WASSUP/Good-GYM/blob/main/LICENSE)

**基于YOLOv11姿态检测的AI健身助手**

[English](README.md) | [中文](README_CN.md)

[![小红书视频介绍](https://img.shields.io/badge/小红书-视频介绍-ff2442)](https://www.xiaohongshu.com/explore/6808b102000000001c0157ad?xsec_token=ABm-Sdk88be4nJCaCVfCI9gQahnLiKt16mUC3gbupYH3g=&xsec_source=pc_user)

</div>

---
<img src="assets/demo.gif" width="600px" alt="演示">

## ✨ 功能特点

- **实时运动计数** - 自动计算您的健身次数
- **多种运动支持** - 包括深蹲、俯卧撑、仰卧起坐、哑铃运动等十多种
- **先进的姿态检测** - 采用YOLOv11实现精准跟踪
- **可视化反馈** - 实时骨骼可视化和角度测量
- **健身统计** - 跟踪您的健身进度
- **用户友好界面** - 基于PyQt5的简洁界面，操作直观
- **兼容普通摄像头** - 无需特殊硬件
- **本地运行** -完全隐私

## 📋 系统要求

- Python 3.7+
- 摄像头
- 推荐使用GPU以获得更好性能(但CPU也可运行)

## 📦 快速下载

- 如果您不想配置Python环境，可以直接下载我们打包好的可执行文件：

  **Windows EXE打包版本**：[百度网盘链接](https://pan.baidu.com/s/your_shared_link) 提取码：xxxx

## 🚀 快速安装

1. **克隆仓库**
   ```bash
   git clone https://github.com/yo-WASSUP/Good-GYM.git
   cd Good-GYM
   ```

2. **创建并激活虚拟环境**
   ```bash
   # Windows系统
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/MacOS系统
   python -m venv venv
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **运行应用**
   ```bash
   python workout_qt_modular.py
   ```

## 🔧 高级安装指南

### GPU版本安装（推荐）

1. **确保您的系统满足要求**
   - NVIDIA GPU卡（建议4GB以上显存）
   - 已安装最新NVIDIA驱动

2. **安装CUDA和cuDNN**
   - 下载并安装[CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)
   - 下载并安装[cuDNN](https://developer.nvidia.com/cudnn)

3. **克隆并安装**
   ```bash
   git clone https://github.com/yo-WASSUP/Good-GYM.git
   cd Good-GYM
   
   # 创建虚拟环境
   python -m venv venv
   # Windows激活环境
   .\venv\Scripts\activate
   # Linux/MacOS激活环境
   source venv/bin/activate
   
   # 安装GPU版PyTorch
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   
   # 安装其他依赖
   pip install -r requirements.txt
   ```

4. **验证GPU可用性**
   ```bash
   python -c "import torch; print('GPU可用:',torch.cuda.is_available())"
   ```

5. **运行应用**
   ```bash
   python workout_qt_modular.py
   ```

6. **创建可执行文件**
   ```powershell
   
   # 或创建可执行文件
   .\build_executable.bat
   ```

### Linux/MacOS安装

1. **安装依赖**
   ```bash
   # Ubuntu/Debian系统
   sudo apt-get update
   sudo apt-get install python-pip python-dev python-opencv
   
   # MacOS系统
   brew install python
   ```

2. **克隆并安装**
   ```bash
   git clone https://github.com/yo-WASSUP/Good-GYM.git
   cd Good-GYM
   
   # 创建虚拟环境
   python -m venv venv
   source venv/bin/activate
   
   # 安装依赖
   pip install -r requirements.txt
   ```

3. **运行应用**
   ```bash
   python workout_qt_modular.py
   ```

## 📝 使用指南

### 控制方式

- 使用界面按钮选择不同的运动类型
- 实时反馈显示您当前的姿势和重复次数
- 按"重置"按钮重置计数器
- 使用手动调整按钮修正计数(如有需要)
- 开关骨骼可视化
- 查看您的健身统计数据

## 🖼️ 应用截图

<img src="assets/Screenshot-ch-1.png" width="600px" alt="截图1">

<img src="assets/Screenshot-ch-2.png" width="600px" alt="截图2">

<img src="assets/Screenshot-ch-3.png" width="600px" alt="截图3">

<img src="assets/Screenshot-ch-4.png" width="600px" alt="截图4">

<img src="assets/Screenshot-ch-5.png" width="600px" alt="截图5">

## 🤝 贡献

欢迎贡献代码！请随时提交Pull Request。

## 📄 许可证

本项目采用MIT许可证 - 详情请参阅LICENSE文件。

## 🔮 开发计划

- [ ] 添加更多运动类型支持
- [ ] 改进姿态检测精度
- [ ] 添加语音反馈
- [ ] 移动应用支持