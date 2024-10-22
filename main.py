import time
import logging
import os
import vlc  # 导入 VLC 库，用于音频播放
import sys
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QLocale, QTimer, QEvent
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QFileDialog,
                             QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout,
                             QSizePolicy)
from PyQt5.QtGui import QPixmap
from qfluentwidgets import FluentTranslator

# 导入自定义模块
import pyqt_interface.Dormancy_window
from pyqt_interface.main_window import Ui_MainWindow
from pyqt_interface.CustomMessageBox import CustomMessageBox
from question_answering import get_response_from_llm
from tts import text_to_speech
from vosk_asr.asr import RealTimeASR

logging.basicConfig(level=logging.DEBUG)


class ASRWorker(QThread):
    transcribed_text = pyqtSignal(str)

    def __init__(self, asr):
        super().__init__()
        self.asr = asr
        self.running = True
        self.paused = False  # 添加暂停标志

    def run(self):
        while self.running:
            if not self.paused:
                try:
                    text = self.asr.listen_and_recognize()
                    if text:
                        self.transcribed_text.emit(text)
                except Exception as e:
                    logging.error(f"ASR Worker Error: {e}. Reinitializing ASR.")
                    try:
                        self.asr = RealTimeASR("vosk_asr/vosk-model-cn-0.22")
                    except Exception as e:
                        logging.error(f"Failed to reinitialize ASR: {e}")
            else:
                time.sleep(0.1)  # 暂停时稍作休眠


class LLMThread(QThread):
    response_ready = pyqtSignal(str)

    def __init__(self, question):
        super().__init__()
        self.question = question

    def run(self):
        try:
            response = get_response_from_llm(self.question)
            self.response_ready.emit(response)
        except Exception as e:
            logging.error(f"LLM Thread Error: {e}")
            self.response_ready.emit(f"Error: {e}")


class TTSWorker(QThread):
    tts_finished = pyqtSignal(str)  # TTS 完成信号，传递音频文件路径

    def __init__(self, text, character):
        super().__init__()
        self.text = text
        self.character = character

    def run(self):
        try:
            audio_path = text_to_speech(self.text, character=self.character)
            self.tts_finished.emit(audio_path)
        except Exception as e:
            logging.error(f"TTS Worker Error: {e}")
            self.tts_finished.emit("")


class MainWindow(QMainWindow):
    playback_finished = pyqtSignal()  # 播放完成信号

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.last_interaction_time = time.time()
        self.dormancy_window = None  # 用于追踪休眠窗口是否存在

        self.setupTimer()

        # 初始化头像路径
        self.you_avatar_path = 'avatars/you.png'
        self.xiaoji_avatar_path = 'avatars/jmu.png'

        # 初始化 ASR 模块
        self.asr = RealTimeASR("vosk_asr/vosk-model-small-cn-0.22")

        # 默认音频路径
        self.default_audio_path = os.path.join('tts_audio', 'output.wav')

        # 初始化预定义音色
        self.predefined_voices = ['胡桃', '云溪', '晓晓', '静静']

        # 设置默认音色
        self.selected_voice = '胡桃'  # 默认音色

        # 连接按钮和槽函数
        self.ui.ToolButton.clicked.connect(self.handleASR)
        self.ui.PushButton_2.clicked.connect(self.createNewVoice)
        self.ui.comboBox_2.currentIndexChanged.connect(self.selectVoice)

        # 连接“打断”按钮
        self.ui.interruptButton.clicked.connect(self.interruptProcess)

        # 初始化 VLC，用于音频播放
        self.vlc_instance = vlc.Instance()
        self.vlc_player = self.vlc_instance.media_player_new()
        self.playback_finished.connect(self.onPlaybackFinished)

        # 开始实时识别
        self.start_real_time_recognition()

    def setupTimer(self):
        # 设置休眠时间
        self.inactivity_timer = QTimer()
        self.inactivity_timer.setInterval(100000)  # 100秒
        self.inactivity_timer.timeout.connect(self.showDormancyWindow)
        self.inactivity_timer.start()
        self.last_interaction_time = time.time()

    def showDormancyWindow(self):
        # 显示休眠窗口
        current_time = time.time()
        if current_time - self.last_interaction_time > 30:
            if self.dormancy_window is None or not self.dormancy_window.isVisible():
                self.dormancy_window = pyqt_interface.Dormancy_window.LoginWindow()
                self.dormancy_window.show()

    def eventFilter(self, obj, event):
        # 更新最后交互时间
        if event.type() in [QEvent.MouseButtonPress, QEvent.KeyPress]:
            self.last_interaction_time = time.time()
        return super().eventFilter(obj, event)

    def start_real_time_recognition(self):
        try:
            # 如果 ASRWorker 线程未运行，启动线程
            if not hasattr(self, 'asr_worker'):
                self.asr_worker = ASRWorker(self.asr)
                self.asr_worker.transcribed_text.connect(self.onTranscribedText)
                self.asr_worker.start()
                logging.info("ASRWorker thread has been started.")
            else:
                # 恢复 ASRWorker，如果已暂停
                self.asr_worker.paused = False
                logging.info("ASRWorker has been resumed.")
        except Exception as e:
            self.showError(f"ASR 初始化错误: {e}")
            logging.error(f"ASR 初始化错误: {e}")

    def handleASR(self):
        self.addMessage('System', "正在监听...")
        try:
            self.asr_worker.paused = False
        except Exception as e:
            self.showError(f"ASR 处理错误: {e}")
            logging.error(f"ASR 处理错误: {e}")

    def onTranscribedText(self, text):
        # 暂停 ASRWorker
        if hasattr(self, 'asr_worker'):
            self.asr_worker.paused = True
            logging.info("ASRWorker has been paused after transcription.")

        # 移除中文字符之间的空格
        text = text.replace(' ', '')
        self.addMessage('You', text)
        self.askQuestion(text)

    def askQuestion(self, question):
        try:
            self.llm_thread = LLMThread(question)
            self.llm_thread.response_ready.connect(self.onLLMResponse)
            self.llm_thread.start()
        except Exception as e:
            self.showError(f"LLM 处理错误: {e}")
            logging.error(f"LLM 处理错误: {e}")

    def onLLMResponse(self, response):
        self.addMessage('XiaoJi', response)
        try:
            # 使用当前选择的音色，启动 TTSWorker
            self.tts_worker = TTSWorker(response, self.selected_voice)
            self.tts_worker.tts_finished.connect(self.onTTSFinished)
            self.tts_worker.start()
        except Exception as e:
            self.showError(f"TTS 处理错误: {e}")
            logging.error(f"TTS 处理错误: {e}")

    def onTTSFinished(self, audio_path):
        if audio_path:
            self.play_audio_with_vlc(audio_path)
        else:
            self.showError("TTS 未能生成音频。")

    def play_audio_with_vlc(self, audio_path, audio_output_device='mmdevice'):
        """
        使用 VLC 播放音频
        """
        try:
            # 确保在播放前暂停 ASRWorker
            if hasattr(self, 'asr_worker'):
                self.asr_worker.paused = True
                logging.info("ASRWorker has been paused before playback.")

            # 如果 VLC 正在播放，停止播放
            if self.vlc_player.is_playing():
                logging.debug("VLC 正在播放，停止播放...")
                self.vlc_player.stop()
                self.vlc_player.set_media(None)

            # 创建新的媒体并加载到播放器
            media = self.vlc_instance.media_new(audio_path)
            self.vlc_player.set_media(media)

            # 设置音频输出设备
            if self.vlc_player.audio_output_device_enum():
                self.vlc_player.audio_output_set(audio_output_device.encode('utf-8'))
                print(f"使用音频设备: {audio_output_device}")
            else:
                print("无法枚举或设置音频输出设备")

            # 开始播放
            self.vlc_player.play()

            # 设置事件管理器，检测播放完成
            event_manager = self.vlc_player.event_manager()
            event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.vlc_callback)

        except Exception as e:
            self.showError(f"播放音频时出错: {str(e)}")
            logging.error(f"播放音频时出错: {e}")

    def vlc_callback(self, event):
        self.playback_finished.emit()

    def onPlaybackFinished(self):
        logging.info("Playback finished.")
        # 恢复 ASRWorker
        if hasattr(self, 'asr_worker'):
            self.asr_worker.paused = False
            logging.info("ASRWorker has been resumed.")

    def selectVoice(self):
        selected_voice = self.ui.comboBox_2.currentText()
        if selected_voice:
            self.selected_voice = selected_voice
            self.addMessage('System', f"已切换到音色：{selected_voice}")
        else:
            self.selected_voice = '胡桃'  # 默认音色

    def createNewVoice(self):
        try:
            text, ok = CustomMessageBox.getText(self, "新语音", "输入文字", "")
            if ok and text:
                self.addMessage('System', f"生成新语音: {text}")
                # 使用当前选择的音色，启动 TTSWorker
                self.tts_worker = TTSWorker(text, self.selected_voice)
                self.tts_worker.tts_finished.connect(self.onTTSFinished)
                self.tts_worker.start()
        except Exception as e:
            self.showError(f"创建新语音时出错: {str(e)}")
            logging.error(f"创建新语音时出错: {e}")

    def showError(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText(message)
        msg_box.setWindowTitle("错误")
        msg_box.exec_()

    def interruptProcess(self):
        # 暂停 ASRWorker
        if hasattr(self, 'asr_worker'):
            self.asr_worker.paused = True
            logging.info("ASRWorker has been paused.")

        # 停止 LLMThread 线程
        if hasattr(self, 'llm_thread') and self.llm_thread.isRunning():
            self.llm_thread.terminate()
            self.llm_thread.wait()
            logging.info("LLMThread thread has been stopped.")

        # 停止 TTSWorker 线程
        if hasattr(self, 'tts_worker') and self.tts_worker.isRunning():
            self.tts_worker.terminate()
            self.tts_worker.wait()
            logging.info("TTSWorker thread has been stopped.")

        # 停止 VLC 播放器
        if self.vlc_player.is_playing():
            self.vlc_player.stop()
            logging.info("VLC player has been stopped.")

        # 清理界面上的显示信息
        self.addMessage('System', "已打断当前操作，请重新输入语音。")

        # 恢复 ASRWorker
        if hasattr(self, 'asr_worker'):
            self.asr_worker.paused = False
            logging.info("ASRWorker has been resumed.")

    def addMessage(self, sender, message):
        # 创建消息容器
        message_widget = QWidget()
        message_layout = QHBoxLayout()
        message_widget.setLayout(message_layout)

        # 创建头像标签
        avatar_label = QLabel()
        avatar_label.setFixedSize(40, 40)  # 设置头像尺寸

        # 加载头像图片
        if sender == 'You':
            avatar_pixmap = QPixmap(self.you_avatar_path).scaled(
                40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            avatar_label.setPixmap(avatar_pixmap)
        elif sender == 'XiaoJi':
            avatar_pixmap = QPixmap(self.xiaoji_avatar_path).scaled(
                40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            avatar_label.setPixmap(avatar_pixmap)

        # 创建消息文本
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        # 设置最大宽度，防止气泡过长
        message_label.setMaximumWidth(400)
        message_label.setStyleSheet("padding: 10px; border-radius: 10px;")

        if sender == 'You':
            # 右侧对齐，绿色背景，头像在右
            message_label.setStyleSheet("""
                background-color: #DCF8C6;
                padding: 10px;
                border-radius: 10px;
                font-size: 14px;
                color: #000000;
            """)
            # 添加外部布局，控制消息的对齐和间距
            inner_layout = QHBoxLayout()
            inner_layout.addStretch()
            inner_layout.addWidget(message_label)
            inner_layout.addWidget(avatar_label)
            message_layout.addLayout(inner_layout)
        elif sender == 'XiaoJi':
            # 左侧对齐，白色背景，头像在左
            message_label.setStyleSheet("""
                background-color: #FFFFFF;
                padding: 10px;
                border-radius: 10px;
                font-size: 14px;
                color: #000000;
            """)
            # 添加外部布局，控制消息的对齐和间距
            inner_layout = QHBoxLayout()
            inner_layout.addWidget(avatar_label)
            inner_layout.addWidget(message_label)
            inner_layout.addStretch()
            message_layout.addLayout(inner_layout)
        else:
            # 系统消息，居中显示
            message_label.setAlignment(Qt.AlignCenter)
            message_label.setStyleSheet("""
                background-color: #E0E0E0;
                padding: 10px;
                border-radius: 10px;
                font-size: 12px;
                color: #555555;
            """)
            message_layout.addStretch()
            message_layout.addWidget(message_label)
            message_layout.addStretch()

        # 设置外部布局，增加一些边距，防止内容被遮挡
        outer_layout = QHBoxLayout()
        outer_layout.addWidget(message_widget)
        outer_layout.setContentsMargins(10, 5, 10, 5)  # 左上右下边距
        container_widget = QWidget()
        container_widget.setLayout(outer_layout)

        self.ui.chatLayout.addWidget(container_widget)
        # 自动滚动到最底部
        self.ui.chatScrollArea.verticalScrollBar().setValue(
            self.ui.chatScrollArea.verticalScrollBar().maximum())


if __name__ == '__main__':
    try:
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

        app = QApplication(sys.argv)
        mainw = MainWindow()
        mainw.show()

        # 国际化
        translator = FluentTranslator(QLocale())
        app.installTranslator(translator)

        sys.exit(app.exec_())

    except Exception as e:
        logging.error(f"应用程序运行时出错: {e}")
        print(f"应用程序运行时出错: {e}")
