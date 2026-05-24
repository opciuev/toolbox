#!/usr/bin/env python3
"""Audit and crop OpenCV web images without guessing by hand.

Default workflow:
  python3 opencv/tools/image_crop_audit.py audit --chapter ch18

This writes CSV/JSON reports plus an HTML review page under
opencv/tools/image-audit/. The audit is non-destructive. To overwrite images,
first copy selected entries from crop-suggestions.json into a checked manifest,
then run:

  python3 opencv/tools/image_crop_audit.py apply --manifest opencv/tools/image-audit/crop-suggestions.json --dry-run
  python3 opencv/tools/image_crop_audit.py apply --manifest opencv/tools/image-audit/crop-suggestions.json
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import shutil
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageOps


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


@dataclass
class ImageRef:
    html_file: str
    src: str
    alt: str
    style: str
    line: int


@dataclass
class ImageAudit:
    image: str
    referenced_by: list[str]
    alt: list[str]
    exists: bool
    width: int | None = None
    height: int | None = None
    bytes: int | None = None
    crop_box: list[int] | None = None
    crop_width: int | None = None
    crop_height: int | None = None
    trim_left: int | None = None
    trim_top: int | None = None
    trim_right: int | None = None
    trim_bottom: int | None = None
    trim_area_pct: float | None = None
    flags: list[str] | None = None


class ImgParser(HTMLParser):
    def __init__(self, html_file: Path, root: Path) -> None:
        super().__init__()
        self.html_file = html_file
        self.root = root
        self.refs: list[ImageRef] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "img":
            return
        attr = {name.lower(): value or "" for name, value in attrs}
        src = attr.get("src", "").strip()
        if not src or src.startswith(("http://", "https://", "data:")):
            return
        line, _ = self.getpos()
        self.refs.append(
            ImageRef(
                html_file=str(self.html_file.relative_to(self.root)),
                src=src,
                alt=attr.get("alt", ""),
                style=attr.get("style", ""),
                line=line,
            )
        )


def site_root_from_args(path: str | None) -> Path:
    if path:
        return Path(path).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


def parse_image_refs(root: Path, chapter: str | None) -> dict[str, list[ImageRef]]:
    refs_by_image: dict[str, list[ImageRef]] = {}
    html_files = sorted((root / "chapters").glob("*.html"))
    if chapter:
        wanted = chapter if chapter.endswith(".html") else f"{chapter}.html"
        html_files = [p for p in html_files if p.name == wanted]
    for html_file in html_files:
        parser = ImgParser(html_file, root)
        parser.feed(html_file.read_text(encoding="utf-8"))
        for ref in parser.refs:
            image_path = (html_file.parent / ref.src).resolve()
            try:
                rel = str(image_path.relative_to(root))
            except ValueError:
                rel = ref.src
            refs_by_image.setdefault(rel, []).append(ref)
    return refs_by_image


def iter_images(root: Path, refs_by_image: dict[str, list[ImageRef]], include_unreferenced: bool) -> list[str]:
    images = set(refs_by_image)
    if include_unreferenced:
        for path in (root / "chapters" / "images").rglob("*"):
            if path.suffix.lower() in IMAGE_SUFFIXES:
                images.add(str(path.relative_to(root)))
    return sorted(images)


def estimate_background(rgb: np.ndarray) -> np.ndarray:
    h, w, _ = rgb.shape
    patch = max(2, min(24, h // 12 or 2, w // 12 or 2))
    samples = np.concatenate(
        [
            rgb[:patch, :patch].reshape(-1, 3),
            rgb[:patch, w - patch :].reshape(-1, 3),
            rgb[h - patch :, :patch].reshape(-1, 3),
            rgb[h - patch :, w - patch :].reshape(-1, 3),
        ],
        axis=0,
    )
    return np.median(samples, axis=0)


def content_bbox(image: Image.Image, tolerance: int = 14, padding: int = 0) -> tuple[int, int, int, int]:
    rgba = ImageOps.exif_transpose(image).convert("RGBA")
    arr = np.asarray(rgba)
    alpha = arr[:, :, 3]
    rgb = arr[:, :, :3].astype(np.int16)
    bg = estimate_background(rgb).astype(np.int16)

    color_delta = np.max(np.abs(rgb - bg), axis=2)
    visible = alpha > 8
    content = (color_delta > tolerance) & visible

    if not np.any(content):
        return (0, 0, image.width, image.height)

    ys, xs = np.nonzero(content)
    x1 = max(int(xs.min()) - padding, 0)
    y1 = max(int(ys.min()) - padding, 0)
    x2 = min(int(xs.max()) + 1 + padding, image.width)
    y2 = min(int(ys.max()) + 1 + padding, image.height)
    return (x1, y1, x2, y2)


def audit_one(root: Path, rel: str, refs: list[ImageRef], tolerance: int, padding: int) -> ImageAudit:
    path = root / rel
    referenced_by = [f"{ref.html_file}:{ref.line}" for ref in refs]
    alt = sorted({ref.alt for ref in refs if ref.alt})
    flags: list[str] = []

    if not path.exists():
        return ImageAudit(rel, referenced_by, alt, False, flags=["missing"])

    try:
        with Image.open(path) as image:
            image = ImageOps.exif_transpose(image)
            width, height = image.size
            box = content_bbox(image, tolerance=tolerance, padding=padding)
    except Exception as exc:  # pragma: no cover - for corrupt local files
        return ImageAudit(rel, referenced_by, alt, False, flags=[f"unreadable:{exc}"])

    x1, y1, x2, y2 = box
    crop_w = x2 - x1
    crop_h = y2 - y1
    trim_right = width - x2
    trim_bottom = height - y2
    area = width * height
    crop_area = crop_w * crop_h
    trim_area_pct = 0.0 if area == 0 else round((area - crop_area) * 100 / area, 2)

    max_margin = max(x1, y1, trim_right, trim_bottom)
    if trim_area_pct >= 8 or max_margin >= max(width, height) * 0.05:
        flags.append("large_border")
    if abs(x1 - trim_right) >= 12 and abs(x1 - trim_right) >= width * 0.04:
        flags.append("unbalanced_horizontal_margin")
    if abs(y1 - trim_bottom) >= 12 and abs(y1 - trim_bottom) >= height * 0.04:
        flags.append("unbalanced_vertical_margin")
    if "page" in Path(rel).stem.lower() or (height > width * 1.22 and height >= 700):
        flags.append("page_like")
    if width > 1600 or height > 1600:
        flags.append("very_large")
    if width < 80 or height < 80:
        flags.append("very_small")

    return ImageAudit(
        image=rel,
        referenced_by=referenced_by,
        alt=alt,
        exists=True,
        width=width,
        height=height,
        bytes=path.stat().st_size,
        crop_box=[x1, y1, crop_w, crop_h],
        crop_width=crop_w,
        crop_height=crop_h,
        trim_left=x1,
        trim_top=y1,
        trim_right=trim_right,
        trim_bottom=trim_bottom,
        trim_area_pct=trim_area_pct,
        flags=flags,
    )


def make_preview(root: Path, audit: ImageAudit, out_dir: Path, thumb_max: int) -> str | None:
    if not audit.exists or not audit.crop_box:
        return None
    source = root / audit.image
    preview_rel = Path("previews") / audit.image
    preview = out_dir / preview_rel
    preview.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        x, y, w, h = audit.crop_box
        boxed = image.copy()
        draw = ImageDraw.Draw(boxed)
        draw.rectangle((x, y, x + w - 1, y + h - 1), outline=(220, 38, 38), width=max(2, min(image.size) // 180))
        boxed.thumbnail((thumb_max, thumb_max))
        boxed.save(preview)
    return preview_rel.as_posix()


def write_reports(root: Path, out_dir: Path, audits: list[ImageAudit], thumb_max: int, tolerance: int, padding: int) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = [asdict(audit) for audit in audits]
    (out_dir / "image-audit.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    fieldnames = list(rows[0].keys()) if rows else list(ImageAudit.__dataclass_fields__.keys())
    with (out_dir / "image-audit.csv").open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    suggestions = {
        "siteRoot": str(root),
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "tolerance": tolerance,
        "padding": padding,
        "note": "Review every crop before applying. Remove entries that should not be overwritten.",
        "crops": [
            {
                "image": audit.image,
                "box": audit.crop_box,
                "originalSize": [audit.width, audit.height],
                "cropSize": [audit.crop_width, audit.crop_height],
                "flags": audit.flags or [],
                "referencedBy": audit.referenced_by,
                "alt": audit.alt,
            }
            for audit in audits
            if audit.exists and audit.crop_box and audit.trim_area_pct and audit.trim_area_pct > 0
        ],
    }
    (out_dir / "crop-suggestions.json").write_text(json.dumps(suggestions, ensure_ascii=False, indent=2), encoding="utf-8")

    html_rows = []
    for audit in audits:
        preview = make_preview(root, audit, out_dir, thumb_max)
        flags = ", ".join(audit.flags or [])
        refs = "<br>".join(html.escape(item) for item in audit.referenced_by)
        alt = "<br>".join(html.escape(item) for item in audit.alt)
        box = "" if not audit.crop_box else ", ".join(str(v) for v in audit.crop_box)
        source_href = Path("..") / ".." / audit.image
        preview_html = "" if not preview else f'<img src="{html.escape(preview)}" loading="lazy">'
        html_rows.append(
            "<tr>"
            f"<td><code>{html.escape(audit.image)}</code></td>"
            f"<td>{audit.width or ''} x {audit.height or ''}</td>"
            f"<td>{audit.trim_area_pct if audit.trim_area_pct is not None else ''}</td>"
            f"<td>{html.escape(box)}</td>"
            f"<td>{html.escape(flags)}</td>"
            f"<td>{refs}</td>"
            f"<td>{alt}</td>"
            f"<td><a href='{html.escape(source_href.as_posix())}'>source</a></td>"
            f"<td>{preview_html}</td>"
            "</tr>"
        )

    review = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>OpenCV Image Audit</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 24px; color: #172033; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #d7dce5; padding: 8px; vertical-align: top; font-size: 13px; }}
    th {{ background: #f3f6fa; position: sticky; top: 0; z-index: 1; }}
    img {{ max-width: 260px; height: auto; display: block; background: #fff; }}
    code {{ font-size: 12px; }}
  </style>
</head>
<body>
  <h1>OpenCV Image Audit</h1>
  <p>Red boxes are automatic content bounds. Review before applying any crop.</p>
  <table>
    <thead>
      <tr>
        <th>Image</th><th>Size</th><th>Trim %</th><th>Crop box x,y,w,h</th>
        <th>Flags</th><th>Referenced by</th><th>Alt</th><th>File</th><th>Preview</th>
      </tr>
    </thead>
    <tbody>
      {''.join(html_rows)}
    </tbody>
  </table>
</body>
</html>
"""
    (out_dir / "review.html").write_text(review, encoding="utf-8")


def command_audit(args: argparse.Namespace) -> int:
    root = site_root_from_args(args.site)
    refs_by_image = parse_image_refs(root, args.chapter)
    images = iter_images(root, refs_by_image, args.include_unreferenced)

    audits = [
        audit_one(root, rel, refs_by_image.get(rel, []), tolerance=args.tolerance, padding=args.padding)
        for rel in images
    ]
    if args.flagged_only:
        audits = [audit for audit in audits if audit.flags]
    audits.sort(key=lambda item: (0 if item.flags else 1, item.image))

    out_dir = Path(args.out).expanduser().resolve() if args.out else root / "tools" / "image-audit"
    write_reports(root, out_dir, audits, thumb_max=args.thumb_max, tolerance=args.tolerance, padding=args.padding)

    flagged = sum(1 for audit in audits if audit.flags)
    print(f"Audited {len(audits)} images; flagged {flagged}.")
    print(f"Report: {out_dir / 'image-audit.csv'}")
    print(f"Review: {out_dir / 'review.html'}")
    print(f"Suggestions: {out_dir / 'crop-suggestions.json'}")
    return 0


def load_manifest(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid manifest JSON: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("crops"), list):
        raise SystemExit("Manifest must contain a top-level 'crops' list.")
    return data


def command_apply(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest).expanduser().resolve()
    manifest = load_manifest(manifest_path)
    root = site_root_from_args(args.site or manifest.get("siteRoot"))
    backup_dir = Path(args.backup_dir).expanduser().resolve() if args.backup_dir else root / "tools" / "image-backups" / datetime.now().strftime("%Y%m%d-%H%M%S")

    applied = 0
    for entry in manifest["crops"]:
        rel = entry.get("image")
        box = entry.get("box")
        if not rel or not box or len(box) != 4:
            print(f"skip invalid entry: {entry}", file=sys.stderr)
            continue
        if args.only and args.only not in rel:
            continue
        source = root / rel
        if not source.exists():
            print(f"missing: {rel}", file=sys.stderr)
            continue

        x, y, w, h = [int(v) for v in box]
        with Image.open(source) as image:
            image = ImageOps.exif_transpose(image)
            if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > image.width or y + h > image.height:
                print(f"invalid box for {rel}: {box}", file=sys.stderr)
                continue
            cropped = image.crop((x, y, x + w, y + h))

        print(f"{'dry-run ' if args.dry_run else ''}crop {rel}: {image.width}x{image.height} -> {w}x{h}")
        if args.dry_run:
            continue

        backup = backup_dir / rel
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, backup)
        cropped.save(source)
        applied += 1

    if not args.dry_run:
        print(f"Applied {applied} crops. Backups: {backup_dir}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit and crop OpenCV website images.")
    parser.add_argument("--site", help="OpenCV site root. Defaults to the parent of this script.")
    sub = parser.add_subparsers(dest="command", required=True)

    audit = sub.add_parser("audit", help="Generate non-destructive image audit reports.")
    audit.add_argument("--chapter", help="Limit to one chapter, for example ch18.")
    audit.add_argument("--include-unreferenced", action="store_true", help="Also scan images not referenced by chapter HTML.")
    audit.add_argument("--flagged-only", action="store_true", help="Write only rows with flags.")
    audit.add_argument("--out", help="Output directory. Defaults to opencv/tools/image-audit.")
    audit.add_argument("--tolerance", type=int, default=14, help="Background color tolerance for auto content box.")
    audit.add_argument("--padding", type=int, default=0, help="Padding added around detected content box.")
    audit.add_argument("--thumb-max", type=int, default=900, help="Maximum preview image side length.")
    audit.set_defaults(func=command_audit)

    apply = sub.add_parser("apply", help="Apply reviewed crop boxes from a manifest.")
    apply.add_argument("--manifest", required=True, help="Manifest JSON with crops list.")
    apply.add_argument("--backup-dir", help="Where originals are copied before overwrite.")
    apply.add_argument("--only", help="Only apply entries whose image path contains this text.")
    apply.add_argument("--dry-run", action="store_true", help="Print changes without writing files.")
    apply.set_defaults(func=command_apply)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
