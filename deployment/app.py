"""
Aplikasi web klasifikasi bentuk wajah pria.

Jalankan:
    streamlit run app.py

Mode:
  - Kamera : ambil foto langsung dari webcam lewat browser
  - Unggah : satu gambar dari file
  - Batch  : banyak gambar sekaligus, hasil bisa diunduh sebagai CSV
"""

import io
import os
import time

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

import faceshape as fs
import recommendations as rec

ART_DIR = os.environ.get("FACESHAPE_ARTIFACTS", "artifacts")

st.set_page_config(page_title="Deteksi Bentuk Wajah", page_icon="🙂",
                   layout="wide")


# --------------------------------------------------------------------------
# Muat sekali, cache selama proses hidup
# --------------------------------------------------------------------------
@st.cache_resource(show_spinner="Memuat model...")
def boot(art_dir):
    cfg = fs.load_config(art_dir)
    models, paths = fs.load_models(art_dir)
    cascade = fs.load_cascade(cfg)
    return cfg, models, cascade, paths


try:
    CFG, MODELS, CASCADE, MODEL_PATHS = boot(ART_DIR)
except Exception as e:
    st.error(f"Gagal memuat model.\n\n{e}")
    st.info(
        "Pastikan folder `artifacts/` ada di sebelah `app.py`, berisi "
        "`model_config.json` dan `faceshape_fold*.keras`. Folder itu "
        "dihasilkan oleh `14_train_final.ipynb`."
    )
    st.stop()


# --------------------------------------------------------------------------
# Tampilan hasil
# --------------------------------------------------------------------------
BADGE = {"tinggi": ("🟢", "Cukup bisa dipercaya"),
         "sedang": ("🟡", "Pertimbangkan juga tebakan kedua"),
         "rendah": ("🔴", "Model tidak yakin — sebaiknya dicek manual")}



def show_recommendations(shape, expanded=True, prefix=""):
    """Tampilkan rekomendasi gaya rambut untuk satu bentuk wajah."""
    r = rec.get(shape)
    if r is None:
        return
    with st.expander(f"{prefix}💇 Rekomendasi gaya rambut — {r['nama_id']}",
                     expanded=expanded):
        st.caption(f"**Ciri:** {r['ciri']}")
        st.caption(f"**Tujuan potongan:** {r['tujuan']}")

        st.markdown("**Gaya yang disarankan**")
        for nama, catatan, s in r["gaya"]:
            st.markdown(
                f"- **{nama}** — {catatan}  \n"
                f"  <span style='color:#888;font-size:0.82em'>"
                f"{rec.SOURCE_LABEL.get(s, s)}</span>",
                unsafe_allow_html=True)

        st.markdown("**Sebaiknya dihindari**")
        for h in r["hindari"]:
            st.markdown(f"- {h}")

        c1, c2 = st.columns(2)
        c1.info(f"**Jenggot** — {r['jenggot']}")
        c2.success(f"**Bilang ke barber** — {r['minta_ke_barber']}")

        if "BERBEDA" in r["catatan_sumber"]:
            st.warning(f"**Catatan sumber** — {r['catatan_sumber']}")
        else:
            st.caption(f"Catatan sumber: {r['catatan_sumber']}")


def show_result(img_rgb, res):
    if not res["wajah_terdeteksi"]:
        st.warning(
            "Wajah tidak terdeteksi. Gambar dipotong di bagian tengah, "
            "jadi hasilnya jauh kurang bisa dipercaya. Coba foto menghadap "
            "depan dengan pencahayaan lebih merata."
        )

    c1, c2, c3 = st.columns([1.1, 1.1, 1.4])
    with c1:
        st.image(img_rgb, caption="Foto asli", use_container_width=True)
    with c2:
        st.image(res["patch"], caption="Yang dilihat model",
                 use_container_width=True)
    with c3:
        icon, note = BADGE[res["tingkat"]]
        st.markdown(f"### {res['prediksi']}")
        st.markdown(f"{icon} **{res['keyakinan']*100:.1f}%** — {note}")

        if res["ambigu"]:
            st.info(
                f"Selisih dengan tebakan kedua hanya "
                f"{res['gap']*100:.1f} poin. Baca hasilnya sebagai "
                f"**antara {res['prediksi']} dan {res['alternatif']}**."
            )

        df = (pd.DataFrame({"kelas": list(res["probs"].keys()),
                            "probabilitas": list(res["probs"].values())})
              .sort_values("probabilitas", ascending=False)
              .set_index("kelas"))
        st.bar_chart(df, height=200)
        st.caption(
            f"Tebakan kedua: {res['alternatif']} "
            f"({res['keyakinan_alt']*100:.1f}%). Model ini benar "
            f"~{CFG.oof_accuracy*100:.0f}% untuk tebakan pertama dan "
            f"~{CFG.top2_accuracy*100:.0f}% kalau dua tebakan teratas dihitung."
        )

    st.divider()
    show_recommendations(res["prediksi"])

    # Kalau model ragu, rekomendasi untuk tebakan kedua ikut ditampilkan —
    # percuma memberi satu set saran kalau kelasnya sendiri belum pasti.
    if res["ambigu"]:
        show_recommendations(res["alternatif"], expanded=False,
                             prefix="Alternatif · ")


def to_rgb(file_like) -> np.ndarray:
    with Image.open(file_like) as im:
        return np.asarray(im.convert("RGB"), dtype=np.uint8)


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------
with st.sidebar:
    st.header("Tentang model")
    st.metric("Akurasi (top-1)", f"{CFG.oof_accuracy*100:.1f}%")
    st.metric("Akurasi (top-2)", f"{CFG.top2_accuracy*100:.1f}%")
    st.caption(
        f"Diukur dengan 5-fold cross-validation pada {CFG.n_gambar} gambar. "
        f"Tebakan acak = 25%."
    )

    if CFG.per_class:
        st.markdown("**Akurasi per kelas**")
        for k, v in sorted(CFG.per_class.items(), key=lambda kv: -kv[1]):
            st.write(f"- {k}: {v*100:.0f}%")

    st.divider()
    st.markdown("**Tips foto**")
    st.markdown(
        "- wajah menghadap depan\n"
        "- pencahayaan merata\n"
        "- dahi & garis rahang tidak tertutup rambut\n"
        "- satu wajah per foto"
    )
    st.divider()
    st.caption(
        f"Ensemble {len(MODELS)} model · dilatih {CFG.dibuat}\n\n"
        "Model dilatih pada dataset wajah pria berukuran kecil dengan "
        "kualitas label tidak sempurna. Jangan dipakai untuk keputusan "
        "yang berdampak nyata bagi seseorang."
    )


# --------------------------------------------------------------------------
# Halaman utama
# --------------------------------------------------------------------------
st.title("Deteksi Bentuk Wajah")
st.caption(
    "Empat kelas: ovale, rectangular, round, square. "
    "Hasil ditampilkan sebagai dua kemungkinan teratas, bukan satu jawaban "
    "pasti — bentuk wajah memang kategori yang saling tumpang tindih."
)

tab_cam, tab_upload, tab_batch, tab_guide = st.tabs(
    ["📷 Kamera", "🖼️ Unggah", "📁 Batch", "💇 Panduan"])

with tab_cam:
    st.markdown("Izinkan akses kamera, lalu tekan tombol untuk mengambil foto.")
    shot = st.camera_input("Ambil foto", label_visibility="collapsed")
    if shot is not None:
        rgb = to_rgb(shot)
        with st.spinner("Menganalisis..."):
            res = fs.predict_image(rgb, MODELS, CASCADE, CFG)
        show_result(rgb, res)

        buf = io.BytesIO()
        Image.fromarray(rgb).save(buf, format="JPEG", quality=95)
        st.download_button(
            "Simpan foto ini",
            buf.getvalue(),
            file_name=f"wajah_{res['prediksi']}_{time.strftime('%Y%m%d_%H%M%S')}.jpg",
            mime="image/jpeg",
        )

with tab_upload:
    up = st.file_uploader("Pilih satu gambar",
                          type=["jpg", "jpeg", "png", "bmp", "webp"])
    if up is not None:
        rgb = to_rgb(up)
        with st.spinner("Menganalisis..."):
            res = fs.predict_image(rgb, MODELS, CASCADE, CFG)
        show_result(rgb, res)

with tab_batch:
    ups = st.file_uploader("Pilih beberapa gambar sekaligus",
                           type=["jpg", "jpeg", "png", "bmp", "webp"],
                           accept_multiple_files=True)
    if ups:
        rows, bar = [], st.progress(0.0, text="Memproses...")
        for i, f in enumerate(ups, 1):
            try:
                rgb = to_rgb(f)
                r = fs.predict_image(rgb, MODELS, CASCADE, CFG)
                rows.append({
                    "file": f.name,
                    "prediksi": r["prediksi"],
                    "keyakinan": round(r["keyakinan"], 4),
                    "alternatif": r["alternatif"],
                    "keyakinan_alt": round(r["keyakinan_alt"], 4),
                    "tingkat": r["tingkat"],
                    "wajah_terdeteksi": r["wajah_terdeteksi"],
                    **{k: round(v, 4) for k, v in r["probs"].items()},
                })
            except Exception as e:
                st.warning(f"{f.name}: gagal diproses ({type(e).__name__})")
            bar.progress(i / len(ups), text=f"{i}/{len(ups)}")
        bar.empty()

        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, height=340)

            c1, c2, c3 = st.columns(3)
            c1.metric("Diproses", len(df))
            c2.metric("Wajah tak terdeteksi",
                      int((~df["wajah_terdeteksi"]).sum()))
            c3.metric("Keyakinan rendah", int((df["tingkat"] == "rendah").sum()))

            st.bar_chart(df["prediksi"].value_counts())
            st.download_button(
                "Unduh CSV",
                df.to_csv(index=False).encode("utf-8"),
                file_name="hasil_prediksi.csv",
                mime="text/csv",
            )

with tab_guide:
    st.markdown(
        "Rekomendasi gaya rambut untuk keempat bentuk wajah, dirangkum dari "
        "dua panduan barbering di bawah. Bisa dibaca tanpa mengunggah foto."
    )
    pilih = st.radio("Bentuk wajah", CFG.classes, horizontal=True,
                     format_func=lambda c: rec.get(c)["nama_id"] if rec.get(c) else c)
    show_recommendations(pilih)

    st.divider()
    st.markdown("**Sumber**")
    for s in rec.SOURCES:
        st.markdown(f"- [{s['label']} — {s['judul']}]({s['url']})")
    st.caption(
        "Isi rekomendasi adalah rangkuman dalam kata-kata sendiri dari kedua "
        "panduan tersebut. Saran gaya rambut bersifat umum: tekstur rambut, "
        "tinggi badan, gaya berpakaian, dan selera pribadi juga menentukan. "
        "Barber yang melihat langsung tetap penasihat terbaik."
    )
