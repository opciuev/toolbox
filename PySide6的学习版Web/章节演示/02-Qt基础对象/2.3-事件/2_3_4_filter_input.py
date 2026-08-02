# 可运行补全：网页 2.3.4 没有给出导入语句，以下导入为独立运行而补充。
from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication, QLineEdit, QWidget


class MyWindow(QWidget):
    def __init__(self):
        super().__init__(None, Qt.Window)
        # 窗口标题
        self.setWindowTitle("事件过滤")
        # 窗口大小
        self.resize(200, 80)
        # 初始化 UI 部件
        self.txtEdit = QLineEdit(self)
        self.txtEdit.move(15, 17)
        # 安装事件过滤器
        self.txtEdit.installEventFilter(self)

    def eventFilter(self, watched: QObject, e: QEvent) -> bool:
        if watched == self.txtEdit:
            # 检查是否为键盘事件
            if e.type() == QEvent.KeyPress or e.type() == QEvent.KeyRelease:
                keyev = QKeyEvent(e)
                # 过滤“空格”键和“#”字符
                if keyev.key() == Qt.Key_Space or keyev.key() == Qt.Key_NumberSign:
                    # 直接返回 True，将跳过该事件
                    return True
        return super().eventFilter(watched, e)


# 可运行补全：网页没有给出本示例的启动入口。
if __name__ == "__main__":
    app = QApplication()
    window = MyWindow()
    window.show()
    app.exec()
