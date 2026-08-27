# Trimatch: Your Style, Your Cut
## AI-Based Hairstyle Recommendation for Men Based on Face Shape

![alt text](files/Logo_Trimatch.jpeg)

# Final Project Student Hacktiv8 Batch HCK-042 FTDS

*Project ini dibuat sebagai bukti penerapan pembelajaran Data Science, Machine Learning, Deep Learning, Computer Vision, serta deployment aplikasi dalam Final Project Hacktiv8.*

---

* Anggota Proyek:

  * Muhammad Cesar Rivaldo
  * Muhammad Rafi Addien
  * Muhammad Zaky Ramadhan
  * Muhammad Zulyandhika

---

## Tentang Proyek Akhir

### **Trimatch: Your Style, Your Cut**

**Trimatch** adalah aplikasi berbasis Computer Vision yang dirancang untuk mengklasifikasikan bentuk wajah pria ke dalam empat kategori, yaitu **ovale**, **rectangular**, **round**, dan **square**.

Hasil klasifikasi kemudian dapat digunakan sebagai dasar untuk memberikan rekomendasi gaya rambut yang sesuai dengan bentuk wajah pengguna.

Model utama yang digunakan adalah **MobileNetV2** dengan pendekatan **transfer learning** dan **fine-tuning**.

---

### Latar Belakang

Pemilihan gaya rambut merupakan salah satu aspek yang dapat memengaruhi penampilan seseorang. Salah satu faktor yang umum digunakan oleh barber atau hairstylist dalam memberikan rekomendasi adalah bentuk wajah.

Namun, tidak semua orang dapat menentukan bentuk wajahnya sendiri secara akurat. Perbedaan antara bentuk wajah seperti `ovale`, `round`, `square`, dan `rectangular` juga sering kali tidak memiliki batas visual yang benar-benar jelas.

Oleh karena itu, proyek ini mencoba mengotomatisasi proses identifikasi bentuk wajah menggunakan metode **Deep Learning berbasis Computer Vision**.

Selain membangun model klasifikasi, proyek ini juga berfokus pada kualitas data dan protokol evaluasi. Eksperimen dilakukan untuk mengetahui pengaruh **face cropping**, **koreksi label**, **deduplikasi gambar**, serta kualitas anotasi dataset terhadap performa model.

---

### Tujuan Pembuatan Aplikasi

Tujuan utama dari proyek ini adalah membangun aplikasi yang dapat:

1. Mengidentifikasi bentuk wajah pria secara otomatis dari sebuah gambar.
2. Mengklasifikasikan wajah ke dalam empat kelas:

   * `ovale`
   * `rectangular`
   * `round`
   * `square`
3. Memberikan dua prediksi bentuk wajah dengan probabilitas tertinggi.
4. Memberikan rekomendasi gaya rambut berdasarkan hasil klasifikasi bentuk wajah.
5. Menyediakan proses klasifikasi melalui upload gambar maupun kamera.
6. Mengetahui pengaruh tahapan preprocessing terhadap performa model.
7. Mengevaluasi pengaruh kualitas anotasi dan duplikasi gambar terhadap hasil klasifikasi.

---

## Dataset

Dataset yang digunakan merupakan dataset publik berisi gambar wajah pria dengan empat kelas bentuk wajah.

Dataset awal memiliki **1.312 gambar** yang kemudian melalui beberapa tahapan pembersihan sebelum digunakan untuk pelatihan model.

| Tahap Dataset                          |    Jumlah |
| -------------------------------------- | --------: |
| Gambar mentah                          |     1.312 |
| Label diperbaiki berdasarkan nama file |        59 |
| Gambar duplikat/nyaris identik dibuang |       173 |
| Dataset final                          | **1.139** |
| Wajah berhasil terdeteksi              | **98,9%** |

Dataset awal memiliki struktur folder `training_set` dan `testing_set`. Namun, pada evaluasi final seluruh data digabungkan terlebih dahulu, dilakukan deduplikasi secara global, kemudian dibagi ulang menggunakan **Stratified 5-Fold Cross Validation**.

---

## Model

Model utama yang digunakan adalah **MobileNetV2** yang telah dilatih sebelumnya menggunakan dataset **ImageNet**.

Arsitektur akhir:

```text
Input Image
    ↓
MobileNetV2 (ImageNet)
    ↓
Global Average Pooling
    ↓
Dropout (0.25)
    ↓
Dense (128)
    ↓
Dropout (0.15)
    ↓
Dense (4, Softmax)
```

---


## Baseline Model

Beberapa metode dibandingkan untuk mengetahui kontribusi transfer learning dan fine-tuning.

| Metode                                 |   Akurasi |
| -------------------------------------- | --------: |
| Random Guess                           |     25,2% |
| Majority Class                         |     27,7% |
| CNN From Scratch                       |    24–44% |
| Logistic Regression + Frozen Embedding |     60,4% |
| **MobileNetV2 Fine-Tuned**             | **61,1%** |

### CNN From Scratch

CNN yang dilatih dari awal menunjukkan performa yang tidak stabil.

Dari lima fold:

* satu fold mencapai **43,67%**
* empat fold lainnya berada di sekitar **25%**

Hal tersebut menunjukkan bahwa dataset sekitar 900 gambar training per fold belum cukup stabil untuk melatih CNN sepenuhnya dari awal.

Jika dibandingkan dengan fold terbaik CNN from scratch sekitar **44%**, transfer learning memberikan peningkatan realistis sekitar **17 poin**.

### Logistic Regression

Regresi logistik menggunakan embedding MobileNetV2 yang dibekukan sudah mencapai akurasi sekitar **60,4%**.

Hasil tersebut sangat dekat dengan MobileNetV2 yang di-fine-tune sebesar **61,1%**.

Hal ini menunjukkan bahwa sebagian besar kemampuan klasifikasi berasal dari representasi fitur hasil pretraining ImageNet.

Walaupun selisihnya kecil, uji **McNemar** menunjukkan bahwa fine-tuning memberikan peningkatan yang signifikan secara statistik:

```text
p-value = 0.046
```

---

## Cara Kerja Aplikasi

Alur utama aplikasi:

```text
Input Gambar / Kamera
        ↓
Deteksi Wajah
        ↓
Face Cropping
        ↓
Resize & Preprocessing
        ↓
MobileNetV2
        ↓
Probabilitas 4 Bentuk Wajah
        ↓
Top-1 & Top-2 Prediction
        ↓
Rekomendasi Gaya Rambut
```

Pengguna dapat memberikan input melalui:

* upload gambar;
* kamera;
* batch image processing;
* aplikasi kamera realtime.

Setelah wajah terdeteksi, gambar diproses oleh model untuk menghasilkan probabilitas dari empat kelas bentuk wajah.

Karena Top-2 Accuracy model jauh lebih tinggi dibanding Top-1 Accuracy, aplikasi menampilkan **dua prediksi tertinggi** kepada pengguna.

---

## Fitur Aplikasi

Aplikasi menyediakan beberapa fitur utama:

### Image Upload

Pengguna dapat mengunggah gambar wajah untuk dianalisis.

### Camera Input

Pengguna dapat mengambil foto langsung menggunakan kamera.

### Batch Processing

Beberapa gambar dapat dianalisis sekaligus.

### Real-Time Camera

Tersedia aplikasi kamera realtime yang dapat melakukan klasifikasi bentuk wajah dan menyimpan screenshot.

### Top-2 Prediction

Aplikasi menampilkan dua bentuk wajah dengan probabilitas tertinggi.

### Confidence Indicator

Tingkat confidence model ditampilkan menggunakan indikator visual.

### Face Detection Warning

Jika wajah tidak berhasil dideteksi, aplikasi memberikan peringatan kepada pengguna.

### Hairstyle Recommendation

Berdasarkan hasil klasifikasi, aplikasi memberikan rekomendasi gaya rambut yang sesuai dengan kelas bentuk wajah pengguna.

---

## Project Output

Aplikasi dikembangkan menggunakan **Streamlit** sebagai antarmuka utama berbasis web.

Output proyek meliputi:

```text
Model Klasifikasi Bentuk Wajah
        +
Streamlit Web Application
        +
Real-Time Camera Application
        +
Hairstyle Recommendation System
```

File utama aplikasi meliputi:

```text
app.py
live_camera.py
faceshape.py
```

---

## Kesimpulan

Berdasarkan hasil eksperimen, diperoleh beberapa kesimpulan utama:

1. **MobileNetV2 dengan transfer learning dan fine-tuning mencapai akurasi OOF sebesar 61,11% ± 1,29** pada klasifikasi empat bentuk wajah pria.

2. Model mencapai **Top-2 Accuracy sebesar 82,88%**, menunjukkan bahwa kelas yang benar sering kali masih berada di antara dua prediksi dengan probabilitas tertinggi.

3. **Face cropping** merupakan preprocessing yang memberikan kontribusi paling besar terhadap performa dengan peningkatan sekitar **5,14 poin**.

4. **Deduplikasi merupakan tahap penting dalam evaluasi model.** Tanpa deduplikasi, akurasi terlihat sekitar **4,67 poin lebih tinggi secara semu** akibat kemungkinan gambar yang hampir identik berada pada data training dan testing.

5. **Pembersihan label menggunakan Confident Learning tidak meningkatkan performa secara signifikan** dengan hasil McNemar `p = 0.805`.

6. Logistic Regression menggunakan fitur MobileNetV2 yang dibekukan sudah mencapai **60,4%**, sangat dekat dengan model fine-tuned sebesar **61,1%**. Hal tersebut menunjukkan bahwa fitur hasil pretraining ImageNet memberikan kontribusi besar terhadap kemampuan klasifikasi.

7. Keterbatasan utama sistem kemungkinan tidak hanya berasal dari kapasitas model, tetapi juga dari **ukuran dataset, kualitas anotasi, dan ambiguitas visual antar-kelas bentuk wajah**.

---

## Pengembangan Selanjutnya

Beberapa pengembangan yang dapat dilakukan pada penelitian selanjutnya:

1. Menggunakan dataset yang lebih besar dengan prosedur anotasi yang lebih terdokumentasi.
2. Melakukan anotasi menggunakan beberapa manusia untuk menghitung **inter-annotator agreement**.
3. Menggunakan **MediaPipe FaceMesh** untuk melakukan face alignment.
4. Mengekstraksi fitur geometris wajah secara eksplisit, seperti:

   * rasio lebar rahang terhadap tinggi wajah;
   * rasio lebar dahi;
   * panjang wajah;
   * lebar cheekbone;
   * sudut rahang.
5. Menggabungkan fitur geometris dengan deep learning.
6. Mengembangkan sistem rekomendasi hairstyle yang lebih personal dengan mempertimbangkan karakteristik tambahan selain bentuk wajah.

---

## Struktur File

```text
project/
│
├── notebooks/
│   ├── 14_train_final.ipynb
│   └── 15_inference_final.ipynb
│
├── artifacts/
│   └── suspected_mislabels.csv
│
├── app.py
├── live_camera.py
├── faceshape.py
│
└── README.md
```

---

### **Trimatch: Your Style, Your Cut**

*Matching your face shape with a hairstyle that fits you.*
