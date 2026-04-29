# WeLearn 听力自动答题

本项目是一个基于 Selenium、Whisper 和 DeepSeek 的 WeLearn 听力自动答题辅助工具。它能够自动登录平台，抓取听力音频并转换为文本，然后结合题目和选项通过大语言模型推理出正确答案，并自动完成点击答题。

## 技术架构

- **Web 自动化**：使用 Selenium 控制 Chrome 浏览器，实现自动登录、页面元素解析（题目、选项、音频链接）以及最终的自动点击答题操作。
- **语音识别**：抓取网页中的音频链接，使用 OpenAI Whisper (tiny 模型) 在本地将英语听力音频快速转换为文本。
- **大模型推理**：将 Whisper 转换后的听力文本、解析出的题目和选项构建为 Prompt，调用 DeepSeek API 进行逻辑推理，获取最符合语境的正确答案。

## 环境依赖与安装

### 0. 前置条件

- 安装 [Python 3.14](https://www.python.org/downloads/)
- 安装 [Chrome](https://www.google.cn/intl/zh-CN/chrome/)

### 1. 安装 FFmpeg

OpenAI Whisper 依赖 FFmpeg 来处理音频文件。如果你使用的是 Windows 系统，推荐使用 winget 包管理器进行安装：

```bash
winget install ffmpeg
```

注意：安装完成后，代码中已包含自动将 winget 默认路径加入环境变量的逻辑。如果仍提示找不到 ffmpeg，请手动将 FFmpeg 的 `bin` 目录添加到系统的环境变量 `PATH` 中，并重启终端。

### 2. 安装 Python 依赖

项目需要 Python 3.8+ 环境。请使用以下命令安装所需的 Python 库：

```bash
pip install -r requirements.txt
```

## 配置 ChromeDriver（可选）

> [!NOTE]
> 这一步不是必须的。如果不配置 ChromeDriver，Selenium 会在运行时自动下载对应版本的 ChromeDriver，但是可能需要花费更长的时间才能启动。

1. **检查 Chrome 版本**：打开 Chrome 浏览器，点击右上角菜单 -> 帮助 -> 关于 Google Chrome，查看当前版本号。
2. **下载 ChromeDriver**：前往 [ChromeDriver 官网](https://googlechromelabs.github.io/chrome-for-testing/) 下载与你 Chrome 浏览器版本匹配的驱动程序。
3. **配置路径**：
   - 将下载的 `chromedriver.exe` 解压到本地某个目录（例如：`C:\Tools\ChromeDriver\chromedriver.exe`）。
   - 在 `config.json` 文件中，将 `chromedriver_path` 的值设置为该绝对路径（注意路径需要使用双反斜杠 `\\` 转义或正斜杠 `/`）。

## 配置文件 (`config.json`)

在运行项目前，请在项目根目录创建或修改 `config.json` 文件，填写以下信息：

```json
{
  "api_key": "你的 DeepSeek API Key",
  "model": "deepseek-v4-pro",
  "chromedriver_path": "C:\\Tools\\ChromeDriver\\chromedriver.exe",
  "username": "你的 WeLearn 账号",
  "password": "你的 WeLearn 密码",
  "target_url": "你要答题的 WeLearn 课程主页"
}
```

## 使用步骤

1. 确保已完成上述所有环境配置和依赖安装。
2. 确保 `config.json` 中的信息已正确填写。
3. 运行主程序：
    ```bash
    python main.py
    ```
4. 程序将自动打开 Chrome 浏览器并尝试登录。
5. 登录成功后，**切换到答题界面，然后在控制台点击任意键继续**，确保页面已完全加载到答题界面。
6. 程序将自动解析音频、调用 Whisper 进行语音识别、请求 DeepSeek 获取答案，并自动在网页上点击对应选项。
