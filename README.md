<<<<<<< HEAD
# HAND TRACKING CAR DODGE USING HSV BLUE COLOR DETECTION

Game arcade balapan mobil 2D top-down yang dikendalikan menggunakan gerakan tangan melalui deteksi objek berwarna biru dengan metode **HSV Color Segmentation** (OpenCV). 

> **Catatan Arsitektur:** Proyek ini **100% murni menggunakan Computer Vision klasik** (Color Thresholding, Morphological Operations, Contours, & Image Moments). Sama sekali **TIDAK menggunakan MediaPipe, Machine Learning, maupun Deep Learning**.

---

## 1. FITUR UTAMA

- **Sistem 3 Jalur Mobil Presisi (Strict 3-Lane Architecture):**
  - **Lane 0 (Kiri):** $X = 135$ px
  - **Lane 1 (Tengah):** $X = 305$ px
  - **Lane 2 (Kanan):** $X = 475$ px
  - Posisi mobil dihitung langsung dari titik tengah jalur (`player_x = lane_centers[current_lane]`).
  - Mobil tidak akan pernah berhenti di antara dua jalur atau berada di atas marka pembatas.
- **Deteksi Warna Biru Non-Blocking:**
  - Pemrosesan citra webcam berjalan pada background thread terpisah sehingga rendering game tetap stabil pada **60 FPS**.
  - Dilengkapi *horizontal mirror*, *morphological opening/closing*, *centroid calculation*, *zone hysteresis*, *temporal smoothing*, dan *cooldown* untuk mencegah jitter.
- **Sistem Gameplay Menantang & Adil:**
  - Mobil NPC dengan 4 variasi sprite mobil unik bergerak dari atas ke bawah.
  - *Fair Spawn Algorithm*: Algoritma menjamin tidak pernah ada 3 jalur yang tertutup bersamaan, selalu ada celah bagi pemain untuk menghindar.
  - Kepadatan dan kecepatan NPC meningkat secara bertahap seiring berjalannya waktu dan skor.
- **Sistem Nyawa, Efek Tabrakan, & Invulnerability:**
  - Pemain memiliki 3 nyawa (diwakili ikon hati).
  - Saat tabrakan terjadi, nyawa berkurang 1, muncul efek ledakan partikel api & suara benturan, serta periode *invulnerability* (1,3 detik) dengan efek kedip untuk mencegah pengurangan nyawa ganda.
- **Panel Dashboard & Webcam Preview:**
  - Terletak rapi di sisi kanan layar ($X = 600 - 1000$ px), tidak pernah menutupi jalan atau mobil.
  - Menampilkan live video webcam, garis pembatas 3 zona, kontur objek biru, titik centroid crosshair, status deteksi, serta tombol toggle mode HSV binary mask (`[M]`).
- **Failsafe & Keyboard Fallback:**
  - Jika webcam tidak terpasang/gagal dibuka, game otomatis menampilkan status peringatan dan beralih ke kontrol keyboard tanpa mengalami crash.
- **Skor & High Score Lokal:**
  - Skor bertambah berdasarkan waktu bertahan (+10/detik) dan bonus berhasil melewati NPC (+50/mobil).
  - High score tersimpan otomatis secara lokal di `assets/highscore.json`.

---

## 2. STRUKTUR FOLDER PROYEK

```
hand_tracking_car_dodge/
├── main.py                    # Entry point utama aplikasi
├── config.py                  # Konfigurasi global, geometri jalur, & parameter HSV
├── requirements.txt           # Dependensi pustaka Python
├── README.md                  # Dokumentasi lengkap proyek
├── src/
│   ├── __init__.py
│   ├── game.py                # Game loop utama, event handler, & orkestrator
│   ├── player.py              # Logika mobil pemain, interpolasi jalur, & nyawa
│   ├── traffic.py             # Mobil NPC & algoritma fair procedural spawn
│   ├── lane_manager.py        # Pengelola 3 jalur tetap & aturan transisi
│   ├── hand_tracking.py       # Computer vision HSV tracker (non-blocking thread)
│   ├── collision.py           # Collision detection & sistem partikel tabrakan
│   ├── asset_manager.py       # Pemuat gambar, audio, font, & fallback caching
│   ├── ui.py                  # Tombol interaktif, HUD dashboard, & layar menu
│   └── state_manager.py       # State machine (HOME, PLAYING, PAUSED, GAME_OVER)
├── assets/
│   ├── backgrounds/
│   │   ├── home_bg.png
│   │   ├── road_bg.png
│   │   └── game_over_bg.png
│   ├── cars/
│   │   ├── player_car.png
│   │   ├── npc_car_01.png
│   │   ├── npc_car_02.png
│   │   ├── npc_car_03.png
│   │   └── npc_car_04.png
│   ├── ui/
│   │   ├── heart_full.png
│   │   ├── heart_empty.png
│   │   ├── start_button.png
│   │   ├── exit_button.png
│   │   ├── restart_button.png
│   │   ├── resume_button.png
│   │   └── home_button.png
│   └── audio/
│       ├── collision.wav
│       └── button_click.wav
├── tests/
│   ├── test_game_mechanics.py # Unit tests logika jalur, pemain, spawn, & HSV
│   └── test_game_loop.py      # Integration test siklus game loop
└── tools/
    └── generate_assets.py     # Script generator aset gambar & audio prosedural
```

---

## 3. PERSYARATAN SISTEM & DEPENDENSI

- **Sistem Operasi:** Linux (Fedora, Ubuntu, Debian, Arch) atau Windows 10/11.
- **Python:** Python 3.12 (disarankan) atau versi stabil yang didukung oleh Pygame 2.6+.
- **Webcam:** Kamera webcam bawaan laptop atau USB webcam.
- **Dependensi Python:**
  - `pygame >= 2.6.0`
  - `opencv-python >= 4.8.0`
  - `numpy >= 1.26.0`

---

## 4. PANDUAN INSTALASI & MENJALANKAN DI VS CODE

### Langkah A: Buka Folder di VS Code
1. Buka Visual Studio Code.
2. Pilih menu **File > Open Folder...**, lalu buka folder direktori proyek (`Game_HSV`).

### Langkah B: Pembuatan Virtual Environment
Buka terminal terintegrasi di VS Code (`Ctrl + ~` atau menu **Terminal > New Terminal**).

**Untuk Linux (Fedora / Ubuntu / Debian):**
```bash
python3.12 -m venv .venv
source .venv/bin/activate
```
*(Catatan Fedora Linux: Jika belum terpasang paket venv, pasang via `sudo dnf install python3.12 python3.12-pip`)*.

**Untuk Windows (PowerShell / Command Prompt):**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Langkah C: Memilih Python Interpreter di VS Code
1. Tekan `Ctrl + Shift + P` di VS Code untuk membuka Command Palette.
2. Ketik **Python: Select Interpreter**.
3. Pilih interpreter dari virtual environment yang baru dibuat: `./.venv/bin/python` (Linux) atau `.\.venv\Scripts\python.exe` (Windows).

### Langkah D: Instal Dependensi
Jalankan perintah berikut di terminal:
```bash
pip install -r requirements.txt
```

### Langkah E: Menjalankan Game
Jalankan game melalui file `main.py`:
```bash
python main.py
```
*(Jika aset belum digenerate sebelumnya, game akan otomatis memanggil `tools/generate_assets.py` saat pertama kali dijalankan).*

---

## 5. CARA KERJA KONTROL & COMPUTER VISION HSV

### A. Kontrol Utama: Gerakan Tangan Objek Biru (Directional Motion Detection)
Pemain mengendalikan arah mobil dengan menggerakkan objek berwarna biru di depan webcam (contoh: kartu biru, kain biru, sarung tangan, atau benda biru pekat).

Deteksi bekerja secara relatif (*swipe / directional displacement*):
- **Gerakkan tangan/objek biru ke Kanan ($\Delta x > +32\text{ px}$):** Mobil berpindah **satu jalur ke kanan**.
- **Gerakkan tangan/objek biru ke Kiri ($\Delta x < -32\text{ px}$):** Mobil berpindah **satu jalur ke kiri**.
- **Tangan diam / perlahan bergerak:** Mobil tetap berada di jalur saat ini tanpa berpindah sembarangan.

### B. Tahapan Pemrosesan Citra HSV:
1. **Frame Capture:** Frame dibaca secara asinkron dari kamera melalui `cv2.VideoCapture`.
2. **Horizontal Flip:** Frame dibalik secara horizontal (`cv2.flip(frame, 1)`) agar pergerakan tangan terasa seperti cermin.
3. **Color Space Conversion:** Frame dikonversi dari BGR ke HSV (`cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)`).
4. **Color Thresholding:** `cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)` menghasilkan binary mask di mana piksel biru bernilai 255 (putih) dan sisanya 0 (hitam).
5. **Morphological Opening & Closing:**
   - *Opening* (`MORPH_OPEN`, 5x5 kernel): Menghilangkan bintik-bintik noise kecil pada background.
   - *Closing* (`MORPH_CLOSE`, 5x5 kernel): Mengisi lubang-lubang kecil pada objek biru agar kontur menyatu.
6. **Contour Filtering:** Menghitung luas seluruh kontur dan memilih kontur terbesar yang luasnya melebihi `MIN_CONTOUR_AREA` (1000 px²).
7. **Centroid Moments Calculation:** Titik pusat massa dihitung menggunakan momen spasial:
   $$c_x = \frac{M_{10}}{M_{00}}, \quad c_y = \frac{M_{01}}{M_{00}}$$
8. **Relative Motion & Gesture Logic:**
   - **Baseline Reference:** Posisi awal tangan saat muncul dicatat sebagai acuan (`baseline_x`).
   - **Swipe Displacement:** Dihitung $\Delta x = c_x - \text{baseline}_x$.
   - **Gesture Cooldown (0,32 detik):** Setelah terjadi perpindahan satu jalur, sistem mengaktifkan jeda singkat agar gerakan satu ayunan tangan tidak menyebabkan mobil melompat berkali-kali.
   - **Baseline Drift:** Ketika tangan diam, posisi acuan perlahan mengikuti posisi tangan dengan faktor redaman sehingga gerakan halus tidak memicu perpindahan yang tidak diinginkan.
   - **Object Loss Preservation:** Jika objek biru hilang dari kamera, posisi mobil tetap terkunci di jalurnya.

### C. Kontrol Alternatif (Keyboard Fallback):
- **A** atau **Panah Kiri (←):** Pindah satu jalur ke kiri.
- **D** atau **Panah Kanan (→):** Pindah satu jalur ke kanan.
- **P** atau **ESC:** Pause / Resume permainan.
- **M:** Toggle tampilan webcam antara mode video asli dan mode **HSV Binary Mask**.
- **R:** Restart permainan saat Game Over.

---

## 6. KALIBRASI THRESHOLD HSV

Threshold warna biru diatur di dalam file [config.py](file:///home/rasyhaaa/Documents/Game_HSV/config.py):

```python
# Rentang HSV warna biru (H: 0-180, S: 0-255, V: 0-255)
LOWER_BLUE = np.array([90, 80, 50], dtype=np.uint8)
UPPER_BLUE = np.array([135, 255, 255], dtype=np.uint8)
```

### Tips Kalibrasi Berdasarkan Pencahayaan:
1. Tekan tombol **`M`** saat game berjalan untuk melihat **HSV Mask Preview** di panel kanan.
2. Jika objek biru Anda tampak bolong-bolong atau kurang putih penuh:
   - Turunkan nilai *Saturation* minimum (misal dari 80 ke 60).
   - Turunkan nilai *Value* minimum (misal dari 50 ke 40) jika ruangan sedikit redup.
3. Jika latar belakang ruangan (tembok/baju) ikut terdeteksi:
   - Naikkan nilai *Saturation* minimum (misal dari 80 ke 110).
   - Pastikan objek biru memiliki warna yang kontras dengan pakaian Anda.

---

## 7. MENJALANKAN PENGUJIAN OTOMATIS (UNIT TESTS)

Untuk memverifikasi seluruh komponen tanpa perlu membuka kamera:
```bash
python -m unittest discover -s tests -p "test_*.py"
```
Semua 13 pengujian (logika jalur, invulnerability, pergerakan pemain, algoritma fair spawn NPC, deteksi tabrakan, dan pemrosesan HSV sintetis) akan dijalankan secara otomatis.

---

## 8. TROUBLESHOOTING

| Gejala | Penyebab Umum | Solusi |
|---|---|---|
| **Webcam tidak terbuka / "NO WEBCAM DETECTED"** | Webcam digunakan aplikasi lain (Zoom, browser) atau indeks salah. | Tutup aplikasi lain yang memakai webcam. Jika memiliki webcam eksternal, ubah `WEBCAM_INDEX = 1` di `config.py`. Anda tetap dapat bermain menggunakan keyboard. |
| **Izin webcam di Linux** | User belum masuk ke grup `video`. | Jalankan perintah `sudo usermod -aG video $USER`, lalu restart terminal/sesi. |
| **Audio tidak bersuara di Linux** | Sistem audio ALSA/PulseAudio tidak aktif. | Game otomatis menonaktifkan audio secara aman tanpa crash jika audio server tidak ditemukan. |
| **Mobil tidak mau berpindah jalur** | Luas objek biru kurang dari `MIN_CONTOUR_AREA`. | Dekatkan objek biru ke kamera atau turunkan nilai `MIN_CONTOUR_AREA` di `config.py` (misal ke 800). |
=======
# Project-1-Mini-Game-Based-on-Hand-Color
Project 1 - Mini Game Based on Hand Color
>>>>>>> a3c6c10508770c8c9fdb559c8ff914626bd9265b
