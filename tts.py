import requests

def text_to_speech(text, character='default', stream=False):
    """将文本转换为语音"""
    url = f"http://127.0.0.1:5000/tts?character={character}&text={text}&format=wav"
    if stream:
        url += "&stream=true"
    response = requests.get(url)

    if response.status_code == 200:
        audio_path = "tts_audio/output.wav"
        with open(audio_path, "wb") as f:
            f.write(response.content)
        print("音频文件已生成: output.wav")
        return audio_path
    else:
        print(f"请求失败，状态码: {response.status_code}")
        try:
            print(response.json())
        except requests.exceptions.JSONDecodeError:
            print("响应内容无法解析为JSON:")
            print(response.text)
        return None



