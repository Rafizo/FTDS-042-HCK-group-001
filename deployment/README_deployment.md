# Deployment — Deteksi Bentuk Wajah

Dua cara memakai model: **aplikasi web** (kamera browser + unggah + batch) dan
**kamera langsung** (jendela realtime dengan tombol screenshot).

## Susunan folder

```
deployment/
├── faceshape.py            ← logika inti, dipakai bersama
├── recommendations.py      ← data rekomendasi gaya rambut per kelas
├── app.py                  ← aplikasi web (Streamlit)
├── live_camera.py          ← kamera realtime (OpenCV)
├── requirements.txt
└── artifacts/              ← dari 14_train_final.ipynb
    ├── model_config.json
    ├── faceshape_fold1..5.keras
    └── class_names.txt
```

Salin folder `artifacts/` hasil training ke sini. Semua parameter
pra-pemrosesan dibaca dari `model_config.json`, jadi tidak ada angka yang
perlu disalin manual.

## Pasang

```bash
pip install -r requirements.txt
```

Untuk Mac Apple Silicon, ganti baris `tensorflow` dengan:

```bash
pip install tensorflow-macos tensorflow-metal
```

## Aplikasi web

```bash
streamlit run app.py
```

Browser terbuka di `http://localhost:8501` dengan tiga tab:

| Tab | Fungsi |
|---|---|
| 📷 Kamera | ambil foto langsung dari webcam, hasil muncul seketika |
| 🖼️ Unggah | satu gambar dari file |
| 📁 Batch | banyak gambar sekaligus, hasil bisa diunduh sebagai CSV |
| 💇 Panduan | rekomendasi gaya rambut keempat kelas, bisa dibaca tanpa foto |

Setiap hasil prediksi langsung diikuti rekomendasi gaya rambut: daftar gaya
yang cocok beserta sumbernya, apa yang sebaiknya dihindari, saran jenggot,
dan kalimat yang bisa disampaikan ke barber. Kalau model ragu antara dua
kelas, rekomendasi untuk tebakan kedua ikut ditampilkan — percuma memberi
satu set saran kalau kelasnya sendiri belum pasti.

Kalau folder artifacts ada di tempat lain:

```bash
FACESHAPE_ARTIFACTS=/path/ke/artifacts streamlit run app.py
```

Untuk diakses dari HP di jaringan yang sama:

```bash
streamlit run app.py --server.address 0.0.0.0
```

Lalu buka `http://<ip-laptop>:8501` di HP. Catatan: kamera browser butuh
HTTPS di sebagian perangkat, jadi tab Kamera mungkin hanya jalan di
`localhost`. Tab Unggah selalu jalan.

## Kamera langsung

```bash
python live_camera.py
```

| Tombol | Fungsi |
|---|---|
| `S` atau `Spasi` | simpan screenshot + hasil ke `screenshots/` |
| `F` | ganti mode cepat (1 model) ↔ akurat (5 model) |
| `Q` atau `Esc` | keluar |

Opsi:

```bash
python live_camera.py --camera 1      # kamera eksternal
python live_camera.py --every 5       # prediksi lebih sering
python live_camera.py --fast          # mulai di mode cepat
python live_camera.py --width 1280    # resolusi tampilan
```

Tiga gaya rambut teratas ditampilkan langsung di panel kamera. Tiap
screenshot menghasilkan empat hal: foto penuh, versi ter-crop yang dilihat
model, satu baris di `screenshots/log.csv` berisi seluruh probabilitas, dan
file `<waktu>_rekomendasi.txt` berisi rekomendasi lengkap.

**Soal performa.** Menjalankan 5 model tiap frame terlalu berat untuk
realtime, jadi prediksi di-throttle setiap 8 frame; deteksi wajah tetap
jalan tiap frame supaya kotaknya mengikuti gerakan dengan mulus. Saat
menekan `S`, prediksi selalu dihitung ulang memakai ensemble penuh — jadi
hasil yang tersimpan tidak pernah memakai mode cepat.

## Cara membaca hasil

Model benar sekitar **61%** untuk tebakan pertama, dan **83%** kalau dua
tebakan teratas dihitung. Karena itu tampilan selalu menyajikan dua
kemungkinan, bukan satu jawaban.

| Warna | Keyakinan | Artinya |
|---|---|---|
| 🟢 hijau | > 70% | cukup bisa dipercaya |
| 🟡 kuning | 40–70% | pertimbangkan juga tebakan kedua |
| 🔴 merah | < 40% | model tidak yakin, cek manual |

Kalau selisih dua tebakan teratas di bawah 15 poin, aplikasi menyatakan
hasilnya secara eksplisit sebagai "antara A dan B".

Akurasi per kelas tidak merata: `square` 75% dan `rectangular` 71% cukup
andal, sementara `round` 50% dan `ovale` 51% sering tertukar satu sama lain.

## Kalau bermasalah

**"Gagal memuat model"** — folder `artifacts/` belum ada di sebelah
`app.py`. Jalankan `14_train_final.ipynb` dulu.

**"Kamera tidak bisa dibuka"** — coba `--camera 1`. Di macOS, beri izin
kamera untuk Terminal di System Settings → Privacy & Security → Camera.

**"wajah tidak terdeteksi"** — Haar cascade gagal menemukan wajah dan
gambar dipotong di tengah. Hasilnya jauh kurang bisa dipercaya. Perbaiki
dengan menghadap depan, pencahayaan lebih merata, dan wajah mengisi
sebagian besar bingkai.

**Lambat di CPU** — pakai `--fast` untuk kamera langsung, atau naikkan
`--every` ke 15.

## Sumber rekomendasi gaya rambut

Isi rekomendasi dirangkum dalam kata-kata sendiri dari dua panduan barbering:

- [Clippers Barbershop — Best Haircut for Different Face Shapes Men](https://clippersbarbershop-tx.com/mens-haircuts-by-face-shape/)
- [London School of Barbering — Best Men's hairstyles for all face shapes](https://www.londonschoolofbarbering.com/mens-hairstyles-face-shapes/)

Tiap gaya diberi label sumbernya, sehingga terlihat mana yang disepakati
kedua panduan dan mana yang hanya disebut salah satu. Untuk wajah **square**
kedua sumber berbeda pendapat — Clippers memasukkan high fade dan undercut,
London School of Barbering justru menyarankan potongan yang tidak terlalu
tegas. Perbedaan itu ditampilkan apa adanya di aplikasi, bukan dipilih
diam-diam, karena keduanya sama-sama masuk akal tergantung apakah tujuanmu
mempertegas atau melunakkan struktur wajah.

Semua saran ini bersifat umum. Tekstur rambut, tinggi badan, gaya
berpakaian, dan selera pribadi juga ikut menentukan, dan barber yang melihat
langsung tetap penasihat terbaik.

## Batasan

Model dilatih pada 1139 foto wajah pria dengan kualitas label yang tidak
sempurna. Belum divalidasi untuk wajah perempuan, anak-anak, atau kelompok
etnis di luar yang ada di dataset. Bentuk wajah juga kategori yang
batasnya kabur — bahkan manusia sering tidak sepakat. Jangan dipakai untuk
keputusan yang berdampak nyata bagi seseorang.
