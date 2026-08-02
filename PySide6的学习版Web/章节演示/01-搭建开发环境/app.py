import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel
from PySide6.QtCore import QRect

# 创建应用程序对象
app = QApplication()

# 创建一个简单窗口
window = QWidget()
# 设置窗口标题
window.setWindowTitle("示例程序")
# 设置窗口的位置和大小
window.setGeometry(QRect(445, 300, 325, 270))

# 创建标签组件，显示在窗口上
lb = QLabel(window)
# 设置标签文本
lb.setText("我的第一个Qt应用程序")
# 设置标签组件
lb.setGeometry(20, 25, 200, 40)

# 显示窗口
window.show()

# 启动主循环
sys.exit(app.exec())
