#!/usr/bin/env python3
"""
Kamera langsung dengan prediksi bentuk wajah secara realtime.

Jalankan:
    python live_camera.py
    python live_camera.py --camera 1 --every 5
    python live_camera.py --fast          # 1 model saja, lebih lancar

Tombol:
    S / SPASI  simpan screenshot + hasil prediksi
    F          ganti mode cepat (1 model) <-> akurat (semua model)
    Q / ESC    keluar

Catatan performa: menjalankan ensemble 5 model tiap frame terlalu berat,
jadi prediksi di-throttle setiap N frame (default 8). Deteksi wajah tetap
jalan tiap frame supaya kotaknya mengikuti gerakan dengan mulus.
Saat menekan S, prediksi selalu dihitung ulang memakai seluruh ensemble.
"""

import argparse
import csv
import os
import sys
import time

import numpy as np

import faceshape as fs
import recommendations as rec

# warna BGR
HIJAU  = (80, 200, 120)
KUNING = (60, 200, 240)
MERAH  = (80, 80, 230)
PUTIH  = (245, 245, 245)
GELAP  = (35, 35, 35)

WARNA_TINGKAT = {"tinggi": HIJAU, "sedang": KUNING, "rendah": MERAH}


def draw_panel(cv2, frame, res, cfg, fps, fast_mode, n_models):
    h, w = frame.shape[:2]

    if res is not None:
        x1, y1, x2, y2 = res["box"]
        warna = WARNA_TINGKAT[res["tingkat"]] if res["wajah_terdeteksi"] else MERAH
        cv2.rectangle(frame, (x1, y1), (x2, y2), warna, 2)

        label = f"{res['prediksi']} {res['keyakinan']*100:.0f}%"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.rectangle(frame, (x1, max(0, y1-th-12)), (x1+tw+12, y1), warna, -1)
        cv2.putText(frame, label, (x1+6, max(th, y1-6)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (20, 20, 20), 2)

        if not res["wajah_terdeteksi"]:
            cv2.putText(frame, "wajah tidak terdeteksi", (x1+6, y2+22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, MERAH, 2)

    # panel bawah: bar probabilitas tiap kelas
    ph = 26 * cfg.n_classes + 78
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, h-ph), (w, h), GELAP, -1)
    cv2.addWeighted(overlay, 0.72, frame, 0.28, 0, frame)

    y = h - ph + 26
    if res is not None:
        for c in res["urutan"]:
            p = res["probs"][c]
            cv2.putText(frame, f"{c:<12}", (14, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, PUTIH, 1)
            bx = 150
            cv2.rectangle(frame, (bx, y-11), (bx+260, y+3), (70, 70, 70), -1)
            cv2.rectangle(frame, (bx, y-11), (bx+int(260*p), y+3),
                          HIJAU if c == res["prediksi"] else (120, 150, 180), -1)
            cv2.putText(frame, f"{p*100:4.1f}%", (bx+272, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, PUTIH, 1)
            y += 26
        if res["ambigu"]:
            cv2.putText(frame,
                        f"selisih tipis: antara {res['prediksi']} dan {res['alternatif']}",
                        (14, y+2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, KUNING, 1)
            y += 20

        # tiga gaya teratas untuk kelas yang diprediksi
        gaya = rec.short_list(res["prediksi"], 3)
        if gaya:
            cv2.putText(frame, "gaya: " + " | ".join(gaya), (14, y+2),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, (200, 220, 255), 1)
    else:
        cv2.putText(frame, "menunggu wajah...", (14, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, PUTIH, 1)

    mode = f"cepat (1/{n_models})" if fast_mode else f"akurat ({n_models} model)"
    cv2.putText(frame, f"{fps:.0f} fps | {mode} | S=simpan  F=mode  Q=keluar",
                (14, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.5, PUTIH, 1)
    return frame


def main():
    ap = argparse.ArgumentParser(
        description="Prediksi bentuk wajah dari kamera secara langsung.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("--artifacts", default="artifacts")
    ap.add_argument("--camera", type=int, default=0, help="indeks kamera")
    ap.add_argument("--every", type=int, default=8,
                    help="prediksi tiap N frame (default 8)")
    ap.add_argument("--fast", action="store_true",
                    help="mulai dengan 1 model saja")
    ap.add_argument("--outdir", default="screenshots")
    ap.add_argument("--width", type=int, default=960)
    args = ap.parse_args()

    try:
        import cv2
    except ImportError:
        sys.exit("Butuh opencv: pip install opencv-python")

    print("Memuat model...")
    cfg = fs.load_config(args.artifacts)
    models, paths = fs.load_models(args.artifacts)
    cascade = fs.load_cascade(cfg)
    print(f"{len(models)} model siap | akurasi top-1 {cfg.oof_accuracy*100:.1f}%"
          f" / top-2 {cfg.top2_accuracy*100:.1f}%")

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        sys.exit(f"Kamera {args.camera} tidak bisa dibuka. "
                 "Coba --camera 1, atau cek izin kamera di pengaturan sistem.")

    os.makedirs(args.outdir, exist_ok=True)
    csv_path = os.path.join(args.outdir, "log.csv")
    if not os.path.exists(csv_path):
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(
                ["waktu", "file", "prediksi", "keyakinan", "alternatif",
                 "keyakinan_alt", "wajah_terdeteksi"] + cfg.classes)

    fast, res, frame_i, n_saved = args.fast, None, 0, 0
    t_prev, fps = time.time(), 0.0
    print("Jendela kamera terbuka. Tekan S untuk simpan, Q untuk keluar.")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Gagal membaca frame."); break

            if args.width and frame.shape[1] != args.width:
                scale = args.width / frame.shape[1]
                frame = cv2.resize(frame, None, fx=scale, fy=scale)
            frame = cv2.flip(frame, 1)          # tampil seperti cermin
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            if frame_i % max(1, args.every) == 0:
                used = models[:1] if fast else models
                res = fs.predict_image(rgb, used, cascade, cfg)

            now = time.time()
            fps = 0.85*fps + 0.15/max(1e-6, now - t_prev)
            t_prev = now

            view = draw_panel(cv2, frame.copy(), res, cfg, fps, fast, len(models))
            cv2.imshow("Deteksi Bentuk Wajah", view)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), 27):
                break
            if key == ord('f'):
                fast = not fast
                print("Mode:", "cepat" if fast else "akurat")
            if key in (ord('s'), 32):
                # screenshot selalu memakai ensemble penuh, bukan mode cepat
                final = fs.predict_image(rgb, models, cascade, cfg)
                ts = time.strftime("%Y%m%d_%H%M%S")
                name = f"{ts}_{final['prediksi']}_{final['keyakinan']*100:.0f}.jpg"
                cv2.imwrite(os.path.join(args.outdir, name), frame)
                cv2.imwrite(os.path.join(args.outdir, f"crop_{name}"),
                            cv2.cvtColor(final["patch"], cv2.COLOR_RGB2BGR))
                with open(csv_path, "a", newline="", encoding="utf-8") as f:
                    csv.writer(f).writerow(
                        [ts, name, final["prediksi"],
                         f"{final['keyakinan']:.4f}", final["alternatif"],
                         f"{final['keyakinan_alt']:.4f}",
                         int(final["wajah_terdeteksi"])] +
                        [f"{final['probs'][c]:.4f}" for c in cfg.classes])
                n_saved += 1
                res = final
                print(f"[{n_saved}] {name}  ->  {final['prediksi']} "
                      f"{final['keyakinan']*100:.1f}% "
                      f"(alt: {final['alternatif']} "
                      f"{final['keyakinan_alt']*100:.1f}%)"
                      + ("  [wajah tak terdeteksi]"
                         if not final["wajah_terdeteksi"] else ""))
                print(rec.as_text(final["prediksi"]))
                if final["ambigu"]:
                    print("\nModel ragu antara dua kelas. Rekomendasi untuk "
                          f"'{final['alternatif']}' juga layak dilihat:")
                    print(rec.as_text(final["alternatif"]))
                # simpan rekomendasi bersama screenshot
                with open(os.path.join(args.outdir, f"{ts}_rekomendasi.txt"),
                          "w", encoding="utf-8") as fr:
                    fr.write(rec.as_text(final["prediksi"]))
            frame_i += 1
    finally:
        cap.release()
        cv2.destroyAllWindows()
        if n_saved:
            print(f"\n{n_saved} screenshot tersimpan di {args.outdir}/")
            print(f"Log: {csv_path}")


if __name__ == "__main__":
    main()
