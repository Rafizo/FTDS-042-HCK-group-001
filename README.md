# Struktur Laporan — Klasifikasi Bentuk Wajah Pria

Kerangka penulisan berdasarkan seluruh eksperimen v1–v15, lengkap dengan
angka yang sudah terverifikasi dan catatan mana yang boleh/tidak boleh
dikutip.

---

## Angka kunci (rujukan cepat)

**Hasil akhir — pakai ini sebagai angka utama**

| Metrik | Nilai |
|---|---|
| Akurasi OOF 5-fold | **61,11% ± 1,29** (n = 1139) |
| Top-2 accuracy | 82,88% |
| Tebak acak | 25,00% |
| Tebak kelas mayoritas | 27,66% |

**Per kelas**

| Kelas | Precision | Recall | F1 |
|---|---|---|---|
| ovale | 0,629 | 0,511 | 0,564 |
| rectangular | 0,600 | 0,710 | 0,651 |
| round | 0,822 | 0,503 | 0,624 |
| square | 0,512 | 0,755 | 0,610 |

**Dataset**

| Tahap | Jumlah |
|---|---|
| Gambar mentah | 1312 |
| Label diperbaiki dari nama file | 59 |
| Gambar kembar dibuang (dHash) | 173 |
| Dataset final | 1139 |
| Wajah berhasil terdeteksi | 98,9% |

---

## Bab 1 — Pendahuluan

**1.1 Latar Belakang.** Bentuk wajah dipakai di industri penataan rambut dan
kacamata sebagai dasar rekomendasi gaya. Otomatisasi klasifikasinya
memungkinkan aplikasi rekomendasi mandiri.

**1.2 Rumusan Masalah.**
1. Seberapa akurat CNN transfer learning mengklasifikasi empat bentuk wajah
   pria?
2. Langkah pra-pemrosesan mana yang benar-benar berkontribusi?
3. Apakah kualitas anotasi dataset membatasi akurasi yang bisa dicapai?

Pertanyaan 2 dan 3 adalah yang membedakan laporanmu dari kebanyakan skripsi
klasifikasi gambar. Tonjolkan keduanya.

**1.3 Batasan.** Wajah pria, empat kelas, dataset publik ~1300 gambar,
satu arsitektur (MobileNetV2).

---

## Bab 2 — Tinjauan Pustaka

Materi yang perlu dibahas, semuanya sudah kamu pakai:

- CNN dan transfer learning; arsitektur MobileNetV2 (depthwise separable
  convolution, inverted residual)
- Fine-tuning dua tahap dan alasan learning rate kecil di tahap kedua
- Augmentasi data dan label smoothing
- **K-fold cross-validation dan out-of-fold prediction** — jelaskan mengapa
  ini lebih tepat daripada satu split tunggal pada dataset kecil
- **Perceptual hashing (dHash)** untuk deteksi duplikat
- **Confident learning** (Northcutt dkk., 2021) untuk deteksi label keliru
- **Uji McNemar** untuk membandingkan dua klasifikator berpasangan
- Haar cascade untuk deteksi wajah

---

## Bab 3 — Metodologi

### 3.1 Dataset
Sumber, struktur folder awal (`training_set` / `testing_set`), distribusi
kelas.

### 3.2 Pra-pemrosesan
Empat tahap, sajikan sebagai diagram alur:

1. Perbaikan format berkas (banyak `.jpg` yang isinya WEBP)
2. Koreksi label dari nama berkas — 59 berkas
3. Face cropping (Haar cascade, margin 35%)
4. Deduplikasi perceptual (dHash, ambang Hamming 5) — 173 berkas

### 3.3 Protokol Evaluasi
**Bagian terpenting di bab ini.** Jelaskan dua protokol dan alasan
pergantiannya (rinciannya di Bab 4.1):

- **Protokol A** — pembagian folder bawaan dataset
- **Protokol B** — gabungkan seluruh gambar, deduplikasi global, lalu
  pecah ulang stratified 5-fold dengan prediksi out-of-fold

### 3.4 Arsitektur dan Pelatihan
MobileNetV2 pra-latih ImageNet → GAP → Dropout 0,25 → Dense 128 → Dropout
0,15 → Dense 4 (softmax).

Dua tahap: (1) kepala dilatih di atas embedding beku, LR 1e-3;
(2) fine-tuning 60 layer teratas, LR 1e-5, BatchNorm tetap beku.

Augmentasi: flip horizontal, rotasi 0,06, zoom 0,06. Label smoothing 0,05.

**Sebutkan juga langkah pencegahan kebocoran:** validation set diambil dari
porsi training (85/15), bukan dari test fold. Ini bukan detail sepele —
kesalahan itu sempat terjadi di eksperimen v12 dan menaikkan akurasi 2–4
poin secara semu.

---

## Bab 4 — Hasil dan Pembahasan

### 4.1 Perbandingan Dua Protokol Evaluasi

Sajikan kedua protokol berdampingan. **Jangan menyembunyikan yang rendah** —
justru perbedaan inilah temuan utamamu.

| Protokol | Akurasi | Keterangan |
|---|---|---|
| A — split folder bawaan | 39,2% → 44,4% → 43,5% | test 100% dari `testing_set` |
| B — 5-fold OOF | **61,11% ± 1,29** | seluruh 1139 gambar |

Kenaikan 17 poin **bukan** karena model jadi lebih pintar. Penjelasannya di
4.2. Kalimat yang bisa dipakai:

> Kedua protokol mengukur hal yang berbeda. Protokol A mengukur kemampuan
> model berpindah antar-subhimpunan dataset yang tingkat kesulitannya
> berbeda; Protokol B mengukur kemampuan klasifikasi bentuk wajah itu
> sendiri. Untuk menjawab rumusan masalah, Protokol B lebih tepat.

### 4.2 Analisis Asal Gambar

Temuan yang direplikasi **empat kali** pada eksperimen independen:

| Eksperimen | Selisih akurasi | z |
|---|---|---|
| v6 | +10,68 poin | 3,40 |
| v9 | +11,75 poin | 3,73 |
| v10 | +11,53 poin | 3,67 |
| v14 (final) | +11,59 poin | 3,62 |

Gambar asal `testing_set` konsisten ~11 poin lebih sulit daripada asal
`training_set`.

**Hipotesis yang diuji dan ditolak:** pergeseran domain. Sebuah classifier
biner yang dilatih membedakan asal gambar hanya mencapai 70,18%, sementara
tebak-kelas-mayoritas sudah 69,10%. Kedua subhimpunan tidak dapat dibedakan
secara visual, sehingga perbedaan kesulitan bukan berasal dari perbedaan
proses pengumpulan.

Tulis penolakan hipotesis ini secara eksplisit. Menunjukkan dugaan yang
diuji lalu gugur adalah nilai tambah, bukan kekurangan.

### 4.3 Studi Ablasi

Dari eksperimen v11, kontribusi tiap langkah pra-pemrosesan diukur terpisah:

| Langkah | Efek |
|---|---|
| Face cropping | **+5,14 poin** |
| Koreksi label dari nama berkas | +1,89 poin |
| Deduplikasi | mencegah **+4,67 poin** akurasi semu |

Angka dedupe perlu penjelasan khusus, dan ini salah satu bagian terkuat
laporanmu:

> Deduplikasi tidak menaikkan akurasi — justru menurunkannya. Tanpa
> deduplikasi, gambar yang nyaris identik tersebar di himpunan latih dan uji
> sekaligus, sehingga akurasi yang dilaporkan rata-rata 4,67 poin lebih
> tinggi daripada kemampuan model yang sebenarnya. Penurunan angka setelah
> deduplikasi adalah koreksi, bukan kemunduran.

### 4.4 Perbandingan Baseline

| Metode | Akurasi |
|---|---|
| Tebak acak proporsional | 25,2% |
| Tebak kelas mayoritas | 27,7% |
| CNN dilatih dari nol | 24–44% (tidak stabil) |
| Regresi logistik atas embedding beku | 60,4% |
| **MobileNetV2 fine-tuned** | **61,1%** |

Dua catatan yang harus ikut ditulis:

**CNN dari nol tidak stabil.** Dari lima fold, satu mencapai 43,67% dan
empat lainnya kolaps ke sekitar 25% (setara tebakan). Pada ~900 gambar,
pelatihan dari nol sangat bergantung inisialisasi. Bandingkan transfer
learning dengan fold terbaiknya (~44%), sehingga kontribusi transfer
learning realistis sekitar **+17 poin** — bukan +35 seperti jika
dibandingkan dengan rata-rata yang didominasi kegagalan.

**Regresi logistik hampir menyamai fine-tuning.** Selisihnya kecil, yang
menunjukkan sebagian besar kemampuan berasal dari fitur pra-latih ImageNet,
bukan dari fine-tuning. Uji McNemar berpasangan tetap menunjukkan
fine-tuning unggul secara signifikan (p = 0,046).

### 4.5 Kualitas Anotasi Dataset

Tiga bukti independen:

1. **59 berkas salah folder** — nama berkas menyebut kelas berbeda dari
   folder tempatnya berada (contoh: `image square 158.jpg` di folder
   `rectangular`)
2. **Blok berurutan** — berkas `ovale` bernomor 500–549: 24 dari 35
   diprediksi `rectangular` dengan keyakinan tinggi, menandakan satu batch
   pengumpulan salah tempat
3. **57 gambar salah dengan keyakinan >90%** — daftar lengkap di
   `artifacts/suspected_mislabels.csv`

**Uji pembersihan label (v10).** Confident learning diterapkan hanya pada
porsi latih di dalam tiap fold; test fold tetap memakai label asli.

| Lengan | Akurasi |
|---|---|
| Tanpa pembersihan | 62,51% |
| Dengan pembersihan | 62,16% |

Uji McNemar: 76 prediksi berubah menjadi salah, 72 menjadi benar,
**p = 0,805**. Pembersihan label tidak memberi efek yang dapat dibedakan
dari kebetulan.

Kesimpulan yang jujur: sebagian besar kesalahan model bukan berasal dari
label keliru, melainkan dari ambiguitas visual antar-kelas yang memang
nyata. Top-2 accuracy 82,88% mendukung ini — jawaban benar hampir selalu
ada di dua tebakan teratas, pola khas kelas yang saling tumpang tindih.

### 4.6 Analisis Kesalahan

Confusion matrix menunjukkan `square` berperan sebagai kelas penampung:

| Pasangan | Frekuensi |
|---|---|
| ovale → square | 85 |
| round → square | 81 |
| ovale → rectangular | 57 |
| round → ovale | 42 |

Kalimat yang akurat untuk laporan:

> Kelas `square` memiliki recall tertinggi (75,5%) namun precision terendah
> (51,2%). Model cenderung memilih `square` saat ragu, sehingga banyak
> gambar berlabel `ovale` dan `round` terklasifikasi ke sana. Sebaliknya
> `round` memiliki precision 82,2% dengan recall hanya 50,3% — model jarang
> menebak `round`, tetapi ketika menebaknya biasanya benar.

⚠️ **Jangan kutip** kalimat yang tercetak di sel 9 notebook 14
("square/rectangular dan round/ovale memang mirip secara visual"). Kalimat
itu tertinggal dari eksperimen lebih awal dan **tidak cocok** dengan
confusion matrix run final.

### 4.7 Implementasi Aplikasi

- Antarmuka web (Streamlit): kamera, unggah, batch, panduan
- Aplikasi kamera realtime dengan fitur tangkapan layar
- Rekomendasi gaya rambut per kelas dari dua panduan barbering
- Desain antarmuka menyesuaikan performa model: dua tebakan selalu
  ditampilkan, indikator warna tingkat keyakinan, dan peringatan ketika
  wajah gagal terdeteksi

---

## Bab 5 — Kesimpulan dan Saran

**Kesimpulan**
1. MobileNetV2 fine-tuned mencapai 61,11% ± 1,29 (top-2 82,88%) pada empat
   kelas bentuk wajah, jauh di atas tebak mayoritas 27,7%
2. Face cropping adalah langkah pra-pemrosesan paling berpengaruh (+5,14)
3. Deduplikasi wajib dilakukan; tanpanya akurasi terlaporkan 4,67 poin
   lebih tinggi secara semu
4. Pembersihan label tidak meningkatkan akurasi (p = 0,805); keterbatasan
   utama adalah ambiguitas antar-kelas, bukan kesalahan anotasi

**Saran**
1. Ukur tingkat kesepakatan antar-anotator manusia sebagai batas atas
   realistis — tanpa angka ini, 61% sulit dinilai bagus atau buruk
2. Face landmark (MediaPipe FaceMesh) untuk penyelarasan dan ekstraksi
   rasio geometris eksplisit (lebar rahang ÷ tinggi wajah, dsb.)
3. Dataset lebih besar dengan protokol anotasi yang terdokumentasi

---

## Lampiran

| Lampiran | Isi |
|---|---|
| A | Kode notebook 14 (pelatihan) dan 15 (inferensi) |
| B | `suspected_mislabels.csv` — daftar kandidat label keliru |
| C | Riwayat eksperimen v1–v13 dan temuan tiap tahap |
| D | Kode aplikasi (`app.py`, `live_camera.py`, `faceshape.py`) |

---

## Pemetaan notebook → bagian laporan

| Notebook | Dipakai di | Temuan |
|---|---|---|
| 1–3 | 4.1 | Protokol A; penemuan 59 label salah |
| 4 | 4.2 | Uji pergeseran domain — hipotesis ditolak |
| 5–8 | 3.3 | Pengembangan protokol 5-fold OOF |
| 9–10 | 4.5 | Confident learning — hasil nol (p = 0,805) |
| 11 | 4.3 | Studi ablasi |
| 12 | 4.4 | Baseline + uji kepala vs fine-tune |
| 14 | 4.1, 4.6 | Hasil akhir |
| 15 + aplikasi | 4.7 | Implementasi |

---

## Catatan integritas data

**Eksperimen v11 dan v12 memakai test fold sebagai validation set.** Akibatnya
nilai absolutnya lebih tinggi 2–4 poin dari yang seharusnya. Yang tetap sah
dari kedua eksperimen itu adalah **perbandingan relatifnya**, karena semua
kombinasi yang dibandingkan mendapat keuntungan yang sama persis:

- v11: selisih antar-kombinasi ablasi → **sah**
- v12: kepala vs fine-tuning, McNemar p = 0,046 → **sah**
- Nilai absolut v11 dan v12 → **jangan dilaporkan sebagai hasil akhir**

Hanya notebook 14 yang memakai protokol tanpa kebocoran, dan hanya angkanya
(61,11%) yang boleh disajikan sebagai hasil.

Sebutkan hal ini di bab metodologi atau catatan kaki. Menuliskan keterbatasan
metode sendiri jauh lebih baik daripada ditemukan penguji.

---

## Pertanyaan penguji yang mungkin muncul

**"Kenapa akurasinya hanya 61%?"**
Bentuk wajah adalah kategori dengan batas kabur; top-2 mencapai 82,88%,
menunjukkan jawaban benar hampir selalu ada di dua tebakan teratas. Dataset
juga kecil (1139) dengan kualitas anotasi yang terbukti bermasalah — 59
berkas salah folder ditemukan secara terdokumentasi.

**"Kenapa hasilnya beda-beda antar-versi?"**
Karena protokol evaluasinya berbeda, dan pergantian protokol itu sendiri
merupakan temuan (Bab 4.1–4.2). Perbandingan yang sah hanya dalam protokol
yang sama.

**"Kenapa tidak memakai model yang lebih besar?"**
Regresi logistik di atas fitur beku sudah mencapai 60,4%, sangat dekat
dengan fine-tuning penuh. Ini menandakan hambatannya ada pada data, bukan
kapasitas model. Memperbesar arsitektur kecil kemungkinan membantu.

**"Bagaimana memastikan tidak ada kebocoran data?"**
Deduplikasi perceptual dilakukan secara global sebelum pembagian fold, dan
validation set diambil dari porsi latih, bukan dari test fold.