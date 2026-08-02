"""原书 3.3.1：分析 action、input、output 三个位置参数。"""

import sys

from PySide6.QtCore import QCommandLineParser, QCoreApplication


args = sys.argv
app = QCoreApplication(args)

parser = QCommandLineParser()
parser.addHelpOption()
parser.addPositionalArgument(
    "action",
    "操作类型，可选的值有 copy、move、rename",
    "<action>",
)
parser.addPositionalArgument("input", "输入文件", "<input file>")
parser.addPositionalArgument("output", "输出文件", "<output file>")

result = parser.parse(app.arguments())

if result:
    posargs = parser.positionalArguments()
    if len(posargs) != 3:
        print("参数个数不正确\n")
        parser.showHelp()
    else:
        action = posargs[0]
        if action == "copy":
            print(f"从{posargs[1]}复制到{posargs[2]}")
        elif action == "move":
            print(f"从{posargs[1]}移动到{posargs[2]}")
        elif action == "rename":
            print(f"将{posargs[1]}重命名为{posargs[2]}")
        else:
            print("action 参数为未知指令\n")
            parser.showHelp()
else:
    print(parser.errorText())
