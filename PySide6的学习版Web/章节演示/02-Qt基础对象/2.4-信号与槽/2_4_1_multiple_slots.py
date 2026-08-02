from PySide6.QtWidgets import QWidget, QPushButton, QApplication

# 以下为槽函数
def func1():
    print("响应函数：1")

def func2():
    print("响应函数：2")

def func3():
    print("响应函数：3")

if __name__ == '__main__':
    app = QApplication()
    # 程序窗口
    window = QWidget(parent=None)
    # 窗口标题
    window.setWindowTitle("连接多个槽")
    # 窗口位置及大小
    window.setGeometry(766, 550, 230, 90)
    # 按钮部件
    button = QPushButton("请单击这里", window)
    # 按钮在窗口中的位置
    button.move(25, 20)
    # clicked 信号连接三个槽对象
    button.clicked.connect(func1)
    button.clicked.connect(func2)
    button.clicked.connect(func3)
    # 显示窗口
    window.show()
    # 启动消息循环
    app.exec()
