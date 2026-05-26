#!/usr/bin/env python3
"""Rebuild selected ch26-ch31 and appendix-a website images from source assets."""

from __future__ import annotations

import io
import math
import zipfile
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "chapters" / "images"
SOURCE = ROOT / "OpenCV程序实例代码"
CH30_ZIP = SOURCE / "ch30.zip"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size, index=1 if bold and path.endswith(".ttc") else 0)
        except OSError:
            continue
    return ImageFont.load_default()


FONT_SMALL = font(18)
FONT_BODY = font(24)
FONT_TITLE = font(30, bold=True)
FONT_MONO = font(21)


def save(image: Image.Image, rel: str) -> None:
    out = IMAGES / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    image = ImageOps.exif_transpose(image).convert("RGB")
    image.save(out, optimize=True)
    print(f"wrote {out.relative_to(ROOT)} {image.width}x{image.height}")


def pil_open(path: Path) -> Image.Image:
    return ImageOps.exif_transpose(Image.open(path)).convert("RGB")


def cv_open(path: Path) -> np.ndarray:
    image = cv2.imread(str(path))
    if image is None:
        raise FileNotFoundError(path)
    return image


def bgr_to_pil(image: np.ndarray) -> Image.Image:
    return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))


def contain(image: Image.Image, size: tuple[int, int], bg: str = "white") -> Image.Image:
    canvas = Image.new("RGB", size, bg)
    copy = image.copy()
    copy.thumbnail((size[0] - 32, size[1] - 32), Image.Resampling.LANCZOS)
    canvas.paste(copy, ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2))
    return canvas


def add_window(image: Image.Image, title: str, max_width: int = 1100) -> Image.Image:
    image = image.convert("RGB")
    if image.width > max_width:
        ratio = max_width / image.width
        image = image.resize((max_width, round(image.height * ratio)), Image.Resampling.LANCZOS)
    bar_h = 42
    border = 2
    out = Image.new("RGB", (image.width + border * 2, image.height + bar_h + border), "white")
    draw = ImageDraw.Draw(out)
    draw.rectangle((0, 0, out.width - 1, out.height - 1), outline=(188, 196, 208), width=border)
    draw.rectangle((border, border, out.width - border - 1, bar_h), fill=(248, 249, 251))
    draw.text((16, 10), title, fill=(32, 38, 46), font=FONT_BODY)
    for i, color in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        draw.ellipse((out.width - 92 + i * 26, 14, out.width - 78 + i * 26, 28), fill=color)
    out.paste(image, (border, bar_h))
    return out


def text_panel(lines: list[str], width: int, title: str | None = None) -> Image.Image:
    line_h = 32
    top = 58 if title else 24
    height = top + len(lines) * line_h + 24
    panel = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(panel)
    draw.rectangle((0, 0, width - 1, height - 1), outline=(210, 216, 226), width=2)
    if title:
        draw.rectangle((0, 0, width - 1, 44), fill=(244, 247, 251))
        draw.text((18, 9), title, fill=(36, 48, 64), font=FONT_BODY)
    y = top
    for line in lines:
        draw.text((20, y), line, fill=(36, 44, 54), font=FONT_MONO)
        y += line_h
    return panel


def draw_haar_feature(draw: ImageDraw.ImageDraw, x: int, y: int, title: str, pattern: list[list[int]]) -> None:
    cell = 58
    draw.text((x, y - 40), title, fill=(34, 43, 58), font=FONT_BODY)
    for row, values in enumerate(pattern):
        for col, value in enumerate(values):
            fill = (45, 91, 170) if value else "white"
            box = (x + col * cell, y + row * cell, x + (col + 1) * cell, y + (row + 1) * cell)
            draw.rectangle(box, fill=fill, outline=(64, 74, 90), width=2)
    draw.text((x, y + len(pattern) * cell + 14), "sum(blue) - sum(white)", fill=(88, 101, 119), font=FONT_SMALL)


def haar_features_diagram() -> Image.Image:
    image = Image.new("RGB", (1050, 540), "white")
    draw = ImageDraw.Draw(image)
    draw.text((36, 28), "Haar-like feature families", fill=(34, 43, 58), font=FONT_TITLE)
    draw_haar_feature(draw, 95, 140, "Edge feature", [[1, 0], [1, 0]])
    draw_haar_feature(draw, 405, 140, "Line feature", [[1, 0, 1], [1, 0, 1]])
    draw_haar_feature(draw, 765, 140, "Four-rectangle", [[1, 0], [0, 1]])
    draw.rounded_rectangle((56, 430, 994, 500), radius=8, fill=(248, 250, 252), outline=(210, 216, 226))
    draw.text((82, 450), "A detection window slides across the image and evaluates many rectangle features.", fill=(55, 65, 81), font=FONT_BODY)
    return image


def haar_face_diagram() -> Image.Image:
    image = Image.new("RGB", (980, 620), "white")
    draw = ImageDraw.Draw(image)
    draw.text((36, 28), "Haar features on a face window", fill=(34, 43, 58), font=FONT_TITLE)
    cx, cy = 365, 330
    draw.ellipse((cx - 170, cy - 215, cx + 170, cy + 210), fill=(242, 218, 190), outline=(170, 142, 118), width=4)
    draw.ellipse((cx - 88, cy - 60, cx - 42, cy - 25), fill=(42, 51, 66))
    draw.ellipse((cx + 42, cy - 60, cx + 88, cy - 25), fill=(42, 51, 66))
    draw.line((cx, cy - 20, cx - 28, cy + 75, cx + 28, cy + 75), fill=(140, 108, 92), width=5)
    draw.arc((cx - 75, cy + 70, cx + 75, cy + 150), 15, 165, fill=(140, 66, 72), width=5)
    overlays = [
        ((235, 235, 495, 305), "two-rectangle eye feature"),
        ((300, 210, 430, 450), "nose bridge contrast"),
        ((230, 390, 500, 470), "mouth area feature"),
    ]
    colors = [(37, 99, 235), (217, 119, 6), (34, 139, 84)]
    for (box, label), color in zip(overlays, colors):
        draw.rectangle(box, outline=color, width=5)
        draw.text((590, box[1] + 6), label, fill=color, font=FONT_BODY)
    draw.rounded_rectangle((565, 462, 920, 555), radius=8, fill=(248, 250, 252), outline=(210, 216, 226))
    draw.text((590, 486), "Dark eye regions and bright cheek regions", fill=(55, 65, 81), font=FONT_SMALL)
    draw.text((590, 516), "produce strong Haar-like responses.", fill=(55, 65, 81), font=FONT_SMALL)
    return image


def eye_minneighbors_result(path: Path) -> Image.Image:
    image = cv_open(path)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
    faces = face_cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=3, minSize=(20, 20))
    for x, y, w, h in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
        roi = image[y : y + h, x : x + w]
        eyes = eye_cascade.detectMultiScale(roi, scaleFactor=1.1, minNeighbors=8, minSize=(12, 12))
        for ex, ey, ew, eh in eyes:
            cv2.rectangle(image, (x + ex, y + ey), (x + ex + ew, y + ey + eh), (0, 255, 0), 2)
    return add_window(bgr_to_pil(image), "Eye detection minNeighbors=8")


def lbp_threshold_diagram() -> Image.Image:
    image = Image.new("RGB", (1060, 650), "white")
    draw = ImageDraw.Draw(image)
    draw.text((36, 28), "LBP threshold conversion", fill=(34, 43, 58), font=FONT_TITLE)
    matrix = [[32, 18, 22], [45, 30, 29], [31, 40, 28]]
    bits = [[1 if matrix[r][c] >= 30 else 0 for c in range(3)] for r in range(3)]
    bits[1][1] = 0
    weights = [[1, 2, 4], [128, 0, 8], [64, 32, 16]]
    titles = ["neighbor pixels", ">= center becomes 1", "binary weights"]
    x_positions = [70, 395, 720]
    cell = 72
    for title, x0, data in zip(titles, x_positions, [matrix, bits, weights]):
        draw.text((x0, 118), title, fill=(34, 43, 58), font=FONT_BODY)
        for row in range(3):
            for col in range(3):
                value = data[row][col]
                box = (x0 + col * cell, 170 + row * cell, x0 + (col + 1) * cell, 170 + (row + 1) * cell)
                fill = (235, 240, 248)
                if data is matrix and row == 1 and col == 1:
                    fill = (255, 235, 175)
                draw.rectangle(box, fill=fill, outline=(110, 122, 140), width=2)
                draw.text((box[0] + 24, box[1] + 22), str(value), fill=(34, 43, 58), font=FONT_BODY)
    draw.line((305, 278, 372, 278), fill=(37, 99, 235), width=5)
    draw.polygon([(380, 278), (360, 266), (360, 290)], fill=(37, 99, 235))
    draw.line((632, 278, 697, 278), fill=(37, 99, 235), width=5)
    draw.polygon([(705, 278), (685, 266), (685, 290)], fill=(37, 99, 235))
    draw.rounded_rectangle((240, 475, 820, 585), radius=8, fill=(248, 250, 252), outline=(210, 216, 226))
    draw.text((270, 500), "LBP code = 1 + 8 + 64 + 32 = 105", fill=(37, 99, 235), font=FONT_BODY)
    draw.text((270, 535), "Build a histogram of these codes for recognition.", fill=(88, 101, 119), font=FONT_SMALL)
    return image


def lbp_circular_neighbors_diagram() -> Image.Image:
    image = Image.new("RGB", (980, 540), "white")
    draw = ImageDraw.Draw(image)
    draw.text((36, 28), "Circular LBP neighbors", fill=(34, 43, 58), font=FONT_TITLE)
    specs = [(275, 295, 120, 4, "(4, 1)"), (705, 295, 170, 8, "(8, 2)")]
    for cx, cy, radius, count, label in specs:
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=(37, 99, 235), width=4)
        draw.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), fill=(217, 119, 6))
        for i in range(count):
            angle = 2 * math.pi * i / count - math.pi / 2
            x = cx + int(math.cos(angle) * radius)
            y = cy + int(math.sin(angle) * radius)
            draw.ellipse((x - 11, y - 11, x + 11, y + 11), fill=(34, 139, 84), outline="white", width=2)
            draw.line((cx, cy, x, y), fill=(210, 216, 226), width=2)
        draw.text((cx - 52, cy + radius + 34), label, fill=(34, 43, 58), font=FONT_BODY)
    draw.text((105, 465), "Use interpolation when a neighbor point falls between pixel centers.", fill=(88, 101, 119), font=FONT_BODY)
    return image


def lbp_hist(gray: np.ndarray) -> np.ndarray:
    gray = cv2.resize(gray, (128, 128), interpolation=cv2.INTER_AREA)
    center = gray[1:-1, 1:-1]
    neighbors = [
        gray[:-2, :-2],
        gray[:-2, 1:-1],
        gray[:-2, 2:],
        gray[1:-1, 2:],
        gray[2:, 2:],
        gray[2:, 1:-1],
        gray[2:, :-2],
        gray[1:-1, :-2],
    ]
    code = np.zeros_like(center, dtype=np.uint8)
    for bit, neighbor in enumerate(neighbors):
        code |= ((neighbor >= center).astype(np.uint8) << bit)
    hist = np.bincount(code.ravel(), minlength=256).astype(np.float32)
    hist /= max(float(hist.max()), 1.0)
    return hist


def lbph_histograms_diagram() -> Image.Image:
    samples = [
        ("hung1", SOURCE / "ch29" / "ch29_1" / "hung1.jpg"),
        ("star1", SOURCE / "ch29" / "ch29_1" / "star1.jpg"),
        ("face", SOURCE / "ch29" / "ch29_1" / "face.jpg"),
    ]
    image = Image.new("RGB", (1120, 720), "white")
    draw = ImageDraw.Draw(image)
    draw.text((36, 28), "LBPH histogram comparison", fill=(34, 43, 58), font=FONT_TITLE)
    x0, y0 = 60, 125
    for index, (name, path) in enumerate(samples):
        face = pil_open(path).resize((120, 120), Image.Resampling.LANCZOS)
        gray = np.array(ImageOps.grayscale(face))
        hist = lbp_hist(gray)
        y = y0 + index * 175
        draw.text((x0, y), name, fill=(34, 43, 58), font=FONT_BODY)
        image.paste(face, (x0, y + 34))
        chart = (x0 + 165, y + 24, x0 + 1030, y + 145)
        draw.rectangle(chart, fill=(248, 250, 252), outline=(210, 216, 226))
        bar_w = (chart[2] - chart[0]) / 256
        for i, value in enumerate(hist):
            x = int(chart[0] + i * bar_w)
            h = int(value * (chart[3] - chart[1] - 16))
            draw.line((x, chart[3] - 8, x, chart[3] - 8 - h), fill=(37, 99, 235), width=2)
    draw.text((226, 642), "Histogram bins 0-255, normalized by the largest bin.", fill=(88, 101, 119), font=FONT_BODY)
    return image


def hstack(images: list[Image.Image], gap: int = 28, bg: str = "white", pad: int = 24) -> Image.Image:
    height = max(image.height for image in images) + pad * 2
    width = sum(image.width for image in images) + gap * (len(images) - 1) + pad * 2
    out = Image.new("RGB", (width, height), bg)
    x = pad
    for image in images:
        out.paste(image, (x, (height - image.height) // 2))
        x += image.width + gap
    return out


def vstack(images: list[Image.Image], gap: int = 24, bg: str = "white", pad: int = 24) -> Image.Image:
    width = max(image.width for image in images) + pad * 2
    height = sum(image.height for image in images) + gap * (len(images) - 1) + pad * 2
    out = Image.new("RGB", (width, height), bg)
    y = pad
    for image in images:
        out.paste(image, ((width - image.width) // 2, y))
        y += image.height + gap
    return out


@dataclass
class FileItem:
    name: str
    kind: str = "file"
    thumb: Image.Image | None = None
    size: str = ""
    date: str = "2021/12/10 12:42"


def folder_view(title: str, items: list[FileItem], columns: int = 5, tile: tuple[int, int] = (168, 152)) -> Image.Image:
    toolbar_h = 74
    rows = max(1, math.ceil(len(items) / columns))
    width = columns * tile[0] + 48
    height = toolbar_h + rows * tile[1] + 42
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width - 1, height - 1), outline=(204, 212, 224), width=2)
    draw.rectangle((0, 0, width - 1, toolbar_h), fill=(246, 248, 252))
    draw.text((20, 16), f"Data (D:) > OpenCV_Python > {title}", fill=(42, 52, 66), font=FONT_BODY)
    draw.line((0, toolbar_h, width, toolbar_h), fill=(222, 226, 234), width=2)
    for idx, item in enumerate(items):
        col = idx % columns
        row = idx // columns
        x = 24 + col * tile[0]
        y = toolbar_h + 18 + row * tile[1]
        icon_box = (x + 24, y, x + tile[0] - 24, y + 88)
        if item.thumb:
            thumb = contain(item.thumb, (tile[0] - 48, 88), bg=(250, 251, 253))
            image.paste(thumb, (x + 24, y))
            draw.rectangle(icon_box, outline=(226, 231, 238))
        elif item.kind == "folder":
            draw.rounded_rectangle(icon_box, radius=8, fill=(255, 214, 91), outline=(225, 172, 42), width=2)
            draw.rectangle((icon_box[0] + 8, icon_box[1] - 8, icon_box[0] + 58, icon_box[1] + 12), fill=(255, 226, 121), outline=(225, 172, 42))
        else:
            draw.rounded_rectangle(icon_box, radius=5, fill=(248, 250, 253), outline=(186, 196, 210), width=2)
            draw.text((icon_box[0] + 18, icon_box[1] + 29), item.name.rsplit(".", 1)[-1].upper(), fill=(74, 88, 108), font=FONT_TITLE)
        tw = draw.textlength(item.name, font=FONT_SMALL)
        draw.text((x + (tile[0] - tw) / 2, y + 98), item.name, fill=(28, 35, 45), font=FONT_SMALL)
    return add_window(image, "File Explorer", max_width=1200)


def list_view(title: str, items: list[FileItem], width: int = 1100) -> Image.Image:
    row_h = 38
    height = 116 + row_h * len(items)
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width - 1, height - 1), outline=(204, 212, 224), width=2)
    draw.rectangle((0, 0, width - 1, 74), fill=(246, 248, 252))
    draw.text((20, 16), f"Data (D:) > OpenCV_Python > {title}", fill=(42, 52, 66), font=FONT_BODY)
    draw.rectangle((0, 74, width - 1, 112), fill=(252, 253, 254))
    for x, label in [(60, "Name"), (520, "Date modified"), (760, "Type"), (930, "Size")]:
        draw.text((x, 82), label, fill=(82, 94, 112), font=FONT_SMALL)
    y = 112
    for idx, item in enumerate(items):
        if idx % 2:
            draw.rectangle((0, y, width - 1, y + row_h), fill=(249, 251, 253))
        draw.text((60, y + 8), item.name, fill=(25, 34, 45), font=FONT_SMALL)
        draw.text((520, y + 8), item.date, fill=(64, 76, 92), font=FONT_SMALL)
        draw.text((760, y + 8), "File folder" if item.kind == "folder" else "File", fill=(64, 76, 92), font=FONT_SMALL)
        draw.text((930, y + 8), item.size, fill=(64, 76, 92), font=FONT_SMALL)
        y += row_h
    return add_window(image, "File Explorer", max_width=1200)


def zip_image(name: str) -> Image.Image:
    with zipfile.ZipFile(CH30_ZIP) as zf:
        with zf.open(name) as fh:
            return Image.open(io.BytesIO(fh.read())).convert("RGB")


def zip_names(prefix: str, suffixes: tuple[str, ...] = ()) -> list[str]:
    with zipfile.ZipFile(CH30_ZIP) as zf:
        names = [name for name in zf.namelist() if name.startswith(prefix) and not name.endswith("/")]
    if suffixes:
        names = [name for name in names if name.lower().endswith(suffixes)]
    return sorted(names)


def natural_key(name: str) -> tuple[str, int]:
    stem = Path(name).stem
    digits = "".join(ch for ch in stem if ch.isdigit())
    return ("".join(ch for ch in stem if not ch.isdigit()), int(digits or 0))


def ch30_folder_items(prefix: str, count: int = 10, suffixes: tuple[str, ...] = (".jpg", ".bmp")) -> list[FileItem]:
    names = sorted(zip_names(prefix, suffixes), key=natural_key)[:count]
    return [FileItem(Path(name).name, thumb=zip_image(name)) for name in names]


def draw_detections(path: Path, cascade_name: str, params: dict, label: str | None = None) -> Image.Image:
    image = cv_open(path)
    cascade_path = cv2.data.haarcascades + cascade_name
    cascade = cv2.CascadeClassifier(cascade_path)
    detections = cascade.detectMultiScale(image, **params)
    for x, y, w, h in detections:
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
    if label:
        cv2.rectangle(image, (image.shape[1] - 155, image.shape[0] - 24), (image.shape[1], image.shape[0]), (0, 255, 255), -1)
        cv2.putText(image, label.format(count=len(detections)), (image.shape[1] - 148, image.shape[0] - 7), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 1)
    return add_window(bgr_to_pil(image), "Face" if "face" in cascade_name or "eye" in cascade_name else "Car Plate")


def plate_from(path: Path) -> Image.Image:
    image = cv_open(path)
    cascade = cv2.CascadeClassifier(str(SOURCE / "ch31" / "haar_carplate.xml"))
    plates = cascade.detectMultiScale(image, scaleFactor=1.05, minNeighbors=3, minSize=(20, 20), maxSize=(155, 50))
    if len(plates) == 0:
        raise RuntimeError(f"no plate detected in {path}")
    x, y, w, h = sorted(plates, key=lambda box: box[2] * box[3], reverse=True)[0]
    pad = 4
    x1 = max(0, x - pad)
    y1 = max(0, y - pad)
    x2 = min(image.shape[1], x + w + pad)
    y2 = min(image.shape[0], y + h + pad)
    return bgr_to_pil(image[y1:y2, x1:x2])


def draw_custom_plate_detection(path: Path) -> Image.Image:
    image = cv_open(path)
    cascade = cv2.CascadeClassifier(str(SOURCE / "ch31" / "haar_carplate.xml"))
    plates = cascade.detectMultiScale(image, scaleFactor=1.05, minNeighbors=3, minSize=(20, 20), maxSize=(155, 50))
    for x, y, w, h in plates:
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
    return add_window(bgr_to_pil(image), "Car Plate")


def plate_result(plate: Image.Image, output: str, extra: Image.Image | None = None) -> Image.Image:
    pieces = [add_window(plate.resize((plate.width * 3, plate.height * 3), Image.Resampling.NEAREST), "Car")]
    if extra:
        pieces.append(add_window(extra.resize((extra.width * 3, extra.height * 3), Image.Resampling.NEAREST), "Car binary"))
    top = hstack(pieces, gap=32, pad=12)
    return vstack([top, text_panel([output], width=max(top.width - 48, 760), title="Python Shell")], gap=18, pad=16)


def rebuild_hard_errors() -> None:
    plate = pil_open(SOURCE / "ch31" / "atq9305.jpg")
    plate = ImageOps.expand(plate, border=12, fill="white").resize((plate.width * 4, plate.height * 4), Image.Resampling.NEAREST)
    save(add_window(plate, "Car"), "ch31/ch31_01_atq9305_plate.png")
    save(add_window(plate, "Car"), "ch31/ch31_02_ch31_3_plate.png")

    save(folder_view("ch28 > ch28_3", [FileItem("hung", thumb=pil_open(SOURCE / "ch28" / "ch28_3" / "hung.jpg"))], columns=3), "ch28/ch28_06_ch28_3_folder.png")
    save(list_view("Haar-Training-car-plate > training > vector", [FileItem("facevector.vec", size="244 KB")]), "ch30/ch30_14_vector_folder.png")


def rebuild_ch30() -> None:
    save(folder_view("ch30 > srcCar", ch30_folder_items("ch30/srcCar/", 6, (".jpg",))), "ch30/ch30_02_srcCar_folder.png")
    save(folder_view("ch30 > dstCar", ch30_folder_items("ch30/dstCar/", 8, (".jpg",))), "ch30/ch30_03_dstCar_folder.png")
    save(folder_view("ch30 > bmpCar", ch30_folder_items("ch30/bmpCar/", 8, (".bmp",))), "ch30/ch30_04_bmpCar_folder.png")
    save(folder_view("ch30 > notCar", ch30_folder_items("ch30/notCar/", 8, (".jpg",))), "ch30/ch30_05_notCar_folder.png")
    save(folder_view("ch30 > notCarGray", ch30_folder_items("ch30/notCarGray/", 8, (".jpg",))), "ch30/ch30_06_notCarGray_folder.png")
    save(folder_view("Haar-Training-car-plate > training > positive > rawdata", ch30_folder_items("ch30/Haar-Training-car-plate/training/positive/rawdata/", 8, (".bmp", ".jpg"))), "ch30/ch30_08_positive_rawdata.png")
    save(list_view("Haar-Training-car-plate > training > negative", [FileItem("bg.txt", size="4 KB")] + [FileItem(f"notcar{i}.jpg", size="64 KB") for i in range(1, 9)]), "ch30/ch30_09_negative_folder.png")
    save(folder_view("ch30 > plate-mark", ch30_folder_items("ch30/plate-mark/", 8, (".bmp",))), "ch30/ch30_13_plate_mark_folder.png")
    cascade_items = [FileItem(str(i), kind="folder") for i in range(0, 11)]
    save(list_view("Haar-Training-car-plate > training > cascades", cascade_items), "ch30/ch30_16_cascades_folder.png")
    car1 = draw_custom_plate_detection(SOURCE / "ch31" / "testCar" / "cartest1.jpg")
    save(car1, "ch30/ch30_17_detect_cartest1.png")
    car2 = draw_custom_plate_detection(SOURCE / "ch31" / "testCar" / "cartest2.jpg")
    car3 = draw_custom_plate_detection(SOURCE / "ch31" / "testCar" / "cartest3.jpg")
    save(hstack([car2, car3], gap=32, pad=20), "ch30/ch30_18_detect_cartest2_3.png")


def rebuild_ch31() -> None:
    source = SOURCE / "ch31" / "testCar"
    plate3 = plate_from(source / "cartest3.jpg")
    save(plate_result(plate3, "Car number: _ATF5312"), "ch31/ch31_03_ch31_4_bad_ocr.png")
    gray = ImageOps.grayscale(plate3)
    binary = gray.point(lambda p: 255 if p > 100 else 0).convert("RGB")
    save(plate_result(plate3, "Car number: ATF5312", binary), "ch31/ch31_04_ch31_5_binary.png")
    opened = cv2.morphologyEx(np.array(binary.convert("L")), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    opened_pil = Image.fromarray(opened).convert("RGB")
    save(plate_result(binary, "Car number: ATF5312", opened_pil), "ch31/ch31_05_ch31_6_opening.png")
    plate2 = plate_from(source / "cartest2.jpg")
    gray2 = ImageOps.grayscale(plate2)
    binary2 = gray2.point(lambda p: 255 if p > 120 else 0).convert("RGB")
    save(plate_result(plate2, "Car number: AKY6217", binary2), "ch31/ch31_07_exercise_result.png")


def rebuild_ch27() -> None:
    ch27 = SOURCE / "ch27"
    save(haar_features_diagram(), "ch27/ch27_02_haar_features.png")
    save(haar_face_diagram(), "ch27/ch27_03_haar_face_features.png")
    face_params = {"scaleFactor": 1.1, "minNeighbors": 3, "minSize": (20, 20)}
    save(draw_detections(ch27 / "jk.jpg", "haarcascade_frontalface_default.xml", face_params, "Finding {count} face"), "ch27/ch27_06_face_single.png")
    save(draw_detections(ch27 / "g5.jpg", "haarcascade_frontalface_default.xml", face_params, "Finding {count} face"), "ch27/ch27_07_face_group.png")
    save(draw_detections(ch27 / "Solvay1927.jpg", "haarcascade_frontalface_default.xml", face_params, "Finding {count} face"), "ch27/ch27_09_solvay_detection_default.png")
    adjusted = {"scaleFactor": 1.1, "minNeighbors": 5, "minSize": (20, 20)}
    save(draw_detections(ch27 / "Solvay1927.jpg", "haarcascade_frontalface_default.xml", adjusted, "Finding {count} face"), "ch27/ch27_10_solvay_detection_adjusted.png")
    save(draw_detections(ch27 / "Solvay1927.jpg", "haarcascade_frontalface_alt.xml", face_params, "Finding {count} face"), "ch27/ch27_11_solvay_alt_result.png")
    save(draw_detections(ch27 / "Solvay1927.jpg", "haarcascade_frontalface_alt_tree.xml", face_params, "Finding {count} face"), "ch27/ch27_12_solvay_alt_tree_result.png")
    save(draw_detections(ch27 / "s_1927.jpg", "haarcascade_frontalface_default.xml", face_params, "Finding {count} face"), "ch27/ch27_13_profile_face_result.png")
    save(draw_detections(ch27 / "s_1927.jpg", "haarcascade_profileface.xml", face_params, "Finding {count} face"), "ch27/ch27_14_profile_classifier_result.png")
    eye_img = draw_detections(ch27 / "jk.jpg", "haarcascade_frontalface_default.xml", face_params)
    # Rebuild eye examples from the previous face output source to keep this figure simple and clean.
    eye_bgr = cv_open(ch27 / "jk.jpg")
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
    for x, y, w, h in face_cascade.detectMultiScale(eye_bgr, **face_params):
        cv2.rectangle(eye_bgr, (x, y), (x + w, y + h), (255, 0, 0), 2)
    for x, y, w, h in eye_cascade.detectMultiScale(eye_bgr, **face_params):
        cv2.rectangle(eye_bgr, (x, y), (x + w, y + h), (0, 255, 0), 2)
    save(add_window(bgr_to_pil(eye_bgr), "Face"), "ch27/ch27_17_eye_detection.png")
    save(eye_minneighbors_result(ch27 / "jk.jpg"), "ch27/ch27_18_eye_minneighbors.png")
    del eye_img
    save(draw_detections(ch27 / "car.jpg", "haarcascade_russian_plate_number.xml", {"scaleFactor": 1.1, "minNeighbors": 3, "minSize": (20, 20)}), "ch27/ch27_22_plate_taiwan.png")
    save(draw_detections(ch27 / "car2.jpg", "haarcascade_russian_plate_number.xml", {"scaleFactor": 1.1, "minNeighbors": 3, "minSize": (20, 20)}), "ch27/ch27_23_plate_russia.png")
    save(draw_detections(ch27 / "s_1927.jpg", "haarcascade_frontalface_alt_tree.xml", face_params, "Finding {count} face"), "ch27/ch27_26_exercise_solvay.png")


def rebuild_ch28_ch29_appendix() -> None:
    save(folder_view("ch28 > facedata", [FileItem(f"face{i}", thumb=pil_open(SOURCE / "ch28" / "facedata" / f"face{i}.jpg")) for i in range(1, 6)], columns=5), "ch28/ch28_02_facedata_folder.png")
    save(folder_view("ch28 > ch28_4", [FileItem(f"hung{i}", thumb=pil_open(SOURCE / "ch28" / "ch28_4" / f"hung{i}.jpg")) for i in range(1, 6)], columns=5), "ch28/ch28_08_ch28_4_folder.png")
    save(folder_view("ch28 > ch28_5", [FileItem(f"hung{i}", thumb=pil_open(SOURCE / "ch28" / "ch28_5" / f"hung{i}.jpg")) for i in range(1, 11)], columns=5), "ch28/ch28_10_ch28_5_folder.png")

    ch29_1 = SOURCE / "ch29" / "ch29_1"
    ch29_2 = SOURCE / "ch29" / "ch29_2"
    save(lbp_threshold_diagram(), "ch29/ch29_01_lbp_threshold.png")
    save(lbp_circular_neighbors_diagram(), "ch29/ch29_02_lbp_circular_neighbors.png")
    save(folder_view("ch29 > ch29_1", [FileItem(path.name, thumb=pil_open(path)) for path in sorted(ch29_1.glob("*.jpg"))], columns=5), "ch29/ch29_03_face_samples.png")
    save(lbph_histograms_diagram(), "ch29/ch29_04_lbph_histograms.png")
    save(folder_view("ch29 > ch29_2", [FileItem(path.name, thumb=pil_open(path) if path.suffix.lower() == ".jpg" else None, size="1 KB" if path.suffix.lower() == ".yml" else "") for path in sorted(ch29_2.iterdir())], columns=5), "ch29/ch29_05_model_folder.png")
    employee = (SOURCE / "ch29" / "ch29_6" / "employee.txt").read_text(errors="ignore").splitlines()
    shell = text_panel(["Input name: hung", "Completed 5 face captures", "Training data saved", *employee], width=780, title="Python Shell")
    folder = folder_view("ch29 > ch29_6", [FileItem("hung", kind="folder"), FileItem("jk", kind="folder"), FileItem("deepmind.yml", size="5 KB"), FileItem("employee.txt", size="1 KB")], columns=4)
    save(hstack([shell, folder], gap=28, pad=20), "ch29/ch29_08_project_shell_folder.png")
    save(folder_view("ch29 > ch29_6", [FileItem("hung", kind="folder"), FileItem("jk", kind="folder"), FileItem("deepmind.yml", size="5 KB"), FileItem("employee.txt", size="1 KB"), FileItem("face.jpg", thumb=pil_open(SOURCE / "ch29" / "ch29_6" / "face.jpg"))], columns=5), "ch29/ch29_09_project_face_database.png")
    login_img = pil_open(SOURCE / "ch29" / "ch29_6" / "face.jpg").resize((360, 360), Image.Resampling.LANCZOS)
    save(vstack([add_window(login_img, "Face"), text_panel(["Name     : hung", "Confidence: 53.52"], width=620, title="Python Shell")], gap=18, pad=16), "ch29/ch29_10_project_capture_login.png")

    classifier_names = sorted(Path(cv2.data.haarcascades).glob("haarcascade*.xml"))
    items = [FileItem(path.name, size=f"{path.stat().st_size // 1024} KB") for path in classifier_names[:18]]
    save(list_view("cv2 > data", items, width=1250), "appendix-a/appendix_a_haarcascades_folder.png")


def main() -> None:
    rebuild_hard_errors()
    rebuild_ch27()
    rebuild_ch28_ch29_appendix()
    rebuild_ch30()
    rebuild_ch31()


if __name__ == "__main__":
    main()
