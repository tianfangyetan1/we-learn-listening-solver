import os
import tempfile
import requests
import whisper

def transcribe_audio_from_url(url: str, model=None, model_size: str = "base") -> str:
    """
    从给定 URL 下载音频文件并使用 Whisper 模型将其转换为文本。
    
    :param url: 音频文件的完整 URL
    :param model: 预先加载的 Whisper 模型实例 (可选，建议在外部加载以提高性能)
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
        # 3. 使用传入的 Whisper 模型，或在未传入时加载模型
        if model is None:
            model = whisper.load_model(model_size)
        
        # 4. 执行转录
        # 显式指定 fp16=False 以避免在 CPU 上运行时出现警告
        result = model.transcribe(temp_file_path, fp16=False)
        return result.get("text", "").strip() # type: ignore
        
    finally:
        # 5. 清理临时文件，防止磁盘空间泄漏
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
