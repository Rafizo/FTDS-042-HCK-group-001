"""
Rekomendasi gaya rambut per bentuk wajah.

Sumber:
  [1] Clippers Barbershop — "Best Haircut for Different Face Shapes Men"
      https://clippersbarbershop-tx.com/mens-haircuts-by-face-shape/
  [2] London School of Barbering — "Best Men's hairstyles for all face shapes"
      https://www.londonschoolofbarbering.com/mens-hairstyles-face-shapes/

Isi di bawah adalah rangkuman dalam kata-kata sendiri dari kedua panduan itu,
bukan kutipan. Di beberapa titik kedua sumber tidak sepakat; perbedaan itu
ditulis apa adanya di field `catatan_sumber` alih-alih dipilih diam-diam.

Pemetaan istilah: kelas model `ovale` = oval, `rectangular` = oblong/rectangular.
"""

from __future__ import annotations

SOURCES = [
    {
        "label": "Clippers Barbershop",
        "judul": "Best Haircut for Different Face Shapes Men",
        "url": "https://clippersbarbershop-tx.com/mens-haircuts-by-face-shape/",
    },
    {
        "label": "London School of Barbering",
        "judul": "Best Men's hairstyles for all face shapes",
        "url": "https://www.londonschoolofbarbering.com/mens-hairstyles-face-shapes/",
    },
]

# S1 = Clippers Barbershop, S2 = London School of Barbering
RECOMMENDATIONS = {
    "ovale": {
        "nama_id": "Oval",
        "ciri": "Proporsi seimbang, panjang wajah sedikit lebih besar "
                "daripada lebarnya.",
        "tujuan": "Bentuk paling fleksibel — hampir semua gaya cocok, jadi "
                  "tujuannya menjaga keseimbangan yang sudah ada.",
        "gaya": [
            ("Crew cut", "Pendek, rapi, cocok untuk keseharian dan kerja.", "S1"),
            ("Textured crop", "Tekstur di atas memberi dimensi tanpa "
                              "mengubah proporsi wajah.", "S1"),
            ("Side part taper", "Belahan samping dengan sisi mengecil "
                                "bertahap; klasik dan rapi.", "S1"),
            ("Undercut", "Sisi sangat pendek, atas dibiarkan panjang.", "S1"),
            ("Pompadour", "Rambut disisir ke atas dan ke belakang, "
                          "menjauh dari dahi.", "S1, S2"),
        ],
        "hindari": [
            "Poni panjang yang menutup dahi — membuat wajah terlihat lebih "
            "pendek dan bulat, justru menghilangkan keunggulan bentuk oval. [S2]",
        ],
        "jenggot": "Tidak ada batasan khusus. Bentuk oval memberi ruang "
                   "bereksperimen dengan berbagai gaya jenggot.",
        "minta_ke_barber": "Sebutkan bahwa wajahmu oval dan kamu ingin rambut "
                           "diarahkan ke atas menjauhi dahi, bukan diturunkan "
                           "menutupi dahi.",
        "catatan_sumber": "Kedua sumber sepakat: oval adalah kanvas kosong. "
                          "Satu-satunya larangan yang disebut adalah poni panjang.",
    },

    "rectangular": {
        "nama_id": "Rectangular / Oblong",
        "ciri": "Wajah memanjang secara vertikal dengan lebar yang relatif "
                "sempit.",
        "tujuan": "Menambah kesan lebar dan memperpendek tampilan vertikal.",
        "gaya": [
            ("Gaya berlapis (layered)", "Lapisan di sisi menambah volume "
                                        "horizontal.", "S1"),
            ("Panjang sedang", "Tidak terlalu pendek di sisi, tidak terlalu "
                               "tinggi di atas.", "S1, S2"),
            ("Side part bertekstur", "Belahan samping memecah garis vertikal "
                                     "wajah.", "S1"),
            ("Poni (fringe)", "Menutup sebagian dahi sehingga wajah tampak "
                              "lebih pendek.", "S2"),
            ("Shaggy / sebahu", "Volume di sisi memberi lebar tambahan.", "S1"),
        ],
        "hindari": [
            "Volume tinggi di bagian atas — memperpanjang wajah lebih jauh. "
            "[S1, S2]",
            "Sisi yang dicukur terlalu pendek sementara atas dibiarkan "
            "panjang; kombinasi itu mempertegas kesan memanjang. [S2]",
        ],
        "jenggot": "London School of Barbering menyarankan menghindari jenggot "
                   "panjang, karena menambah panjang wajah. Kalau tetap ingin "
                   "berjenggot, pilih yang pendek dan lebih lebar di sisi "
                   "rahang daripada memanjang di dagu.",
        "minta_ke_barber": "Minta gaya yang seimbang, tanpa tinggi berlebih di "
                           "atas, dan pertimbangkan poni untuk memperpendek "
                           "tampilan dahi.",
        "catatan_sumber": "Kedua sumber sepakat penuh: tambah lebar, kurangi "
                          "tinggi.",
    },

    "round": {
        "nama_id": "Round",
        "ciri": "Lekuk lembut, lebar dan tinggi wajah hampir sama, sedikit "
                "sudut tajam.",
        "tujuan": "Menciptakan tinggi dan sudut agar wajah tampak lebih "
                  "panjang dan terstruktur.",
        "gaya": [
            ("High fade + atas bertekstur", "Sisi sangat pendek, atas "
                                            "bervolume — kontras ini "
                                            "memanjangkan wajah.", "S1"),
            ("Pompadour", "Volume tinggi di depan, salah satu gaya yang paling "
                          "sering disebut untuk wajah bulat.", "S1, S2"),
            ("Quiff", "Bagian depan diangkat, sisi tetap rapi.", "S1"),
            ("Flat top", "Bidang datar di atas memberi sudut tegas.", "S2"),
            ("Faux hawk", "Volume terpusat di tengah menambah tinggi.", "S1"),
            ("Side part", "Belahan menciptakan garis lurus yang memecah "
                          "lekuk.", "S1"),
        ],
        "hindari": [
            "Sisi yang dibiarkan tebal atau penuh — menambah lebar wajah. [S1]",
            "Bagian atas yang terlalu pendek — menghilangkan tinggi yang "
            "justru dibutuhkan. [S1]",
        ],
        "jenggot": "Jenggot justru membantu di sini. London School of "
                   "Barbering menyebut jenggot memanjangkan tampilan wajah "
                   "dan mengurangi kesan bulat.",
        "minta_ke_barber": "Minta tinggi di atas dan sisi yang rapat. Bisa juga "
                           "minta sudut siku di area pelipis atas untuk "
                           "menajamkan garis yang lembut.",
        "catatan_sumber": "Kedua sumber sepakat: tinggi di atas, rapat di sisi.",
    },

    "square": {
        "nama_id": "Square",
        "ciri": "Garis rahang tegas, dahi lebar, tulang pipi lebar — lebar "
                "yang merata di semua titik.",
        "tujuan": "Melunakkan sudut tajam tanpa menghilangkan struktur yang "
                  "sudah kuat.",
        "gaya": [
            ("Crew cut", "Disebut oleh kedua sumber; membulatkan tampilan "
                         "tanpa menambah ketegasan.", "S1, S2"),
            ("Side part", "Disebut oleh kedua sumber; belahan samping "
                          "melembutkan garis wajah.", "S1, S2"),
            ("Textured crop", "Tekstur acak mengurangi kesan kaku.", "S1"),
            ("Quiff", "Menambah tinggi dan kesan rapi.", "S1"),
            ("High fade / undercut", "Menonjolkan struktur rahang — pilih "
                                     "kalau ingin mempertegas, bukan "
                                     "melunakkan.", "S1"),
            ("Panjang sedang di atas, potongan santai", "Garis potong yang "
                                                        "tidak terlalu tegas.",
             "S2"),
        ],
        "hindari": [
            "Potongan yang garisnya sangat tegas dan geometris kalau tujuanmu "
            "melunakkan wajah — wajah square sudah punya banyak sudut. [S2]",
        ],
        "jenggot": "Rahang sudah tegas, jadi jenggot tebal berpotensi membuat "
                   "bagian bawah wajah terlihat makin berat. Jenggot pendek "
                   "yang dirapikan biasanya lebih seimbang.",
        "minta_ke_barber": "Tentukan dulu tujuanmu: melunakkan sudut (crew cut, "
                           "side part, potongan santai) atau justru "
                           "mempertegasnya (high fade, undercut). Sampaikan "
                           "pilihan itu ke barber.",
        "catatan_sumber": "DI SINI KEDUA SUMBER BERBEDA. Clippers Barbershop "
                          "memasukkan high fade dan undercut sebagai pilihan "
                          "untuk wajah square. London School of Barbering "
                          "justru menyarankan potongan yang tidak terlalu "
                          "tegas, karena wajah square sudah sangat maskulin. "
                          "Keduanya masuk akal — bedanya pada tujuan: "
                          "mempertegas struktur atau melunakkannya.",
    },
}

SOURCE_LABEL = {"S1": "Clippers Barbershop",
                "S2": "London School of Barbering",
                "S1, S2": "kedua sumber"}


def get(face_shape: str) -> dict | None:
    """Ambil rekomendasi untuk satu kelas. Nama kelas tidak case-sensitive."""
    return RECOMMENDATIONS.get(str(face_shape).strip().lower())


def as_text(face_shape: str, lebar: int = 72) -> str:
    """Versi teks polos, untuk terminal atau log."""
    r = get(face_shape)
    if r is None:
        return f"Tidak ada rekomendasi untuk '{face_shape}'."

    baris = ["=" * lebar,
             f"REKOMENDASI GAYA RAMBUT — {r['nama_id'].upper()}",
             "=" * lebar,
             f"\nCiri   : {r['ciri']}",
             f"Tujuan : {r['tujuan']}",
             "\nGaya yang disarankan:"]
    for nama, catatan, src in r["gaya"]:
        baris.append(f"  • {nama} [{SOURCE_LABEL.get(src, src)}]")
        baris.append(f"      {catatan}")
    baris.append("\nSebaiknya dihindari:")
    for h in r["hindari"]:
        baris.append(f"  ✗ {h}")
    baris.append(f"\nJenggot : {r['jenggot']}")
    baris.append(f"\nKe barber: {r['minta_ke_barber']}")
    baris.append(f"\nCatatan sumber: {r['catatan_sumber']}")
    baris.append("\nSumber:")
    for s in SOURCES:
        baris.append(f"  - {s['label']}: {s['url']}")
    return "\n".join(baris)


def short_list(face_shape: str, n: int = 3) -> list:
    """Beberapa nama gaya teratas saja — untuk overlay kamera."""
    r = get(face_shape)
    return [g[0] for g in r["gaya"][:n]] if r else []
