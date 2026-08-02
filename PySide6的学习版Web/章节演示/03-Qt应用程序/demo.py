"""原书 3.4：单击按钮后显示消息框。"""

from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton, QWidget


def build_window() -> QWidget:
    mainwin = QWidget()
    mainwin.resize(150, 62)
    mainwin.setWindowTitle("Test App")

    btn = QPushButton(mainwin)
    btn.setText("请单击这里")
    btn.move(12, 8)
    btn.clicked.connect(
        lambda: QMessageBox.information(
            mainwin,
            "提示信息",
            "你已单击按钮",
        )
    )

    return mainwin


if __name__ == "__main__":
    thisApp = QApplication()
    mainwin = build_window()
    mainwin.showNormal()
    thisApp.exec()
