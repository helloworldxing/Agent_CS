# Agent-Pr

项目快速说明与启动指南。

## 简介
这是一个基于 Streamlit 的聊天 Agent 项目，支持语音输入（本地 Whisper 或远端 ASR）和向量检索（Chroma）。

## 环境准备
建议在虚拟环境中运行：

```bash
python -m venv .venv
source .venv/bin/activate    # macOS / Linux
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
# 或 .\.venv\Scripts\activate.bat  # Windows cmd
```

安装依赖：

```bash
pip install -r requirements.txt
pip install -r dev-requirements.txt  # 可选：开发工具
```

> Windows 注意：项目使用 `imageio-ffmpeg` 提供的 ffmpeg 二进制以兼容 Whisper/ffmpeg 调用，如果系统已有 `ffmpeg`，也可使用。若遇到 `ffmpeg` 找不到错误，请安装 `imageio-ffmpeg` 并确保 Python 环境可见。

## 配置
将敏感配置（例如 `DASHSCOPE_API_KEY`）放入环境变量或 `.env`，不要提交到仓库。示例：

```bash
export DASHSCOPE_API_KEY="your_key_here"   # macOS / Linux
setx DASHSCOPE_API_KEY "your_key_here"    # Windows (持久)
```

## 快速运行
主界面（聊天 Agent）:

```bash
streamlit run app.py
```

测试语音输入页面（开发用）:

```bash
streamlit run tests/record_test.py
```

## 开发与测试
- 运行单元/集成测试：`pytest`
- 格式化代码：`black .`
- 代码检查：`flake8`

## 常见问题
- 如果在 Windows 下遇到 `StreamlitAPIException`，通常是因为尝试在 widget 创建后修改 `st.session_state` 的键，确保把 `session_state` 的 pending 值在创建输入 widget 之前写入。
- 如果 Whisper 报错找不到 `ffmpeg`，请先安装 `imageio-ffmpeg`，或在系统路径中安装 `ffmpeg`。

如果你希望我把 README 扩展为部署文档或加入 Docker、CI 配置，我可以继续实现。
