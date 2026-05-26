#!/usr/bin/env python3
"""Rebuild problematic Chapter 3-10 OpenCV website images.

The original assets for these chapters included several screenshots of book
pages, code, or cropped desktop windows. This script regenerates clean,
standalone figures from the bundled example assets where possible, and uses
small deterministic redraws or crops where source material is unavailable.
"""

from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
IMAGE_ROOT = ROOT / "chapters" / "images"
SAMPLE_ROOT = ROOT / "OpenCV程序实例代码"

TEXT = (36, 44, 58)
MUTED = (99, 111, 129)
LINE = (190, 198, 211)
PANEL = (246, 248, 251)
BLUE = (46, 92, 190)
RED = (218, 60, 67)
GREEN = (72, 165, 62)


def font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = []
    if mono:
        candidates = [
            "/System/Library/Fonts/Menlo.ttc",
            "/System/Library/Fonts/Monaco.ttf",
        ]
    elif bold:
        candidates = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf"]
    else:
        candidates = ["/System/Library/Fonts/Supplemental/Arial.ttf"]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def save_image(image: Image.Image, rel: str) -> None:
    path = IMAGE_ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() in {".jpg", ".jpeg"}:
        image.convert("RGB").save(path, quality=94, optimize=True)
    else:
        image.save(path, optimize=True)


def read_bgr(chapter: str, name: str) -> np.ndarray:
    path = SAMPLE_ROOT / chapter / name
    image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if image is None:
        raise FileNotFoundError(path)
    return image


def cv_to_pil(image: np.ndarray) -> Image.Image:
    if image.ndim == 2:
        return Image.fromarray(image).convert("RGB")
    if image.shape[2] == 4:
        rgba = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
        return Image.fromarray(rgba)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def as_gray(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return image
    if image.shape[2] == 4:
        return cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def with_checker(image: Image.Image, cell: int = 16) -> Image.Image:
    rgba = image.convert("RGBA")
    bg = Image.new("RGB", rgba.size, "white")
    draw = ImageDraw.Draw(bg)
    for y in range(0, rgba.height, cell):
        for x in range(0, rgba.width, cell):
            fill = (230, 234, 240) if (x // cell + y // cell) % 2 else (250, 252, 255)
            draw.rectangle((x, y, x + cell - 1, y + cell - 1), fill=fill)
    bg.paste(rgba, mask=rgba.getchannel("A"))
    return bg


def fit(image: Image.Image, max_w: int, max_h: int) -> Image.Image:
    result = ImageOps.exif_transpose(image).convert("RGB")
    result.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    return result


def compose_tiles(
    items: list[tuple[Image.Image | np.ndarray, str]],
    *,
    rel: str,
    cols: int = 2,
    tile_w: int = 390,
    tile_h: int = 300,
    label_h: int = 42,
    pad: int = 24,
    bg: tuple[int, int, int] = (255, 255, 255),
) -> None:
    rows = (len(items) + cols - 1) // cols
    width = cols * tile_w + (cols + 1) * pad
    height = rows * (tile_h + label_h) + (rows + 1) * pad
    canvas = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(canvas)
    label_font = font(22, bold=True)

    for index, (raw, label) in enumerate(items):
        image = cv_to_pil(raw) if isinstance(raw, np.ndarray) else raw.convert("RGB")
        image = fit(image, tile_w, tile_h)
        col = index % cols
        row = index // cols
        x0 = pad + col * (tile_w + pad)
        y0 = pad + row * (tile_h + label_h + pad)
        box = (x0, y0, x0 + tile_w, y0 + tile_h)
        draw.rounded_rectangle(box, radius=6, fill=PANEL, outline=LINE, width=1)
        canvas.paste(image, (x0 + (tile_w - image.width) // 2, y0 + (tile_h - image.height) // 2))
        draw.text((x0, y0 + tile_h + 12), label, fill=TEXT, font=label_font)

    save_image(canvas, rel)


def compose_opencv_windows(
    items: list[tuple[Image.Image | np.ndarray, str]],
    *,
    rel: str,
    cols: int = 2,
    content_w: int = 430,
    content_h: int = 330,
    pad: int = 24,
) -> None:
    """Render a compact contact sheet that matches the cv2.imshow windows."""
    title_h = 34
    border = 2
    rows = (len(items) + cols - 1) // cols
    window_w = content_w + border * 2
    window_h = title_h + content_h + border * 2
    width = cols * window_w + (cols + 1) * pad
    height = rows * window_h + (rows + 1) * pad
    canvas = Image.new("RGB", (width, height), (238, 241, 245))
    draw = ImageDraw.Draw(canvas)
    title_font = font(18, bold=True)

    for index, (raw, title) in enumerate(items):
        source = cv_to_pil(raw) if isinstance(raw, np.ndarray) else raw
        image = fit(source, content_w, content_h)
        col = index % cols
        row = index // cols
        x = pad + col * (window_w + pad)
        y = pad + row * (window_h + pad)
        draw.rectangle((x, y, x + window_w - 1, y + window_h - 1), fill=(255, 255, 255), outline=(138, 148, 163), width=border)
        draw.rectangle((x + border, y + border, x + window_w - border - 1, y + border + title_h - 1), fill=(226, 231, 238))
        draw.text((x + 12, y + 8), title, fill=TEXT, font=title_font)
        content_x = x + border
        content_y = y + border + title_h
        draw.rectangle((content_x, content_y, content_x + content_w - 1, content_y + content_h - 1), fill=(250, 251, 253))
        canvas.paste(image.convert("RGB"), (content_x + (content_w - image.width) // 2, content_y + (content_h - image.height) // 2))

    save_image(canvas, rel)


def simple_panel(raw: Image.Image | np.ndarray, rel: str, label: str | None = None, scale: int = 3) -> None:
    image = cv_to_pil(raw) if isinstance(raw, np.ndarray) else raw.convert("RGB")
    image = image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)
    margin = 32
    label_h = 46 if label else 0
    canvas = Image.new("RGB", (image.width + margin * 2, image.height + margin * 2 + label_h), "white")
    draw = ImageDraw.Draw(canvas)
    x = margin
    y = margin
    draw.rectangle((x - 1, y - 1, x + image.width, y + image.height), outline=LINE, width=2)
    canvas.paste(image, (x, y))
    if label:
        draw.text((x, y + image.height + 16), label, fill=TEXT, font=font(22, True))
    save_image(canvas, rel)


def text_figure(lines: list[str], rel: str, title: str) -> None:
    title_font = font(28, True)
    mono_font = font(23, mono=True)
    margin = 36
    line_h = 32
    max_w = max([ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), line, font=mono_font)[2] for line in lines] + [0])
    width = max(720, max_w + margin * 2)
    height = margin * 2 + 48 + len(lines) * line_h
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    draw.text((margin, margin), title, fill=TEXT, font=title_font)
    y = margin + 54
    for line in lines:
        draw.text((margin, y), line, fill=TEXT, font=mono_font)
        y += line_h
    save_image(image, rel)


def crop_existing(rel: str, box: tuple[int, int, int, int], out_size: tuple[int, int] | None = None) -> None:
    path = IMAGE_ROOT / rel
    image = Image.open(path).convert("RGB").crop(box)
    if out_size:
        image = image.resize(out_size, Image.Resampling.LANCZOS)
    save_image(image, rel)


def make_flower_ref() -> None:
    path = IMAGE_ROOT / "ch03/exercise_ref_2.png"
    image = Image.open(path).convert("RGB")
    if image.width > 1500 and image.height > 1200:
        image = image.crop((60, 0, 1990, 1560))
    else:
        arr = np.asarray(image)
        non_black = np.max(arr, axis=2) > 12
        ys, xs = np.nonzero(non_black)
        if len(xs):
            image = image.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))
    image.thumbnail((1120, 905), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", image.size, "white")
    canvas.paste(image, (0, 0))
    save_image(canvas, "ch03/exercise_ref_2.png")


def make_hsv_cone() -> None:
    w, h = 980, 760
    image = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(image)
    draw.text((52, 36), "HSV cone model", fill=TEXT, font=font(36, True))
    center = (490, 250)
    radius = 190
    for angle in range(360):
        color = tuple(int(v) for v in cv2.cvtColor(np.uint8([[[angle // 2, 220, 235]]]), cv2.COLOR_HSV2RGB)[0, 0])
        x = center[0] + np.cos(np.deg2rad(angle)) * radius
        y = center[1] + np.sin(np.deg2rad(angle)) * radius * 0.42
        draw.line((center[0], center[1], x, y), fill=color, width=4)
    draw.ellipse((center[0] - radius, center[1] - radius * 0.42, center[0] + radius, center[1] + radius * 0.42), outline=LINE, width=3)
    apex = (490, 620)
    draw.polygon((center[0] - radius, center[1], center[0] + radius, center[1], apex[0], apex[1]), outline=LINE)
    draw.line((center[0], center[1], apex[0], apex[1]), fill=MUTED, width=3)
    draw.text((90, 470), "Hue: angle around the circle", fill=TEXT, font=font(24))
    draw.text((90, 510), "Saturation: distance from center", fill=TEXT, font=font(24))
    draw.text((90, 550), "Value: brightness along the vertical axis", fill=TEXT, font=font(24))
    draw.line((735, 150, 735, 610), fill=MUTED, width=4)
    draw.polygon([(735, 135), (722, 160), (748, 160)], fill=MUTED)
    draw.text((760, 138), "V", fill=TEXT, font=font(28, True))
    save_image(image, "ch04/ch04_hsv_cone_model.jpg")


def make_hsv_hsv() -> None:
    w, h = 1060, 720
    image = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(image)
    draw.text((50, 34), "Hue, Saturation, Value", fill=TEXT, font=font(36, True))
    center = (270, 310)
    radius = 190
    for r in range(radius, 0, -3):
        sat = int(255 * r / radius)
        for angle in range(360):
            color = tuple(int(v) for v in cv2.cvtColor(np.uint8([[[angle // 2, sat, 235]]]), cv2.COLOR_HSV2RGB)[0, 0])
            x = center[0] + np.cos(np.deg2rad(angle)) * r
            y = center[1] + np.sin(np.deg2rad(angle)) * r
            draw.point((int(x), int(y)), fill=color)
    draw.ellipse((center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius), outline=LINE, width=2)
    draw.text((158, 535), "Hue + Saturation", fill=TEXT, font=font(24, True))
    x0, y0 = 610, 145
    for i in range(256):
        value = 255 - i
        color = tuple(int(v) for v in cv2.cvtColor(np.uint8([[[14, 210, value]]]), cv2.COLOR_HSV2RGB)[0, 0])
        draw.rectangle((x0, y0 + i, x0 + 260, y0 + i), fill=color)
    draw.rectangle((x0, y0, x0 + 260, y0 + 255), outline=LINE, width=2)
    draw.text((612, 430), "Value: bright to dark", fill=TEXT, font=font(24, True))
    for x, label in [(55, "0"), (183, "120"), (317, "240"), (444, "360")]:
        draw.text((x, 650), label, fill=MUTED, font=font(20))
    draw.line((75, 630, 460, 630), fill=LINE, width=3)
    save_image(image, "ch04/ch04_hsv_hue_saturation_value.jpg")


def make_rgb_hsv_formula() -> None:
    lines = [
        "R' = R / 255,  G' = G / 255,  B' = B / 255",
        "Cmax = max(R', G', B')",
        "Cmin = min(R', G', B')",
        "Delta = Cmax - Cmin",
        "",
        "Hue:",
        "  0                         if Delta = 0",
        "  60 x (((G'-B')/Delta) mod 6) if Cmax = R'",
        "  60 x (((B'-R')/Delta) + 2)   if Cmax = G'",
        "  60 x (((R'-G')/Delta) + 4)   if Cmax = B'",
        "",
        "Saturation = 0 if Cmax = 0 else Delta / Cmax",
        "Value      = Cmax",
    ]
    text_figure(lines, "ch04/ch04_rgb_to_hsv_formula.jpg", "RGB to HSV conversion")


def make_ch03() -> None:
    text_figure(
        [
            "arr1:",
            "  ndim  = 2",
            "  shape = (1, 3)",
            "  size  = 3",
            "  [[1 2 3]]",
            "",
            "arr2:",
            "  ndim  = 2",
            "  shape = (2, 3)",
            "  size  = 6",
            "  [[1 2 3]",
            "   [4 5 6]]",
        ],
        "ch03/ch3_1_result.png",
        "ch3_1.py result",
    )
    text_figure(
        [
            "array 1:",
            "[[0 1]",
            " [2 3]]",
            "",
            "array 2:",
            "[[4 5]",
            " [6 7]]",
            "",
            "vstack result:",
            "[[0 1]",
            " [2 3]",
            " [4 5]",
            " [6 7]]",
        ],
        "ch03/ch3_17_result.png",
        "ch3_17.py vertical stack",
    )
    text_figure(
        [
            "array 1:       array 2:",
            "[[0 1]         [[4 5]",
            " [2 3]]         [6 7]]",
            "",
            "hstack result:",
            "[[0 1 4 5]",
            " [2 3 6 7]]",
        ],
        "ch03/ch3_18_result.png",
        "ch3_18.py horizontal stack",
    )
    huang = cv_to_pil(read_bgr("ch10", "huang.jpg"))
    compose_tiles([(huang, "huang.jpg"), (huang, "hstack result")], rel="ch03/exercise_ref_1.png", cols=2, tile_w=360, tile_h=270)
    make_flower_ref()


def make_ch04() -> None:
    make_hsv_cone()
    make_hsv_hsv()
    make_rgb_hsv_formula()

    view = read_bgr("ch4", "view.jpg")
    view_rgb = cv2.cvtColor(view, cv2.COLOR_BGR2RGB)
    compose_opencv_windows(
        [(view, "view.jpg"), (view_rgb, "RGB Color Space")],
        rel="ch04/ch4_1_rgb_result.png",
        content_h=380,
    )

    jk = read_bgr("ch4", "jk.jpg")
    gray = cv2.cvtColor(jk, cv2.COLOR_BGR2GRAY)
    compose_opencv_windows(
        [(jk, "BGR Color Space"), (gray, "GRAY Color Space")],
        rel="ch04/ch4_4_gray_result.png",
        content_h=360,
    )

    mountain = read_bgr("ch4", "mountain.jpg")
    hsv = cv2.cvtColor(mountain, cv2.COLOR_BGR2HSV)
    compose_opencv_windows(
        [(mountain, "BGR Color Space"), (hsv, "HSV Color Space")],
        rel="ch04/ch4_6_hsv_result.png",
        content_h=330,
    )

    colorbar = read_bgr("ch4", "colorbar.jpg")
    b, g, r = cv2.split(colorbar)
    compose_opencv_windows(
        [(colorbar, "bgr"), (b, "blue"), (g, "green"), (r, "red")],
        rel="ch04/ch4_7_colorbar_split_result.png",
        cols=2,
        content_w=310,
        content_h=330,
    )

    b, g, r = cv2.split(mountain)
    compose_opencv_windows(
        [(mountain, "bgr"), (b, "blue"), (g, "green"), (r, "red")],
        rel="ch04/ch4_8_mountain_split_result.png",
        cols=2,
        content_h=330,
    )

    street = read_bgr("ch4", "street.jpg")
    b, g, r = cv2.split(street)
    bgr_image = cv2.merge([b, g, r])
    rgb_image = cv2.merge([r, g, b])
    compose_opencv_windows(
        [(bgr_image, "B -> G -> R "), (rgb_image, "R -> G -> B ")],
        rel="ch04/ch4_10_merge_result.png",
        content_h=330,
    )
    hsv_street = cv2.cvtColor(street, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv_street)
    hsv_merged = cv2.merge([h, s, v])
    compose_opencv_windows(
        [(street, "The Image"), (hsv_merged, "The Merge Image")],
        rel="ch04/ch4_11_hsv_merge_result.png",
        content_h=330,
    )

    hue_200 = np.full_like(h, 200)
    hue_result = cv2.cvtColor(cv2.merge([hue_200, s, v]), cv2.COLOR_HSV2BGR)
    compose_opencv_windows(
        [(street, "The Image"), (hue_result, "The New Image")],
        rel="ch04/ch4_12_hue_result.png",
        content_h=330,
    )

    saturation_255 = np.full_like(s, 255)
    saturation_result = cv2.cvtColor(cv2.merge([h, saturation_255, v]), cv2.COLOR_HSV2BGR)
    compose_opencv_windows(
        [(street, "The Image"), (saturation_result, "The New Image")],
        rel="ch04/ch4_13_saturation_result.png",
        content_h=330,
    )

    value_255 = np.full_like(v, 255)
    value_result = cv2.cvtColor(cv2.merge([h, s, value_255]), cv2.COLOR_HSV2BGR)
    compose_opencv_windows(
        [(street, "The Image"), (value_result, "The New Image")],
        rel="ch04/ch4_14_value_result.png",
        content_h=330,
    )

    bgra = cv2.cvtColor(street, cv2.COLOR_BGR2BGRA)
    b, g, r, a = cv2.split(bgra)
    a32 = cv2.merge([b, g, r, np.full_like(a, 32)])
    a128 = cv2.merge([b, g, r, np.full_like(a, 128)])
    compose_opencv_windows(
        [(street, "The Image"), (a32[:, :, :3], "The a32 Image"), (a128[:, :, :3], "The a128 Image")],
        rel="ch04/ch4_15_alpha_result.png",
        cols=3,
        content_w=330,
        content_h=260,
    )
    a32_saved = Image.open(SAMPLE_ROOT / "ch4" / "a32.png")
    a128_saved = Image.open(SAMPLE_ROOT / "ch4" / "a128.png")
    compose_opencv_windows(
        [(with_checker(a32_saved), "a32.png"), (with_checker(a128_saved), "a128.png")],
        rel="ch04/ch4_15_alpha_saved_result.png",
        content_h=330,
    )

    night = read_bgr("ch4", "night.png")
    night_hsv = cv2.cvtColor(night, cv2.COLOR_BGR2HSV)
    nh, ns, nv = cv2.split(night_hsv)
    night_rgb = cv2.cvtColor(night, cv2.COLOR_BGR2RGB)
    compose_opencv_windows(
        [(night, "BGR"), (night_rgb, "RGB")],
        rel="ch04/exercise_1_bgr_rgb.png",
        content_h=370,
    )
    compose_opencv_windows(
        [(ns, "saturation"), (nv, "value")],
        rel="ch04/exercise_1_sv.png",
        content_h=370,
    )
    compose_opencv_windows(
        [(cv2.merge([ns, nv, nh]), "S-V-H"), (cv2.merge([nv, nh, ns]), "V-H-S")],
        rel="ch04/exercise_2_hsv_order.png",
        content_h=330,
    )


def make_ch05() -> None:
    h, w = 160, 280
    black = np.zeros((h, w), np.uint8)
    white = np.ones((h, w), np.uint8) * 255
    rect = black.copy()
    rect[40:120, 70:210] = 255
    stripes_h = black.copy()
    for y in range(0, h, 20):
        stripes_h[y : y + 10, :] = 255
    rng = np.random.default_rng(506)
    random_gray = rng.integers(0, 256, (h, w), dtype=np.uint8)
    blue = np.zeros((h, w, 3), np.uint8)
    blue[:, :, 0] = 255
    green = np.zeros_like(blue)
    green[:, :, 1] = 255
    red = np.zeros_like(blue)
    red[:, :, 2] = 255
    random_color = rng.integers(0, 256, (h, w, 3), dtype=np.uint8)
    bars = np.zeros((150, 300, 3), np.uint8)
    bars[0:50, :, 0] = 255
    bars[50:100, :, 1] = 255
    bars[100:150, :, 2] = 255
    vertical = black.copy()
    for x in range(0, w, 20):
        vertical[:, x : x + 10] = 255
    vbars = np.zeros((150, 300, 3), np.uint8)
    vbars[:, 0:100, 0] = 255
    vbars[:, 100:200, 1] = 255
    vbars[:, 200:300, 2] = 255

    simple_panel(black, "ch05/ch5_1_black_result.png", "zeros((160, 280))")
    simple_panel(white, "ch05/ch5_2_white_result.png", "fill(255)")
    simple_panel(rect, "ch05/ch5_4_white_rectangle_result.png", "image[40:120, 70:210] = 255")
    simple_panel(stripes_h, "ch05/ch5_5_horizontal_stripes_result.png", "horizontal stripes")
    simple_panel(random_gray, "ch05/ch5_6_random_gray_result.png", "random grayscale")
    simple_panel(blue, "ch05/ch5_7_blue_result.png", "B channel = 255")
    compose_tiles([(blue, "B"), (green, "G"), (red, "R")], rel="ch05/ch5_8_bgr_images_result.png", cols=3, tile_w=300, tile_h=210)
    simple_panel(random_color, "ch05/ch5_9_random_color_result.png", "random BGR")
    simple_panel(bars, "ch05/ch5_10_color_bars_result.png", "B / G / R horizontal bars", scale=2)
    simple_panel(vertical, "ch05/exercise_1_vertical_stripes.png", "vertical stripes")
    simple_panel(vbars, "ch05/exercise_2_vertical_color_bars.png", "B / G / R vertical bars", scale=2)
    make_ch05_coordinate_system()


def make_ch05_coordinate_system() -> None:
    image = Image.new("RGB", (980, 650), "white")
    draw = ImageDraw.Draw(image)
    draw.text((42, 34), "OpenCV image coordinate system", fill=TEXT, font=font(32, True))

    x0, y0 = 165, 135
    img_w, img_h = 560, 360
    for y in range(img_h):
        color = (
            int(245 - y * 0.18),
            int(235 - y * 0.12),
            int(218 - y * 0.08),
        )
        draw.line((x0, y0 + y, x0 + img_w, y0 + y), fill=color)
    for x in range(0, img_w, 40):
        draw.line((x0 + x, y0, x0 + x, y0 + img_h), fill=(235, 239, 245))
    for y in range(0, img_h, 40):
        draw.line((x0, y0 + y, x0 + img_w, y0 + y), fill=(235, 239, 245))
    draw.rectangle((x0, y0, x0 + img_w, y0 + img_h), outline=TEXT, width=3)

    draw.line((x0, y0 - 55, x0 + img_w + 120, y0 - 55), fill=BLUE, width=4)
    draw.polygon([(x0 + img_w + 135, y0 - 55), (x0 + img_w + 105, y0 - 70), (x0 + img_w + 105, y0 - 40)], fill=BLUE)
    draw.text((x0 + img_w + 150, y0 - 70), "x / width", fill=TEXT, font=font(22, True))

    draw.line((x0 - 55, y0, x0 - 55, y0 + img_h + 105), fill=BLUE, width=4)
    draw.polygon([(x0 - 55, y0 + img_h + 120), (x0 - 70, y0 + img_h + 90), (x0 - 40, y0 + img_h + 90)], fill=BLUE)
    draw.text((x0 - 120, y0 + img_h + 132), "y / height", fill=TEXT, font=font(22, True))

    points = [
        ((x0, y0), "(0, 0)"),
        ((x0 + img_w, y0), "(width - 1, 0)"),
        ((x0, y0 + img_h), "(0, height - 1)"),
        ((x0 + img_w, y0 + img_h), "(width - 1, height - 1)"),
    ]
    for (px, py), label in points:
        draw.ellipse((px - 7, py - 7, px + 7, py + 7), fill=RED)
        lx = px + 12 if px < x0 + img_w // 2 else px - 205
        ly = py + 10 if py < y0 + img_h // 2 else py - 32
        draw.text((lx, ly), label, fill=TEXT, font=font(18, True))

    draw.text((x0, y0 + img_h + 68), "OpenCV addresses a pixel as image[y, x].", fill=MUTED, font=font(22))
    save_image(image, "ch05/ch5_coordinate_system.png")


def make_ch07() -> None:
    image = np.ones((350, 500, 3), np.uint8) * 255
    cv2.rectangle(image, (1, 1), (300, 300), (0, 255, 255), -1)
    cv2.rectangle(image, (1, 1), (300, 300), (255, 0, 0), 1)
    for x in range(150, 300, 10):
        cv2.line(image, (x, 1), (300, x - 150), (255, 0, 0))
    for y in range(150, 300, 10):
        cv2.line(image, (1, y), (y - 150, 300), (255, 0, 0))
    simple_panel(image, "ch07/ch7_6_yellow_rectangle_result.png", "ch7_6.py yellow filled rectangle", scale=2)


def make_ch06() -> None:
    before = np.zeros((5, 12), np.uint8)
    after = before.copy()
    after[1, 4] = 255
    before_lines = np.array2string(before).splitlines()
    after_lines = np.array2string(after).splitlines()
    text_figure(
        ["before:", *before_lines, "", "after image[1, 4] = 255:", *after_lines],
        "ch06/ch6_1_gray_array_result.png",
        "ch6_1.py array edit",
    )

    jk = read_bgr("ch6", "jk.jpg")
    gray_before = as_gray(jk)
    gray_after = gray_before.copy()
    gray_after[120:140, 110:210] = 255
    compose_tiles([(gray_before, "before"), (gray_after, "after")], rel="ch06/ch6_2_gray_mask_result.png")

    blue = np.zeros((100, 150, 3), np.uint8)
    blue[:, :, 0] = 255
    green = np.zeros_like(blue)
    green[:, :, 1] = 255
    red = np.zeros_like(blue)
    red[:, :, 2] = 255
    compose_tiles([(blue, "Blue Image"), (green, "Green Image"), (red, "Red Image")], rel="ch06/ch6_4_bgr_windows_result.png", cols=3, tile_w=260, tile_h=190)

    bars = jk.copy()
    bars[115:125, 110:210] = [255, 0, 255]
    bars[125:135, 110:210] = [255, 255, 255]
    bars[135:145, 110:210] = [0, 255, 255]
    compose_tiles([(jk, "before"), (bars, "after")], rel="ch06/ch6_7_color_bars_result.png")

    street = read_bgr("ch6", "street.png")
    alpha = street.copy()
    alpha[:200, :200, 3] = 128
    compose_tiles([(with_checker(cv_to_pil(street)), "street.png"), (with_checker(cv_to_pil(alpha)), "street128.png")], rel="ch06/ch6_8_alpha_saved_result.png")

    rng = np.random.default_rng(609)
    matrix = rng.integers(0, 200, (3, 5), dtype=np.uint8)
    old_value = int(matrix[1, 3])
    matrix_after = matrix.copy()
    matrix_after[1, 3] = 255
    text_figure(
        [
            "image:",
            *np.array2string(matrix).splitlines(),
            f"before image.item(1, 3) = {old_value}",
            "",
            "after image.itemset((1, 3), 255):",
            *np.array2string(matrix_after).splitlines(),
            "after image.item(1, 3) = 255",
        ],
        "ch06/ch6_9_itemset_gray_result.png",
        "ch6_9.py itemset",
    )

    white_strip = jk.copy()
    white_strip[115:145, 110:210] = [255, 255, 255]
    compose_tiles([(jk, "before"), (white_strip, "after")], rel="ch06/ch6_12_itemset_color_result.png")

    face = jk[30:220, 80:250]
    compose_tiles([(jk, "source"), (face, "ROI face")], rel="ch06/ch6_13_roi_face_result.png")

    mosaic = jk.copy()
    mosaic[30:220, 80:250] = rng.integers(0, 256, (190, 170, 3), dtype=np.uint8)
    compose_tiles([(jk, "source"), (mosaic, "mosaic ROI")], rel="ch06/ch6_14_mosaic_result.png")

    money = read_bgr("ch6", "money.jpg")
    transferred = money.copy()
    transferred[30:220, 120:290] = face
    compose_tiles([(jk, "source"), (money, "money.jpg"), (transferred, "ROI transferred")], rel="ch06/ch6_15_roi_transfer_result.png", cols=3, tile_w=300, tile_h=240)


def make_ch08() -> None:
    jk = read_bgr("ch8", "jk.jpg")
    compose_tiles([(jk, "source"), (cv2.add(jk, jk), "cv2.add")], rel="ch08/ch8_3_color_add_result.png")
    compose_tiles([(jk, "source"), (cv2.add(jk, jk), "cv2.add"), (jk + jk, "operator +")], rel="ch08/ch8_6_plus_wrap_result.png", cols=3, tile_w=300, tile_h=260)

    base = np.zeros((200, 250, 3), np.uint8)
    b = base.copy(); b[:, :, 0] = 255
    g = base.copy(); g[:, :, 1] = 255
    r = base.copy(); r[:, :, 2] = 255
    bg = cv2.add(b, g)
    gr = cv2.add(g, r)
    bgr = cv2.add(bg, r)
    compose_tiles([(b, "B"), (g, "G"), (r, "R"), (bg, "B+G"), (gr, "G+R"), (bgr, "B+G+R")], rel="ch08/ch8_7_bgr_add_result.png", cols=3, tile_w=260, tile_h=220)

    img1 = np.zeros((200, 300, 3), np.uint8); img1[:, :, 1] = 255
    img2 = np.zeros((200, 300, 3), np.uint8); img2[:, :, 2] = 255
    mask = np.zeros((200, 300, 1), np.uint8); mask[50:150, 100:200, :] = 255
    compose_tiles([(img1, "img1"), (img2, "img2"), (mask[:, :, 0], "mask"), (cv2.add(img1, img2), "img1+img2"), (cv2.add(img1, img2, mask=mask), "with mask")], rel="ch08/ch8_8_1_mask_add_result.png", cols=3, tile_w=280, tile_h=205)

    lake = read_bgr("ch8", "lake.jpg")
    geneva = read_bgr("ch8", "geneva.jpg")
    weighted = cv2.addWeighted(lake, 1, geneva, 0.2, 0)
    compose_tiles([(lake, "lake.jpg"), (geneva, "geneva.jpg")], rel="ch08/ch8_10_weighted_sources.png")
    simple_panel(weighted, "ch08/ch8_10_weighted_result.png", "addWeighted(lake, 1, geneva, 0.2, 0)", scale=2)

    mask_color = np.zeros(jk.shape, np.uint8)
    mask_color[30:260, 70:260, :] = 255
    compose_tiles([(jk, "source"), (mask_color, "mask"), (cv2.bitwise_and(jk, mask_color), "AND result")], rel="ch08/ch8_13_bitwise_and_mask_result.png", cols=3, tile_w=300, tile_h=260)
    compose_tiles([(jk, "source"), (mask_color, "mask"), (cv2.bitwise_or(jk, mask_color), "OR result")], rel="ch08/ch8_15_bitwise_or_result.png", cols=3, tile_w=300, tile_h=260)

    forest = read_bgr("ch8", "forest.jpg")
    compose_tiles([(forest, "forest.jpg"), (cv2.bitwise_not(forest), "NOT result")], rel="ch08/ch8_16_bitwise_not_result.png")
    xor_mask = np.zeros(forest.shape, np.uint8)
    xor_mask[:, 120:360, :] = 255
    compose_tiles([(forest, "source"), (xor_mask, "mask"), (cv2.bitwise_xor(forest, xor_mask), "XOR result")], rel="ch08/ch8_17_bitwise_xor_result.png", cols=3, tile_w=300, tile_h=240)
    rng = np.random.default_rng(818)
    key = rng.integers(0, 256, forest.shape, dtype=np.uint8)
    encrypted = cv2.bitwise_xor(forest, key)
    decrypted = cv2.bitwise_xor(key, encrypted)
    compose_tiles([(forest, "source"), (key, "random key"), (encrypted, "encrypted"), (decrypted, "decrypted")], rel="ch08/ch8_18_encrypt_decrypt_result.png", cols=2)


def make_ch09() -> None:
    jk_gray = as_gray(read_bgr("ch9", "jk.jpg"))
    jk_color = read_bgr("ch9", "jk.jpg")
    numbers = read_bgr("ch9", "numbers.jpg")

    def threshold(src: np.ndarray, mode: int, value: int) -> np.ndarray:
        return cv2.threshold(src, value, 255, mode)[1]

    compose_tiles([(jk_gray, "source"), (threshold(jk_gray, cv2.THRESH_BINARY, 127), "threshold 127"), (threshold(jk_gray, cv2.THRESH_BINARY, 80), "threshold 80")], rel="ch09/ch9_2_binary_gray.png", cols=3, tile_w=300, tile_h=280)
    compose_tiles([(jk_color, "source"), (threshold(jk_color, cv2.THRESH_BINARY, 127), "threshold 127"), (threshold(jk_color, cv2.THRESH_BINARY, 80), "threshold 80")], rel="ch09/ch9_3_binary_color.png", cols=3, tile_w=300, tile_h=280)
    compose_tiles([(numbers, "numbers.jpg"), (threshold(numbers, cv2.THRESH_BINARY, 127), "THRESH_BINARY")], rel="ch09/ch9_4_numbers_binary.png")
    compose_tiles([(numbers, "numbers.jpg"), (threshold(numbers, cv2.THRESH_BINARY_INV, 127), "THRESH_BINARY_INV")], rel="ch09/ch9_8_numbers_binary_inv.png")
    compose_tiles([(jk_color, "source"), (threshold(jk_color, cv2.THRESH_TRUNC, 127), "TRUNC 127"), (threshold(jk_color, cv2.THRESH_TRUNC, 80), "TRUNC 80")], rel="ch09/ch9_11_trunc_color.png", cols=3, tile_w=300, tile_h=280)
    compose_tiles([(jk_gray, "source"), (threshold(jk_gray, cv2.THRESH_TOZERO, 127), "TOZERO 127"), (threshold(jk_gray, cv2.THRESH_TOZERO, 80), "TOZERO 80")], rel="ch09/ch9_13_tozero_gray.png", cols=3, tile_w=300, tile_h=280)
    compose_tiles([(jk_color, "source"), (threshold(jk_color, cv2.THRESH_TOZERO_INV, 127), "TOZERO_INV 127"), (threshold(jk_color, cv2.THRESH_TOZERO_INV, 80), "TOZERO_INV 80")], rel="ch09/ch9_17_tozero_inv_color.png", cols=3, tile_w=300, tile_h=280)
    otsu = cv2.threshold(jk_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    compose_tiles([(jk_gray, "source"), (threshold(jk_gray, cv2.THRESH_BINARY, 127), "threshold 127"), (otsu, "Otsu")], rel="ch09/ch9_20_otsu_result.png", cols=3, tile_w=300, tile_h=280)

    school = as_gray(read_bgr("ch9", "school.jpg"))
    binary = threshold(school, cv2.THRESH_BINARY, 127)
    mean = cv2.adaptiveThreshold(school, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 3, 5)
    gauss = cv2.adaptiveThreshold(school, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 3, 5)
    compose_tiles([(school, "source"), (binary, "THRESH_BINARY"), (mean, "ADAPTIVE_MEAN"), (gauss, "ADAPTIVE_GAUSSIAN")], rel="ch09/ch9_21_adaptive_threshold.png", cols=2)

    planes = [(jk_gray & (1 << i)) * (255 // (1 << i)) for i in range(8)]
    compose_tiles([(planes[i], f"bit {i}") for i in range(4)], rel="ch09/ch9_22_bit_planes_low.png", cols=4, tile_w=220, tile_h=230)
    compose_tiles([(planes[i], f"bit {i}") for i in range(4, 8)], rel="ch09/ch9_22_bit_planes_high.png", cols=4, tile_w=220, tile_h=230)

    h7 = np.ones(jk_gray.shape, np.uint8) * 254
    lsb_zero = cv2.bitwise_and(jk_gray, h7)
    compose_tiles([(jk_gray, "source"), (h7, "254 mask"), (lsb_zero, "LSB cleared")], rel="ch09/ch9_23_lsb_effect.png", cols=3, tile_w=300, tile_h=280)

    watermark = as_gray(read_bgr("ch9", "copyright.jpg"))
    wm = cv2.threshold(watermark, 0, 1, cv2.THRESH_BINARY)[1]
    embedded = cv2.bitwise_or(lsb_zero, wm)
    extracted = cv2.threshold(cv2.bitwise_and(embedded, np.ones(jk_gray.shape, np.uint8)), 0, 255, cv2.THRESH_BINARY)[1]
    compose_tiles([(jk_gray, "source"), (watermark, "watermark"), (embedded, "embedded")], rel="ch09/ch9_24_embed_watermark.png", cols=3, tile_w=300, tile_h=280)
    compose_tiles([(embedded, "embedded image"), (extracted, "extracted watermark")], rel="ch09/ch9_25_extract_watermark.png")


def make_ch10() -> None:
    southpole = read_bgr("ch10", "southpole.jpg")
    resized = cv2.resize(southpole, (300, 200))
    compose_tiles([(southpole, "source"), (resized, "resize to 300x200")], rel="ch10/ch10_resize_dsize_result.png")

    python_img = read_bgr("ch10", "python.jpg")
    compose_tiles(
        [
            (python_img, "source"),
            (cv2.flip(python_img, 0), "flip 0"),
            (cv2.flip(python_img, 1), "flip 1"),
            (cv2.flip(python_img, -1), "flip -1"),
        ],
        rel="ch10/ch10_flip_modes_result.png",
        cols=4,
        tile_w=220,
        tile_h=330,
    )

    rural = read_bgr("ch10", "rural.jpg")
    height, width = rural.shape[:2]
    translate = cv2.warpAffine(rural, np.float32([[1, 0, 50], [0, 1, 100]]), (width, height))
    compose_tiles([(rural, "source"), (translate, "x=50, y=100")], rel="ch10/ch10_affine_translation_result.png")
    rot_ccw = cv2.warpAffine(rural, cv2.getRotationMatrix2D((width / 2, height / 2), 30, 1), (width, height))
    rot_cw = cv2.warpAffine(rural, cv2.getRotationMatrix2D((width / 2, height / 2), -30, 1), (width, height))
    compose_tiles([(rural, "source"), (rot_ccw, "rotate +30"), (rot_cw, "rotate -30")], rel="ch10/ch10_affine_rotation_result.png", cols=3, tile_w=300, tile_h=230)
    srcp = np.float32([[0, 0], [width - 1, 0], [0, height - 1]])
    dstp = np.float32([[0, height * 0.4], [width * 0.8, height * 0.2], [width * 0.1, height * 0.9]])
    shear = cv2.warpAffine(rural, cv2.getAffineTransform(srcp, dstp), (width, height))
    compose_tiles([(rural, "source"), (shear, "affine shear")], rel="ch10/ch10_affine_shear_result.png")

    tunnel = read_bgr("ch10", "tunnel.jpg")
    th, tw = tunnel.shape[:2]
    srcp4 = np.float32([[0, 0], [tw, 0], [0, th], [tw - 1, th - 1]])
    dstp4 = np.float32([[150, 0], [tw - 150, 0], [0, th - 1], [tw - 1, th - 1]])
    perspective = cv2.warpPerspective(tunnel, cv2.getPerspectiveTransform(srcp4, dstp4), (tw, th))
    compose_tiles([(tunnel, "source"), (perspective, "perspective")], rel="ch10/ch10_perspective_result.png")

    huang = read_bgr("ch10", "huang.jpg")
    rows, cols = huang.shape[:2]
    grid_x, grid_y = np.meshgrid(np.arange(cols, dtype=np.float32), np.arange(rows, dtype=np.float32))
    identity = cv2.remap(huang, grid_x, grid_y, cv2.INTER_LINEAR)
    vflip = cv2.remap(huang, grid_x, (rows - 1 - grid_y).astype(np.float32), cv2.INTER_LINEAR)
    hflip = cv2.remap(huang, (cols - 1 - grid_x).astype(np.float32), grid_y, cv2.INTER_LINEAR)
    both = cv2.remap(huang, (cols - 1 - grid_x).astype(np.float32), (rows - 1 - grid_y).astype(np.float32), cv2.INTER_LINEAR)
    compose_tiles([(huang, "source"), (identity, "remap copy")], rel="ch10/ch10_remap_identity_result.png")
    compose_tiles([(huang, "source"), (vflip, "vertical flip")], rel="ch10/ch10_remap_vertical_flip_result.png")
    compose_tiles([(huang, "source"), (hflip, "horizontal flip")], rel="ch10/ch10_remap_horizontal_flip_result.png")
    compose_tiles([(huang, "source"), (both, "flip both axes")], rel="ch10/ch10_exercise_remap_flip_result.jpg")

    tr, tc = tunnel.shape[:2]
    gx, gy = np.meshgrid(np.arange(tc, dtype=np.float32), np.arange(tr, dtype=np.float32))
    shrink_x = np.zeros((tr, tc), np.float32)
    shrink_y = np.zeros((tr, tc), np.float32)
    mask = (0.25 * tr < gy) & (gy < 0.75 * tr) & (0.25 * tc < gx) & (gx < 0.75 * tc)
    shrink_x[mask] = 2 * (gx[mask] - tc * 0.25)
    shrink_y[mask] = 2 * (gy[mask] - tr * 0.25)
    shrink = cv2.remap(tunnel, shrink_x, shrink_y, cv2.INTER_LINEAR)
    compress = cv2.remap(tunnel, gx, (2 * gy).astype(np.float32), cv2.INTER_LINEAR)
    compose_tiles([(tunnel, "source"), (shrink, "remap shrink")], rel="ch10/ch10_remap_shrink_result.png")
    compose_tiles([(tunnel, "source"), (compress, "vertical compress")], rel="ch10/ch10_remap_vertical_compress_result.png")

    face = read_bgr("ch6", "jk.jpg")
    rotated = cv2.rotate(face, cv2.ROTATE_90_COUNTERCLOCKWISE)
    compose_tiles([(face, "source"), (rotated, "rotate 90 CCW")], rel="ch10/ch10_exercise_face_rotate_result.jpg")


def backup_targets() -> Path:
    backup_dir = Path("/tmp") / "opencv-image-backups" / f"ch03-ch10-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    for rel in TARGETS:
        source = IMAGE_ROOT / rel
        if source.exists():
            target = backup_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    return backup_dir


TARGETS = [
    "ch03/ch3_1_result.png",
    "ch03/ch3_17_result.png",
    "ch03/ch3_18_result.png",
    "ch03/exercise_ref_1.png",
    "ch03/exercise_ref_2.png",
    "ch04/ch04_hsv_cone_model.jpg",
    "ch04/ch04_hsv_hue_saturation_value.jpg",
    "ch04/ch04_rgb_to_hsv_formula.jpg",
    "ch04/ch4_1_rgb_result.png",
    "ch04/ch4_4_gray_result.png",
    "ch04/ch4_6_hsv_result.png",
    "ch04/ch4_7_colorbar_split_result.png",
    "ch04/ch4_8_mountain_split_result.png",
    "ch04/ch4_10_merge_result.png",
    "ch04/ch4_11_hsv_merge_result.png",
    "ch04/ch4_12_hue_result.png",
    "ch04/ch4_13_saturation_result.png",
    "ch04/ch4_14_value_result.png",
    "ch04/ch4_15_alpha_result.png",
    "ch04/ch4_15_alpha_saved_result.png",
    "ch04/exercise_1_bgr_rgb.png",
    "ch04/exercise_1_sv.png",
    "ch04/exercise_2_hsv_order.png",
    "ch05/ch5_1_black_result.png",
    "ch05/ch5_2_white_result.png",
    "ch05/ch5_4_white_rectangle_result.png",
    "ch05/ch5_5_horizontal_stripes_result.png",
    "ch05/ch5_6_random_gray_result.png",
    "ch05/ch5_7_blue_result.png",
    "ch05/ch5_8_bgr_images_result.png",
    "ch05/ch5_9_random_color_result.png",
    "ch05/ch5_10_color_bars_result.png",
    "ch05/ch5_coordinate_system.png",
    "ch05/exercise_1_vertical_stripes.png",
    "ch05/exercise_2_vertical_color_bars.png",
    "ch06/ch6_1_gray_array_result.png",
    "ch06/ch6_2_gray_mask_result.png",
    "ch06/ch6_4_bgr_windows_result.png",
    "ch06/ch6_7_color_bars_result.png",
    "ch06/ch6_8_alpha_saved_result.png",
    "ch06/ch6_9_itemset_gray_result.png",
    "ch06/ch6_12_itemset_color_result.png",
    "ch06/ch6_13_roi_face_result.png",
    "ch06/ch6_14_mosaic_result.png",
    "ch06/ch6_15_roi_transfer_result.png",
    "ch07/ch7_6_yellow_rectangle_result.png",
    "ch08/ch8_3_color_add_result.png",
    "ch08/ch8_6_plus_wrap_result.png",
    "ch08/ch8_7_bgr_add_result.png",
    "ch08/ch8_8_1_mask_add_result.png",
    "ch08/ch8_10_weighted_sources.png",
    "ch08/ch8_10_weighted_result.png",
    "ch08/ch8_13_bitwise_and_mask_result.png",
    "ch08/ch8_15_bitwise_or_result.png",
    "ch08/ch8_16_bitwise_not_result.png",
    "ch08/ch8_17_bitwise_xor_result.png",
    "ch08/ch8_18_encrypt_decrypt_result.png",
    "ch09/ch9_2_binary_gray.png",
    "ch09/ch9_3_binary_color.png",
    "ch09/ch9_4_numbers_binary.png",
    "ch09/ch9_8_numbers_binary_inv.png",
    "ch09/ch9_11_trunc_color.png",
    "ch09/ch9_13_tozero_gray.png",
    "ch09/ch9_17_tozero_inv_color.png",
    "ch09/ch9_20_otsu_result.png",
    "ch09/ch9_21_adaptive_threshold.png",
    "ch09/ch9_22_bit_planes_low.png",
    "ch09/ch9_22_bit_planes_high.png",
    "ch09/ch9_23_lsb_effect.png",
    "ch09/ch9_24_embed_watermark.png",
    "ch09/ch9_25_extract_watermark.png",
    "ch10/ch10_resize_dsize_result.png",
    "ch10/ch10_flip_modes_result.png",
    "ch10/ch10_affine_translation_result.png",
    "ch10/ch10_affine_rotation_result.png",
    "ch10/ch10_affine_shear_result.png",
    "ch10/ch10_perspective_result.png",
    "ch10/ch10_remap_identity_result.png",
    "ch10/ch10_remap_vertical_flip_result.png",
    "ch10/ch10_remap_horizontal_flip_result.png",
    "ch10/ch10_remap_shrink_result.png",
    "ch10/ch10_remap_vertical_compress_result.png",
    "ch10/ch10_exercise_remap_flip_result.jpg",
    "ch10/ch10_exercise_face_rotate_result.jpg",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebuild OpenCV chapter 3-10 problematic images.")
    parser.add_argument("--no-backup", action="store_true", help="Do not copy originals before overwriting images.")
    args = parser.parse_args()

    if not args.no_backup:
        backup_dir = backup_targets()
        print(f"Backed up originals to {backup_dir}")

    make_ch03()
    make_ch04()
    make_ch05()
    make_ch06()
    make_ch07()
    make_ch08()
    make_ch09()
    make_ch10()
    print(f"Rebuilt {len(TARGETS)} images.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
