# OpenCV Image Audit

Use `image_crop_audit.py` to check OpenCV chapter images before editing them.
The workflow is intentionally non-destructive first:

```sh
python3 opencv/tools/image_crop_audit.py audit --chapter ch18
```

This creates local-only reports in `opencv/tools/image-audit/`:

- `image-audit.csv`: dimensions, crop boxes, margins, and flags
- `crop-suggestions.json`: automatic crop boxes for review
- `review.html`: visual preview with red crop boxes

For the full site, write only images that need review:

```sh
python3 opencv/tools/image_crop_audit.py audit --flagged-only --out opencv/tools/image-audit-all-flagged
```

After reviewing and removing any bad suggestions from the manifest, verify the
planned changes:

```sh
python3 opencv/tools/image_crop_audit.py apply --manifest opencv/tools/image-audit/crop-suggestions.json --dry-run
```

Apply reviewed crops only after the dry run looks correct:

```sh
python3 opencv/tools/image_crop_audit.py apply --manifest opencv/tools/image-audit/crop-suggestions.json
```

Original images are copied into `opencv/tools/image-backups/` before overwrite.
