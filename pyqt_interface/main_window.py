from PyQt5 import QtCore, QtWidgets
from qfluentwidgets import ComboBox, LineEdit, PushButton, ToolButton, FluentIcon
from PyQt5.QtWidgets import QSlider, QHBoxLayout, QVBoxLayout, QFrame, QScrollArea, QLabel, QWidget


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(400, 1000)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # 主布局：垂直布局包含上部按钮和文本框部分
        self.mainLayout = QVBoxLayout(self.centralwidget)

        # 上方布局：包含角色替换、音色替换及新建按钮
        self.topLayout = QHBoxLayout()

        # ComboBox for "角色替换"
        self.comboBox_1 = ComboBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.comboBox_1.setSizePolicy(sizePolicy)
        self.comboBox_1.setObjectName("comboBox_1")
        self.topLayout.addWidget(self.comboBox_1)

        # ComboBox for "音色替换"
        self.comboBox_2 = ComboBox(self.centralwidget)
        self.comboBox_2.setSizePolicy(sizePolicy)
        self.comboBox_2.setObjectName("comboBox_2")
        self.topLayout.addWidget(self.comboBox_2)

        # Button for "新建形象"
        self.PushButton = PushButton(self.centralwidget)
        self.PushButton.setSizePolicy(sizePolicy)
        self.PushButton.setObjectName("newImageButton")
        self.topLayout.addWidget(self.PushButton)

        # Button for "新建音色"
        self.PushButton_2 = PushButton(self.centralwidget)
        self.PushButton_2.setSizePolicy(sizePolicy)
        self.PushButton_2.setObjectName("newVoiceButton")
        self.topLayout.addWidget(self.PushButton_2)

        # 将上方布局添加到主布局
        self.mainLayout.addLayout(self.topLayout)

        # 聊天区域布局：包含滚动区域，用于显示聊天记录
        self.chatScrollArea = QScrollArea(self.centralwidget)
        self.chatScrollArea.setWidgetResizable(True)
        self.chatScrollArea.setObjectName("chatScrollArea")

        self.chatWidget = QWidget()
        self.chatWidget.setObjectName("chatWidget")

        self.chatLayout = QVBoxLayout(self.chatWidget)
        self.chatLayout.setAlignment(QtCore.Qt.AlignTop)
        self.chatScrollArea.setWidget(self.chatWidget)

        # 将聊天滚动区域添加到主布局
        self.mainLayout.addWidget(self.chatScrollArea)

        # 底部布局：包含输入框、发送按钮和打断按钮
        self.bottomLayout = QHBoxLayout()

        # LineEdit for user input
        self.lineEdit = LineEdit(self.centralwidget)
        self.lineEdit.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.lineEdit.setObjectName("lineEdit")
        self.bottomLayout.addWidget(self.lineEdit)

        # ToolButton for sending message
        self.ToolButton = ToolButton(FluentIcon.SEND.icon(FluentIcon.SEND))
        self.ToolButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.ToolButton.setIconSize(QtCore.QSize(15, 15))
        self.ToolButton.setObjectName("toolButton")
        self.bottomLayout.addWidget(self.ToolButton)



        # PushButton for interrupting
        self.interruptButton = PushButton("打断", self.centralwidget)
        self.interruptButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.interruptButton.setObjectName("interruptButton")
        self.bottomLayout.addWidget(self.interruptButton)

        # 使用QFrame作为视频输出窗口
        self.videoFrame = QFrame(self.centralwidget)
        self.videoFrame.setFrameShape(QFrame.StyledPanel)  # 设置为可嵌入视频的面板
        self.videoFrame.setObjectName("videoFrame")
        # self.verticalLayout_4.addWidget(self.videoFrame)
        # 在初始化时隐藏视频播放界面
        self.videoFrame.hide()

        # 将底部布局添加到主布局
        self.mainLayout.addLayout(self.bottomLayout)

        # 设置 central widget
        MainWindow.setCentralWidget(self.centralwidget)

        # 初始化界面文本
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "数字人智慧问答系统"))

        # 设置 ComboBox 组件的文本
        self.comboBox_1.setText(_translate("MainWindow", "形象替换"))
        image_items = ['形象1', '形象2', '形象3', '形象4']
        self.comboBox_1.addItems(image_items)
        self.comboBox_1.setPlaceholderText("形象替换")
        self.comboBox_1.setCurrentIndex(-1)

        self.comboBox_2.setText(_translate("MainWindow", "音色替换"))
        voice_items = ['胡桃', '云溪', '晓晓', '静静']
        self.comboBox_2.addItems(voice_items)
        self.comboBox_2.setPlaceholderText("音色替换")
        self.comboBox_2.setCurrentIndex(-1)

        # 设置按钮文本
        self.PushButton.setText(_translate("MainWindow", "新建形象"))
        self.PushButton_2.setText(_translate("MainWindow", "新建音色"))
        self.interruptButton.setText(_translate("MainWindow", "打断"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
