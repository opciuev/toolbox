#!/usr/bin/env python3
"""Rebuild and audit selected ch19-ch25 OpenCV website images.

The rebuild step is intentionally scoped to known bad/high-risk images in
chapters 20, 21, 23, 24, and 25. The audit step only reads ch19-ch25 images and
prints diagnostics, so it can be rerun without creating extra repo artifacts.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager


ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = ROOT / "OpenCV程序实例代码"
IMAGE_ROOT = ROOT / "chapters" / "images"

FONT_CANDIDATES = [
    "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/3419f2a427639ad8c8e139149a287865a90fa17e.asset/AssetData/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]


def cjk_font_path() -> str | None:
    for item in FONT_CANDIDATES:
        if Path(item).exists():
            return item
    return None


FONT_PATH = cjk_font_path()
FONT_PROP = font_manager.FontProperties(fname=FONT_PATH) if FONT_PATH else None


def chapter_src(chapter: int, name: str) -> Path:
    return SRC_ROOT / f"ch{chapter}" / name


def chapter_out(chapter: int, name: str) -> Path:
    return IMAGE_ROOT / f"ch{chapter:02d}" / name


def read_bgr(path: Path) -> np.ndarray:
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(path)
    return img


def bgr_to_rgb(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def save_rgb_image(rgb: np.ndarray, path: Path, scale: float = 1.0) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.fromarray(rgb)
    if scale != 1.0:
        image = image.resize(
            (round(image.width * scale), round(image.height * scale)),
            Image.Resampling.LANCZOS,
        )
    image.save(path)


def save_panels(path: Path, panels: list[tuple[str, np.ndarray]], *, dpi: int = 180) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, len(panels), figsize=(4.0 * len(panels), 3.2))
    if len(panels) == 1:
        axes = [axes]
    fig.patch.set_facecolor("white")
    for axis, (title, image) in zip(axes, panels):
        if image.ndim == 2:
            axis.imshow(image, cmap="gray")
        else:
            axis.imshow(image)
        axis.set_title(title, fontproperties=FONT_PROP, fontsize=13)
        axis.axis("off")
    fig.tight_layout(pad=0.6)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", pad_inches=0.08, facecolor="white")
    plt.close(fig)


def save_digit_card(src_path: Path, out_path: Path, label: str) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    digit = Image.open(src_path).convert("RGB")
    scale = min(560 / digit.width, 560 / digit.height)
    digit = digit.resize(
        (round(digit.width * scale), round(digit.height * scale)),
        Image.Resampling.NEAREST,
    )
    canvas = Image.new("RGB", (720, 720), "white")
    x = (canvas.width - digit.width) // 2
    y = (canvas.height - digit.height) // 2 + 20
    canvas.paste(digit, (x, y))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(FONT_PATH, 34) if FONT_PATH else ImageFont.load_default()
    draw.text((36, 28), label, fill=(40, 40, 40), font=font)
    canvas.save(out_path)


def pil_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    return ImageFont.truetype(FONT_PATH, size) if FONT_PATH else ImageFont.load_default()


def save_pil(image: Image.Image, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(out_path, optimize=True)


def draw_arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], fill: tuple[int, int, int]) -> None:
    draw.line((start, end), fill=fill, width=4)
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    arrow = [
        end,
        (int(end[0] - ux * 20 + px * 9), int(end[1] - uy * 20 + py * 9)),
        (int(end[0] - ux * 20 - px * 9), int(end[1] - uy * 20 - py * 9)),
    ]
    draw.polygon(arrow, fill=fill)


def score_xy(x_score: int, y_score: int, origin: tuple[int, int], scale: float) -> tuple[int, int]:
    return int(origin[0] + x_score * scale), int(origin[1] - y_score * scale)


def department_chart(*, highlight: str | None = None) -> Image.Image:
    image = Image.new("RGB", (980, 700), "white")
    draw = ImageDraw.Draw(image)
    title_font = pil_font(34)
    label_font = pil_font(24)
    small_font = pil_font(20)
    origin = (120, 600)
    scale = 5.0
    axis = (37, 45, 60)
    blue = (37, 99, 235)
    green = (34, 139, 84)
    orange = (230, 126, 34)
    red = (210, 55, 65)

    draw.text((40, 28), "KNN department assignment example", fill=axis, font=title_font)
    draw_arrow(draw, origin, (860, origin[1]), axis)
    draw_arrow(draw, origin, (origin[0], 80), axis)
    draw.text((820, 620), "English", fill=axis, font=label_font)
    draw.text((42, 88), "Social", fill=axis, font=label_font)

    for value in range(0, 101, 20):
        x = origin[0] + value * scale
        y = origin[1] - value * scale
        draw.line((x, origin[1] - 6, x, origin[1] + 6), fill=axis, width=2)
        draw.text((x - 12, origin[1] + 18), str(value), fill=axis, font=small_font)
        draw.line((origin[0] - 6, y, origin[0] + 6, y), fill=axis, width=2)
        draw.text((origin[0] - 48, y - 12), str(value), fill=axis, font=small_font)
        if value:
            draw.line((origin[0], y, 820, y), fill=(232, 236, 244), width=1)
            draw.line((x, 100, x, origin[1]), fill=(232, 236, 244), width=1)

    points = {
        "new": ((60, 55), red, "New employee (60, 55)"),
        "editor": ((80, 60), blue, "Editor avg. (80, 60)"),
        "marketing": ((40, 80), green, "Marketing avg. (40, 80)"),
    }
    if highlight in {"editor", "marketing"}:
        start = score_xy(*points["new"][0], origin, scale)
        end = score_xy(*points[highlight][0], origin, scale)
        draw.line((start, end), fill=orange, width=5)
        mx, my = (start[0] + end[0]) // 2, (start[1] + end[1]) // 2
        label = "distance = 20.6" if highlight == "editor" else "distance = 32.0"
        draw.text((mx + 16, my - 34), label, fill=orange, font=label_font)

    label_offsets = {"new": (18, 18), "editor": (-260, -42), "marketing": (18, -40)}
    for key, ((sx, sy), color, label) in points.items():
        x, y = score_xy(sx, sy, origin, scale)
        draw.ellipse((x - 11, y - 11, x + 11, y + 11), fill=color, outline="white", width=3)
        dx, dy = label_offsets[key]
        draw.text((x + dx, y + dy), label, fill=color, font=label_font)

    draw.rounded_rectangle((590, 440, 940, 620), radius=8, fill=(248, 250, 252), outline=(210, 216, 226))
    draw.text((612, 462), "Nearest neighbor", fill=axis, font=label_font)
    draw.text((612, 502), "20.6 < 32.0", fill=orange, font=label_font)
    draw.text((612, 542), "Assign to editor department", fill=blue, font=label_font)
    return image


def draw_digit_matrix(draw: ImageDraw.ImageDraw, x: int, y: int, values: list[int], title: str, cell: int = 54) -> None:
    title_font = pil_font(26)
    number_font = pil_font(18)
    draw.text((x, y - 40), title, fill=(35, 43, 58), font=title_font)
    for row in range(5):
        for col in range(4):
            value = values[row * 4 + col]
            shade = max(20, 255 - int(value * 5.5))
            box = (x + col * cell, y + row * cell, x + (col + 1) * cell, y + (row + 1) * cell)
            draw.rectangle(box, fill=(shade, shade, shade), outline=(80, 88, 102), width=2)
            fill = "white" if shade < 120 else (32, 40, 54)
            draw.text((box[0] + 14, box[1] + 16), str(value), fill=fill, font=number_font)


def draw_big_digit(draw: ImageDraw.ImageDraw, x: int, y: int, pattern: list[str], title: str, cell: int = 38) -> None:
    draw.text((x, y - 34), title, fill=(35, 43, 58), font=pil_font(24))
    for row, line in enumerate(pattern):
        for col, ch in enumerate(line):
            fill = (34, 44, 60) if ch == "1" else (248, 250, 252)
            box = (x + col * cell, y + row * cell, x + (col + 1) * cell, y + (row + 1) * cell)
            draw.rectangle(box, fill=fill, outline=(190, 198, 211), width=2)


DIGIT5 = [18, 30, 30, 6, 30, 0, 0, 0, 12, 30, 36, 5, 6, 0, 6, 26, 32, 30, 40, 5]
DIGIT8 = [20, 30, 30, 14, 30, 8, 6, 22, 20, 30, 34, 18, 28, 8, 8, 28, 34, 30, 40, 20]
UNKNOWN = [18, 30, 30, 8, 30, 0, 1, 4, 14, 28, 32, 6, 7, 1, 8, 24, 31, 29, 38, 8]


def rebuild_ch25_theory() -> None:
    save_pil(department_chart(), chapter_out(25, "ch25_01_department_knn.png"))
    save_pil(department_chart(highlight="editor"), chapter_out(25, "ch25_02_editor_distance.png"))
    save_pil(department_chart(highlight="marketing"), chapter_out(25, "ch25_03_marketing_distance.png"))

    image = Image.new("RGB", (900, 620), "white")
    draw = ImageDraw.Draw(image)
    draw.text((40, 28), "Digit 5 feature extraction", fill=(35, 43, 58), font=pil_font(34))
    draw_big_digit(draw, 80, 135, ["1110", "1000", "0110", "0001", "1110"], "5 split into 5 x 4 cells")
    draw_digit_matrix(draw, 500, 135, DIGIT5, "Feature counts")
    draw.text((80, 545), "Each grid value counts foreground pixels in that cell.", fill=(90, 103, 120), font=pil_font(22))
    save_pil(image, chapter_out(25, "ch25_04_digit_feature_5.png"))

    image = Image.new("RGB", (980, 500), "white")
    draw = ImageDraw.Draw(image)
    draw.text((40, 28), "Feature comparison: 5 and 8", fill=(35, 43, 58), font=pil_font(34))
    draw_digit_matrix(draw, 120, 145, DIGIT5, "Digit 5")
    draw_digit_matrix(draw, 600, 145, DIGIT8, "Digit 8")
    save_pil(image, chapter_out(25, "ch25_05_digit_5_8_features.png"))

    image = Image.new("RGB", (1240, 650), "white")
    draw = ImageDraw.Draw(image)
    draw.text((40, 28), "Classify an unknown digit by distance", fill=(35, 43, 58), font=pil_font(34))
    draw_digit_matrix(draw, 70, 150, DIGIT5, "Digit 5")
    draw_digit_matrix(draw, 440, 150, DIGIT8, "Digit 8")
    draw_digit_matrix(draw, 810, 150, UNKNOWN, "Unknown")
    draw.rounded_rectangle((360, 535, 880, 615), radius=8, fill=(248, 250, 252), outline=(210, 216, 226))
    draw.text((388, 558), "Nearest feature vector: digit 5", fill=(37, 99, 235), font=pil_font(28))
    save_pil(image, chapter_out(25, "ch25_06_digit_classification.png"))

    image = Image.new("RGB", (900, 560), "white")
    draw = ImageDraw.Draw(image)
    draw.text((40, 28), "Simplified 2 x 2 feature comparison", fill=(35, 43, 58), font=pil_font(34))
    simplified = [("Digit 5", [30, 12, 8, 32]), ("Digit 8", [34, 34, 32, 32]), ("Unknown", [30, 16, 22, 28])]
    for index, (title, values) in enumerate(simplified):
        x = 86 + index * 280
        y = 150
        draw.text((x, y - 42), title, fill=(35, 43, 58), font=pil_font(26))
        for row in range(2):
            for col in range(2):
                value = values[row * 2 + col]
                shade = max(32, 255 - value * 5)
                box = (x + col * 90, y + row * 90, x + (col + 1) * 90, y + (row + 1) * 90)
                draw.rectangle(box, fill=(shade, shade, shade), outline=(82, 94, 110), width=3)
                fill = "white" if shade < 120 else (32, 40, 54)
                draw.text((box[0] + 28, box[1] + 30), str(value), fill=fill, font=pil_font(24))
    draw.text((96, 430), "distance to 5 = 15.1", fill=(37, 99, 235), font=pil_font(24))
    draw.text((392, 430), "distance to 8 = 32.8", fill=(217, 119, 6), font=pil_font(24))
    save_pil(image, chapter_out(25, "ch25_07_simplified_features.png"))


def rebuild_ch20_04() -> None:
    src = read_bgr(chapter_src(20, "shapes.jpg"))
    templ = read_bgr(chapter_src(20, "heart.jpg"))
    height, width = templ.shape[:2]
    result = cv2.matchTemplate(src, templ, cv2.TM_SQDIFF_NORMED)
    _, _, min_loc, _ = cv2.minMaxLoc(result)
    lower_right = (min_loc[0] + width, min_loc[1] + height)
    dst = cv2.rectangle(src.copy(), min_loc, lower_right, (0, 255, 0), 4)
    save_rgb_image(bgr_to_rgb(dst), chapter_out(20, "ch20_04_shapes_single_match_result.png"), scale=2.0)


def grouped_template_locations(result: np.ndarray, threshold: float, width: int, height: int) -> list[tuple[int, int]]:
    raw = np.argwhere(result > threshold)
    scored = sorted(
        ((float(result[row, col]), int(col), int(row)) for row, col in raw),
        reverse=True,
    )
    locations: list[tuple[int, int]] = []
    min_dx = max(6, width // 2)
    min_dy = max(6, height // 2)
    for _, x, y in scored:
        if all(abs(x - old_x) > min_dx or abs(y - old_y) > min_dy for old_x, old_y in locations):
            locations.append((x, y))
    return sorted(locations, key=lambda item: (item[1], item[0]))


def rebuild_ch20_ex02() -> None:
    src = read_bgr(chapter_src(20, "baidu.jpg"))
    templ = read_bgr(chapter_src(20, "mountain_mark.jpg"))
    height, width = templ.shape[:2]
    result = cv2.matchTemplate(src, templ, cv2.TM_CCOEFF_NORMED)
    locations = grouped_template_locations(result, 0.95, width, height)
    dst = src.copy()
    for x, y in locations:
        cv2.rectangle(dst, (x, y), (x + width, y + height), (0, 0, 255), 3)
    save_rgb_image(bgr_to_rgb(dst), chapter_out(20, "ch20_ex02_all_mountains.png"), scale=2.0)


def rebuild_ch20_ex04() -> None:
    start = (450, 180)
    src = read_bgr(chapter_src(20, "airport.jpg"))
    templ = read_bgr(chapter_src(20, "airport_mark.jpg"))
    height, width = templ.shape[:2]
    result = cv2.matchTemplate(src, templ, cv2.TM_CCOEFF_NORMED)
    locations = grouped_template_locations(result, 0.9, width, height)
    centers = [(x + width // 2, y + height // 2) for x, y in locations]
    if not centers:
        raise RuntimeError("No airport markers found in airport.jpg")
    nearest = min(centers, key=lambda point: (point[0] - start[0]) ** 2 + (point[1] - start[1]) ** 2)
    dst = src.copy()
    cv2.circle(dst, start, 10, (255, 0, 0), -1)
    for x, y in locations:
        cv2.rectangle(dst, (x, y), (x + width, y + height), (0, 180, 0), 2)
    cv2.line(dst, start, nearest, (0, 0, 255), 3)
    cv2.circle(dst, nearest, 5, (0, 0, 255), -1)
    save_rgb_image(bgr_to_rgb(dst), chapter_out(20, "ch20_ex04_airport_distance.png"), scale=1.5)


def save_equalize_grid(out_path: Path, rows: list[tuple[str, np.ndarray, np.ndarray]]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(len(rows), 4, figsize=(14, 3.4 * len(rows)))
    if len(rows) == 1:
        axes = np.array([axes])
    fig.patch.set_facecolor("white")
    for row_idx, (label, src, dst) in enumerate(rows):
        row = axes[row_idx]
        row[0].imshow(src, cmap="gray")
        row[0].set_title(f"{label} 原始图像", fontproperties=FONT_PROP, fontsize=12)
        row[1].hist(src.ravel(), 256)
        row[1].set_title("原始直方图", fontproperties=FONT_PROP, fontsize=12)
        row[2].imshow(dst, cmap="gray")
        row[2].set_title(f"{label} 处理后", fontproperties=FONT_PROP, fontsize=12)
        row[3].hist(dst.ravel(), 256)
        row[3].set_title("处理后直方图", fontproperties=FONT_PROP, fontsize=12)
        for axis in (row[0], row[2]):
            axis.axis("off")
    fig.tight_layout(pad=1.0)
    fig.savefig(out_path, dpi=170, bbox_inches="tight", pad_inches=0.08, facecolor="white")
    plt.close(fig)


def rebuild_ch19_problem_images() -> None:
    springfield = cv2.imread(str(chapter_src(19, "springfield.jpg")), cv2.IMREAD_GRAYSCALE)
    highway = cv2.imread(str(chapter_src(19, "highway1.png")), cv2.IMREAD_GRAYSCALE)
    office = cv2.imread(str(chapter_src(19, "office.jpg")), cv2.IMREAD_GRAYSCALE)
    if springfield is None or highway is None or office is None:
        raise FileNotFoundError("missing ch19 source image")

    save_equalize_grid(
        chapter_out(19, "ch19_19_equalize_springfield_highway.png"),
        [
            ("springfield.jpg", springfield, cv2.equalizeHist(springfield)),
            ("highway1.png", highway, cv2.equalizeHist(highway)),
        ],
    )
    save_equalize_grid(
        chapter_out(19, "ch19_21_equalize_office.png"),
        [("office.jpg", office, cv2.equalizeHist(office))],
    )
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    save_equalize_grid(
        chapter_out(19, "ch19_ex01_clahe_springfield.png"),
        [("springfield.jpg CLAHE", springfield, clahe.apply(springfield))],
    )


def best_match_box(src: np.ndarray, templ: np.ndarray) -> tuple[tuple[int, int], tuple[int, int], float]:
    height, width = templ.shape[:2]
    result = cv2.matchTemplate(src, templ, cv2.TM_SQDIFF_NORMED)
    min_val, _, min_loc, _ = cv2.minMaxLoc(result)
    return min_loc, (min_loc[0] + width, min_loc[1] + height), float(min_val)


def draw_single_match(src: np.ndarray, templ: np.ndarray, *, color: tuple[int, int, int] = (0, 255, 0)) -> np.ndarray:
    upper_left, lower_right, _ = best_match_box(src, templ)
    dst = src.copy()
    cv2.rectangle(dst, upper_left, lower_right, color, 3)
    return dst


def draw_threshold_matches(src: np.ndarray, templ: np.ndarray, threshold: float, *, color: tuple[int, int, int]) -> np.ndarray:
    height, width = templ.shape[:2]
    result = cv2.matchTemplate(src, templ, cv2.TM_CCOEFF_NORMED)
    locations = grouped_template_locations(result, threshold, width, height)
    dst = src.copy()
    for x, y in locations:
        cv2.rectangle(dst, (x, y), (x + width, y + height), color, 3)
    return dst


def rebuild_ch20_problem_images() -> None:
    heart = read_bgr(chapter_src(20, "heart.jpg"))
    shapes = read_bgr(chapter_src(20, "shapes.jpg"))
    save_panels(
        chapter_out(20, "ch20_03_shapes_template_source.png"),
        [("heart.jpg 模板", bgr_to_rgb(heart)), ("shapes.jpg 原始图像", bgr_to_rgb(shapes))],
    )

    group = read_bgr(chapter_src(20, "g5.jpg"))
    face = read_bgr(chapter_src(20, "face1.jpg"))
    face_result = draw_single_match(group, face)
    save_panels(
        chapter_out(20, "ch20_05_face_template_source_result.png"),
        [("face1.jpg 模板", bgr_to_rgb(face)), ("g5.jpg 原始图像", bgr_to_rgb(group)), ("匹配结果", bgr_to_rgb(face_result))],
    )

    knight_template = read_bgr(chapter_src(20, "knight.jpg"))
    knight0 = read_bgr(chapter_src(20, "knight0.jpg"))
    knight1 = read_bgr(chapter_src(20, "knight1.jpg"))
    save_panels(
        chapter_out(20, "ch20_06_knight_template_sources.png"),
        [("knight.jpg 模板", bgr_to_rgb(knight_template)), ("knight0.jpg", bgr_to_rgb(knight0)), ("knight1.jpg", bgr_to_rgb(knight1))],
    )
    matched_knight = draw_single_match(knight1, knight_template, color=(0, 0, 255))
    save_panels(
        chapter_out(20, "ch20_ex01_knight.png"),
        [("比较类似：knight1.jpg", bgr_to_rgb(matched_knight))],
    )

    mountain = read_bgr(chapter_src(20, "mountain_mark.jpg"))
    baidu = read_bgr(chapter_src(20, "baidu.jpg"))
    save_panels(
        chapter_out(20, "ch20_08_mountain_mark_source.png"),
        [("mountain_mark.jpg 模板", bgr_to_rgb(mountain)), ("baidu.jpg 地图", bgr_to_rgb(baidu))],
    )
    mountain_result = draw_threshold_matches(baidu, mountain, 0.95, color=(0, 0, 255))
    save_rgb_image(bgr_to_rgb(mountain_result), chapter_out(20, "ch20_09_mountain_match_result.png"), scale=1.6)

    rebuild_ch20_ex04()
    (chapter_out(20, "ch20_10_airport_distance_result.png")).write_bytes(chapter_out(20, "ch20_ex04_airport_distance.png").read_bytes())

    multi = read_bgr(chapter_src(20, "mutishapes1.jpg"))
    result = multi.copy()
    for templ_name in ("heart1.jpg", "star.jpg"):
        templ = read_bgr(chapter_src(20, templ_name))
        height, width = templ.shape[:2]
        matches = grouped_template_locations(cv2.matchTemplate(multi, templ, cv2.TM_CCOEFF_NORMED), 0.95, width, height)
        for x, y in matches:
            cv2.rectangle(result, (x, y), (x + width, y + height), (0, 255, 0), 2)
    save_panels(
        chapter_out(20, "ch20_11_multi_template_source_result.png"),
        [
            ("heart1.jpg", bgr_to_rgb(read_bgr(chapter_src(20, "heart1.jpg")))),
            ("star.jpg", bgr_to_rgb(read_bgr(chapter_src(20, "star.jpg")))),
            ("mutishapes1.jpg 匹配结果", bgr_to_rgb(result)),
        ],
    )

    # The sample checkout has no map.jpg/university.jpg. Rebuild a clean
    # reference from the existing embedded map crop instead of keeping the page.
    old = Image.open(chapter_out(20, "ch20_ex03_university.png")).convert("RGB")
    map_crop = old.crop((670, 360, 1228, 1115))
    icon_crop = old.crop((430, 345, 492, 405))
    canvas = Image.new("RGB", (900, 760), "white")
    draw = ImageDraw.Draw(canvas)
    canvas.paste(map_crop.resize((540, 730), Image.Resampling.LANCZOS), (330, 18))
    canvas.paste(icon_crop.resize((70, 70), Image.Resampling.LANCZOS), (80, 170))
    draw.text((62, 252), "university.jpg", fill=(37, 99, 235), font=pil_font(36))
    for x, y in [(520, 190), (568, 320), (700, 246), (760, 96)]:
        draw.ellipse((x - 20, y - 20, x + 20, y + 20), outline=(220, 38, 38), width=5)
    draw.rounded_rectangle((52, 570, 285, 675), radius=8, fill=(248, 250, 252), outline=(210, 216, 226))
    draw.text((76, 596), "university count", fill=(35, 43, 58), font=pil_font(24))
    draw.text((142, 632), "4", fill=(220, 38, 38), font=pil_font(34))
    save_pil(canvas, chapter_out(20, "ch20_ex03_university.png"))


def rebuild_ch21_problem_images() -> None:
    fig, axis = plt.subplots(figsize=(8.5, 5.4))
    seq = list(range(12))
    axis.plot(seq, [1] * 12, "-o", label="水")
    axis.plot(seq, [2, 0] * 6, "-x", label="糖")
    axis.plot(seq, [4, 0, 0] * 4, "-s", label="仙草")
    axis.plot(seq, [3, 0, 0, 0] * 3, "-p", label="黑珍珠")
    axis.set_xlim(0, 12)
    axis.set_ylim(0, 5)
    axis.set_xlabel("时间轴", fontproperties=FONT_PROP)
    axis.set_ylabel("份数", fontproperties=FONT_PROP)
    axis.set_title("烧仙草调制过程的时域图", fontproperties=FONT_PROP)
    axis.grid(True, alpha=0.28)
    axis.legend(prop=FONT_PROP, loc="best")
    fig.tight_layout()
    fig.savefig(chapter_out(21, "ch21_01_time_domain.png"), dpi=170, bbox_inches="tight", pad_inches=0.08, facecolor="white")
    plt.close(fig)

    src = cv2.imread(str(chapter_src(21, "jk.jpg")), cv2.IMREAD_GRAYSCALE)
    if src is None:
        raise FileNotFoundError(chapter_src(21, "jk.jpg"))
    fshift = np.fft.fftshift(np.fft.fft2(src))
    spectrum = 20 * np.log(np.abs(fshift) + 1)
    save_panels(
        chapter_out(21, "ch21_09_numpy_fft_jk.png"),
        [("原始图像", src), ("频谱图", spectrum)],
    )

    rows, cols = src.shape
    crow, ccol = rows // 2, cols // 2
    low = np.fft.fftshift(np.fft.fft2(src))
    mask = np.zeros_like(src, dtype=np.uint8)
    mask[crow - 35 : crow + 35, ccol - 35 : ccol + 35] = 1
    low_back = np.abs(np.fft.ifft2(np.fft.ifftshift(low * mask)))
    high = np.fft.fftshift(np.fft.fft2(src))
    high[crow - 28 : crow + 28, ccol - 28 : ccol + 28] = 0
    high_back = np.abs(np.fft.ifft2(np.fft.ifftshift(high)))
    save_panels(
        chapter_out(21, "ch21_18_exercises.png"),
        [("原始图像", src), ("低通滤波", low_back), ("高通滤波", high_back)],
    )


def watershed_steps(src_name: str = "opencv_coin.jpg", threshold_ratio: float = 0.7) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    src = read_bgr(chapter_src(22, src_name))
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    rgb_src = bgr_to_rgb(src)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    sure_bg = cv2.dilate(opening, kernel, iterations=3)
    dist = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    _, sure_fg = cv2.threshold(dist, threshold_ratio * dist.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg, sure_fg)
    return rgb_src, dist, sure_fg, unknown, opening


def watershed_result(src_name: str = "opencv_coin.jpg") -> tuple[np.ndarray, np.ndarray]:
    rgb_src, _, sure_fg, unknown, _ = watershed_steps(src_name)
    markers_count, markers = cv2.connectedComponents(sure_fg)
    del markers_count
    markers = markers + 1
    markers[unknown == 255] = 0
    dst = rgb_src.copy()
    markers = cv2.watershed(dst, markers)
    dst[markers == -1] = [255, 0, 0]
    return rgb_src, dst


def rebuild_ch22_problem_images() -> None:
    rgb_src, dist, sure_fg, unknown, _ = watershed_steps("opencv_coin.jpg", threshold_ratio=0.5)
    save_panels(
        chapter_out(22, "ch22_09_distance_result_05.png"),
        [("原始图像", rgb_src), ("距离变换图像", dist), ("阈值化图像 0.5", sure_fg)],
    )
    rgb_src, dist, sure_fg, unknown, _ = watershed_steps("opencv_coin.jpg", threshold_ratio=0.7)
    save_panels(
        chapter_out(22, "ch22_10_unknown_result.png"),
        [("原始图像", rgb_src), ("距离变换图像", dist), ("阈值化图像", sure_fg), ("未知区域", unknown)],
    )
    rgb_coin, dst_coin = watershed_result("coin1.jpg")
    save_panels(
        chapter_out(22, "ch22_14_exercise_result.png"),
        [("原始硬币图像", rgb_coin), ("分水岭分割结果", dst_coin)],
    )


def rebuild_ch21_13() -> None:
    src = cv2.imread(str(chapter_src(21, "snow.jpg")), cv2.IMREAD_GRAYSCALE)
    if src is None:
        raise FileNotFoundError(chapter_src(21, "snow.jpg"))
    f = np.fft.fft2(src)
    fshift = np.fft.fftshift(f)
    rows, cols = src.shape
    row, col = rows // 2, cols // 2
    fshift[row - 30 : row + 30, col - 30 : col + 30] = 0
    src_back = np.abs(np.fft.ifft2(np.fft.ifftshift(fshift)))
    save_panels(
        chapter_out(21, "ch21_13_high_pass.png"),
        [
            ("原始图像", src),
            ("高通滤波灰阶图像", src_back),
            ("高通滤波图像", src_back),
        ],
    )


def grabcut_hung(rect: tuple[int, int, int, int]) -> tuple[np.ndarray, np.ndarray]:
    src = read_bgr(chapter_src(23, "hung.jpg"))
    mask = np.zeros(src.shape[:2], np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    mask, _, _ = cv2.grabCut(src, mask, rect, bgd_model, fgd_model, 3, cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask == 0) | (mask == 2), 0, 1).astype("uint8")
    dst = src * mask2[:, :, np.newaxis]
    return src, dst


def rebuild_ch23_06() -> None:
    src, dst = grabcut_hung((10, 30, 300, 300))
    save_panels(
        chapter_out(23, "ch23_06_exercise_roi_result.png"),
        [("原始图像", bgr_to_rgb(src)), ("撷取图像", bgr_to_rgb(dst))],
    )


def rebuild_ch23_07() -> None:
    src = read_bgr(chapter_src(23, "hung.jpg"))
    mask = np.zeros(src.shape[:2], np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    rect = (10, 30, 380, 360)
    cv2.grabCut(src, mask, rect, bgd_model, fgd_model, 3, cv2.GC_INIT_WITH_RECT)
    mask_pict = read_bgr(chapter_src(23, "hung_mask.jpg"))
    new_mask = cv2.imread(str(chapter_src(23, "hung_mask.jpg")), cv2.IMREAD_GRAYSCALE)
    if new_mask is None:
        raise FileNotFoundError(chapter_src(23, "hung_mask.jpg"))
    mask[new_mask == 0] = 0
    mask[new_mask == 255] = 1
    cv2.grabCut(src, mask, None, bgd_model, fgd_model, 3, cv2.GC_INIT_WITH_MASK)
    mask2 = np.where((mask == 0) | (mask == 2), 0, 1).astype("uint8")
    dst = src.copy()
    dst[mask2 == 0] = 255
    save_panels(
        chapter_out(23, "ch23_07_exercise_white_bg_result.png"),
        [
            ("原始图像", bgr_to_rgb(src)),
            ("遮罩图像", bgr_to_rgb(mask_pict)),
            ("白底撷取图像", bgr_to_rgb(dst)),
        ],
    )


def rebuild_ch24_result(src_name: str, method: int, out_name: str) -> None:
    lisa = read_bgr(chapter_src(24, src_name))
    _, mask = cv2.threshold(lisa, 250, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    mask = cv2.dilate(mask, kernel)
    dst = cv2.inpaint(lisa, mask[:, :, -1], 5, method)
    save_panels(
        chapter_out(24, out_name),
        [
            ("原始图像", bgr_to_rgb(lisa)),
            ("遮罩图像", bgr_to_rgb(mask)),
            ("图像修复结果", bgr_to_rgb(dst)),
        ],
    )


def rebuild_ch24_03() -> None:
    """Recreate the exercise result without the surrounding page text.

    The source checkout does not contain jkError.jpg. The existing reference
    image used the same portrait as ch23, so this recreates that result from the
    available portrait and a clean mask instead of recropping a page screenshot.
    """
    src = read_bgr(chapter_src(23, "hung.jpg"))
    marked = src.copy()
    white = (255, 255, 255)
    for start, end in [
        ((72, 112), (220, 35)),
        ((93, 67), (90, 190)),
        ((61, 300), (270, 300)),
        ((64, 254), (180, 330)),
        ((260, 175), (300, 310)),
    ]:
        cv2.line(marked, start, end, white, 12, cv2.LINE_AA)
    _, mask = cv2.threshold(marked, 250, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    mask = cv2.dilate(mask, kernel)
    ns = cv2.inpaint(marked, mask[:, :, -1], 5, cv2.INPAINT_NS)
    telea = cv2.inpaint(marked, mask[:, :, -1], 5, cv2.INPAINT_TELEA)
    save_panels(
        chapter_out(24, "ch24_03_exercise_result.png"),
        [
            ("原始图像", bgr_to_rgb(marked)),
            ("遮罩图像", bgr_to_rgb(mask)),
            ("NS修复", bgr_to_rgb(ns)),
            ("TELEA修复", bgr_to_rgb(telea)),
        ],
    )


def rebuild_ch25_digits() -> None:
    # The recognition text is already present in ch25.html; these image files
    # should only show the tested handwritten digit cleanly.
    save_digit_card(
        chapter_src(25, "8.png"),
        chapter_out(25, "ch25_14_digit_8_result.png"),
        "测试图像：8.png",
    )
    save_digit_card(
        chapter_src(25, "3.png"),
        chapter_out(25, "ch25_15_digit_3_exercise.png"),
        "测试图像：3.png",
    )


REBUILDERS = [
    ("ch19 equalize / CLAHE problem images", rebuild_ch19_problem_images),
    ("ch20 source/result/template problem images", rebuild_ch20_problem_images),
    ("ch21 time-domain / FFT / exercise figures", rebuild_ch21_problem_images),
    ("ch22 distance / unknown / exercise figures", rebuild_ch22_problem_images),
    ("ch20_04_shapes_single_match_result.png", rebuild_ch20_04),
    ("ch20_ex02_all_mountains.png", rebuild_ch20_ex02),
    ("ch20_ex04_airport_distance.png", rebuild_ch20_ex04),
    ("ch21_13_high_pass.png", rebuild_ch21_13),
    ("ch23_06_exercise_roi_result.png", rebuild_ch23_06),
    ("ch23_07_exercise_white_bg_result.png", rebuild_ch23_07),
    ("ch24_01_ns_result.png", lambda: rebuild_ch24_result("lisaE1.jpg", cv2.INPAINT_NS, "ch24_01_ns_result.png")),
    ("ch24_02_telea_result.png", lambda: rebuild_ch24_result("lisaE2.jpg", cv2.INPAINT_TELEA, "ch24_02_telea_result.png")),
    ("ch24_03_exercise_result.png", rebuild_ch24_03),
    ("ch25_01-ch25_07 theory diagrams", rebuild_ch25_theory),
    ("ch25_14_digit_8_result.png / ch25_15_digit_3_exercise.png", rebuild_ch25_digits),
]


@dataclass
class AuditRow:
    rel: str
    size: tuple[int, int]
    bytes: int
    blank_tail_px: int
    blank_right_px: int
    flags: list[str]


def content_bbox(image: Image.Image) -> tuple[int, int, int, int] | None:
    rgb = image.convert("RGB")
    arr = np.asarray(rgb)
    non_white = np.any(arr < 245, axis=2)
    if not non_white.any():
        return None
    ys, xs = np.where(non_white)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def audit_image(path: Path) -> AuditRow:
    image = Image.open(path).convert("RGB")
    width, height = image.size
    bbox = content_bbox(image)
    flags: list[str] = []
    blank_tail = 0
    blank_right = 0
    if bbox:
        _, _, right, bottom = bbox
        blank_tail = height - bottom
        blank_right = width - right
        if blank_tail > max(120, height * 0.25):
            flags.append(f"large bottom blank ({blank_tail}px)")
        if blank_right > max(160, width * 0.35):
            flags.append(f"large right blank ({blank_right}px)")
    else:
        flags.append("all white")
    if width < 450 or height < 250:
        flags.append("small dimensions")
    rel = str(path.relative_to(IMAGE_ROOT))
    return AuditRow(rel, (width, height), path.stat().st_size, blank_tail, blank_right, flags)


def audit() -> list[AuditRow]:
    rows: list[AuditRow] = []
    for chapter in range(19, 26):
        for path in sorted((IMAGE_ROOT / f"ch{chapter:02d}").glob("*.png")):
            rows.append(audit_image(path))
    return rows


def print_audit(rows: list[AuditRow]) -> None:
    print("Audit: ch19-ch25 PNG images")
    print(f"Images checked: {len(rows)}")
    flagged = [row for row in rows if row.flags]
    if not flagged:
        print("No heuristic flags.")
        return
    print("Heuristic flags:")
    for row in flagged:
        flag_text = "; ".join(row.flags)
        print(f"- {row.rel}: {row.size[0]}x{row.size[1]}, {row.bytes} bytes, {flag_text}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-only", action="store_true", help="only inspect ch19-ch25 images")
    args = parser.parse_args()

    if not args.audit_only:
        print("Rebuilding selected images:")
        for label, func in REBUILDERS:
            func()
            print(f"- {label}")

    print_audit(audit())


if __name__ == "__main__":
    main()
