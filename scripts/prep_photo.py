from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/prep_photo.py source-photo.jpg")

    src = Path(sys.argv[1])
    if not src.exists():
        raise SystemExit(f"File not found: {src}")

    output = Path("source-prepped.png")

    with src.open("rb") as f:
        cutout = remove(f.read())

    rgba = Image.open(__import__("io").BytesIO(cutout)).convert("RGBA")
    arr = np.array(rgba)

    alpha = arr[:, :, 3].astype(np.float32) / 255.0
    rgb = arr[:, :, :3].astype(np.float32)

    white = np.full_like(rgb, 255.0)
    composited = rgb * alpha[:, :, None] + white * (1.0 - alpha[:, :, None])
    composited = composited.astype(np.uint8)

    gray = cv2.cvtColor(composited, cv2.COLOR_RGB2GRAY)

    clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    Image.fromarray(enhanced).save(output)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
