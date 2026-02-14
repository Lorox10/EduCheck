from io import BytesIO
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont


def _safe_filename(value: str) -> str:
    return "".join(ch for ch in value if ch.isalnum()) or "unknown"


def build_qr_path(qr_dir: Path, documento: str) -> Path:
    filename = f"{_safe_filename(documento)}.png"
    return qr_dir / filename


def ensure_qr(qr_dir: Path, documento: str) -> str:
    path = build_qr_path(qr_dir, documento)
    if not path.exists():
        img = qrcode.make(documento)
        img.save(path)
    return str(path)


def render_qr_with_name(qr_path: Path, full_name: str) -> BytesIO:
    qr_image = Image.open(qr_path).convert("RGB")
    font = ImageFont.load_default()
    text = full_name.strip() or "ESTUDIANTE"

    padding = 12
    bbox = font.getbbox(text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    width = max(qr_image.width, text_width + padding * 2)
    height = qr_image.height + text_height + padding * 2

    canvas = Image.new("RGB", (width, height), color="white")
    qr_x = (width - qr_image.width) // 2
    canvas.paste(qr_image, (qr_x, padding))

    draw = ImageDraw.Draw(canvas)
    text_x = (width - text_width) // 2
    text_y = qr_image.height + padding
    draw.text((text_x, text_y), text, fill="black", font=font)

    output = BytesIO()
    canvas.save(output, format="PNG")
    output.seek(0)
    return output
