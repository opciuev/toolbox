const chapters = [
  { id: "ch01", title: "第 1 章 搭建 PySide 开发环境", sections: ["1.1 配置 Python", "1.2 配置 Visual Studio Code", "1.2.1 Windows", "1.2.2 Linux", "1.2.3 macOS", "1.2.4 VS Code 配置用户数据目录", "1.2.5 安装 Python 扩展", "1.3 创建 Python 虚拟环境（可选）", "1.4 安装 PySide6 库", "1.5 在 VS Code 中选择 Python 解释器", "1.6 验证开发环境是否搭建成功"] },
  { id: "ch02", title: "第 2 章 Qt 基础对象", cardCount: 10, readySections: 6, sections: ["2.1 QObject 类与 Qt 对象模型", "2.2 建立对象的层级关系", "2.3 事件与 event 方法", "2.3.1 接受与忽略事件", "2.3.2 sendEvent 与 postEvent", "2.3.3 自定义事件", "2.4 信号与槽", "2.5 字节序列——QByteArray", "2.6 QBuffer", "2.7 位序列——QBitArray", "2.8 QSysInfo", "2.9 Qt 的动态属性", "2.10 生成随机数"] },
  { id: "ch03", title: "第 3 章 Qt 应用程序", sections: ["3.1 三个应用程序类", "3.2 示例：控制台应用程序", "3.3 命令行参数", "3.4 图形化应用程序"] },
  { id: "ch04", title: "第 4 章 QWindow", sections: ["4.1 关于 QWindow 类", "4.2 绘制窗口内容", "4.3 QRasterWindow", "4.4 鼠标事件", "4.5 键盘事件", "4.6 嵌套窗口"] },
  { id: "ch05", title: "第 5 章 窗口组件", sections: ["5.1 QWidget 类", "5.2 窗口的显示方式", "5.3 拖放操作", "5.4 剪贴板", "5.5 调整窗口的透明度", "5.6 调色板"] },
  { id: "ch06", title: "第 6 章 按钮", sections: ["6.1 常用的按钮组件", "6.2 QPushButton", "6.3 QCheckBox", "6.4 QRadioButton", "6.5 按钮分组", "6.6 在按钮上显示图标", "6.7 按钮与快捷键"] },
  { id: "ch07", title: "第 7 章 布局", sections: ["7.1 布局管理", "7.2 “盒子”模型", "7.3 网格布局", "7.4 组件的缩放策略", "7.5 表单布局", "7.6 QStackedLayout"] },
  { id: "ch08", title: "第 8 章 输入组件", sections: ["8.1 QLineEdit", "8.2 QTextEdit", "8.3 数值输入组件", "8.4 日期和时间"] },
  { id: "ch09", title: "第 9 章 容器组件", sections: ["9.1 将 QWidget 组件作为容器", "9.2 示例：自定义容器", "9.3 QFrame", "9.4 QTabWidget", "9.5 QGroupBox", "9.6 QScrollArea", "9.7 QToolBox"] },
  { id: "ch10", title: "第 10 章 菜单栏、工具栏与状态栏", sections: ["10.1 QMenu", "10.2 菜单栏", "10.3 工具栏", "10.4 contextMenu 事件", "10.5 状态栏", "10.6 快捷键", "10.7 QWidgetAction"] },
  { id: "ch11", title: "第 11 章 主窗口", sections: ["11.1 QMainWindow", "11.2 QDockWidget", "11.3 MDI"] },
  { id: "ch12", title: "第 12 章 交互组件", sections: ["12.1 进度条", "12.2 滑动条", "12.3 仪表盘", "12.4 QLCDNumber", "12.5 托盘图标", "12.6 工具提示"] },
  { id: "ch13", title: "第 13 章 对话框", sections: ["13.1 QDialog", "13.2 QInputDialog", "13.3 QColorDialog", "13.4 QFileDialog", "13.5 QFontDialog", "13.6 QDialogButtonBox", "13.7 QWizard", "13.8 无按钮对话框", "13.9 QMessageBox"] },
  { id: "ch14", title: "第 14 章 列表模型与视图", sections: ["14.1 模型的抽象基类", "14.2 QStringListModel", "14.3 QStandardItemModel", "14.4 QFileSystemModel", "14.5 编辑功能", "14.6 QListWidget", "14.7 QTableWidget", "14.8 QTreeWidget"] },
  { id: "ch15", title: "第 15 章 目录与文件", sections: ["15.1 QDir", "15.2 QFile", "15.3 QSaveFile", "15.4 QBuffer", "15.5 QTextStream", "15.6 QDataStream"] },
  { id: "ch16", title: "第 16 章 动画", sections: ["16.1 与动画有关的类型", "16.2 基于属性的动画", "16.3 自定义属性", "16.4 关键帧动画", "16.5 动画分组"] },
  { id: "ch17", title: "第 17 章 Qt 样式表", sections: ["17.1 Qt 样式表概述", "17.2 盒子模型", "17.3 颜色", "17.4 渐变画刷", "17.5 字体", "17.6 伪状态", "17.7 子控件"] },
  { id: "ch18", title: "第 18 章 多线程", sections: ["18.1 单线程与多线程的比较", "18.2 QThread 类", "18.3 QThreadPool", "18.4 互斥锁", "18.5 QWaitCondition"] },
  { id: "ch19", title: "第 19 章 QML 基础", sections: ["19.1 QML 与 QtQuick", "19.2 QML 文档的结构", "19.3 加载 QML 文档", "19.4 QQuickItem 类", "19.5 布局", "19.6 控件基类——Control", "19.7 按钮控件", "19.8 输入控件", "19.9 菜单", "19.10 工具栏", "19.11 列表控件——ListView", "19.12 在 QWidget 中呈现 QtQuick 对象"] }
];

const bookToc = [
  ["第 1 章", "搭建 PySide 开发环境", "1", [["1.1", "配置 Python", "1"], ["1.2", "配置 Visual Studio Code", "2"], ["1.3", "创建 Python 虚拟环境（可选）", "3"], ["1.4", "安装 PySide6 库", "4"], ["1.5", "在 VS Code 中选择 Python 解释器", "4"], ["1.6", "验证开发环境是否搭建成功", "5"]]],
  ["第 2 章", "Qt 基础对象", "6", [["2.1", "QObject 类与 Qt 对象模型", "6"], ["2.2", "建立对象的层级关系", "6"], ["2.3", "事件与 event 方法", "7"], ["2.4", "信号与槽", "16"], ["2.5", "字节序列——QByteArray", "26"], ["2.6", "QBuffer", "32"], ["2.7", "位序列——QBitArray", "35"], ["2.8", "QSysInfo", "36"], ["2.9", "Qt 的动态属性", "37"], ["2.10", "生成随机数", "38"]]],
  ["第 3 章", "Qt 应用程序", "42", [["3.1", "三个应用程序类", "42"], ["3.2", "示例：控制台应用程序", "43"], ["3.3", "命令行参数", "44"], ["3.4", "图形化应用程序", "53"]]],
  ["第 4 章", "QWindow", "55", [["4.1", "关于 QWindow 类", "55"], ["4.2", "绘制窗口内容", "58"], ["4.3", "QRasterWindow", "63"], ["4.4", "鼠标事件", "64"], ["4.5", "键盘事件", "66"], ["4.6", "嵌套窗口", "69"]]],
  ["第 5 章", "窗口组件", "74", [["5.1", "QWidget 类", "74"], ["5.2", "窗口的显示方式", "77"], ["5.3", "拖放操作", "78"], ["5.4", "剪贴板", "87"], ["5.5", "调整窗口的透明度", "92"], ["5.6", "调色板", "93"]]],
  ["第 6 章", "按钮", "98", [["6.1", "常用的按钮组件", "98"], ["6.2", "QPushButton", "100"], ["6.3", "QCheckBox", "104"], ["6.4", "QRadioButton", "107"], ["6.5", "按钮分组", "109"], ["6.6", "在按钮上显示图标", "113"], ["6.7", "按钮与快捷键", "118"]]],
  ["第 7 章", "布局", "120", [["7.1", "布局管理", "120"], ["7.2", "“盒子”模型", "120"], ["7.3", "网格布局", "125"], ["7.4", "组件的缩放策略", "129"], ["7.5", "表单布局", "131"], ["7.6", "QStackedLayout", "134"]]],
  ["第 8 章", "输入组件", "138", [["8.1", "QLineEdit", "138"], ["8.2", "QTextEdit", "145"], ["8.3", "数值输入组件", "151"], ["8.4", "日期和时间", "157"]]],
  ["第 9 章", "容器组件", "161", [["9.1", "将 QWidget 组件作为容器", "161"], ["9.2", "示例：自定义容器", "162"], ["9.3", "QFrame", "163"], ["9.4", "QTabWidget", "167"], ["9.5", "QGroupBox", "170"], ["9.6", "QScrollArea", "173"], ["9.7", "QToolBox", "178"]]],
  ["第 10 章", "菜单栏、工具栏与状态栏", "181", [["10.1", "QMenu", "181"], ["10.2", "菜单栏", "184"], ["10.3", "工具栏", "189"], ["10.4", "contextMenu 事件", "191"], ["10.5", "状态栏", "193"], ["10.6", "快捷键", "196"], ["10.7", "QWidgetAction", "199"]]],
  ["第 11 章", "主窗口", "203", [["11.1", "QMainWindow", "203"], ["11.2", "QDockWidget", "207"], ["11.3", "MDI", "211"]]],
  ["第 12 章", "交互组件", "220", [["12.1", "进度条", "220"], ["12.2", "滑动条", "224"], ["12.3", "仪表盘", "229"], ["12.4", "QLCDNumber", "232"], ["12.5", "托盘图标", "234"], ["12.6", "工具提示", "237"]]],
  ["第 13 章", "对话框", "242", [["13.1", "QDialog", "242"], ["13.2", "QInputDialog", "245"], ["13.3", "QColorDialog", "253"], ["13.4", "QFileDialog", "256"], ["13.5", "QFontDialog", "261"], ["13.6", "QDialogButtonBox", "263"], ["13.7", "QWizard", "270"], ["13.8", "无按钮对话框", "279"], ["13.9", "QMessageBox", "283"]]],
  ["第 14 章", "列表模型与视图", "289", [["14.1", "模型的抽象基类", "289"], ["14.2", "QStringListModel", "296"], ["14.3", "QStandardItemModel", "297"], ["14.4", "QFileSystemModel", "303"], ["14.5", "编辑功能", "306"], ["14.6", "QListWidget", "314"], ["14.7", "QTableWidget", "318"], ["14.8", "QTreeWidget", "320"]]],
  ["第 15 章", "目录与文件", "322", [["15.1", "QDir", "322"], ["15.2", "QFile", "328"], ["15.3", "QSaveFile", "332"], ["15.4", "QBuffer", "333"], ["15.5", "QTextStream", "334"], ["15.6", "QDataStream", "336"]]],
  ["第 16 章", "动画", "340", [["16.1", "与动画有关的类型", "340"], ["16.2", "基于属性的动画", "340"], ["16.3", "自定义属性", "344"], ["16.4", "关键帧动画", "347"], ["16.5", "动画分组", "348"]]],
  ["第 17 章", "Qt 样式表", "351", [["17.1", "Qt 样式表概述", "351"], ["17.2", "盒子模型", "356"], ["17.3", "颜色", "363"], ["17.4", "渐变画刷", "366"], ["17.5", "字体", "376"], ["17.6", "伪状态", "381"], ["17.7", "子控件", "385"]]],
  ["第 18 章", "多线程", "390", [["18.1", "单线程与多线程的比较", "390"], ["18.2", "QThread 类", "390"], ["18.3", "QThreadPool", "395"], ["18.4", "互斥锁", "398"], ["18.5", "QWaitCondition", "402"]]],
  ["第 19 章", "QML 基础", "406", [["19.1", "QML 与 QtQuick", "406"], ["19.2", "QML 文档的结构", "407"], ["19.3", "加载 QML 文档", "409"], ["19.4", "QQuickItem 类", "412"], ["19.5", "布局", "412"], ["19.6", "控件基类——Control", "421"], ["19.7", "按钮控件", "425"], ["19.8", "输入控件", "431"], ["19.9", "菜单", "438"], ["19.10", "工具栏", "444"], ["19.11", "列表控件——ListView", "447"], ["19.12", "在 QWidget 中呈现 QtQuick 对象", "451"]]]
];

function buildSidebar(currentChapterId) {
  const nav = document.getElementById("sidebar-nav");
  if (!nav) return;

  nav.innerHTML = chapters.map((ch) => {
    const isCurrent = ch.id === currentChapterId;
    const isReady = ch.id === "ch01" || ch.id === "ch02";
    const chapterHref = ch.id === "ch01" ? "index.html#chapter-1" : `${ch.id}.html`;
    const titleClass = isCurrent ? "nav-group-title current active" : "nav-group-title";
    const subClass = isCurrent ? "nav-sub show" : "nav-sub";
    const sections = ch.sections.map((sec, idx) => {
      const href = isCurrent ? `#section-${idx}` : chapterHref;
      const sectionReady = isReady && (!isCurrent || !ch.readySections || idx < ch.readySections);
      const disabled = sectionReady ? "" : " style=\"opacity:0.45;pointer-events:none\"";
      return `<li><a href="${href}"${disabled}>${sec}</a></li>`;
    }).join("");
    const titleClick = isCurrent
      ? " onclick=\"toggleNav(this)\""
      : (isReady ? ` onclick="location.href='${chapterHref}'"` : " onclick=\"toggleNav(this)\"");

    return `<div class="nav-group">
      <div class="${titleClass}"${titleClick} data-id="${ch.id}">
        <span>${ch.title}</span><span class="arrow">&#9654;</span>
      </div>
      <ul class="${subClass}">${sections}</ul>
    </div>`;
  }).join("");
}

function renderChapterGrid(targetId) {
  const target = document.getElementById(targetId);
  if (!target) return;

  target.innerHTML = chapters.map((ch, idx) => {
    const isReady = ch.id === "ch01" || ch.id === "ch02";
    const statusHtml = isReady
      ? '<span class="card-status ready">已完成</span>'
      : '<span class="card-status todo">待建置</span>';
    const href = ch.id === "ch01" ? "#chapter-1" : (ch.id === "ch02" ? "ch02.html" : "#");
    const cardClass = isReady ? "chapter-card" : "chapter-card disabled";
    const chapterLabel = `第${String(idx + 1).padStart(2, "0")}章`;
    const cleanTitle = ch.title.replace(/^第 \d+ 章\s*/, "");

    return `<a class="${cardClass}" id="chapter-card-${ch.id}" href="${href}">
      <span class="card-num">${chapterLabel}</span>
      ${statusHtml}
      <h3>${cleanTitle}</h3>
      <div class="card-sections">${ch.cardCount || ch.sections.length} 个小节</div>
    </a>`;
  }).join("");
}

function toggleNav(el) {
  const sub = el.nextElementSibling;
  if (sub) sub.classList.toggle("show");
  el.classList.toggle("active");
}

function toggleSidebar() {
  const sidebar = document.querySelector(".sidebar");
  const overlay = document.querySelector(".overlay");
  if (sidebar) sidebar.classList.toggle("open");
  if (overlay) overlay.classList.toggle("show");
}
