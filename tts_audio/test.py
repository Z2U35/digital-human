import logging

from pydub import AudioSegment
from pydub.playback import play

def check_audio_file(audio_path):
    try:
        audio = AudioSegment.from_file(audio_path)
        if len(audio) == 0:
            logging.error("Audio file is empty")
        else:
            logging.debug(f"Audio file duration: {len(audio)} milliseconds")
            play(audio)  # 播放音频以确认内容
    except Exception as e:
        logging.error(f"Error while checking audio file: {e}")

# 调用生成音频文件后检查
audio_path = 'c7caf5c2d06f426b9a8b5a4d8fe43fe6.wav'
check_audio_file(audio_path)
