# DesktopToolAssistant

## 项目简介
DesktopToolAssistant 是一个集成虚拟角色、语音识别、语音合成、记忆管理和大语言模型的桌面助手。项目支持 Live2D 虚拟形象驱动，具备口型同步、语音交互、个性化记忆和多模型支持。

## 主要功能
- **虚拟角色驱动**：支持 Live2D 模型，角色可根据语音和文本进行动作和表情变化。
- **语音识别**：集成 Whisper 语音识别，支持多说话人识别。
- **语音合成**：支持 ChatTTS 语音生成，自动口型同步。
- **记忆管理**：基于 AmpliGraph，支持知识图谱记忆与个性化角色设定。
- **大语言模型**：支持 OpenAI、Ollama 等多种 LLM，灵活切换。
- **日志系统**：彩色日志输出，支持文件记录。

## 目录结构
```
├── main.py                # 主入口，初始化各组件并运行主循环
├── config.yaml            # 配置文件，角色、模型、参数等
├── lipsync.py             # 口型同步接口
├── audio/                 # 语音生成相关模块
├── display/               # 显示与动作控制
├── LLM/                   # 大语言模型相关模块
├── log/                   # 日志管理
├── memory/                # 记忆管理与知识图谱
├── speechRecognize/       # 语音识别相关模块
├── Characteristic/        # 角色个性与特征
├── Live2DModels/          # Live2D 模型资源
├── requirements.txt       # 依赖包列表
```

## 快速开始

1. **安装依赖**
   python建议版本: 3.12
   ```cmd
   pip install -r requirements.txt
   ```

2. **配置参数**
   编辑 `config.yaml`，设置角色信息、模型参数等。

3. **运行项目**
   ```cmd
   python main.py
   ```

## 主要依赖
- torch, torchvision
- openai, ChatTTS, ollama
- live2d-py
- openai-whisper
- pyAudioAnalysis, pyaudio
- AmpliGraph
- pygame, jinja2, ffmpeg-python 等

## 许可证与素材说明
Live2D 示例模型遵循 Live2D Cubism 官方授权协议，详见 [Live2DModels/hiyori_free_zh/ReadMe.txt](Live2DModels/hiyori_free_zh/ReadMe.txt)。

## 联系与反馈
如有问题或建议，请在 Issues 区留言。