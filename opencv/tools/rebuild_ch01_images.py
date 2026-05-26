#!/usr/bin/env python3
"""Rebuild Chapter 1 images that were originally cropped from book pages."""

from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
IMAGE_ROOT = ROOT / "chapters" / "images" / "ch01"
SAMPLE_ROOT = ROOT / "OpenCV程序实例代码" / "ch1"

TEXT = (35, 43, 58)
MUTED = (96, 108, 126)
LINE = (196, 205, 218)
PANEL = (248, 250, 252)
BLUE = (52, 109, 219)


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf"] if bold else ["/System/Library/Fonts/Supplemental/Arial.ttf"]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


F13 = font(13)
F16 = font(16)
F18 = font(18, bold=True)
F22 = font(22, bold=True)


def save_image(image: Image.Image, name: str) -> None:
    IMAGE_ROOT.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(IMAGE_ROOT / name, optimize=True)


def titlebar(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str) -> None:
    x1, y1, x2, y2 = box
    draw.rectangle(box, fill=(250, 250, 251), outline=LINE)
    draw.text((x1 + 12, y1 + 7), title, fill=TEXT, font=F13)
    cy = (y1 + y2) // 2
    for i, fill in enumerate([(118, 128, 144), (118, 128, 144), (223, 55, 68)]):
        cx = x2 - 68 + i * 23
        draw.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=fill)


def opencv_window(title: str, content: Image.Image, *, scale: int = 1) -> Image.Image:
    image = ImageOps.exif_transpose(content).convert("RGB")
    if scale != 1:
        image = image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)
    border = 10
    bar_h = 34
    canvas = Image.new("RGB", (image.width + border * 2, image.height + border * 2 + bar_h), "white")
    draw = ImageDraw.Draw(canvas)
    titlebar(draw, (0, 0, canvas.width - 1, bar_h), title)
    draw.rectangle((0, 0, canvas.width - 1, canvas.height - 1), outline=LINE)
    canvas.paste(image, (border, bar_h + border))
    return canvas


def two_windows(title: str, windows: list[tuple[str, Image.Image]]) -> Image.Image:
    rendered = [opencv_window(name, image) for name, image in windows]
    gap = 28
    margin = 32
    title_h = 44
    width = sum(img.width for img in rendered) + gap * (len(rendered) - 1) + margin * 2
    height = max(img.height for img in rendered) + margin * 2 + title_h
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, margin), title, fill=TEXT, font=F22)
    x = margin
    y = margin + title_h
    for image in rendered:
        canvas.paste(image, (x, y))
        x += image.width + gap
    return canvas


def folder_result() -> Image.Image:
    width, height = 820, 300
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((24, 24, width - 24, height - 24), radius=8, fill=PANEL, outline=LINE)
    draw.text((48, 44), "OpenCV_Python > ch1", fill=TEXT, font=F18)
    draw.rectangle((48, 86, width - 48, 118), fill=(238, 242, 247), outline=LINE)
    draw.text((92, 94), "Name", fill=MUTED, font=F16)
    draw.text((330, 94), "Type", fill=MUTED, font=F16)
    draw.text((470, 94), "Result", fill=MUTED, font=F16)

    rows = [("out1_7_1.tiff", "TIFF image", "saved"), ("out1_7_2.png", "PNG image", "saved")]
    for i, (name, kind, result) in enumerate(rows):
        y = 128 + i * 58
        draw.rectangle((48, y, width - 48, y + 46), fill="white", outline=(224, 229, 238))
        draw.rectangle((68, y + 12, 86, y + 31), fill=(220, 232, 255), outline=BLUE)
        draw.text((100, y + 13), name, fill=TEXT, font=F16)
        draw.text((330, y + 13), kind, fill=MUTED, font=F16)
        draw.text((470, y + 13), result, fill=(31, 137, 72), font=F16)
    return image


def exercise_reference(jk: Image.Image) -> Image.Image:
    gray = ImageOps.grayscale(jk).convert("RGB")
    return two_windows("Exercise reference", [("Color", jk), ("Gray", gray)])


TARGETS = ["ch1_2_result.png", "ch1_6_result.png", "ch1_7_result.png", "exercise_ref.png"]


def backup_targets() -> Path:
    backup_dir = Path("/tmp") / "opencv-image-backups" / f"ch01-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    for name in TARGETS:
        source = IMAGE_ROOT / name
        if source.exists():
            target = backup_dir / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    return backup_dir


def rebuild() -> None:
    jk = Image.open(SAMPLE_ROOT / "jk.jpg").convert("RGB")
    save_image(opencv_window("MyPicture", jk), "ch1_2_result.png")
    save_image(two_windows("Window display modes", [("MyPicture1", jk), ("MyPicture2", ImageOps.grayscale(jk).convert("RGB"))]), "ch1_6_result.png")
    save_image(folder_result(), "ch1_7_result.png")
    save_image(exercise_reference(jk), "exercise_ref.png")


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebuild OpenCV chapter 1 problematic images.")
    parser.add_argument("--no-backup", action="store_true", help="Do not copy originals before overwriting images.")
    args = parser.parse_args()
    if not args.no_backup:
        print(f"Backed up originals to {backup_targets()}")
    rebuild()
    print(f"Rebuilt {len(TARGETS)} images.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
