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
    
    # Cargar fuente moderna y llamativa con soporte UTF-8
    text = full_name.strip() or "ESTUDIANTE"
    font_size = 24
    font = None
    
    # Intentar fuentes modernas en orden de preferencia
    font_options = [
        "C:/Windows/Fonts/bahnschrift.ttf",  # Moderna, geométrica
        "C:/Windows/Fonts/ariblk.ttf",       # Arial Black - negrita y llamativa
        "C:/Windows/Fonts/arialbd.ttf",      # Arial Bold
        "C:/Windows/Fonts/arial.ttf",        # Arial regular fallback
    ]
    
    for font_path in font_options:
        try:
            font = ImageFont.truetype(font_path, font_size)
            break
        except:
            continue
    
    # Si no se pudo cargar ninguna, usar default
    if font is None:
        font = ImageFont.load_default()

    padding = 20
    bbox = font.getbbox(text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    width = max(qr_image.width, text_width + padding * 2)
    height = qr_image.height + text_height + padding * 3

    # Fondo blanco
    canvas = Image.new("RGB", (width, height), color="white")
    qr_x = (width - qr_image.width) // 2
    canvas.paste(qr_image, (qr_x, padding))

    # Dibujar texto con color más moderno
    draw = ImageDraw.Draw(canvas)
    text_x = (width - text_width) // 2
    text_y = qr_image.height + padding * 2
    draw.text((text_x, text_y), text, fill="#1a1a1a", font=font)

    output = BytesIO()
    canvas.save(output, format="PNG")
    output.seek(0)
    return output
