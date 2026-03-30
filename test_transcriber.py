import os
import whisper
from audio_transcriber import transcribe_audio_from_url

# 确保 ffmpeg 所在的路径在环境变量中
winget_links_path = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links")
if winget_links_path not in os.environ.get("PATH", ""):
    os.environ["PATH"] += os.pathsep + winget_links_path

def main():
    # 使用音频url.md中提供的测试URL
    test_url = "https://wetestoss.sflep.com/resource/sound/0afa817b69a64a0b82f662f80e7de777.mp3"
    
    print("正在加载 Whisper 模型 (tiny)...")
    # 提前在外部加载模型
    model = whisper.load_model("tiny")
    
    print(f"正在下载并转换音频: {test_url}")
    
    try:
        # 传入已加载的模型
        text = transcribe_audio_from_url(test_url, model=model)
        print("\n--- 转换结果 ---")
        print(text)
        print("----------------")
    except Exception as e:
        print(f"\n转换过程中发生错误: {e}")

if __name__ == "__main__":
    main()
