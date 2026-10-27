# Hand Tracking Car Dodge — HSV Blue Detection

Game arcade balapan mobil 2D dengan sudut pandang *top-down*. Pemain mengendalikan mobil menggunakan gerakan objek berwarna biru yang dideteksi melalui **HSV Color Segmentation** dengan OpenCV.

> **Pendekatan computer vision:** Proyek ini menggunakan teknik computer vision klasik, yaitu color thresholding, morphological operations, contour detection, dan image moments. Proyek ini tidak menggunakan MediaPipe, machine learning, atau deep learning.

## Daftar Isi

- [Dokumentasi Permainan](#dokumentasi-permainan)
- [Fitur Utama](#fitur-utama)
- [Struktur Proyek](#struktur-proyek)
- [Persyaratan Sistem](#persyaratan-sistem)
- [Instalasi](#instalasi)
- [Menjalankan Game](#menjalankan-game)
- [Kontrol Permainan](#kontrol-permainan)
- [Cara Kerja Deteksi HSV](#cara-kerja-deteksi-hsv)
- [Kalibrasi HSV](#kalibrasi-hsv)
- [Troubleshooting](#troubleshooting)

## Dokumentasi Permainan

Berikut adalah tampilan antarmuka visual dari game:

### 1. Menu Utama (Home Screen)
![Menu Utama](dokumentasi/dokum%20home.png)

### 2. Gameplay (Saat Permainan Berlangsung)
![Gameplay Permainan](dokumentasi/dokum%20game.png)

### 3. Layar Game Over
![Layar Game Over](dokumentasi/dokum%20gameover.png)

## Fitur Utama

### 1. Sistem Tiga Jalur

Mobil pemain hanya bergerak di antara tiga jalur yang telah ditentukan:

| Jalur | Posisi X |
|---|---:|
| Kiri | 135 px |
| Tengah | 305 px |
| Kanan | 475 px |

Posisi mobil disesuaikan dengan titik tengah jalur sehingga mobil tidak berhenti di antara dua jalur.

### 2. Kontrol dengan Deteksi Objek Biru

- Pemrosesan webcam dijalankan pada *background thread* agar tidak menghambat rendering game.
- Frame webcam dibalik secara horizontal agar gerakan terasa seperti bercermin.
- Pemrosesan dilengkapi *morphological opening/closing*, perhitungan centroid, *temporal smoothing*, dan *cooldown* untuk membantu mengurangi gangguan deteksi.
- Gerakan objek biru ke kiri atau kanan digunakan untuk memindahkan mobil satu jalur.

### 3. Gameplay dan Lalu Lintas

- Mobil NPC memiliki empat variasi sprite.
- NPC bergerak dari bagian atas ke bagian bawah layar.
- Algoritma *fair spawn* dirancang agar tidak semua jalur tertutup secara bersamaan.
- Kepadatan dan kecepatan NPC meningkat seiring waktu dan skor.

### 4. Nyawa dan Efek Tabrakan

- Pemain memulai permainan dengan tiga nyawa.
- Tabrakan mengurangi satu nyawa dan memunculkan efek partikel serta suara benturan.
- Periode *invulnerability* selama sekitar 1,3 detik membantu mencegah satu tabrakan mengurangi beberapa nyawa sekaligus.

### 5. Dashboard dan Preview Webcam

Panel di sisi kanan layar menampilkan preview webcam, pembagian zona, kontur objek biru, titik centroid, dan status deteksi. Tombol `M` digunakan untuk mengganti preview antara video asli dan *HSV binary mask*.

### 6. Keyboard Fallback dan Skor

- Jika webcam tidak tersedia, game menyediakan kontrol keyboard sebagai alternatif.
- Skor bertambah berdasarkan waktu bertahan dan NPC yang berhasil dilewati.
- *High score* disimpan secara lokal di `assets/highscore.json`.

## Struktur Proyek

```text
Game_HSV/
├── assets/
│   ├── backgrounds/
│   ├── cars/
│   ├── ui/
│   └── highscore.json
├── dokumentasi/
│   ├── dokum home.png
│   ├── dokum game.png
│   └── dokum gameover.png
├── game/
│   ├── assets.py
│   ├── camera.py
│   ├── config.py
│   ├── entities.py
│   ├── game.py
│   └── particles.py
├── main.py
├── README.md
└── requirements.txt
```

## Persyaratan Sistem

- **Sistem operasi:** Linux (termasuk Fedora, Ubuntu, Debian, atau Arch) atau Windows 10/11.
- **Python:** Python 3.12 direkomendasikan.
- **Webcam:** Webcam bawaan laptop atau webcam USB untuk kontrol berbasis warna.
- **Pustaka Python:**
  - `pygame >= 2.6.0`
  - `opencv-python >= 4.8.0`
  - `numpy >= 1.26.0`

Versi pustaka yang digunakan sebaiknya mengikuti `requirements.txt` di repository.

## Instalasi

### 1. Clone Repository

```bash
git clone https://github.com/rasyhaa/Project-1-Mini-Game-Based-on-Hand-Color.git
cd Project-1-Mini-Game-Based-on-Hand-Color
```

Jika kamu sudah memiliki folder proyek lokal, buka folder tersebut dan lewati langkah clone.

### 2. Buat Virtual Environment

**Linux (Fedora/Ubuntu/Debian):**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Jika PowerShell menolak aktivasi karena kebijakan eksekusi, gunakan Command Prompt:

```bat
.venv\Scripts\activate.bat
```

### 3. Instal Dependensi

Pastikan virtual environment sudah aktif, lalu jalankan:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Pilih Python Interpreter di VS Code

1. Buka Command Palette dengan `Ctrl + Shift + P`.
2. Pilih **Python: Select Interpreter**.
3. Pilih interpreter dari `.venv` di folder proyek.

## Menjalankan Game

Jalankan perintah berikut dari direktori utama proyek:

```bash
python main.py
```

Jika aset belum tersedia, ikuti mekanisme pembuatan aset yang disediakan proyek, misalnya melalui `tools/generate_assets.py`.

## Kontrol Permainan

| Tombol / Gerakan | Fungsi |
|---|---|
| Gerakkan objek biru ke kanan | Pindah satu jalur ke kanan |
| Gerakkan objek biru ke kiri | Pindah satu jalur ke kiri |
| `A` atau `←` | Pindah satu jalur ke kiri |
| `D` atau `→` | Pindah satu jalur ke kanan |
| `P` atau `Esc` | Pause/resume permainan |
| `M` | Ganti preview webcam dan HSV binary mask |
| `R` | Restart saat Game Over |

Untuk kontrol berbasis warna, arahkan objek biru yang kontras—misalnya kartu, kain, atau sarung tangan—ke area yang terlihat oleh webcam. Gerakkan objek ke kiri atau kanan untuk berpindah jalur.

## Cara Kerja Deteksi HSV

Proses deteksi objek biru secara umum terdiri dari langkah berikut:

1. **Pengambilan frame:** Frame dibaca dari webcam menggunakan `cv2.VideoCapture`.
2. **Horizontal flip:** Frame dibalik dengan `cv2.flip(frame, 1)` agar gerakan terlihat seperti cermin.
3. **Konversi warna:** Frame diubah dari BGR ke HSV menggunakan `cv2.cvtColor`.
4. **Thresholding:** `cv2.inRange()` membuat *binary mask* berdasarkan rentang HSV yang ditentukan.
5. **Operasi morfologi:** *Opening* membantu mengurangi noise kecil, sedangkan *closing* membantu menyambungkan bagian objek yang terputus.
6. **Penyaringan kontur:** Kontur dievaluasi berdasarkan luas minimum.
7. **Perhitungan centroid:** Titik pusat objek dihitung menggunakan momen spasial:

   \[
   c_x = \frac{M_{10}}{M_{00}}, \qquad
   c_y = \frac{M_{01}}{M_{00}}
   \]

8. **Deteksi gerakan:** Perubahan posisi horizontal objek digunakan untuk menentukan arah perpindahan mobil. *Cooldown* membantu mencegah satu gerakan terhitung berkali-kali.

## Kalibrasi HSV

Rentang HSV dapat disesuaikan pada konfigurasi proyek di `game/config.py`.

Contoh rentang warna biru:

```python
LOWER_BLUE = np.array([90, 80, 50], dtype=np.uint8)
UPPER_BLUE = np.array([135, 255, 255], dtype=np.uint8)
```

Nilai tersebut merupakan titik awal dan mungkin perlu disesuaikan berdasarkan pencahayaan, kamera, dan warna objek.

### Tips Kalibrasi

1. Jalankan game dan gerakkan objek biru di depan webcam.
2. Jika objek biru tampak terputus atau tidak terdeteksi penuh, coba turunkan batas minimum *saturation* atau *value* secara bertahap.
3. Jika latar belakang ikut terdeteksi, coba naikkan batas minimum *saturation* atau sesuaikan rentang hue.
4. Gunakan objek biru yang kontras dengan lingkungan dan hindari pencahayaan yang berubah-ubah.

## Troubleshooting

| Masalah | Kemungkinan penyebab | Solusi |
|---|---|---|
| Webcam tidak terbuka | Webcam digunakan aplikasi lain atau indeks kamera tidak sesuai | Tutup aplikasi lain yang menggunakan webcam. Periksa pengaturan indeks kamera di `config.py`. |
| Tidak ada izin webcam di Linux | Izin perangkat belum sesuai | Periksa izin perangkat dan konfigurasi grup pengguna. Jika perlu, tambahkan pengguna ke grup `video`, lalu masuk kembali ke sesi. |
| Audio tidak terdengar | Perangkat atau layanan audio tidak tersedia | Periksa pengaturan audio sistem dan output audio yang digunakan. |
| Mobil tidak berpindah jalur | Objek biru tidak terdeteksi atau luas kontur di bawah batas minimum | Perbaiki pencahayaan, dekatkan objek ke kamera, atau sesuaikan parameter HSV dan luas kontur di konfigurasi. |
| Banyak objek lain ikut terdeteksi | Warna latar belakang mirip dengan objek target | Sesuaikan rentang HSV dan gunakan objek biru yang lebih kontras. |
| Dependensi gagal dipasang | Versi Python atau pustaka tidak cocok | Pastikan virtual environment aktif dan gunakan versi dependensi yang sesuai dengan `requirements.txt`. |

---

## Kredit dan Catatan

Proyek ini dibuat sebagai **Project 1 — Mini Game Based on Hand Color**, dengan pendekatan computer vision klasik menggunakan OpenCV dan gameplay 2D menggunakan Pygame.

Pastikan dokumentasi dan struktur folder diperbarui apabila implementasi proyek berubah.
