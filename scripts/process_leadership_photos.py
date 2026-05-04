"""
Process Leadership / LEADERSHIP PICTURES 2 sources into standardized assets/leadership JPEGs.

- Neutral background (#f5f7fa) for transparency / odd edges
- 4:3 card portraits at 1200x900 (executive + board) via letterbox fit — full subject visible, no decapitating crop
- Square advisor avatars at 240x240 (displayed small in UI)
- Mild sharpen + JPEG quality 90

Run from repo root:
  python scripts/process_leadership_photos.py
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    from pillow_heif import register_heif_opener

    register_heif_opener()
except ImportError:
    pass

from PIL import Image, ImageEnhance, ImageOps

REPO = Path(__file__).resolve().parents[1]
SRC_DIR = REPO / "Leadership" / "LEADERSHIP PICTURES 2"
OUT_DIR = REPO / "assets" / "leadership"

# Site background-adjacent neutral (matches .team-card-media / .board-card-media feel)
NEUTRAL = (245, 247, 250)

CARD = (1200, 900)
AVATAR = (240, 240)


def _open(path: Path) -> Image.Image:
    return Image.open(path)


def to_rgb_on_neutral(im: Image.Image) -> Image.Image:
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        base = Image.new("RGB", im.size, NEUTRAL)
        if im.mode != "RGBA":
            im = im.convert("RGBA")
        base.paste(im, mask=im.split()[-1])
        return base
    if im.mode != "RGB":
        return im.convert("RGB")
    return im


def cover_crop(im: Image.Image, w: int, h: int) -> Image.Image:
    im = to_rgb_on_neutral(im)
    im = ImageOps.exif_transpose(im)
    src_w, src_h = im.size
    scale = max(w / src_w, h / src_h)
    nw, nh = int(round(src_w * scale)), int(round(src_h * scale))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - w) // 2
    top = (nh - h) // 2
    return im.crop((left, top, left + w, top + h))


def contain_pad(im: Image.Image, w: int, h: int) -> Image.Image:
    """Scale uniformly to fit inside w×h, pad with neutral (no cropping)."""
    im = to_rgb_on_neutral(im)
    im = ImageOps.exif_transpose(im)
    src_w, src_h = im.size
    scale = min(w / src_w, h / src_h)
    nw, nh = max(1, int(round(src_w * scale))), max(1, int(round(src_h * scale)))
    resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (w, h), NEUTRAL)
    left = (w - nw) // 2
    top = (h - nh) // 2
    canvas.paste(resized, (left, top))
    return canvas


def enhance_clarity(im: Image.Image) -> Image.Image:
    im = ImageEnhance.Contrast(im).enhance(1.04)
    im = ImageEnhance.Sharpness(im).enhance(1.1)
    return im


def save_jpeg(im: Image.Image, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, format="JPEG", quality=90, optimize=True, subsampling=1)


# (source_filename, output_filename, kind: "card" | "avatar")
# kind=avatar: square center crop for advisory row; kind=card: 4:3 for team + board
MAPPINGS: list[tuple[str, str, str]] = [
    ("Sherriff.png", "abdul-hamid-sherriff.jpg", "card"),
    ("isabella Agyekum.jpg", "isabella-agyekum.jpg", "card"),
    # Windows filename uses typographic apostrophes (U+2032 / U+2019), not ASCII 0x27
    ("Ouattara Mafine\u2032 N\u2019Charic.jpg", "ouattara-ncharick.jpg", "card"),
    ("mahmoud.jpg", "mahamadou-sissoko.jpg", "card"),
    ("onyeche.jpg", "onyeche-tefase.jpg", "avatar"),
    ("chris antewi-removebg-preview(1).jpg", "christopher-antwi.jpg", "avatar"),
    ("andre dewitt-removebg-preview.jpg", "andre-de-witt.jpg", "avatar"),
    ("DADSON AWUNYO-VITOR.jpg", "dadson-awunyo-vitor.jpg", "card"),
    ("sehora.jpg", "sephora-fondop-medjowe.jpg", "card"),
    ("sylvester AKPAH.jpg", "sylvester-akpah.jpg", "card"),
    ("Josephine Akuba.jpg", "josephine-buah-timtey.jpg", "card"),
    ("kelly_baker.avif", "kelly-baker.jpg", "avatar"),
    ("rohlman_diane.jpg", "diane-rohlman.jpg", "avatar"),
    ("Nicky Kingston.png", "nicky-kingston.jpg", "avatar"),
    ("patricia-araba-annan.png", "patricia-araba-annan.jpg", "avatar"),
    ("john-paul-engel.png", "john-paul-engel.jpg", "avatar"),
    ("kimm-harris.png", "kimm-harris.jpg", "avatar"),
]


def process_pair(src_name: str, out_name: str, kind: str) -> str:
    src = SRC_DIR / src_name
    if not src.exists():
        return f"SKIP missing source -> {out_name}"
    im = _open(src)
    if kind == "avatar":
        out_im = cover_crop(im, *AVATAR)
    else:
        out_im = contain_pad(im, *CARD)
    out_im = enhance_clarity(out_im)
    save_jpeg(out_im, OUT_DIR / out_name)
    return f"OK -> {out_name}"


def reprocess_existing(out_name: str) -> str | None:
    """Re-standardize a file already in assets/leadership (no new source in PICTURES 2)."""
    p = OUT_DIR / out_name
    if not p.exists():
        return None
    im = _open(p)
    out_im = contain_pad(im, *CARD)
    out_im = enhance_clarity(out_im)
    save_jpeg(out_im, p)
    return f"OK (reprocess existing) {out_name}"


def main() -> int:
    if not SRC_DIR.is_dir():
        print(f"Source folder not found: {SRC_DIR}", file=sys.stderr)
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for src_name, out_name, kind in MAPPINGS:
        lines.append(process_pair(src_name, out_name, kind))
    for msg in lines:
        print(msg)

    for extra in ("francisca-mensah.jpg", "gifty-quarshie-ngissah.jpg"):
        m = reprocess_existing(extra)
        if m:
            print(m)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
