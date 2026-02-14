from pathlib import Path

import qrcode


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
