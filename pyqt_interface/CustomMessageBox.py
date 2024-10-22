import sys
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QApplication, QWidget
from qfluentwidgets import MessageBoxBase, SubtitleLabel, LineEdit, PushButton

class CustomMessageBox(MessageBoxBase):
    """ Custom message box """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.titleLabel = SubtitleLabel('打开 URL', self)
        self.urlLineEdit = LineEdit(self)
        self.urlLineEdit.setPlaceholderText('输入/拖入文件、流或者播放列表的 URL')
        self.urlLineEdit.setClearButtonEnabled(True)
        self.setAcceptDrops(True)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.urlLineEdit)

        self.yesButton.setText('打开')
        self.cancelButton.setText('取消')
        self.widget.setMinimumWidth(350)
        self.yesButton.setDisabled(True)

        self.urlLineEdit.textChanged.connect(self._validateUrl)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            self.urlLineEdit.setText(file_path)

    def _validateUrl(self, text):
        self.yesButton.setEnabled(QUrl(text).isValid())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    box = CustomMessageBox()
    box.show()
    sys.exit(app.exec_())
