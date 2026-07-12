#!/usr/bin/env python3
"""Create a compact grayscale ASCII portrait without retaining the source photo."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

RAMP = "@%#*+=-:. "


def crop_box(value: str) -> tuple[int, int, int, int]:
    values = tuple(int(part) for part in value.split(","))
    if len(values) != 4:
        raise argparse.ArgumentTypeError("crop must be left,top,right,bottom")
    return values  # type: ignore[return-value]


def convert(source: Path, width: int, crop: tuple[int, int, int, int] | None) -> str:
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image).convert("L")
        if crop:
            image = image.crop(crop)
        image = ImageOps.fit(image, (width, max(1, round(width * 0.52))))
        image = ImageEnhance.Contrast(image).enhance(1.35)
        pixels = list(image.getdata())
        lines = []
        for y in range(image.height):
            row = pixels[y * image.width : (y + 1) * image.width]
            lines.append("".join(RAMP[min(len(RAMP) - 1, value * len(RAMP) // 256)] for value in row).rstrip())
        return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--crop", type=crop_box)
    parser.add_argument("--width", type=int, default=34)
    parser.add_argument("--output", type=Path, default=Path("assets/avatar-ascii.txt"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(convert(args.source, args.width, args.crop), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
