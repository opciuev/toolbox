"""原书 2.4.5：使用对象名和槽命名规则自动建立连接。"""

import PySide6.QtCore as core
import PySide6.QtWidgets as widgets


class AppWindow(widgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo")
        self.resize(220, 65)

        self.btn = widgets.QPushButton("Click Me", self)
        self.btn.move(35, 20)
        self.btn.setObjectName("myButton")

        # 根据 on_<对象名称>_<信号> 的规则自动连接。
        core.QMetaObject.connectSlotsByName(self)

    @core.Slot()
    def on_myButton_clicked(self):
        widgets.QMessageBox.information(
            self,
            "提示",
            "你单击了按钮",
            widgets.QMessageBox.Ok,
        )


if __name__ == "__main__":
    app = widgets.QApplication()
    window = AppWindow()
    window.show()
    app.exec()
