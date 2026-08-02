# 可运行补全：网页 2.3.3 没有给出导入语句，以下导入为独立运行而补充。
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


# MyCustomEvent1 = QEvent.Type(QEvent.Type.User + 1)
# MyCustomEvent2 = QEvent.Type(QEvent.Type.User + 2)

MyCustomEvent1 = QEvent.Type(QEvent.registerEventType())
MyCustomEvent2 = QEvent.Type(QEvent.registerEventType())

# 可运行补全：网页按方法分段展示，但省略了下面这行类声明。
class AppWindow(QWidget):
    def __init__(self):
        super().__init__(None)
        # 初始化用户界面
        self.initUI()

    def initUI(self):
        # 布局
        layout = QVBoxLayout(self)
        # 标签部件
        self.label = QLabel()
        # 按钮部件
        self.btn1 = QPushButton("点这里，触发自定义事件1")
        self.btn2 = QPushButton("点这里，触发自定义事件2")

        # 将以上部件添加到布局中
        layout.addWidget(self.label)
        layout.addWidget(self.btn1)
        layout.addWidget(self.btn2)
        # 应用布局
        self.setLayout(layout)

        # 为按钮的 clicked 信号绑定槽函数
        self.btn1.clicked.connect(self.onClicked1)
        self.btn2.clicked.connect(self.onClicked2)
        # 窗口标题
        self.setWindowTitle("示例程序")
        # 窗口大小
        self.resize(200, 160)

    def onClicked1(self):
        QApplication.postEvent(self, QEvent(MyCustomEvent1))

    def onClicked2(self):
        QApplication.postEvent(self, QEvent(MyCustomEvent2))

    def event(self, e: QEvent) -> bool:
        if e.type() == MyCustomEvent1:
            self.label.setText("自定义事件1已触发")
            return True
        if e.type() == MyCustomEvent2:
            self.label.setText("自定义事件2已触发")
            return True
        # 其余事件将交给基类处理
        return super().event(e)


# 可运行补全：网页最后给出的是四行直接启动代码，这里加判断以便导入测试。
if __name__ == "__main__":
    # QEvent.registerEventType(MyCustomEvent1)
    # QEvent.registerEventType(MyCustomEvent2)
    app = QApplication()
    wind = AppWindow()
    wind.show()
    app.exec()
