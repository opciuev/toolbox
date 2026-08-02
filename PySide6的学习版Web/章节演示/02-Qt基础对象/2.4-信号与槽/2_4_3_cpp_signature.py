from PySide6.QtWidgets import QApplication, QWidget, QLineEdit, QLabel
from PySide6.QtCore import SIGNAL, SLOT

class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        # 设置窗口大小
        self.resize(280, 90)
        # 设置窗口标题
        self.setWindowTitle("Demo App")
        # 初始化单行文本输入部件
        self.lineTxt = QLineEdit(self)
        # 建立信号与槽的连接
        self.lineTxt.connect(SIGNAL('cursorPositionChanged(int,int)'), self,
SLOT('onCursorPsChanged(int,int)'))
        # 初始化标签部件
        self.lb = QLabel(self)
        # 设置部件在窗口中的位置和大小
        self.lineTxt.setGeometry(20,15, 200, 25)
        self.lb.setGeometry(20, 45, 160, 35)

    # 接收 cursorPositionChanged 信号的槽
    def onCursorPsChanged(self, oldPos, newPos):
        msg = f'光标已从{oldPos}移动到{newPos}'
        self.lb.setText(msg)

if __name__ == '__main__':
    app = QApplication()
    window = AppWindow()
    # 显示窗口
    window.show()
    # 启动消息循环
    app.exec()
