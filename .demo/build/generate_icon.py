"""Generate the demo application icon from the original square logo."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BUILD_DIR = Path(__file__).resolve().parent
SOURCE = BUILD_DIR / "icon-base.png"
PNG_OUTPUT = BUILD_DIR / "icon.png"
ICO_OUTPUT = BUILD_DIR / "icon.ico"
SIZE = 512


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/ariblk.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def generate() -> None:
    base = Image.open(SOURCE).convert("RGBA").resize(
        (SIZE, SIZE), Image.Resampling.LANCZOS
    )

    draw = ImageDraw.Draw(base)
    draw.polygon(
        [(220, 512), (355, 512), (512, 355), (512, 220)],
        fill=(229, 57, 53, 255),
    )

    font = load_font(57)
    text_layer = Image.new("RGBA", (300, 100), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_layer)
    text_draw.text((150, 50), "DEMO", font=font, fill="white", anchor="mm")
    rotated_text = text_layer.rotate(45, resample=Image.Resampling.BICUBIC, expand=True)
    base.alpha_composite(rotated_text, (406 - rotated_text.width // 2, 406 - rotated_text.height // 2))

    base.save(PNG_OUTPUT, format="PNG")
    base.save(
        ICO_OUTPUT,
        format="ICO",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    print(f"Generated {PNG_OUTPUT} and {ICO_OUTPUT}")


if __name__ == "__main__":
    generate()
