# AI-Pet-Assistant
# AI智能桌宠 - 池年

一个基于PyQt5和智谱AI大模型的桌面智能助手，可以聊天、执行电脑操作、有情绪变化。

## 功能

- 💬 **AI聊天**：调用智谱AI GLM-4-Flash模型，支持多轮对话
- 🤖 **智能操作**：集成AutoClaw，让AI帮你操作电脑（如：在桌面新建文件夹、打开浏览器）
- 😊 **情绪系统**：根据对话内容自动改变情绪（开心/难过/生气/期待），情绪值实时显示
- 🖱️ **桌宠交互**：鼠标拖动、点击摸头、睡觉、重置情绪

## 如何运行

1. 安装依赖：`pip install PyQt5 requests`
2. 申请智谱AI API密钥：https://open.bigmodel.cn/
3. 安装AutoClaw（可选，用于智能操作功能）
4. 在代码中填入你的API密钥
5. 运行：`python smart_pet.py`

## 技术栈

- Python 3.8+
- PyQt5（桌面应用框架）
- 智谱AI API（大语言模型）
- AutoClaw（AI操作电脑工具）

## 备注

- 有喜欢的素材可自行替换
- 智能操作功能需要单独安装AutoClaw客户端
