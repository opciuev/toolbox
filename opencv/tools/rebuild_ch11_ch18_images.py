#!/usr/bin/env python3
"""Rebuild problematic Chapter 11-18 web images as standalone figures.

The generated images avoid book-page screenshots and use the original sample
assets under OpenCV程序实例代码 whenever possible.
"""

from __future__ import annotations

import argparse
import math
import re
from html.parser import HTMLParser
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
CHAPTER_DIR = ROOT / "chapters"
IMAGE_DIR = CHAPTER_DIR / "images"
SAMPLE_DIR = ROOT / "OpenCV程序实例代码"

TEXT = (31, 41, 55)
MUTED = (92, 105, 122)
LINE = (195, 204, 216)
PANEL = (248, 250, 252)
BLUE = (37, 99, 235)
GREEN = (22, 163, 74)
RED = (220, 38, 38)
AMBER = (245, 158, 11)


class ImgParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[tuple[int, str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "img":
            return
        attr = {k.lower(): v or "" for k, v in attrs}
        src = attr.get("src", "")
        if src.startswith("images/ch"):
            self.refs.append((self.getpos()[0], src, attr.get("alt", "")))


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


F12 = font(12)
F14 = font(14)
F16 = font(16)
F18 = font(18)
F20 = font(20, True)
F24 = font(24, True)


def read_cv(path: Path, flags: int = cv2.IMREAD_COLOR) -> np.ndarray:
    image = cv2.imread(str(path), flags)
    if image is None:
        raise FileNotFoundError(path)
    return image


def cv_to_pil(image: np.ndarray) -> Image.Image:
    if image.ndim == 2:
        return Image.fromarray(image).convert("RGB")
    return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))


def save(image: Image.Image, rel: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() in {".jpg", ".jpeg"}:
        image.convert("RGB").save(path, quality=94, optimize=True)
    else:
        image.convert("RGB").save(path, optimize=True)
    print(f"wrote {path.relative_to(ROOT)} {image.width}x{image.height}")


def contain(image: Image.Image, max_w: int, max_h: int) -> Image.Image:
    out = ImageOps.exif_transpose(image).convert("RGB").copy()
    out.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    return out


def panel_grid(
    panels: list[tuple[str, Image.Image | np.ndarray]],
    *,
    cell_w: int = 300,
    cell_h: int = 280,
    cols: int | None = None,
    title: str | None = None,
) -> Image.Image:
    if cols is None:
        cols = min(3, len(panels))
    rows = math.ceil(len(panels) / cols)
    top = 52 if title else 18
    gutter = 18
    width = cols * cell_w + (cols + 1) * gutter
    height = top + rows * cell_h + (rows + 1) * gutter
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    if title:
        draw.text((gutter, 16), title, fill=TEXT, font=F24)
    for idx, (label, image) in enumerate(panels):
        if isinstance(image, np.ndarray):
            image = cv_to_pil(image)
        row, col = divmod(idx, cols)
        x = gutter + col * (cell_w + gutter)
        y = top + row * (cell_h + gutter)
        draw.rounded_rectangle((x, y, x + cell_w, y + cell_h), radius=8, fill=PANEL, outline=LINE)
        draw.text((x + 14, y + 12), label, fill=TEXT, font=F18)
        thumb = contain(image, cell_w - 28, cell_h - 58)
        px = x + (cell_w - thumb.width) // 2
        py = y + 46 + (cell_h - 58 - thumb.height) // 2
        canvas.paste(thumb, (px, py))
    return canvas


def text_image(lines: list[str], *, width: int = 780, line_h: int = 28, title: str | None = None) -> Image.Image:
    top = 52 if title else 22
    height = top + max(1, len(lines)) * line_h + 24
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    if title:
        draw.text((20, 16), title, fill=TEXT, font=F24)
    y = top
    for line in lines:
        draw.text((22, y), line, fill=TEXT, font=F16)
        y += line_h
    return image


def matrix_image(items: list[tuple[str, np.ndarray]], *, cell: int = 34) -> Image.Image:
    blocks: list[Image.Image] = []
    for title, matrix in items:
        matrix = np.asarray(matrix)
        h, w = matrix.shape[:2]
        img = Image.new("RGB", (max(210, w * cell + 32), h * cell + 72), "white")
        draw = ImageDraw.Draw(img)
        draw.text((16, 12), title, fill=TEXT, font=F18)
        ox, oy = 16, 48
        for y in range(h):
            for x in range(w):
                value = int(matrix[y, x])
                fill = (240, 248, 255) if value else (42, 48, 58)
                box = (ox + x * cell, oy + y * cell, ox + (x + 1) * cell, oy + (y + 1) * cell)
                draw.rectangle(box, fill=fill, outline=LINE)
                draw.text((box[0] + 11, box[1] + 7), str(value), fill=TEXT if value else "white", font=F14)
        blocks.append(img)
    return panel_grid([(f"", block) for block in blocks], cell_w=max(260, blocks[0].width + 26), cell_h=blocks[0].height + 28, cols=len(blocks))


def threshold_contours(src: np.ndarray, threshold: int = 127, mode: int = cv2.RETR_LIST) -> tuple[np.ndarray, list[np.ndarray], np.ndarray | None]:
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(binary, mode, cv2.CHAIN_APPROX_SIMPLE)
    return binary, list(contours), hierarchy


def largest_contour(contours: list[np.ndarray]) -> np.ndarray:
    return max(contours, key=cv2.contourArea)


def hausdorff(a: np.ndarray, b: np.ndarray) -> float:
    aa = a.reshape(-1, 2).astype(np.float32)
    bb = b.reshape(-1, 2).astype(np.float32)
    d = np.sqrt(((aa[:, None, :] - bb[None, :, :]) ** 2).sum(axis=2))
    return float(max(d.min(axis=1).max(), d.min(axis=0).max()))


def rebuild_ch11() -> None:
    d = SAMPLE_DIR / "ch11"
    out = "chapters/images/ch11"
    hung = read_cv(d / "hung.jpg")
    border = read_cv(d / "border.jpg")
    save(panel_grid([
        ("src", hung),
        ("blur 3x3", cv2.blur(hung, (3, 3))),
        ("blur 5x5", cv2.blur(hung, (5, 5))),
        ("blur 7x7", cv2.blur(hung, (7, 7))),
    ], cols=4, title="Mean filter"), f"{out}/ch11_blur_hung_compare_01.png")
    save(panel_grid([("src", hung), ("blur 29x29", cv2.blur(hung, (29, 29)))], cols=2, title="Large mean filter"), f"{out}/ch11_blur_hung_compare_02.png")
    save(panel_grid([
        ("src", hung),
        ("boxFilter 2x2", cv2.boxFilter(hung, -1, (2, 2), normalize=0)),
        ("boxFilter 3x3", cv2.boxFilter(hung, -1, (3, 3), normalize=0)),
        ("boxFilter 5x5", cv2.boxFilter(hung, -1, (5, 5), normalize=0)),
    ], cols=4, title="boxFilter without normalization"), f"{out}/ch11_mean_gaussian_compare.png")
    save(matrix_image([
        ("source", np.array([[66, 18, 10], [34, 190, 28], [26, 43, 57]], dtype=np.uint8)),
        ("sorted", np.sort(np.array([66, 18, 10, 34, 190, 28, 26, 43, 57], dtype=np.uint8)).reshape(3, 3)),
        ("median", np.array([[0, 0, 0], [0, 43, 0], [0, 0, 0]], dtype=np.uint8)),
    ], cell=44), f"{out}/ch11_median_array_example.png")
    save(panel_grid([
        ("src", hung),
        ("median 3x3", cv2.medianBlur(hung, 3)),
        ("median 5x5", cv2.medianBlur(hung, 5)),
        ("median 7x7", cv2.medianBlur(hung, 7)),
    ], cols=4, title="Median filter"), f"{out}/ch11_median_hung_compare.png")
    save(panel_grid([
        ("src", hung),
        ("Gaussian 3x3", cv2.GaussianBlur(hung, (3, 3), 0, 0)),
        ("Gaussian 5x5", cv2.GaussianBlur(hung, (5, 5), 0, 0)),
        ("Gaussian 29x29", cv2.GaussianBlur(hung, (29, 29), 0, 0)),
    ], cols=4, title="Gaussian filter"), f"{out}/ch11_gaussian_hung_compare.png")
    save(panel_grid([
        ("src", border),
        ("blur 3x3", cv2.blur(border, (3, 3))),
        ("blur 7x7", cv2.blur(border, (7, 7))),
        ("Gaussian 3x3", cv2.GaussianBlur(border, (3, 3), 0, 0)),
        ("Gaussian 7x7", cv2.GaussianBlur(border, (7, 7), 0, 0)),
    ], cols=5, title="2D kernel edge comparison"), f"{out}/ch11_2d_kernel_compare.png")
    save(panel_grid([
        ("src", hung),
        ("blur 15x15", cv2.blur(hung, (15, 15))),
        ("Gaussian 15x15", cv2.GaussianBlur(hung, (15, 15), 0, 0)),
        ("bilateral", cv2.bilateralFilter(hung, 15, 100, 100)),
    ], cols=4, title="Bilateral filter"), f"{out}/ch11_bilateral_compare.png")
    kernel = np.ones((5, 5), np.float32) / 25
    save(panel_grid([("src", hung), ("filter2D 5x5 average", cv2.filter2D(hung, -1, kernel))], cols=2, title="Custom average kernel"), f"{out}/ch11_custom_kernel_compare.png")
    # Exercises are references without matching source files; crop the old page text away by redrawing clean panels from source images.
    save(panel_grid([("original", hung), ("median 7x7", cv2.medianBlur(hung, 7)), ("Gaussian 29x29", cv2.GaussianBlur(hung, (29, 29), 0))], cols=3, title="Chapter 11 exercise reference"), f"{out}/ch11_exercise_01_03.jpg")
    save(panel_grid([("blur", cv2.blur(hung, (15, 15))), ("Gaussian", cv2.GaussianBlur(hung, (15, 15), 0)), ("bilateral", cv2.bilateralFilter(hung, 15, 100, 100))], cols=3, title="Filter comparison exercise"), f"{out}/ch11_exercise_compare_01.png")


def rebuild_ch12() -> None:
    d = SAMPLE_DIR / "ch12"
    out = "chapters/images/ch12"
    src = np.zeros((7, 7), np.uint8)
    src[1:6, 1:6] = 1
    kernel = np.ones((3, 3), np.uint8)
    save(matrix_image([("src", src), ("kernel", kernel), ("erosion", cv2.erode(src, kernel))]), f"{out}/ch12_erode_array_result.png")
    src2 = np.zeros((7, 7), np.uint8)
    src2[2:5, 2:5] = 1
    save(matrix_image([("src", src2), ("kernel", kernel), ("dilation", cv2.dilate(src2, kernel))]), f"{out}/ch12_dilate_array_result.png")

    def op_panel(name: str, image: str, op: str, sizes: list[int]) -> Image.Image:
        src_img = read_cv(d / image)
        panels: list[tuple[str, np.ndarray]] = [("src", src_img)]
        for size in sizes:
            k = np.ones((size, size), np.uint8)
            if op == "erode":
                panels.append((f"erode {size}x{size}", cv2.erode(src_img, k)))
            elif op == "dilate":
                panels.append((f"dilate {size}x{size}", cv2.dilate(src_img, k)))
            elif op == "open":
                panels.append((f"open {size}x{size}", cv2.morphologyEx(src_img, cv2.MORPH_OPEN, k)))
            elif op == "close":
                panels.append((f"close {size}x{size}", cv2.morphologyEx(src_img, cv2.MORPH_CLOSE, k)))
            elif op == "gradient":
                panels.append((f"gradient {size}x{size}", cv2.morphologyEx(src_img, cv2.MORPH_GRADIENT, k)))
            elif op == "tophat":
                panels.append((f"tophat {size}x{size}", cv2.morphologyEx(src_img, cv2.MORPH_TOPHAT, k)))
            elif op == "blackhat":
                panels.append((f"blackhat {size}x{size}", cv2.morphologyEx(src_img, cv2.MORPH_BLACKHAT, k)))
        return panel_grid(panels, cols=len(panels), title=name)

    save(op_panel("Erosion kernel comparison", "bw.jpg", "erode", [5, 11]), f"{out}/ch12_erode_kernel_compare.png")
    save(op_panel("Dilation kernel comparison", "bw_dilate.jpg", "dilate", [5, 11]), f"{out}/ch12_dilate_kernel_compare.png")
    save(op_panel("Erosion removes noise", "bw_noise.jpg", "erode", [3, 5]), f"{out}/ch12_erosion_binary_results.jpg")
    save(op_panel("Color image erosion", "whilster.jpg", "erode", [3, 5]), f"{out}/ch12_erosion_color_result.jpg")
    save(op_panel("Letter dilation", "a.jpg", "dilate", [3, 5]), f"{out}/ch12_dilation_letter_a_result.jpg")
    save(op_panel("Binary dilation", "bw_dilate.jpg", "dilate", [5, 11]), f"{out}/ch12_dilation_binary_results.jpg")
    save(op_panel("Opening binary tree", "btree.jpg", "open", [3]), f"{out}/ch12_opening_tree_result.png")
    save(op_panel("Opening night image", "night.jpg", "open", [9]), f"{out}/ch12_opening_night_result.png")
    save(op_panel("Opening night image", "night.jpg", "open", [9]), f"{out}/ch12_opening_night_result.jpg")
    save(op_panel("Closing snowman", "snowman.jpg", "close", [11]), f"{out}/ch12_closing_snowman_result.jpg")
    save(op_panel("Closing smile", "snowman1.jpg", "close", [11]), f"{out}/ch12_closing_smile_result.png")
    night = read_cv(d / "night.jpg")
    mid = cv2.dilate(night, np.ones((9, 9), np.uint8))
    dst = cv2.erode(mid, np.ones((9, 9), np.uint8))
    save(panel_grid([("src", night), ("dilate 9x9", mid), ("erode after dilation", dst)], cols=3, title="Manual closing"), f"{out}/ch12_closing_snowman_shifted_result.jpg")
    save(op_panel("Morphological gradient: K", "k.jpg", "gradient", [5]), f"{out}/ch12_gradient_result.png")
    save(op_panel("Morphological gradient: K", "k.jpg", "gradient", [5]), f"{out}/ch12_gradient_k_result.jpg")
    save(op_panel("Morphological gradient: city", "hole.jpg", "gradient", [5]), f"{out}/ch12_gradient_city_result.jpg")
    save(op_panel("Tophat binary tree", "btree.jpg", "tophat", [3]), f"{out}/ch12_tophat_result.png")
    save(op_panel("Tophat snowman", "snowman.jpg", "tophat", [9]), f"{out}/ch12_tophat_snowman_result.jpg")
    save(op_panel("Tophat city", "hole.jpg", "tophat", [9]), f"{out}/ch12_tophat_city_result.jpg")
    save(op_panel("Blackhat snowman", "snowman.jpg", "blackhat", [11]), f"{out}/ch12_blackhat_result.png")
    save(op_panel("Blackhat snowman", "snowman.jpg", "blackhat", [11]), f"{out}/ch12_blackhat_snowman_result.jpg")
    save(op_panel("Blackhat book cover", "excel.jpg", "blackhat", [11]), f"{out}/ch12_blackhat_excel_result.jpg")
    mats = [
        ("MORPH_RECT", cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))),
        ("MORPH_ELLIPSE", cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))),
        ("MORPH_CROSS", cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))),
    ]
    save(matrix_image(mats, cell=38), f"{out}/ch12_getstructuringelement_kernel_demo.jpg")
    circ = read_cv(d / "bw_circle.jpg")
    panels = [("src", circ)]
    for name, shape in [("MORPH_RECT", cv2.MORPH_RECT), ("MORPH_ELLIPSE", cv2.MORPH_ELLIPSE), ("MORPH_CROSS", cv2.MORPH_CROSS)]:
        panels.append((name, cv2.dilate(circ, cv2.getStructuringElement(shape, (39, 39)))))
    save(panel_grid(panels, cols=4, title="Structuring element shapes"), f"{out}/ch12_getstructuringelement_shape_results.jpg")
    save(panel_grid([("erode 5x5", cv2.erode(read_cv(d / "bw_circle.jpg"), np.ones((5, 5), np.uint8))), ("dilate 5x5", cv2.dilate(read_cv(d / "bw_circle.jpg"), np.ones((5, 5), np.uint8)))], cols=2, title="Exercise reference 1"), f"{out}/ch12_exercise_ref_1.png")
    save(panel_grid([("open night", cv2.morphologyEx(read_cv(d / "night.jpg"), cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))), ("close night", cv2.morphologyEx(read_cv(d / "night.jpg"), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)))], cols=2, title="Exercise reference 2"), f"{out}/ch12_exercise_ref_2.png")
    save(op_panel("Temple gradient exercise", "church.jpg", "gradient", [5]), f"{out}/ch12_exercise_temple_gradient.jpg")
    save(op_panel("Book blackhat exercise", "excel.jpg", "blackhat", [9]), f"{out}/ch12_exercise_book_blackhat.jpg")
    save(draw_morph_theory("erosion"), f"{out}/ch12_erosion_theory_diagram.jpg")
    save(draw_morph_theory("dilation"), f"{out}/ch12_dilation_theory_diagram.jpg")
    save(panel_grid([("src", read_cv(d / "btree.jpg")), ("hit-or-miss style result", cv2.morphologyEx(read_cv(d / "btree.jpg"), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)))], cols=2, title="Hit-or-miss concept"), f"{out}/ch12_hitmiss_result.png")
    save(op_panel("Opening binary tree", "btree.jpg", "open", [3]), f"{out}/ch12_opening_binary_tree_result.jpg")


def draw_morph_theory(kind: str) -> Image.Image:
    image = Image.new("RGB", (980, 430), "white")
    draw = ImageDraw.Draw(image)
    draw.text((32, 24), f"{kind.title()} with a 3x3 kernel", fill=TEXT, font=F24)
    centers = [(160, 220), (480, 220), (800, 220)]
    labels = ["source", "kernel", "result"]
    colors = [(30, 41, 59), (250, 204, 21), (37, 99, 235)]
    for (cx, cy), label, color in zip(centers, labels, colors):
        draw.text((cx - 42, 100), label, fill=TEXT, font=F18)
        for y in range(5):
            for x in range(5):
                box = (cx - 85 + x * 34, cy - 85 + y * 34, cx - 51 + x * 34, cy - 51 + y * 34)
                active = 1 <= x <= 3 and 1 <= y <= 3
                if label == "kernel":
                    active = 1 <= x <= 3 and 1 <= y <= 3
                if label == "result":
                    active = (kind == "erosion" and x == 2 and y == 2) or (kind == "dilation" and 0 <= x <= 4 and 0 <= y <= 4)
                draw.rectangle(box, fill=color if active else (241, 245, 249), outline=LINE)
        if label != "result":
            draw.line((cx + 112, cy, cx + 210, cy), fill=MUTED, width=3)
            draw.polygon([(cx + 210, cy), (cx + 194, cy - 9), (cx + 194, cy + 9)], fill=MUTED)
    return image


def rebuild_ch13() -> None:
    d = SAMPLE_DIR / "ch13"
    out = "chapters/images/ch13"
    save(draw_gradient_examples(), f"{out}/ch13_gradient_examples.png")
    map_img = read_cv(d / "map.jpg")
    save(panel_grid([("src", map_img), ("Sobel x", cv2.Sobel(map_img, -1, 1, 0))], cols=2, title="Sobel x direction"), f"{out}/ch13_sobel_x_result.png")
    sobely = cv2.convertScaleAbs(cv2.Sobel(map_img, cv2.CV_32F, 0, 1))
    save(panel_grid([("src", map_img), ("Sobel y", sobely)], cols=2, title="Sobel y direction"), f"{out}/ch13_sobel_y_result.png")
    lena = read_cv(d / "lena.jpg")
    sx = cv2.convertScaleAbs(cv2.Sobel(lena, cv2.CV_32F, 1, 0))
    sy = cv2.convertScaleAbs(cv2.Sobel(lena, cv2.CV_32F, 0, 1))
    sobel = cv2.addWeighted(sx, 0.5, sy, 0.5, 0)
    save(panel_grid([("src", lena), ("Sobel x", sx), ("Sobel y", sy), ("combined", sobel)], cols=4, title="Sobel on lena"), f"{out}/ch13_sobel_lena_result.png")
    snow = read_cv(d / "snow.jpg")
    shx = cv2.convertScaleAbs(cv2.Scharr(snow, cv2.CV_32F, 1, 0))
    shy = cv2.convertScaleAbs(cv2.Scharr(snow, cv2.CV_32F, 0, 1))
    scharr = cv2.addWeighted(shx, 0.5, shy, 0.5, 0)
    save(panel_grid([("src", snow), ("Scharr x", shx), ("Scharr y", shy), ("Scharr", scharr)], cols=4, title="Scharr"), f"{out}/ch13_scharr_result.png")
    geneva = read_cv(d / "geneva.jpg", cv2.IMREAD_GRAYSCALE)
    geneva_blur = cv2.GaussianBlur(geneva, (3, 3), 0)
    sob = cv2.addWeighted(cv2.convertScaleAbs(cv2.Sobel(geneva_blur, cv2.CV_32F, 1, 0)), 0.5, cv2.convertScaleAbs(cv2.Sobel(geneva_blur, cv2.CV_32F, 0, 1)), 0.5, 0)
    sch = cv2.addWeighted(cv2.convertScaleAbs(cv2.Scharr(geneva_blur, cv2.CV_32F, 1, 0)), 0.5, cv2.convertScaleAbs(cv2.Scharr(geneva_blur, cv2.CV_32F, 0, 1)), 0.5, 0)
    lap = cv2.convertScaleAbs(cv2.Laplacian(geneva_blur, cv2.CV_32F, ksize=3))
    save(panel_grid([("src", geneva), ("Sobel", sob), ("Scharr", sch), ("Laplacian", lap)], cols=4, title="Sobel, Scharr and Laplacian"), f"{out}/ch13_scharr_lena_result.png")
    lap_src = read_cv(d / "laplacian.jpg")
    save(panel_grid([("src", lap_src), ("Laplacian", cv2.convertScaleAbs(cv2.Laplacian(lap_src, cv2.CV_32F)))], cols=2, title="Laplacian"), f"{out}/ch13_laplacian_result.png")
    save(panel_grid([("src", geneva_blur), ("Sobel", sob), ("Scharr", sch), ("Laplacian", lap)], cols=4, title="Gradient comparison"), f"{out}/ch13_laplacian_lena_result.png")
    lena_gray = read_cv(d / "lena.jpg", cv2.IMREAD_GRAYSCALE)
    save(panel_grid([("src", lena_gray), ("Canny 50/100", cv2.Canny(lena_gray, 50, 100)), ("Canny 50/200", cv2.Canny(lena_gray, 50, 200))], cols=3, title="Canny thresholds"), f"{out}/ch13_canny_lena_result.png")
    circle = np.zeros((260, 260), np.uint8)
    cv2.circle(circle, (130, 130), 92, 255, -1)
    save(panel_grid([("src", circle), ("Sobel", cv2.Sobel(circle, -1, 1, 0)), ("Canny", cv2.Canny(circle, 50, 160))], cols=3, title="Exercise circle edge detection"), f"{out}/ch13_exercise_circle_ref.png")
    whilster = read_cv(d / "whilster.jpg")
    save(panel_grid([("src", whilster), ("Sobel", cv2.convertScaleAbs(cv2.Sobel(whilster, cv2.CV_32F, 1, 1))), ("Canny", cv2.Canny(cv2.cvtColor(whilster, cv2.COLOR_BGR2GRAY), 60, 180))], cols=3, title="Exercise reference"), f"{out}/ch13_exercise_03_05.jpg")
    board = read_cv(d / "board.jpg")
    save(panel_grid([("src", board), ("Sobel", cv2.convertScaleAbs(cv2.Sobel(board, cv2.CV_32F, 1, 1))), ("Canny", cv2.Canny(cv2.cvtColor(board, cv2.COLOR_BGR2GRAY), 80, 180))], cols=3, title="Exercise summary"), f"{out}/ch13_exercise_refs.png")


def draw_gradient_examples() -> Image.Image:
    image = Image.new("RGB", (920, 320), "white")
    draw = ImageDraw.Draw(image)
    draw.text((28, 18), "Image gradients emphasize intensity changes", fill=TEXT, font=F24)
    for i, (title, axis) in enumerate([("Sobel X", "x"), ("Sobel Y", "y"), ("Laplacian", "xy")]):
        x0 = 55 + i * 295
        draw.text((x0, 72), title, fill=TEXT, font=F18)
        arr = np.zeros((150, 220), np.uint8)
        if axis == "x":
            arr[:, 90:130] = 255
        elif axis == "y":
            arr[55:95, :] = 255
        else:
            cv2.rectangle(arr, (55, 35), (165, 115), 255, 10)
        edge = cv2.Canny(arr, 20, 80)
        thumb = cv_to_pil(edge)
        image.paste(thumb, (x0, 112))
    return image


def rebuild_ch14() -> None:
    d = SAMPLE_DIR / "ch14"
    out = "chapters/images/ch14"
    macau = read_cv(d / "macau.jpg")
    d1, d2, d3 = cv2.pyrDown(macau), cv2.pyrDown(cv2.pyrDown(macau)), cv2.pyrDown(cv2.pyrDown(cv2.pyrDown(macau)))
    save(panel_grid([("src", macau), ("pyrDown 1", d1), ("pyrDown 2", d2), ("pyrDown 3", d3)], cols=4, title="pyrDown"), f"{out}/ch14_1_pyrdown_result.png")
    small = read_cv(d / "macau_small.jpg")
    u1, u2, u3 = cv2.pyrUp(small), cv2.pyrUp(cv2.pyrUp(small)), cv2.pyrUp(cv2.pyrUp(cv2.pyrUp(small)))
    save(panel_grid([("src", small), ("pyrUp 1", u1), ("pyrUp 2", u2), ("pyrUp 3", u3)], cols=4, title="pyrUp"), f"{out}/ch14_2_pyrup_result.png")
    rng = np.random.default_rng(14)
    a = rng.integers(0, 256, size=(2, 3), dtype=np.uint8)
    b = rng.integers(0, 256, size=(2, 3), dtype=np.uint8)
    save(matrix_image([("src1", a), ("src2", b), ("src1 + src2", (a + b).astype(np.uint8))], cell=54), f"{out}/ch14_3_numeric_result.png")
    penguin = read_cv(d / "pengiun.jpg")
    save(panel_grid([("src", penguin), ("src + src", penguin + penguin), ("src - src", penguin - penguin)], cols=3, title="Image add and subtract"), f"{out}/ch14_4_penguin_add_sub.png")
    down = cv2.pyrDown(penguin)
    up = cv2.pyrUp(down)
    save(panel_grid([("src", penguin), ("down then up", up), ("difference", up - penguin)], cols=3, title="pyrDown then pyrUp"), f"{out}/ch14_5_down_up_compare.png")
    up1 = cv2.pyrUp(penguin)
    down1 = cv2.pyrDown(up1)
    save(panel_grid([("src", penguin), ("up then down", down1), ("difference", down1 - penguin)], cols=3, title="pyrUp then pyrDown"), f"{out}/ch14_6_up_down_compare.png")
    g0 = penguin
    g1 = cv2.pyrDown(g0)
    g2 = cv2.pyrDown(g1)
    l0 = g0 - cv2.pyrUp(g1)
    l1 = g1 - cv2.pyrUp(g2)
    save(panel_grid([("G0", g0), ("G1", g1), ("L0", l0), ("L1", l1)], cols=4, title="Laplacian pyramid"), f"{out}/ch14_7_laplacian_diagram.png")
    rec = l0 + cv2.pyrUp(g1)
    save(panel_grid([("src", penguin), ("recovered", rec), ("difference", rec - penguin)], cols=3, title="Recover from Laplacian pyramid"), f"{out}/ch14_8_recover_result.png")
    macau_l0 = macau - cv2.pyrUp(cv2.pyrDown(macau), dstsize=(macau.shape[1], macau.shape[0]))
    d1_l0 = d1 - cv2.pyrUp(cv2.pyrDown(d1), dstsize=(d1.shape[1], d1.shape[0]))
    save(panel_grid([("old building source", macau), ("L0", macau_l0)], cols=2, title="Exercise reference"), f"{out}/ch14_ex1_error_and_result.png")
    save(panel_grid([("L0", macau_l0), ("L1", d1_l0)], cols=2, title="Old building Laplacian"), f"{out}/ch14_ex2_old_building_laplacian.png")


def rebuild_ch15() -> None:
    d = SAMPLE_DIR / "ch15"
    out = "chapters/images/ch15"
    easy = read_cv(d / "easy.jpg")
    binary, contours, _ = threshold_contours(easy, 127, cv2.RETR_EXTERNAL)
    dst = cv2.drawContours(easy.copy(), contours, -1, (0, 255, 0), 5)
    save(panel_grid([("src", easy), ("binary", binary), ("contours", dst)], cols=3, title="findContours"), f"{out}/ch15_1_find_contours_result.png")
    save(panel_grid([("src after drawContours", dst), ("src copy", easy)], cols=2, title="Repeated source display"), f"{out}/ch15_1_1_find_contours_repeat_result.png")
    lake = read_cv(d / "lake.jpg")
    binary, contours, _ = threshold_contours(lake, 150, cv2.RETR_LIST)
    mask = np.zeros(lake.shape, np.uint8)
    cv2.drawContours(mask, contours, -1, (255, 255, 255), -1)
    result = cv2.bitwise_and(lake, mask)
    save(panel_grid([("src", lake), ("binary", binary), ("result", result)], cols=3, title="Lake contour mask"), f"{out}/ch15_10_lake_contours_result.png")
    for fname, srcname, mode, title in [
        ("ch15_13_retr_ccomp_result.png", "easy3.jpg", cv2.RETR_CCOMP, "RETR_CCOMP hierarchy"),
        ("ch15_3_hierarchy_result.png", "easy2.jpg", cv2.RETR_LIST, "Contour hierarchy"),
    ]:
        img = read_cv(d / srcname)
        binary, contours, hierarchy = threshold_contours(img, 127, mode)
        drawn = cv2.drawContours(img.copy(), contours, -1, (0, 255, 0), 3)
        lines = [str(hierarchy.tolist() if hierarchy is not None else [])]
        save(panel_grid([("src", img), ("contours", drawn), ("hierarchy", text_image(lines, width=360, line_h=22))], cols=3, title=title), f"{out}/{fname}")
    masks: list[tuple[str, np.ndarray]] = []
    areas: list[str] = []
    for i, c in enumerate(contours_for(read_cv(d / "easy.jpg"), cv2.RETR_EXTERNAL)):
        mask = np.zeros(easy.shape, np.uint8)
        cv2.drawContours(mask, [c], -1, (255, 255, 255), 5)
        masks.append((f"contour {i}", mask))
        areas.append(f"contour {i} area = {cv2.moments(c)['m00']:.1f}")
    save(panel_grid(masks + [("moments", text_image(areas, width=360))], cols=4, title="Area and moments"), f"{out}/ch15_15_area_moments_result.png")
    cent = dst.copy()
    for c in contours_for(easy, cv2.RETR_EXTERNAL):
        m = cv2.moments(c)
        if m["m00"]:
            cv2.circle(cent, (int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"])), 5, (255, 0, 0), -1)
    save(panel_grid([("src", easy), ("centroids", cent)], cols=2, title="Centroids"), f"{out}/ch15_16_centroid_result.png")
    for fname, srcname, title in [
        ("ch15_20_hu_moments_3heart_result.png", "3heart.jpg", "Hu moments: hearts"),
        ("ch15_21_hu_moments_3shapes_result.png", "3shapes.jpg", "Hu moments: shapes"),
    ]:
        img = read_cv(d / srcname)
        cs = contours_for(img, cv2.RETR_LIST)
        lines = []
        for i, c in enumerate(cs[:3]):
            hu = cv2.HuMoments(cv2.moments(c)).flatten()
            lines.append(f"{i}: " + "  ".join(f"{v:.2e}" for v in hu[:4]))
        save(panel_grid([("src", img), ("Hu moments", text_image(lines, width=680))], cols=2, title=title), f"{out}/{fname}")
    myheart = read_cv(d / "myheart.jpg")
    cs = contours_for(myheart, cv2.RETR_LIST)
    lines = [f"contour 0 vs 0 = {cv2.matchShapes(cs[0], cs[0], 1, 0):.6f}", f"contour 0 vs 1 = {cv2.matchShapes(cs[0], cs[1], 1, 0):.6f}", f"contour 0 vs 2 = {cv2.matchShapes(cs[0], cs[2], 1, 0):.6f}"]
    save(panel_grid([("src", myheart), ("matchShapes", text_image(lines, width=420))], cols=2, title="matchShapes"), f"{out}/ch15_22_match_shapes_result.png")
    cloud1 = read_cv(d / "mycloud1.jpg")
    cloud2 = read_cv(d / "mycloud2.jpg")
    explode = read_cv(d / "explode1.jpg")
    c1, c2, c3 = contours_for(cloud1, cv2.RETR_LIST)[0], contours_for(cloud2, cv2.RETR_LIST)[0], contours_for(explode, cv2.RETR_LIST)[0]
    match_lines = [
        f"cloud1 vs cloud1 = {cv2.matchShapes(c1, c1, 1, 0):.6f}",
        f"cloud1 vs cloud2 = {cv2.matchShapes(c1, c2, 1, 0):.6f}",
        f"cloud1 vs explode = {cv2.matchShapes(c1, c3, 1, 0):.6f}",
    ]
    save(panel_grid([("cloud1", cloud1), ("cloud2", cloud2), ("explode", explode), ("Shape Context fallback", text_image(match_lines, width=440))], cols=4, title="Shape Context comparison"), f"{out}/ch15_23_shape_context_result.png")
    haus_lines = [f"cloud1 vs cloud1 = {hausdorff(c1, c1):.3f}", f"cloud1 vs cloud2 = {hausdorff(c1, c2):.3f}", f"cloud1 vs explode = {hausdorff(c1, c3):.3f}"]
    save(panel_grid([("cloud1", cloud1), ("cloud2", cloud2), ("explode", explode), ("Hausdorff", text_image(haus_lines, width=420))], cols=4, title="Hausdorff distance"), f"{out}/ch15_24_hausdorff_result.png")
    save(panel_grid([("easy", easy), ("contours", dst)], cols=2, title="Exercise 1 reference"), f"{out}/ch15_exercise_01.jpg")
    save(panel_grid([("easy1", read_cv(d / "easy1.jpg")), ("heart", read_cv(d / "heart.jpg")), ("3heart", read_cv(d / "3heart.jpg"))], cols=3, title="Exercise 2-3 reference"), f"{out}/ch15_exercise_02_03.jpg")
    save(panel_grid([("cloud1", cloud1), ("cloud2", cloud2), ("explode", explode)], cols=3, title="Exercise 4-5 reference"), f"{out}/ch15_exercise_04_05.jpg")
    save(panel_grid([("heart1", read_cv(d / "heart1.jpg")), ("phone", read_cv(d / "phone.png"))], cols=2, title="Exercise 5-6 reference"), f"{out}/ch15_exercise_05_06.jpg")


def contours_for(img: np.ndarray, mode: int = cv2.RETR_LIST) -> list[np.ndarray]:
    _, contours, _ = threshold_contours(img, 127, mode)
    return sorted(contours, key=cv2.contourArea, reverse=True)


def rebuild_ch16() -> None:
    d = SAMPLE_DIR / "ch16"
    out = "chapters/images/ch16"

    def draw_for(srcname: str, fn) -> tuple[np.ndarray, np.ndarray]:
        src = read_cv(d / srcname)
        cs = contours_for(src, cv2.RETR_LIST)
        dst = src.copy()
        fn(dst, largest_contour(cs), cs)
        return src, dst

    def bounding(dst, c, cs):
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(dst, (x, y), (x + w, y + h), (0, 255, 255), 2)

    src, dst = draw_for("explode1.jpg", bounding)
    x, y, w, h = cv2.boundingRect(largest_contour(contours_for(src)))
    save(panel_grid([("src", src), ("boundingRect", dst), ("values", text_image([f"rect = ({x}, {y}, {w}, {h})"], width=320))], cols=3, title="boundingRect"), f"{out}/ch16_01_result_rect.png")
    src2, dst2 = draw_for("explode2.jpg", bounding)
    save(panel_grid([("explode1", dst), ("explode2", dst2)], cols=2, title="Bounding rectangles"), f"{out}/ch16_02_result_rect_box.png")

    def min_rect(dst, c, cs):
        box = cv2.minAreaRect(c)
        pts = cv2.boxPoints(box).astype(np.int32)
        cv2.drawContours(dst, [pts], 0, (0, 255, 0), 2)

    src, dst = draw_for("explode2.jpg", min_rect)
    save(panel_grid([("src", src), ("minAreaRect", dst)], cols=2, title="Minimum area rectangle"), f"{out}/ch16_04_result_min_rect.png")

    def circle(dst, c, cs):
        (x, y), r = cv2.minEnclosingCircle(c)
        cv2.circle(dst, (int(x), int(y)), int(r), (0, 255, 255), 2)

    src, dst = draw_for("explode3.jpg", circle)
    srcb, dstb = draw_for("explode1.jpg", circle)
    save(panel_grid([("explode3", dst), ("explode1", dstb)], cols=2, title="Minimum enclosing circle"), f"{out}/ch16_05_result_circle.png")

    def ellipse(dst, c, cs):
        cv2.ellipse(dst, cv2.fitEllipse(c), (0, 255, 0), 2)

    src, dst = draw_for("cloud.jpg", ellipse)
    save(panel_grid([("src", src), ("fitEllipse", dst)], cols=2, title="Ellipse fitting"), f"{out}/ch16_07_result_ellipse.png")

    def triangle(dst, c, cs):
        _, tri = cv2.minEnclosingTriangle(c)
        tri = tri.astype(np.int32)
        cv2.polylines(dst, [tri], True, (0, 255, 0), 2)

    src, dst = draw_for("heart.jpg", triangle)
    save(panel_grid([("src", src), ("minEnclosingTriangle", dst)], cols=2, title="Minimum enclosing triangle"), f"{out}/ch16_08_result_triangle.png")
    multiple = read_cv(d / "multiple.jpg")
    cs = contours_for(multiple)
    d1, d2 = multiple.copy(), multiple.copy()
    for c in cs:
        cv2.polylines(d1, [cv2.approxPolyDP(c, 3, True)], True, (0, 255, 0), 2)
        cv2.polylines(d2, [cv2.approxPolyDP(c, 15, True)], True, (0, 255, 0), 2)
    save(panel_grid([("src", multiple), ("epsilon 3", d1), ("epsilon 15", d2)], cols=3, title="approxPolyDP"), f"{out}/ch16_09_result_approx_eps3_15.png")

    def fitline(dst, c, cs):
        rows, cols = dst.shape[:2]
        vx, vy, x, y = cv2.fitLine(c, cv2.DIST_L2, 0, 0.01, 0.01)
        vx, vy, x, y = map(float, (vx[0], vy[0], x[0], y[0]))
        lefty = int((-x * vy / vx) + y)
        righty = int(((cols - x) * vy / vx) + y)
        cv2.line(dst, (0, lefty), (cols - 1, righty), (0, 255, 0), 2)

    src, dst = draw_for("unregular.jpg", fitline)
    save(panel_grid([("src", src), ("fitLine", dst)], cols=2, title="Line fitting"), f"{out}/ch16_10_result_fitline.png")

    def hull(dst, c, cs):
        cv2.polylines(dst, [cv2.convexHull(c)], True, (0, 255, 0), 2)

    for fname, srcname, title in [
        ("ch16_11_result_hull_heart.png", "heart1.jpg", "Convex hull: heart"),
        ("ch16_12_result_hull_hand1.png", "hand1.jpg", "Convex hull: hand1"),
        ("ch16_12_1_result_hull_area_hand1.png", "hand1.jpg", "Convex hull area"),
    ]:
        src, dst = draw_for(srcname, hull)
        panels: list[tuple[str, Image.Image | np.ndarray]] = [("src", src), ("hull", dst)]
        if "area" in title.lower():
            area = cv2.contourArea(cv2.convexHull(largest_contour(contours_for(src))))
            panels.append(("area", text_image([f"convex area = {area:.1f}"], width=340)))
        save(panel_grid(panels, cols=len(panels), title=title), f"{out}/{fname}")
    hand2 = read_cv(d / "hand2.jpg")
    dst = hand2.copy()
    for c in contours_for(hand2):
        cv2.polylines(dst, [cv2.convexHull(c)], True, (0, 255, 0), 2)
    save(panel_grid([("src", hand2), ("all hulls", dst)], cols=2, title="Multiple convex hulls"), f"{out}/ch16_13_result_hull_hand2.png")

    star = read_cv(d / "star.jpg")
    dst = star.copy()
    c = largest_contour(contours_for(star))
    hull_idx = cv2.convexHull(c, returnPoints=False)
    defects = cv2.convexityDefects(c, hull_idx)
    if defects is not None:
        for i in range(defects.shape[0]):
            s, e, f, _ = defects[i, 0]
            cv2.line(dst, tuple(c[s][0]), tuple(c[e][0]), (0, 255, 0), 2)
            cv2.circle(dst, tuple(c[f][0]), 3, (0, 0, 255), -1)
    save(panel_grid([("src", star), ("convexityDefects", dst)], cols=2, title="Convexity defects"), f"{out}/ch16_14_result_defects_star.png")
    heart1 = read_cv(d / "heart1.jpg")
    c = largest_contour(contours_for(heart1))
    h = cv2.convexHull(c)
    hdst = heart1.copy()
    cv2.polylines(hdst, [h], True, (0, 255, 0), 2)
    adst = heart1.copy()
    approx = cv2.approxPolyDP(c, 10, True)
    cv2.polylines(adst, [approx], True, (0, 255, 0), 2)
    save(panel_grid([("convex hull", hdst), ("epsilon 10", adst), ("isConvex", text_image([f"hull = {cv2.isContourConvex(h)}", f"approx = {cv2.isContourConvex(approx)}"], width=330))], cols=3, title="isContourConvex"), f"{out}/ch16_15_result_isconvex_heart.png")
    save(draw_defects_diagram(), f"{out}/ch16_defects_diagram.png")
    save(draw_point_test_diagram(), f"{out}/ch16_point_test_diagram.png")
    for fname, measure in [("ch16_16_result_point_polygon_test.png", True), ("ch16_17_result_point_polygon_test_false.png", False)]:
        dst = heart1.copy()
        cv2.polylines(dst, [h], True, (0, 255, 0), 2)
        points = [("A", (231, 85)), ("B", (150, 100)), ("C", (80, 85))]
        lines = []
        for label, pt in points:
            dist = cv2.pointPolygonTest(h, pt, measure)
            lines.append(f"{label}: {dist:.3f}" if measure else f"{label}: {dist:.0f}")
            cv2.circle(dst, pt, 4, (0, 0, 255), -1)
            cv2.putText(dst, label, (pt[0] + 7, pt[1] + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        save(panel_grid([("points", dst), ("distances", text_image(lines, width=260))], cols=2, title=f"pointPolygonTest measureDist={measure}"), f"{out}/{fname}")
    save(panel_grid([("hand3 substitute", read_cv(d / "hand2.jpg")), ("defects", dst)], cols=2, title="Exercise hand defects"), f"{out}/ch16_ex3_result_hand3_defects.png")
    multi = read_cv(d / "multiple.jpg")
    mdst = multi.copy()
    for c in contours_for(multi):
        cv2.polylines(mdst, [cv2.convexHull(c)], True, (0, 255, 0), 2)
    save(panel_grid([("multiple", multi), ("convex hulls", mdst)], cols=2, title="Exercise multiple stars"), f"{out}/ch16_ex4_result_multistars_defects.png")


def rebuild_ch17() -> None:
    d = SAMPLE_DIR / "ch17"
    out = "chapters/images/ch17"

    explode = read_cv(d / "explode1.jpg")
    explode_binary, explode_contours, _ = threshold_contours(explode)
    explode_cnt = explode_contours[0]

    rect = explode.copy()
    x, y, w, h = cv2.boundingRect(explode_cnt)
    cv2.rectangle(rect, (x, y), (x + w, y + h), (0, 255, 255), 2)
    save(
        panel_grid(
            [
                ("src", explode),
                ("boundingRect", rect),
                ("console", text_image([f"rect = ({x}, {y}, {w}, {h})", f"aspect ratio = {w / h:.6f}"], width=330)),
            ],
            cols=3,
            title="Aspect ratio from contour bounding box",
        ),
        f"{out}/ch17_01_aspect_ratio.png",
    )

    point_lines = [
        f"type(cnt) = {type(explode_cnt)}",
        f"cnt.ndim = {explode_cnt.ndim}",
        f"len(cnt) = {len(explode_cnt)}",
        "first 3 points:",
        *[str(explode_cnt[i].tolist()) for i in range(3)],
    ]
    contour_vis = explode.copy()
    cv2.drawContours(contour_vis, [explode_cnt], 0, (0, 255, 0), 2)
    save(
        panel_grid(
            [("binary", explode_binary), ("contour", contour_vis), ("console", text_image(point_lines, width=370, line_h=26))],
            cols=3,
            title="Contour point array",
        ),
        f"{out}/ch17_02_contour_points.png",
    )

    data1 = np.array([3, 9, 8, 5, 2])
    data2 = np.array([[3, 9], [8, 2], [5, 3]])
    data3 = np.array([[[186, 39]], [[181, 44]], [[180, 44]]])
    arg_lines = [
        "ch17_3.py / ch17_4.py",
        f"data = {data1.tolist()}",
        f"argmax = {data1.argmax()}, value = {data1[data1.argmax()]}",
        f"argmin = {data1.argmin()}, value = {data1[data1.argmin()]}",
        "",
        "ch17_5.py",
        f"data = {data2.tolist()}",
        f"x argmax = {data2[:, 0].argmax()}, pair = {tuple(data2[data2[:, 0].argmax()])}",
        "",
        "ch17_6.py",
        f"data shape = {data3.shape}",
        f"x argmax = {data3[:, :, 0].argmax()}, tuple = {tuple(data3[data3[:, :, 0].argmax()][0])}",
        f"x argmin = {data3[:, :, 0].argmin()}, tuple = {tuple(data3[data3[:, :, 0].argmin()][0])}",
    ]
    save(text_image(arg_lines, width=860, line_h=28, title="argmax / argmin examples"), f"{out}/ch17_03_argmax_argmin.png")

    left = tuple(explode_cnt[explode_cnt[:, :, 0].argmin()][0])
    right = tuple(explode_cnt[explode_cnt[:, :, 0].argmax()][0])
    top = tuple(explode_cnt[explode_cnt[:, :, 1].argmin()][0])
    bottom = tuple(explode_cnt[explode_cnt[:, :, 1].argmax()][0])
    extremes = explode.copy()
    for label, pt, color in [
        ("left", left, (0, 255, 0)),
        ("right", right, (0, 255, 0)),
        ("top", top, (0, 255, 255)),
        ("bottom", bottom, (0, 255, 255)),
    ]:
        cv2.circle(extremes, pt, 5, color, -1)
        cv2.putText(extremes, label, (pt[0] + 7, max(18, pt[1] - 7)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)
    save(
        panel_grid(
            [
                ("src", explode),
                ("extreme points", extremes),
                ("console", text_image([f"left = {left}", f"right = {right}", f"top = {top}", f"bottom = {bottom}"], width=330)),
            ],
            cols=3,
            title="Contour extreme points",
        ),
        f"{out}/ch17_04_extreme_points.png",
    )

    extent_vis = explode.copy()
    cv2.drawContours(extent_vis, [explode_cnt], 0, (0, 255, 0), 2)
    cv2.rectangle(extent_vis, (x, y), (x + w, y + h), (0, 255, 255), 2)
    con_area = cv2.contourArea(explode_cnt)
    square_area = w * h
    save(
        panel_grid(
            [
                ("contour and rect", extent_vis),
                ("values", text_image([f"contour area = {con_area:.1f}", f"rect area = {square_area}", f"extent = {con_area / square_area:.6f}"], width=360)),
            ],
            cols=2,
            title="Extent = contour area / bounding rectangle area",
        ),
        f"{out}/ch17_05_extent.png",
    )

    star = read_cv(d / "star1.jpg")
    _, star_contours, _ = threshold_contours(star)
    star_cnt = star_contours[0]
    star_vis = star.copy()
    cv2.drawContours(star_vis, [star_cnt], 0, (0, 255, 0), 2)
    star_area = cv2.contourArea(star_cnt)
    ed = float(np.sqrt(4 * star_area / np.pi))
    cv2.circle(star_vis, (260, 110), int(ed / 2), (0, 255, 0), 3)
    save(
        panel_grid(
            [("src", star), ("equivalent circle", star_vis), ("console", text_image([f"contour area = {star_area:.1f}", f"equivalent diameter = {ed:.6f}"], width=360))],
            cols=3,
            title="Equivalent diameter",
        ),
        f"{out}/ch17_07_equivalent_diameter.png",
    )

    nz_matrix = np.array([[0, 1, 0, 1, 1], [1, 0, 0, 1, 0], [0, 1, 1, 0, 0]], dtype=np.uint8)
    nonzero = np.nonzero(nz_matrix)
    transposed = np.transpose(nonzero)
    save(
        panel_grid(
            [
                ("matrix", matrix_image([("img", nz_matrix)], cell=38)),
                ("np.nonzero", text_image([f"rows = {nonzero[0].tolist()}", f"cols = {nonzero[1].tolist()}"], width=360)),
                ("transpose", text_image([str(row.tolist()) for row in transposed], width=260, line_h=24)),
            ],
            cols=3,
            title="Numpy nonzero coordinates",
        ),
        f"{out}/ch17_08_nonzero_numpy.png",
    )

    cv_points = cv2.findNonZero(nz_matrix)
    cv_lines = ["cv2.findNonZero(img) returns (x, y):", f"shape = {cv_points.shape}", *[str(pt.tolist()) for pt in cv_points[:8]]]
    save(
        panel_grid(
            [("matrix", matrix_image([("img", nz_matrix)], cell=38)), ("findNonZero", text_image(cv_lines, width=390, line_h=25))],
            cols=2,
            title="OpenCV findNonZero matrix output",
        ),
        f"{out}/ch17_09_nonzero_opencv.png",
    )

    simple = read_cv(d / "simple.jpg")
    simple_gray = cv2.cvtColor(simple, cv2.COLOR_BGR2GRAY)
    _, simple_binary = cv2.threshold(simple_gray, 127, 255, cv2.THRESH_BINARY)
    simple_contours, _ = cv2.findContours(simple_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    simple_cnt = simple_contours[0]
    hollow = np.zeros(simple_gray.shape, np.uint8)
    cv2.drawContours(hollow, [simple_cnt], 0, 255, 1)
    filled = np.zeros(simple_gray.shape, np.uint8)
    cv2.drawContours(filled, [simple_cnt], 0, 255, -1)
    hollow_points_np = np.transpose(np.nonzero(hollow))
    filled_points_np = np.transpose(np.nonzero(filled))
    hollow_points_cv = cv2.findNonZero(hollow)
    filled_points_cv = cv2.findNonZero(filled)
    save(
        panel_grid(
            [
                ("src", simple),
                ("hollow contour", hollow),
                ("filled contour", filled),
                (
                    "counts",
                    text_image(
                        [
                            f"np hollow len = {len(hollow_points_np)}",
                            f"np filled len = {len(filled_points_np)}",
                            f"cv hollow len = {len(hollow_points_cv)}",
                            f"cv filled len = {len(filled_points_cv)}",
                            "first cv hollow:",
                            *[str(pt.tolist()) for pt in hollow_points_cv[:4]],
                        ],
                        width=330,
                        line_h=24,
                    ),
                ),
            ],
            cols=4,
            title="Non-zero pixels from contour masks",
        ),
        f"{out}/ch17_10_find_nonzero.png",
    )

    hand = read_cv(d / "hand.jpg")
    hand_gray = cv2.cvtColor(hand, cv2.COLOR_BGR2GRAY)
    _, hand_binary = cv2.threshold(hand_gray, 50, 255, cv2.THRESH_BINARY)
    hand_contours, _ = cv2.findContours(hand_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    hand_cnt = hand_contours[0]
    hand_mask = np.zeros(hand_gray.shape, np.uint8)
    cv2.drawContours(hand_mask, [hand_cnt], -1, 255, -1)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(hand_gray, mask=hand_mask)
    marked = hand.copy()
    cv2.circle(marked, min_loc, 20, (0, 255, 0), 3)
    cv2.circle(marked, max_loc, 20, (0, 0, 255), 3)
    roi_mask = np.zeros(hand.shape, np.uint8)
    cv2.drawContours(roi_mask, [hand_cnt], -1, (255, 255, 255), -1)
    roi = cv2.bitwise_and(hand, roi_mask)
    save(
        panel_grid(
            [
                ("src", hand),
                ("mask", hand_mask),
                ("min / max", marked),
                ("ROI", roi),
                ("console", text_image([f"min = {min_val:.1f} at {min_loc}", f"max = {max_val:.1f} at {max_loc}"], width=310)),
            ],
            cols=5,
            cell_w=240,
            cell_h=260,
            title="minMaxLoc with mask",
        ),
        f"{out}/ch17_11_minmaxloc_mask.png",
    )

    forest = read_cv(d / "forest.png")
    forest_mean = cv2.mean(forest)
    hand_mean = cv2.mean(hand)
    masked_mean = cv2.mean(hand, mask=hand_mask)
    save(
        panel_grid(
            [
                ("forest", forest),
                ("hand", hand),
                ("hand mask", hand_mask),
                ("masked hand", roi),
                (
                    "mean values",
                    text_image(
                        [
                            f"forest BGR = ({forest_mean[0]:.2f}, {forest_mean[1]:.2f}, {forest_mean[2]:.2f})",
                            f"hand BGR = ({hand_mean[0]:.2f}, {hand_mean[1]:.2f}, {hand_mean[2]:.2f})",
                            f"masked hand BGR = ({masked_mean[0]:.2f}, {masked_mean[1]:.2f}, {masked_mean[2]:.2f})",
                        ],
                        width=420,
                        line_h=27,
                    ),
                ),
            ],
            cols=5,
            cell_w=240,
            cell_h=260,
            title="cv2.mean with and without mask",
        ),
        f"{out}/ch17_12_mean_hand.png",
    )


def draw_defects_diagram() -> Image.Image:
    image = Image.new("RGB", (860, 450), "white")
    draw = ImageDraw.Draw(image)
    draw.text((28, 20), "Convexity defect points", fill=TEXT, font=F24)
    pts = [(150, 320), (260, 120), (360, 315), (265, 250)]
    draw.polygon(pts[:3], outline=GREEN, fill=None)
    draw.line((150, 320, 260, 120, 360, 315, 150, 320), fill=GREEN, width=4)
    draw.line((150, 320, 265, 250, 360, 315), fill=RED, width=4)
    for label, pt, color in [("start", pts[0], BLUE), ("end", pts[2], BLUE), ("far", pts[3], RED)]:
        draw.ellipse((pt[0] - 8, pt[1] - 8, pt[0] + 8, pt[1] + 8), fill=color)
        draw.text((pt[0] + 12, pt[1] - 12), label, fill=TEXT, font=F18)
    draw.text((470, 150), "green: convex hull edge", fill=TEXT, font=F18)
    draw.text((470, 190), "red: contour indentation", fill=TEXT, font=F18)
    draw.text((470, 230), "far: deepest point", fill=TEXT, font=F18)
    return image


def draw_point_test_diagram() -> Image.Image:
    image = Image.new("RGB", (860, 450), "white")
    draw = ImageDraw.Draw(image)
    draw.text((28, 20), "pointPolygonTest", fill=TEXT, font=F24)
    poly = [(270, 95), (395, 210), (330, 355), (170, 355), (105, 210)]
    draw.polygon(poly, outline=GREEN, fill=(235, 253, 245))
    for label, pt, note in [("A", (395, 210), "0 on edge"), ("B", (245, 235), "+ inside"), ("C", (80, 120), "- outside")]:
        draw.ellipse((pt[0] - 7, pt[1] - 7, pt[0] + 7, pt[1] + 7), fill=RED)
        draw.text((pt[0] + 12, pt[1] - 13), f"{label}: {note}", fill=TEXT, font=F18)
    return image


def rebuild_ch18() -> None:
    d = SAMPLE_DIR / "ch18"
    out = "chapters/images/ch18"
    save(draw_ch18_title(), f"{out}/ch18_page_01.png")
    for idx, img in enumerate(draw_hough_theory(), start=2):
        save(img, f"{out}/ch18_page_{idx:02d}.png")
    calendar = read_cv(d / "calendar.jpg")
    cal_edges = cv2.Canny(cv2.cvtColor(calendar, cv2.COLOR_BGR2GRAY), 100, 200)
    cal_dst = calendar.copy()
    lines = cv2.HoughLines(cal_edges, 1, np.pi / 180, 200)
    if lines is not None:
        for line in lines[:80]:
            rho, theta = line[0]
            a, b = np.cos(theta), np.sin(theta)
            x0, y0 = rho * a, rho * b
            x1, y1 = int(x0 + 1000 * (-b)), int(y0 + 1000 * a)
            x2, y2 = int(x0 - 1000 * (-b)), int(y0 - 1000 * a)
            cv2.line(cal_dst, (x1, y1), (x2, y2), (0, 255, 0), 2)
    save(draw_hough_curve_demo(), f"{out}/ch18_page_07.png")
    save(panel_grid([("src", calendar), ("Canny", cal_edges), ("HoughLines", cal_dst)], cols=3, title="HoughLines on calendar"), f"{out}/ch18_page_08.png")
    lane = read_cv(d / "lane.jpg")
    lane_edges = cv2.Canny(cv2.cvtColor(lane, cv2.COLOR_BGR2GRAY), 100, 200)
    lane_dst = lane.copy()
    lines = cv2.HoughLines(lane_edges, 1, np.pi / 180, 150)
    if lines is not None:
        for line in lines[:80]:
            rho, theta = line[0]
            a, b = np.cos(theta), np.sin(theta)
            x0, y0 = rho * a, rho * b
            cv2.line(lane_dst, (int(x0 + 1000 * (-b)), int(y0 + 1000 * a)), (int(x0 - 1000 * (-b)), int(y0 - 1000 * a)), (0, 0, 255), 2)
    save(panel_grid([("src", lane), ("HoughLines", lane_dst)], cols=2, title="Warehouse lane detection"), f"{out}/ch18_page_09.png")
    road = read_cv(d / "roadtest.jpg")
    road_edges = cv2.Canny(cv2.cvtColor(road, cv2.COLOR_BGR2GRAY), 50, 200)
    road_dst = road.copy()
    linesp = cv2.HoughLinesP(road_edges, 1, np.pi / 180, 50, minLineLength=10, maxLineGap=100)
    if linesp is not None:
        for line in linesp:
            x1, y1, x2, y2 = line[0]
            cv2.line(road_dst, (x1, y1), (x2, y2), (255, 0, 0), 3)
    save(panel_grid([("src", road), ("Canny", road_edges), ("HoughLinesP", road_dst)], cols=3, title="Probabilistic Hough transform"), f"{out}/ch18_page_10.png")
    save(draw_hough_circles_syntax(), f"{out}/ch18_page_11.png")
    shapes = read_cv(d / "shapes.jpg")
    circles_dst = hough_circles(shapes, 70, 200)
    save(panel_grid([("src", shapes), ("HoughCircles", circles_dst)], cols=2, title="Circle detection"), f"{out}/ch18_page_12.png")
    lane1 = read_cv(d / "lane1.jpg")
    lane1_edges = cv2.Canny(cv2.cvtColor(lane1, cv2.COLOR_BGR2GRAY), 100, 200)
    lane1_dst = lane1.copy()
    lines = cv2.HoughLines(lane1_edges, 1, np.pi / 180, 150)
    if lines is not None:
        for line in lines[:80]:
            rho, theta = line[0]
            a, b = np.cos(theta), np.sin(theta)
            x0, y0 = rho * a, rho * b
            cv2.line(lane1_dst, (int(x0 + 1000 * (-b)), int(y0 + 1000 * a)), (int(x0 - 1000 * (-b)), int(y0 - 1000 * a)), (0, 0, 255), 2)
    save(panel_grid([("src", lane1), ("exercise result", lane1_dst)], cols=2, title="Exercise lane reference"), f"{out}/ch18_page_13.png")
    save(panel_grid([("src", shapes), ("all circles", hough_circles(shapes, 20, 220, param2=20))], cols=2, title="Exercise circle reference"), f"{out}/ch18_page_14.png")


def hough_circles(src: np.ndarray, min_radius: int, max_radius: int, param2: int = 30) -> np.ndarray:
    dst = src.copy()
    blur = cv2.medianBlur(src, 5)
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 100, param1=50, param2=param2, minRadius=min_radius, maxRadius=max_radius)
    if circles is not None:
        for x, y, r in np.uint16(np.around(circles))[0]:
            cv2.circle(dst, (int(x), int(y)), int(r), (0, 255, 0), 3)
            cv2.circle(dst, (int(x), int(y)), 2, (0, 0, 255), 2)
    return dst


def draw_ch18_title() -> Image.Image:
    image = Image.new("RGB", (980, 420), (255, 247, 252))
    draw = ImageDraw.Draw(image)
    draw.text((70, 70), "Chapter 18", fill=(190, 24, 93), font=font(52, True))
    draw.text((70, 145), "Hough Transform", fill=TEXT, font=font(44, True))
    draw.text((72, 220), "18-1  Hough basics", fill=TEXT, font=F24)
    draw.text((72, 260), "18-2  HoughLines()", fill=TEXT, font=F24)
    draw.text((72, 300), "18-3  HoughLinesP()", fill=TEXT, font=F24)
    draw.text((72, 340), "18-4  HoughCircles()", fill=TEXT, font=F24)
    for x in range(610, 900, 42):
        draw.line((x, 80, x, 340), fill=(244, 114, 182), width=2)
    for y in range(80, 360, 42):
        draw.line((590, y, 900, y), fill=(244, 114, 182), width=2)
    draw.line((620, 320, 875, 120), fill=BLUE, width=5)
    draw.line((720, 80, 720, 350), fill=GREEN, width=5)
    return image


def draw_hough_theory() -> list[Image.Image]:
    return [
        draw_axes("Point and line in Cartesian space", [(0, 0), (1, 2), (-2, -3)], [(80, 280, 430, 90)]),
        draw_axes("Line maps to a point in Hough space", [(1, 2)], [(80, 280, 430, 90)], hough=True),
        draw_axes("Two points intersect in parameter space", [(1, 2), (-2, -3)], [(80, 280, 430, 90), (100, 110, 420, 270)], hough=True),
        draw_polar(),
        draw_axes("Polar Hough line: rho = x cos theta + y sin theta", [(2, 1)], [(220, 320, 390, 105)], polar=True),
    ]


def draw_axes(title: str, points: list[tuple[int, int]], lines: list[tuple[int, int, int, int]], *, hough: bool = False, polar: bool = False) -> Image.Image:
    image = Image.new("RGB", (980, 500), "white")
    draw = ImageDraw.Draw(image)
    draw.text((28, 20), title, fill=TEXT, font=F24)
    ox, oy = 250, 275
    draw.line((70, oy, 455, oy), fill=MUTED, width=2)
    draw.line((ox, 95, ox, 430), fill=MUTED, width=2)
    draw.text((462, oy - 8), "x", fill=TEXT, font=F18)
    draw.text((ox + 8, 82), "y", fill=TEXT, font=F18)
    for line in lines:
        draw.line(line, fill=BLUE, width=4)
    for px, py in points:
        x, y = ox + px * 55, oy - py * 55
        draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=RED)
        draw.text((x + 10, y - 12), f"({px},{py})", fill=TEXT, font=F16)
    if hough:
        hx, hy = 700, 275
        draw.line((550, hy, 900, hy), fill=MUTED, width=2)
        draw.line((hx, 110, hx, 420), fill=MUTED, width=2)
        draw.text((905, hy - 8), "m", fill=TEXT, font=F18)
        draw.text((hx + 8, 96), "b", fill=TEXT, font=F18)
        draw.line((565, 360, 880, 150), fill=GREEN, width=3)
        draw.line((570, 165, 870, 355), fill=AMBER, width=3)
        draw.ellipse((695, 258, 709, 272), fill=RED)
    if polar:
        draw.arc((575, 170, 835, 430), 210, 300, fill=AMBER, width=4)
        draw.line((700, 300, 860, 210), fill=GREEN, width=4)
        draw.text((780, 230), "rho", fill=TEXT, font=F18)
        draw.text((610, 345), "theta", fill=TEXT, font=F18)
    return image


def draw_polar() -> Image.Image:
    image = Image.new("RGB", (820, 520), "white")
    draw = ImageDraw.Draw(image)
    draw.text((28, 20), "Polar coordinate basics", fill=TEXT, font=F24)
    cx, cy, r = 380, 290, 170
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=LINE, width=3)
    draw.line((cx - 230, cy, cx + 230, cy), fill=MUTED, width=2)
    draw.line((cx, cy + 210, cx, cy - 210), fill=MUTED, width=2)
    px, py = cx + 120, cy - 95
    draw.line((cx, cy, px, py), fill=GREEN, width=4)
    draw.line((px, py, px, cy), fill=RED, width=3)
    draw.arc((cx - 70, cy - 70, cx + 70, cy + 70), 318, 360, fill=AMBER, width=4)
    draw.text((px + 10, py - 10), "(r cos theta, r sin theta)", fill=TEXT, font=F18)
    draw.text((cx + 70, cy - 28), "theta", fill=TEXT, font=F18)
    draw.text((cx + 55, cy - 70), "r", fill=TEXT, font=F18)
    return image


def draw_hough_curve_demo() -> Image.Image:
    image = Image.new("RGB", (980, 420), "white")
    draw = ImageDraw.Draw(image)
    draw.text((28, 18), "Several image points vote in Hough space", fill=TEXT, font=F24)
    for x0, color in [(120, BLUE), (180, GREEN), (240, AMBER)]:
        pts = []
        for t in range(0, 180, 3):
            x = 560 + t * 2
            y = 225 - int(80 * math.sin(math.radians(t + x0)))
            pts.append((x, y))
        draw.line(pts, fill=color, width=3)
    draw.ellipse((730 - 8, 225 - 8, 730 + 8, 225 + 8), fill=RED)
    draw.text((745, 208), "intersection = detected line", fill=TEXT, font=F18)
    draw.line((70, 320, 380, 100), fill=BLUE, width=4)
    for pt in [(140, 270), (230, 205), (320, 142)]:
        draw.ellipse((pt[0] - 7, pt[1] - 7, pt[0] + 7, pt[1] + 7), fill=RED)
    return image


def draw_hough_circles_syntax() -> Image.Image:
    lines = [
        "circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, dp, minDist,",
        "                           param1=50, param2=30,",
        "                           minRadius=70, maxRadius=200)",
        "",
        "x, y, r = circle center and radius",
        "Use medianBlur before detection to reduce noise.",
    ]
    return text_image(lines, width=980, line_h=34, title="HoughCircles parameters")


def update_html() -> None:
    ch15 = CHAPTER_DIR / "ch15.html"
    text = ch15.read_text(encoding="utf-8")
    text = text.replace("images/ch15/ch15_23_shape_context_result.png\" alt=\"ch15_24.py Hausdorff Distance 执行结果", "images/ch15/ch15_24_hausdorff_result.png\" alt=\"ch15_24.py Hausdorff Distance 执行结果")
    ch15.write_text(text, encoding="utf-8")

    ch18 = CHAPTER_DIR / "ch18.html"
    text = ch18.read_text(encoding="utf-8")
    replacements = {
        "原书第 18-1 页裁切：本章标题与 18-1、18-2、18-3、18-4 小节目录。": "重建图：本章标题与 18-1、18-2、18-3、18-4 小节目录。",
        "原书第 18-2 页裁切：笛卡儿座标中的点与直线方程式示意图。": "重建图：笛卡儿座标中的点与直线方程式示意图。",
        "原书第 18-3 页裁切：笛卡儿直线映射到霍夫空间中的点。": "重建图：笛卡儿直线映射到霍夫空间中的点。",
        "原书第 18-4 页裁切：单点映射成直线、两点映射成霍夫空间交点。": "重建图：单点映射成直线、两点映射成霍夫空间交点。",
        "原书第 18-5 页裁切：极座标 <code>(r cosθ, r sinθ)</code> 与半径分量。": "重建图：极座标 <code>(r cosθ, r sinθ)</code> 与半径分量。",
        "原书第 18-6 页裁切：垂直线、极座标直线与霍夫空间点的对应关系。": "重建图：垂直线、极座标直线与霍夫空间点的对应关系。",
        "原书第 18-7 页裁切：极座标空间的多条曲线交会示意。": "重建图：极座标空间的多条曲线交会示意。",
        "原书第 18-8 页裁切：原始图像、Canny 边缘图像与 <code>HoughLines()</code> 检测结果。": "重建图：原始图像、Canny 边缘图像与 <code>HoughLines()</code> 检测结果。",
        "原书第 18-9 页裁切：仓库道路原图与直线检测结果。": "重建图：仓库道路原图与直线检测结果。",
        "原书第 18-10 页裁切：道路、Canny 边缘与 <code>HoughLinesP()</code> 车道线检测结果。": "重建图：道路、Canny 边缘与 <code>HoughLinesP()</code> 车道线检测结果。",
        "原书第 18-11 页裁切：<code>HoughCircles()</code> 语法与核心参数说明表。": "重建图：<code>HoughCircles()</code> 语法与核心参数说明表。",
        "原书第 18-12 页裁切：检测半径大于 70 的圆圈，并以绿色外圈与红色中心点标示。": "重建图：检测半径大于 70 的圆圈，并以绿色外圈与红色中心点标示。",
        "原书第 18-13 页裁切：习题 1 的 <code>lane2.jpg</code> 仓库道路检测参考输出。": "重建图：习题 1 的仓库道路检测参考输出。",
        "原书第 18-13 页下方裁切：习题 2 的全部圆圈检测参考输出。": "重建图：习题 2 的全部圆圈检测参考输出。",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = text.replace('alt="第 18 章习题 lane2 仓库道路图像"', 'alt="第 18 章习题仓库道路图像"')
    ch18.write_text(text, encoding="utf-8")
    print("updated chapters/ch15.html and chapters/ch18.html")


def audit() -> int:
    issues = 0
    print("\nAudit ch11-ch18 referenced images")
    for ch in range(11, 19):
        html_file = CHAPTER_DIR / f"ch{ch:02d}.html"
        parser = ImgParser()
        parser.feed(html_file.read_text(encoding="utf-8"))
        for line, src, alt in parser.refs:
            if not re.search(r"images/ch1[1-8]/", src):
                continue
            path = CHAPTER_DIR / src
            if not path.exists():
                print(f"missing {html_file.name}:{line} {src}")
                issues += 1
                continue
            with Image.open(path) as im:
                w, h = im.size
            if w > 1800 or h > 1800:
                print(f"large {html_file.name}:{line} {src} {w}x{h} {alt}")
                issues += 1
            if h > w * 1.55 and h > 900:
                print(f"page-like aspect {html_file.name}:{line} {src} {w}x{h} {alt}")
                issues += 1
    if issues:
        print(f"Audit found {issues} size/aspect warnings.")
    else:
        print("Audit passed: no missing images or very large/page-like referenced images.")
    return issues


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()
    if not args.audit_only:
        rebuild_ch11()
        rebuild_ch12()
        rebuild_ch13()
        rebuild_ch14()
        rebuild_ch15()
        rebuild_ch16()
        rebuild_ch17()
        rebuild_ch18()
        update_html()
    raise SystemExit(1 if audit() else 0)


if __name__ == "__main__":
    main()
