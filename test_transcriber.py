from audio_transcriber import transcribe_audio_from_url

def main():
    # 使用音频url.md中提供的测试URL
    test_url = "https://wetestoss.sflep.com/resource/sound/0afa817b69a64a0b82f662f80e7de777.mp3"
    
    print(f"正在下载并转换音频: {test_url}")
    print("这可能需要一些时间，因为需要下载音频并加载Whisper模型...")
    
    try:
        # 使用 tiny 模型以加快测试速度
        text = transcribe_audio_from_url(test_url, model_size="tiny")
        print("\n--- 转换结果 ---")
        print(text)
        print("----------------")
    except Exception as e:
        print(f"\n转换过程中发生错误: {e}")

if __name__ == "__main__":
    main()
