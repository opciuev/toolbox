// Sidebar navigation data - all chapters
const chapters = [
  {
    id: "ch01", title: "第 1 章 图像的读取、显示与保存", file: "ch01.html",
    sections: ["1-0 建议阅读书籍","1-1 程序导入 OpenCV 模块","1-2 读取图像文件","1-3 显示图像与关闭图像窗口","1-4 保存图像"]
  },
  {
    id: "ch02", title: "第 2 章 认识图像表示方法", file: "ch02.html",
    sections: ["2-1 位图像表示法","2-2 GRAY 色彩空间","2-3 RGB 色彩空间","2-4 BGR 色彩空间","2-5 获得图像的属性","2-6 像素的 BGR 值"]
  },
  {
    id: "ch03", title: "第 3 章 学习 OpenCV 需要的 Numpy 知识", file: "ch03.html",
    sections: ["3-1 数组 ndarray","3-2 Numpy 的数据类型","3-3 创建一维或多维数组","3-4 一维数组的运算与切片","3-5 多维数组的索引与切片","3-6 数组水平与垂直合并"]
  },
  {
    id: "ch04", title: "第 4 章 认识色彩空间到艺术创作", file: "ch04.html",
    sections: ["4-1 BGR 与 RGB 色彩空间的转换","4-2 BGR 转换至 GRAY","4-3 HSV 色彩空间","4-4 拆分色彩通道","4-5 合并色彩通道","4-6 拆分与合并的应用","4-7 alpha 通道"]
  },
  {
    id: "ch05", title: "第 5 章 妙手空空创建图像", file: "ch05.html",
    sections: ["5-1 图像坐标","5-2 创建与编辑灰度图像","5-3 创建彩色图像"]
  },
  {
    id: "ch06", title: "第 6 章 图像处理的基础知识", file: "ch06.html",
    sections: ["6-1 灰度图像的编辑","6-2 彩色图像的编辑","6-3 含 alpha 通道的彩色图像","6-4 Numpy 高效率像素方法","6-5 图像感兴趣区域的编辑"]
  },
  {
    id: "ch07", title: "第 7 章 从静态到动态的绘图功能", file: "ch07.html",
    sections: ["7-1 创建画布","7-2 绘制直线","7-3 画布背景色彩","7-4 绘制矩形","7-5 绘制圆","7-6 绘制椭圆","7-7 绘制多边形","7-8 输出文本","7-9 反弹球设计","7-10 鼠标事件","7-11 滚动条设计","7-12 滚动条开关应用"]
  },
  {
    id: "ch08", title: "第 8 章 图像计算迈向图像创作", file: "ch08.html",
    sections: ["8-1 图像加法运算","8-2 遮罩 mask","8-3 重复曝光技术","8-4 图像的位运算","8-5 图像加密与解密"]
  },
  {
    id: "ch09", title: "第 9 章 阈值处理迈向数字情报", file: "ch09.html",
    sections: ["9-1 threshold() 函数","9-2 Otsu 算法","9-3 自适应阈值方法","9-4 平面图的分解","9-5 数字水印"]
  },
  {
    id: "ch10", title: "第 10 章 图像的几何变换", file: "ch10.html",
    sections: ["10-1 图像缩放效果","10-2 图像翻转","10-3 图像仿射","10-4 图像透视","10-5 重映射"]
  },
  {
    id: "ch11", title: "第 11 章 删除图像噪声", file: "ch11.html",
    sections: ["11-1 平滑图像名词","11-2 均值滤波器","11-3 方框滤波器","11-4 中值滤波器","11-5 高斯滤波器","11-6 双边滤波器","11-7 2D 滤波核"]
  },
  {
    id: "ch12", title: "第 12 章 数学形态学", file: "ch12.html",
    sections: ["12-1 腐蚀","12-2 膨胀","12-3 通用函数","12-4 开运算","12-5 闭运算","12-6 形态学梯度","12-7 礼帽运算","12-8 黑帽运算","12-9 核函数"]
  },
  {
    id: "ch13", title: "第 13 章 图像梯度与边缘检测", file: "ch13.html",
    sections: ["13-1 图像梯度概念","13-2 Sobel()","13-3 Scharr()","13-4 Laplacian()","13-5 Canny 边缘检测"]
  },
  {
    id: "ch14", title: "第 14 章 图像金字塔", file: "ch14.html",
    sections: ["14-1 图像金字塔原理","14-2 pyrDown()","14-3 pyrUp()","14-4 采样逆运算","14-5 拉普拉斯金字塔"]
  },
  {
    id: "ch15", title: "第 15 章 轮廓的检测与匹配", file: "ch15.html",
    sections: ["15-1 图像内图形的轮廓","15-2 绘制轮廓示例","15-3 轮廓层级","15-4 图像矩","15-5 Hu 矩","15-6 轮廓外形匹配"]
  },
  {
    id: "ch16", title: "第 16 章 轮廓拟合与凸包", file: "ch16.html",
    sections: ["16-1 轮廓的拟合","16-2 凸包","16-3 轮廓几何测试"]
  },
  {
    id: "ch17", title: "第 17 章 轮廓的特征", file: "ch17.html",
    sections: ["17-1 宽高比","17-2 轮廓的极点","17-3 Extent","17-4 Solidity","17-5 等效直径","17-6 遮罩和非0像素","17-7 最小值与最大值","17-8 均值与标准差","17-9 方向"]
  },
  {
    id: "ch18", title: "第 18 章 从直线检测到无人驾驶车道检测", file: "ch18.html",
    sections: ["18-1 霍夫变换原理","18-2 HoughLines()","18-3 HoughLinesP()","18-4 霍夫圆环变换"]
  },
  {
    id: "ch19", title: "第 19 章 直方图均衡化", file: "ch19.html",
    sections: ["19-1 认识直方图","19-2 绘制直方图","19-3 直方图均衡化","19-4 限制自适应方法"]
  },
  {
    id: "ch20", title: "第 20 章 模板匹配", file: "ch20.html",
    sections: ["20-1 模板匹配概念","20-2 matchTemplate()","20-3 单模板匹配","20-4 多模板匹配"]
  },
  {
    id: "ch21", title: "第 21 章 傅里叶变换", file: "ch21.html",
    sections: ["21-1 坐标轴转换","21-2 傅里叶理论","21-3 Numpy 傅里叶","21-4 OpenCV 傅里叶"]
  },
  {
    id: "ch22", title: "第 22 章 分水岭算法", file: "ch22.html",
    sections: ["22-1 前言","22-2 分水岭算法","22-3 distanceTransform()","22-4 找出未知区域","22-5 创建标记","22-6 完成分水岭"]
  },
  {
    id: "ch23", title: "第 23 章 图像提取", file: "ch23.html",
    sections: ["23-1 图像提取原理","23-2 grabCut()","23-3 基础实作","23-4 自定义遮罩"]
  },
  {
    id: "ch24", title: "第 24 章 图像修复", file: "ch24.html",
    sections: ["24-1 图像修复算法","24-2 inpaint()","24-3 修复蒙娜丽莎"]
  },
  {
    id: "ch25", title: "第 25 章 识别手写数字", file: "ch25.html",
    sections: ["25-1 KNN 算法","25-2 Numpy 与 KNN","25-3 KNN 函数","25-4 手写数字 Numpy","25-5 识别手写数字"]
  },
  {
    id: "ch26", title: "第 26 章 OpenCV 的拍摄功能", file: "ch26.html",
    sections: ["26-1 VideoCapture","26-2 VideoWriter 录像","26-3 播放视频","26-4 拍摄功能属性"]
  },
  {
    id: "ch27", title: "第 27 章 对象检测原理与资源", file: "ch27.html",
    sections: ["27-1 对象检测原理","27-2 资源文件来源","27-3 认识资源文件","27-4 人脸检测","27-5 侧面人脸","27-6 路人检测","27-7 眼睛检测","27-8 检测猫脸","27-9 车牌识别"]
  },
  {
    id: "ch28", title: "第 28 章 摄像头与人脸文件", file: "ch28.html",
    sections: ["28-1 提取人脸存档","28-2 摄像头提取人脸","28-3 自动化拍摄提取","28-4 半自动拍摄","28-5 全自动拍摄"]
  },
  {
    id: "ch29", title: "第 29 章 人脸识别", file: "ch29.html",
    sections: ["29-1 LBPH 人脸识别","29-2 Eigenfaces","29-3 Fisherfaces","29-4 员工人脸识别系统"]
  },
  {
    id: "ch30", title: "第 30 章 创建哈尔特征分类器", file: "ch30.html",
    sections: ["30-1 正负样本数据","30-2 处理正样本","30-3 处理负样本","30-4 创建分类器","30-5 训练分类器","30-6 车牌检测","30-7 心得报告"]
  },
  {
    id: "ch31", title: "第 31 章 车牌识别", file: "ch31.html",
    sections: ["31-1 提取车牌图像","31-2 Tesseract OCR","31-3 检测与识别车牌","31-4 二值化处理","31-5 形态学处理","31-6 车牌识别心得"]
  },
  {
    id: "appendix-a", title: "附录 A 安装 OpenCV", file: "appendix-a.html",
    sections: ["A-1 安装 Numpy","A-2 基本安装","A-3 扩展模块","A-4 资源文件"]
  },
  {
    id: "appendix-b", title: "附录 B 函数索引表", file: "appendix-b.html",
    sections: []
  }
];

const readyChapters = new Set([
  "ch01", "ch02", "ch03", "ch04", "ch05", "ch06", "ch07",
  "ch08", "ch09", "ch10", "ch11", "ch12", "ch13", "ch14", "ch15", "ch16", "ch17", "ch18", "ch19"
]);

// Build sidebar HTML
function buildSidebar(currentChapterId) {
  const nav = document.getElementById("sidebar-nav");
  if (!nav) return;

  let html = "";
  chapters.forEach((ch) => {
    const isCurrent = ch.id === currentChapterId;
    const titleClass = isCurrent ? "nav-group-title current active" : "nav-group-title";
    const subClass = isCurrent ? "nav-sub show" : "nav-sub";

    html += `<div class="nav-group">`;
    html += `<div class="${titleClass}" onclick="toggleNav(this)" data-id="${ch.id}">`;
    html += `<span>${ch.title}</span>`;
    html += `<span class="arrow">&#9654;</span>`;
    html += `</div>`;

    if (ch.sections.length > 0) {
      html += `<ul class="${subClass}">`;
      ch.sections.forEach((sec, idx) => {
        const sectionId = `section-${idx}`;
        if (isCurrent) {
          html += `<li><a href="#${sectionId}">${sec}</a></li>`;
        } else if (readyChapters.has(ch.id)) {
          html += `<li><a href="chapters/${ch.file}#section-${idx}">${sec}</a></li>`;
        } else {
          html += `<li><a href="#" style="opacity:0.45;pointer-events:none">${sec}</a></li>`;
        }
      });
      html += `</ul>`;
    }
    html += `</div>`;
  });

  nav.innerHTML = html;
}

// Build sidebar for chapter pages (paths relative to chapters/)
function buildSidebarForChapter(currentChapterId) {
  const nav = document.getElementById("sidebar-nav");
  if (!nav) return;

  let html = "";
  chapters.forEach((ch) => {
    const isCurrent = ch.id === currentChapterId;
    const titleClass = isCurrent ? "nav-group-title current active" : "nav-group-title";
    const subClass = isCurrent ? "nav-sub show" : "nav-sub";

    html += `<div class="nav-group">`;
    html += `<div class="${titleClass}" onclick="toggleNav(this)" data-id="${ch.id}">`;
    html += `<span>${ch.title}</span>`;
    html += `<span class="arrow">&#9654;</span>`;
    html += `</div>`;

    if (ch.sections.length > 0) {
      html += `<ul class="${subClass}">`;
      ch.sections.forEach((sec, idx) => {
        const sectionId = `section-${idx}`;
        if (isCurrent) {
          html += `<li><a href="#${sectionId}">${sec}</a></li>`;
        } else if (readyChapters.has(ch.id)) {
          html += `<li><a href="${ch.file}#section-${idx}">${sec}</a></li>`;
        } else {
          html += `<li><a href="#" style="opacity:0.45;pointer-events:none">${sec}</a></li>`;
        }
      });
      html += `</ul>`;
    }
    html += `</div>`;
  });

  nav.innerHTML = html;
}

function toggleNav(el) {
  const sub = el.nextElementSibling;
  if (sub) {
    sub.classList.toggle("show");
  }
  el.classList.toggle("active");
}

// Get prev/next chapter
function getChapterNav(currentId) {
  const idx = chapters.findIndex((c) => c.id === currentId);
  return {
    prev: idx > 0 ? chapters[idx - 1] : null,
    next: idx < chapters.length - 1 ? chapters[idx + 1] : null,
  };
}

// Mobile menu toggle
function toggleSidebar() {
  const sidebar = document.querySelector(".sidebar");
  const overlay = document.querySelector(".overlay");
  sidebar.classList.toggle("open");
  if (overlay) overlay.classList.toggle("show");
}

// Highlight active section on scroll
function setupScrollSpy() {
  const sections = document.querySelectorAll("[id^='section-']");
  const links = document.querySelectorAll(".nav-sub a");

  if (sections.length === 0) return;

  window.addEventListener("scroll", () => {
    let current = "";
    sections.forEach((sec) => {
      const top = sec.getBoundingClientRect().top;
      if (top < 120) current = sec.id;
    });

    links.forEach((link) => {
      link.classList.remove("active");
      if (link.getAttribute("href") === `#${current}`) {
        link.classList.add("active");
      }
    });
  });
}

document.addEventListener("DOMContentLoaded", setupScrollSpy);
