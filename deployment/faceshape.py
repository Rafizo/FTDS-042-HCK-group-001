"""
Logika inti klasifikasi bentuk wajah.

Dipakai bersama oleh app.py (web) dan live_camera.py (kamera langsung),
supaya keduanya memakai pra-pemrosesan yang persis sama dengan training.

Semua parameter dibaca dari artifacts/model_config.json - tidak ada
angka yang ditulis ulang di sini.
"""

from __future__ import annotations

import glob
import json
import os
from dataclasses import dataclass, field

import numpy as np

DEFAULT_ART_DIR = "artifacts"


# --------------------------------------------------------------------------
# Konfigurasi
# --------------------------------------------------------------------------
@dataclass
class Config:
    classes: list
    img_size: tuple
    crop_margin: float
    cascade: str
    oof_accuracy: float = 0.0
    top2_accuracy: float = 0.0
    per_class: dict = field(default_factory=dict)
    n_gambar: int = 0
    dibuat: str = "?"

    @property
    def n_classes(self) -> int:
        return len(self.classes)


def load_config(art_dir: str = DEFAULT_ART_DIR) -> Config:
    path = os.path.join(art_dir, "model_config.json")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{path} tidak ditemukan.\n"
            "Jalankan 14_train_final.ipynb dulu untuk membuat folder artifacts/."
        )
    raw = json.load(open(path, encoding="utf-8"))
    return Config(
        classes=raw["classes"],
        img_size=tuple(raw["img_size"]),
        crop_margin=float(raw["crop_margin"]),
        cascade=raw.get("cascade", "haarcascade_frontalface_default.xml"),
        oof_accuracy=float(raw.get("oof_accuracy", 0.0)),
        top2_accuracy=float(raw.get("top2_accuracy", 0.0)),
        per_class=raw.get("akurasi_per_kelas", {}),
        n_gambar=int(raw.get("n_gambar", 0)),
        dibuat=raw.get("dibuat", "?"),
    )


# --------------------------------------------------------------------------
# Model
# --------------------------------------------------------------------------
def load_models(art_dir: str = DEFAULT_ART_DIR, limit: int | None = None):
    """Muat seluruh model fold. `limit` berguna untuk mode kamera
    yang butuh cepat (misal limit=1 untuk pratinjau langsung)."""
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
    from tensorflow import keras

    paths = sorted(glob.glob(os.path.join(art_dir, "faceshape_fold*.keras")))
    if not paths:
        raise FileNotFoundError(f"Tidak ada file model .keras di {art_dir}/")
    if limit:
        paths = paths[:limit]
    return [keras.models.load_model(p) for p in paths], paths


def load_cascade(cfg: Config):
    import cv2

    c = cv2.CascadeClassifier(cv2.data.haarcascades + cfg.cascade)
    if c.empty():
        raise RuntimeError(f"Gagal memuat cascade: {cfg.cascade}")
    return c


# --------------------------------------------------------------------------
# Pra-pemrosesan
# --------------------------------------------------------------------------
def detect_face_box(img_rgb: np.ndarray, cascade, cfg: Config):
    """Kembalikan (x1, y1, x2, y2, terdeteksi) - kotak yang sudah diperluas
    sebesar crop_margin. Kalau wajah tidak terdeteksi, pakai center crop."""
    import cv2

    h, w = img_rgb.shape[:2]
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    faces = cascade.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))

    if len(faces):
        fx, fy, fw, fh = max(faces, key=lambda b: b[2] * b[3])
        mx, my = int(fw * cfg.crop_margin), int(fh * cfg.crop_margin)
        return (max(0, fx - mx), max(0, fy - my),
                min(w, fx + fw + mx), min(h, fy + fh + my), True)

    s = min(h, w)
    x1, y1 = (w - s) // 2, (h - s) // 2
    return (x1, y1, x1 + s, y1 + s, False)


def crop_face(img_rgb: np.ndarray, cascade, cfg: Config):
    """Kembalikan (patch uint8 seukuran img_size, terdeteksi, kotak)."""
    import cv2

    x1, y1, x2, y2, ok = detect_face_box(img_rgb, cascade, cfg)
    patch = cv2.resize(img_rgb[y1:y2, x1:x2], cfg.img_size,
                       interpolation=cv2.INTER_AREA)
    return patch.astype(np.uint8), ok, (x1, y1, x2, y2)


# --------------------------------------------------------------------------
# Prediksi
# --------------------------------------------------------------------------
def predict_probs(patch_uint8: np.ndarray, models) -> np.ndarray:
    """Rata-ratakan probabilitas seluruh model fold.
    Model menerima uint8 mentah - normalisasi ada di dalam model."""
    batch = patch_uint8[None]
    return np.mean([m.predict(batch, verbose=0)[0] for m in models], axis=0)


def summarise(probs: np.ndarray, cfg: Config, detected: bool = True) -> dict:
    """Ubah vektor probabilitas jadi hasil yang siap ditampilkan."""
    order = np.argsort(probs)[::-1]
    t1, t2 = int(order[0]), int(order[1])
    gap = float(probs[t1] - probs[t2])
    return {
        "prediksi": cfg.classes[t1],
        "keyakinan": float(probs[t1]),
        "alternatif": cfg.classes[t2],
        "keyakinan_alt": float(probs[t2]),
        "gap": gap,
        "ambigu": gap < 0.15,
        "wajah_terdeteksi": detected,
        "tingkat": confidence_level(float(probs[t1])),
        "probs": {cfg.classes[i]: float(probs[i]) for i in range(cfg.n_classes)},
        "urutan": [cfg.classes[i] for i in order],
    }


def confidence_level(p: float) -> str:
    """Ambang ini berasal dari performa sebenarnya: top-1 ~61%, top-2 ~83%.
    Satu jawaban tunggal tidak cukup, jadi tingkat keyakinan dinyatakan
    eksplisit alih-alih menampilkan satu label seolah pasti."""
    if p >= 0.70:
        return "tinggi"
    if p >= 0.40:
        return "sedang"
    return "rendah"


def predict_image(img_rgb: np.ndarray, models, cascade, cfg: Config) -> dict:
    """Jalur lengkap: crop -> prediksi -> ringkas."""
    patch, detected, box = crop_face(img_rgb, cascade, cfg)
    probs = predict_probs(patch, models)
    out = summarise(probs, cfg, detected)
    out["patch"] = patch
    out["box"] = box
    return out
