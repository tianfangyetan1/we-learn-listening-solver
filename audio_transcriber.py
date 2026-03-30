import os
import tempfile
import requests
import whisper

# 确保 ffmpeg 所在的路径在环境变量中
winget_links_path = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links")
if winget_links_path not in os.environ.get("PATH", ""):
    os.environ["PATH"] += os.pathsep + winget_links_path

def transcribe_audio_from_url(url: str, model_size: str = "base") -> str:
    """
    从给定 URL 下载音频文件并使用 Whisper 模型将其转换为文本。
    
    :param url: 音频文件的完整 URL
    :param model_size: Whisper 模型大小 (可选: 'tiny', 'base', 'small', 'medium', 'large')
    :return: 转换后的文本字符串
    """
    # 1. 下载音频文件
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    # 尝试从 URL 获取扩展名，若无则默认使用 .tmp
    ext = os.path.splitext(url)[1]
    if not ext or len(ext) > 5:
        ext = ".tmp"
        
    # 2. 将音频保存到当前目录下的 temp 文件夹
    temp_dir = os.path.join(os.getcwd(), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    with tempfile.NamedTemporaryFile(dir=temp_dir, delete=False, suffix=ext) as temp_file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                temp_file.write(chunk)
        temp_file_path = temp_file.name

    try:
        # 3. 加载 Whisper 模型 (如果需要频繁调用，建议将模型加载提取到函数外部以提高性能)
        model = whisper.load_model(model_size)
        
        # 4. 执行转录
        result = model.transcribe(temp_file_path)
        return result.get("text", "").strip()
        
    finally:
        # 5. 清理临时文件，防止磁盘空间泄漏
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
