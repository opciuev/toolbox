#!/usr/bin/env python3
"""Rebuild Chapter 2 images from deterministic sources.

The previous Chapter 2 assets were large page screenshots with surrounding
book text. This script regenerates the web images as standalone figures, using
the original chapter sample images where possible.
"""

from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "chapters" / "images" / "ch02"
SAMPLE_DIR = ROOT / "OpenCV程序实例代码" / "ch2"

TEXT = (39, 45, 58)
MUTED = (105, 116, 133)
BLUE = (42, 117, 187)
CYAN = (20, 154, 190)
GRID = (74, 85, 104)
PANEL = (245, 248, 252)
AXIS = (84, 64, 170)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    name = "Arial Bold.ttf" if bold else "Arial.ttf"
    path = Path("/System/Library/Fonts/Supplemental") / name
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:
        return ImageFont.load_default()


def save_image(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() in {".jpg", ".jpeg"}:
        image.convert("RGB").save(path, quality=94, optimize=True)
    else:
        image.save(path, optimize=True)


def trim_whitespace(image: Image.Image, padding: int = 24) -> Image.Image:
    rgb = image.convert("RGB")
    bg = Image.new("RGB", rgb.size, "white")
    diff = Image.new("L", rgb.size, 0)
    rgb_px = rgb.load()
    diff_px = diff.load()
    width, height = rgb.size
    for y in range(height):
        for x in range(width):
            r, g, b = rgb_px[x, y]
            if abs(r - 255) > 8 or abs(g - 255) > 8 or abs(b - 255) > 8:
                diff_px[x, y] = 255
    bbox = diff.getbbox()
    if not bbox:
        return image
    x1, y1, x2, y2 = bbox
    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(width, x2 + padding)
    y2 = min(height, y2 + padding)
    return image.crop((x1, y1, x2, y2))


def h_matrix() -> list[list[int]]:
    rows: list[list[int]] = []
    for y in range(12):
        row = []
        for x in range(12):
            is_bar = 5 <= y <= 6 and 2 <= x <= 9
            is_left = 1 <= x <= 3 and 1 <= y <= 10
            is_right = 8 <= x <= 10 and 1 <= y <= 10
            row.append(1 if is_bar or is_left or is_right else 0)
        rows.append(row)
    return rows


def draw_grid(draw: ImageDraw.ImageDraw, origin: tuple[int, int], values: list[list[int]], cell: int, mode: str) -> None:
    x0, y0 = origin
    for y, row in enumerate(values):
        for x, value in enumerate(row):
            box = (x0 + x * cell, y0 + y * cell, x0 + (x + 1) * cell, y0 + (y + 1) * cell)
            if mode == "bitmap":
                fill = (250, 250, 250) if value else (79, 83, 93)
                draw.rectangle(box, fill=fill, outline=(39, 43, 52), width=2)
            elif mode == "blue":
                fill = (48, 88, 189) if value else (75, 82, 93)
                draw.rectangle(box, fill=fill, outline=(40, 45, 55), width=2)
            else:
                draw.rectangle(box, fill="white", outline=(122, 130, 142), width=1)
                text = str(value)
                bbox = draw.textbbox((0, 0), text, font=font(16))
                tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                draw.text((box[0] + (cell - tw) / 2, box[1] + (cell - th) / 2 - 1), text, fill=TEXT, font=font(16))


def draw_arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: tuple[int, int, int]) -> None:
    draw.line((*start, *end), fill=color, width=4)
    ex, ey = end
    sx, sy = start
    if ex >= sx:
        points = [(ex, ey), (ex - 16, ey - 9), (ex - 16, ey + 9)]
    else:
        points = [(ex, ey), (ex + 16, ey - 9), (ex + 16, ey + 9)]
    draw.polygon(points, fill=color)


def make_bitmap_h_matrix() -> Image.Image:
    values = h_matrix()
    image = Image.new("RGB", (1120, 590), "white")
    draw = ImageDraw.Draw(image)
    draw.text((56, 34), "Bitmap H", fill=TEXT, font=font(34, True))
    draw.text((612, 34), "0 / 1 Matrix", fill=TEXT, font=font(34, True))
    draw_grid(draw, (66, 96), values, 34, "bitmap")
    draw_grid(draw, (612, 96), values, 34, "matrix")
    draw.text((68, 535), "1 = white pixel, 0 = black pixel", fill=MUTED, font=font(22))
    return image


def make_gray_scale() -> Image.Image:
    src = ImageOps.exif_transpose(Image.open(SAMPLE_DIR / "jk_gray.jpg")).convert("L").resize((300, 303))
    image = Image.new("RGB", (880, 430), "white")
    draw = ImageDraw.Draw(image)
    image.paste(src.convert("RGB"), (70, 82))
    draw.rectangle((69, 81, 370, 385), outline=(185, 190, 200), width=2)
    draw.text((70, 34), "Gray image", fill=TEXT, font=font(30, True))
    draw.text((470, 34), "0 - 255 gray values", fill=TEXT, font=font(30, True))
    values = [0, 32, 64, 96, 128, 160, 192, 224, 255]
    for i, value in enumerate(values):
        y = 82 + i * 34
        fill = (value, value, value)
        draw.rectangle((470, y, 660, y + 30), fill=fill, outline=(110, 118, 130))
        draw.text((688, y + 3), str(value), fill=TEXT, font=font(22))
    return image


def make_rgb_material() -> Image.Image:
    image = Image.new("RGB", (1120, 730), "white")
    draw = ImageDraw.Draw(image)
    circles = [((225, 160), (237, 38, 50), "R (Red)"), ((560, 160), (83, 198, 52), "G (Green)"), ((895, 160), (55, 86, 176), "B (Blue)")]
    for center, color, label in circles:
        x, y = center
        draw.ellipse((x - 80, y - 80, x + 80, y + 80), fill=color)
        bbox = draw.textbbox((0, 0), label, font=font(25, True))
        draw.text((x - (bbox[2] - bbox[0]) / 2, y + 105), label, fill=AXIS, font=font(25, True))

    browser = (80, 365, 1040, 660)
    draw.rounded_rectangle(browser, radius=8, fill=(250, 251, 253), outline=(190, 197, 210), width=2)
    draw.rectangle((80, 365, 1040, 415), fill=(239, 242, 247), outline=(190, 197, 210))
    draw.rounded_rectangle((120, 378, 530, 403), radius=12, fill="white", outline=(199, 206, 218))
    draw.text((140, 381), "https://materialui.co/colors", fill=MUTED, font=font(17))

    swatches = [
        (244, 67, 54), (233, 30, 99), (156, 39, 176), (103, 58, 183), (63, 81, 181),
        (33, 150, 243), (3, 169, 244), (0, 188, 212), (0, 150, 136), (76, 175, 80),
        (139, 195, 74), (205, 220, 57), (255, 235, 59), (255, 193, 7), (255, 152, 0),
        (255, 87, 34), (121, 85, 72), (158, 158, 158), (96, 125, 139), (77, 182, 172),
    ]
    labels = ["Red", "Pink", "Purple", "Deep", "Indigo", "Blue", "Light", "Cyan", "Teal", "Green"]
    x0, y0, cell_w, cell_h = 120, 445, 82, 48
    for i, color in enumerate(swatches):
        row, col = divmod(i, 10)
        box = (x0 + col * cell_w, y0 + row * cell_h, x0 + (col + 1) * cell_w, y0 + (row + 1) * cell_h)
        draw.rectangle(box, fill=color)
        if row == 0:
            draw.text((box[0] + 8, box[1] - 24), labels[col], fill=MUTED, font=font(13))
    draw.ellipse((840, 512, 886, 558), outline=(64, 72, 88), width=4)
    draw.text((910, 515), "rgb(77, 182, 172)", fill=TEXT, font=font(23, True))
    return image


def make_color_dialog() -> Image.Image:
    image = Image.new("RGB", (880, 640), "white")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((110, 50, 770, 590), radius=10, fill=(247, 248, 250), outline=(172, 178, 190), width=2)
    draw.rectangle((110, 50, 770, 96), fill=(236, 239, 244), outline=(172, 178, 190))
    draw.text((136, 62), "Colors", fill=TEXT, font=font(22, True))
    draw.text((270, 122), "Custom", fill=TEXT, font=font(24, True))

    for i in range(250):
        r = int(255 * i / 249)
        for j in range(150):
            g = int(255 * (1 - j / 149))
            b = int(255 * (1 - i / 249) * (j / 149))
            draw.point((160 + i, 170 + j), fill=(r, g, b))
    draw.rectangle((160, 170, 410, 320), outline=(132, 140, 152), width=2)
    for j in range(150):
        shade = int(255 * (1 - j / 149))
        draw.line((426, 170 + j, 446, 170 + j), fill=(shade, shade, shade))

    draw.text((160, 350), "Color model: RGB", fill=TEXT, font=font(21))
    fields = [("Red", "255"), ("Green", "255"), ("Blue", "0")]
    for i, (name, value) in enumerate(fields):
        y = 392 + i * 46
        draw.text((160, y + 6), name, fill=TEXT, font=font(21))
        draw.rectangle((300, y, 410, y + 34), fill="white", outline=(163, 171, 184))
        draw.text((330, y + 5), value, fill=TEXT, font=font(21, True))

    draw.text((540, 170), "New", fill=TEXT, font=font(20))
    draw.rectangle((540, 200, 690, 275), fill=(255, 255, 0), outline=(112, 120, 132), width=2)
    draw.text((540, 304), "Current", fill=TEXT, font=font(20))
    draw.rectangle((540, 334, 690, 409), fill=(0, 0, 0), outline=(112, 120, 132), width=2)
    draw.rounded_rectangle((562, 500, 704, 546), radius=5, fill=(232, 239, 250), outline=(104, 128, 170))
    draw.text((608, 510), "OK", fill=TEXT, font=font(22, True))
    return image


def make_rgb_pixel_channels() -> Image.Image:
    values = h_matrix()
    image = Image.new("RGB", (1160, 700), "white")
    draw = ImageDraw.Draw(image)
    draw.text((60, 34), "RGB pixel as channels", fill=TEXT, font=font(34, True))
    draw_grid(draw, (70, 140), values, 34, "blue")
    draw.rectangle((104, 174, 138, 208), outline=(250, 250, 250), width=3)
    draw_arrow(draw, (500, 250), (610, 250), (202, 58, 92))
    draw.text((632, 222), "(R, G, B) = (0, 0, 255)", fill=(96, 50, 150), font=font(31, True))

    labels = [("R", 0, (245, 99, 99)), ("G", 0, (80, 190, 90)), ("B", 255, (76, 128, 220))]
    for idx, (label, on_value, color) in enumerate(labels):
        x0 = 520 + idx * 205
        y0 = 360
        draw.text((x0 + 74, y0 - 46), label, fill=color, font=font(32, True))
        for y, row in enumerate(values):
            for x, v in enumerate(row):
                number = on_value if v else 0
                box = (x0 + x * 14, y0 + y * 14, x0 + (x + 1) * 14, y0 + (y + 1) * 14)
                draw.rectangle(box, fill=(255, 255, 255), outline=(175, 181, 190))
                if x % 2 == 0 and y % 2 == 0:
                    draw.text((box[0] + 1, box[1] - 1), str(number), fill=TEXT, font=font(9))
    return image


def jk_image() -> Image.Image:
    return ImageOps.exif_transpose(Image.open(SAMPLE_DIR / "jk.jpg")).convert("RGB")


def make_paint_coords(cursor: bool = False) -> Image.Image:
    photo = jk_image()
    image = Image.new("RGB", (940, 660), "white")
    draw = ImageDraw.Draw(image)
    canvas = (80, 90, 860, 555)
    draw.rectangle(canvas, fill=(210, 224, 244), outline=(177, 188, 206))
    px, py = 210, 135
    image.paste(photo, (px, py))
    draw.rectangle((px, py, px + photo.width, py + photo.height), outline=(120, 126, 136), width=2)
    if cursor:
        cx, cy = px + 118, py + 169
        draw.ellipse((cx - 45, cy - 45, cx + 45, cy + 45), outline=(218, 54, 66), width=5)
        draw.text((112, 590), "118, 169 pixels", fill=TEXT, font=font(28, True))
    else:
        draw_arrow(draw, (px, py - 28), (px + photo.width + 410, py - 28), AXIS)
        draw_arrow(draw, (px - 26, py), (px - 26, py + photo.height + 90), AXIS)
        draw.ellipse((px - 16, py - 16, px + 16, py + 16), fill=(225, 38, 58))
        draw.ellipse((px + photo.width - 16, py + photo.height - 16, px + photo.width + 16, py + photo.height + 16), fill=(225, 38, 58))
        draw.text((px - 40, py - 70), "x = 0, y = 0", fill=BLUE, font=font(26, True))
        draw.text((px + photo.width + 48, py + photo.height - 24), "x = 342, y = 345", fill=BLUE, font=font(24, True))
        draw.text((px + 120, py + photo.height + 30), "x = 342", fill=BLUE, font=font(25, True))
        draw.text((px + photo.width + 54, py + 150), "y = 345", fill=BLUE, font=font(25, True))
        draw.text((760, 590), "342 x 345 pixels", fill=TEXT, font=font(24, True))
    return image


def window_pair(after: str) -> Image.Image:
    photo = jk_image()
    scale = 1.25
    display = photo.resize((round(photo.width * scale), round(photo.height * scale)))
    changed = display.copy()
    if after == "white_square":
        draw_changed = ImageDraw.Draw(changed)
        square = round(50 * scale)
        draw_changed.rectangle((changed.width - square, changed.height - square, changed.width, changed.height), fill="white")
    elif after == "yellow_bar":
        draw_changed = ImageDraw.Draw(changed)
        bar = round(50 * scale)
        draw_changed.rectangle((0, changed.height - bar, changed.width, changed.height), fill=(255, 255, 0))

    title_h = 34
    gap = 24
    win_w = display.width
    win_h = display.height + title_h
    image = Image.new("RGB", (win_w * 2 + gap + 60, win_h + 54), "white")
    draw = ImageDraw.Draw(image)
    for i, (title, content) in enumerate([("Before the change", display), ("After the change", changed)]):
        x = 30 + i * (win_w + gap)
        y = 24
        draw.rectangle((x, y, x + win_w, y + win_h), fill=(250, 250, 250), outline=(172, 178, 190))
        draw.rectangle((x, y, x + win_w, y + title_h), fill=(246, 247, 249), outline=(172, 178, 190))
        draw.text((x + 14, y + 7), title, fill=MUTED, font=font(18, True))
        image.paste(content, (x, y + title_h))
    return image


BUILDERS = {
    "ch02_bitmap_h_matrix.jpg": make_bitmap_h_matrix,
    "ch02_gray_scale_example.jpg": make_gray_scale,
    "ch02_rgb_materialui_example.jpg": make_rgb_material,
    "ch02_rgb_custom_color_dialog.jpg": make_color_dialog,
    "ch02_rgb_pixel_channels.jpg": make_rgb_pixel_channels,
    "ch2_5_paint_coords.png": lambda: make_paint_coords(cursor=False),
    "ch2_6_cursor.png": lambda: make_paint_coords(cursor=True),
    "ch2_7_result.png": lambda: window_pair("white_square"),
    "exercise_ref.png": lambda: window_pair("yellow_bar"),
}


def backup_existing(files: list[str], backup_root: Path) -> None:
    for name in files:
        src = IMAGE_DIR / name
        if src.exists():
            dst = backup_root / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def command_rebuild(args: argparse.Namespace) -> int:
    missing = [p for p in [SAMPLE_DIR / "jk.jpg", SAMPLE_DIR / "jk_gray.jpg"] if not p.exists()]
    if missing:
        for path in missing:
            print(f"missing source: {path}")
        return 1

    names = list(BUILDERS)
    backup_root = ROOT / "tools" / "image-backups" / f"ch02-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    if not args.dry_run:
        backup_existing(names, backup_root)

    for name in names:
        out = IMAGE_DIR / name
        image = trim_whitespace(BUILDERS[name]())
        print(f"{'dry-run ' if args.dry_run else ''}write {out.relative_to(ROOT)} {image.width}x{image.height}")
        if not args.dry_run:
            save_image(image, out)

    if not args.dry_run:
        print(f"Backups: {backup_root}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebuild Chapter 2 OpenCV web images.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned outputs without writing images.")
    args = parser.parse_args()
    return command_rebuild(args)


if __name__ == "__main__":
    raise SystemExit(main())
