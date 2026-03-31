import os
import json
import time
import re
import requests
import whisper
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from audio_transcriber import transcribe_audio_from_url

# 确保 ffmpeg 所在的路径在环境变量中
winget_links_path = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links")
if winget_links_path not in os.environ.get("PATH", ""):
    os.environ["PATH"] += os.pathsep + winget_links_path

def load_config():
    config_path = "config.json"
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件 {config_path} 不存在，请创建并填写相关信息。")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_deepseek_answer(api_key, model, prompt):
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一个英语听力答题助手。请直接输出正确选项的字母，不要输出其他任何内容。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0
    }
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    
    content = result["choices"][0]["message"]["content"].strip()
    
    # 提取最后一个有效字母 [A-D]
    matches = re.findall(r'[A-Da-d]', content)
    if matches:
        return matches[-1].upper()
    return None

def main():
    # 1. 读取配置文件
    config = load_config()
    api_key = config.get("api_key")
    model_name = config.get("model", "deepseek-chat")
    chromedriver_path = config.get("chromedriver_path")
    username = config.get("username")
    password = config.get("password")
    target_url = config.get("target_url")
    
    if not all([api_key, username, password, target_url]):
        print("请确保 config.json 中包含 api_key, username, password, target_url")
        return

    # 2. 浏览器初始化
    # 如果 chromedriver_path 为空，则使用 webdriver_manager 自动管理
    if chromedriver_path:
        service = Service(executable_path=chromedriver_path)
        driver = Chrome(service=service)
    else:
        # 尝试使用 selenium 4.6+ 内置的自动驱动管理
        driver = Chrome()
    
    driver.get(target_url)
    
    # 3. 自动登录
    try:
        print("正在尝试自动登录...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        
        username_input = driver.find_element(By.ID, "username")
        username_input.clear()
        username_input.send_keys(username)
        
        password_input = driver.find_element(By.ID, "password")
        password_input.clear()
        password_input.send_keys(password)
        
        login_btn = driver.find_element(By.ID, "login")
        login_btn.click()
        
        print("登录操作已执行。")
    except Exception as e:
        print(f"自动登录失败或未找到登录元素: {e}")
    
    
    # 4. 等待页面就绪
    print("请进入答题界面，然后继续")
    os.system("pause")
    
    print("正在加载 Whisper 模型 (tiny)...")
    whisper_model = whisper.load_model("tiny")
    
    # 5. 遍历题目结构
    print("开始解析页面题目...")
    item_divs = driver.find_elements(By.CLASS_NAME, "itemDiv")
    
    passage_cache = {}
    
    for item_idx, item_div in enumerate(item_divs):
        print(f"\n--- 处理第 {item_idx + 1} 个篇章 ---")
        
        # 提取篇章音频
        passage_text = ""
        # 查找 itemDiv 下所有的 a 标签，但不属于 test_hov 的
        # 简单方法：查找所有 a 标签，过滤掉祖先包含 test_hov 的
        play_links = item_div.find_elements(By.XPATH, ".//a[contains(@href, 'PlaySound')]")
        
        passage_audio_url = None
        for link in play_links:
            # 检查是否在 test_hov 内部
            try:
                # 如果这个链接的父级或祖先有 test_hov，则说明是小题的音频
                link.find_element(By.XPATH, "ancestor::div[contains(@class, 'test_hov')]")
                # 是小题音频，跳过
            except:
                # 不是小题音频，说明是篇章音频
                href = link.get_attribute("href")
                match = re.search(r'PlaySound\("([^"]+)"', href)
                if match:
                    filename = match.group(1)
                    passage_audio_url = f"https://wetestoss.sflep.com/resource/sound/{filename}"
                    break
        
        if passage_audio_url:
            if passage_audio_url in passage_cache:
                passage_text = passage_cache[passage_audio_url]
                print("使用缓存的篇章听力文本。")
            else:
                print(f"正在下载并转换篇章音频: {passage_audio_url}")
                try:
                    passage_text = transcribe_audio_from_url(passage_audio_url, model=whisper_model)
                    passage_cache[passage_audio_url] = passage_text
                    print(f"篇章文本: {passage_text}")
                except Exception as e:
                    print(f"转换篇章音频失败: {e}")
        else:
            print("未找到篇章音频。")
            
        # 遍历小题
        test_hovs = item_div.find_elements(By.CLASS_NAME, "test_hov")
        for q_idx, test_hov in enumerate(test_hovs):
            print(f"\n  处理小题 {q_idx + 1}")
            
            # 提取小题音频
            question_text = ""
            q_play_links = test_hov.find_elements(By.XPATH, ".//a[contains(@href, 'PlaySound')]")
            if q_play_links:
                href = q_play_links[0].get_attribute("href")
                match = re.search(r'PlaySound\("([^"]+)"', href)
                if match:
                    filename = match.group(1)
                    q_audio_url = f"https://wetestoss.sflep.com/resource/sound/{filename}"
                    print(f"  下载并转换小题音频: {q_audio_url}")
                    try:
                        question_text = transcribe_audio_from_url(q_audio_url, model=whisper_model)
                        print(f"  小题文本: {question_text}")
                    except Exception as e:
                        print(f"  转换小题音频失败: {e}")
            
            # 提取选项
            options = []
            option_elements = test_hov.find_elements(By.XPATH, ".//div[contains(@class, 'choiceList')]//label")
            for opt_elem in option_elements:
                options.append(opt_elem.text.strip())
            
            options_text = "\n".join(options)
            print(f"  选项:\n{options_text}")
            
            # 构造 Prompt
            prompt = f"听力篇章文本：\n{passage_text}\n\n听力问题文本：\n{question_text}\n\n选项：\n{options_text}\n\n请根据听力内容选择最合适的选项。直接输出选项字母（如 A、B、C 或 D）。"
            
            # 请求 DeepSeek API
            print("  正在请求 DeepSeek API...")
            try:
                answer = get_deepseek_answer(api_key, model_name, prompt)
                print(f"  DeepSeek 返回答案: {answer}")
                
                if answer:
                    # 自动点击对应选项
                    # 查找对应的 input radio
                    # 选项文本一般是 "A) ..."，我们可以根据首字母匹配
                    for opt_elem in option_elements:
                        text = opt_elem.text.strip()
                        if text.startswith(f"{answer})") or text.startswith(f"{answer}."):
                            radio_input = opt_elem.find_element(By.XPATH, ".//input[@type='radio']")
                            driver.execute_script("arguments[0].click();", radio_input)
                            print(f"  已自动点击选项: {answer}")
                            break
            except Exception as e:
                print(f"  请求 DeepSeek 或点击选项失败: {e}")

    print("\n所有题目处理完毕。")
    os.system("pause")
    driver.quit()

if __name__ == "__main__":
    main()
