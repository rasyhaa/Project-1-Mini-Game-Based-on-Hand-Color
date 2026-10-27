# Hand Tracking Car Dodge — HSV Blue Detection

Game arcade balapan mobil 2D dengan sudut pandang _top-down_. Pemain mengendalikan mobil menggunakan gerakan objek berwarna biru yang dideteksi melalui **HSV Color Segmentation** dengan OpenCV.

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
Berikut adalah demonstrasi gameplay selama 14 detik, yang menunjukkan sistem kontrol menggunakan deteksi warna biru berbasis HSV.

https://github.com/user-attachments/assets/bc43e23f-9ddd-4289-bda3-49bf3bc4a67c

### 3. Layar Game Over

![Layar Game Over](dokumentasi/dokum%20gameover.png)

## Fitur Utama

### 1. Sistem Tiga Jalur

Mobil pemain hanya bergerak di antara tiga jalur yang telah ditentukan:

- **Jalur Kiri**: 135 px
- **Jalur Tengah**: 305 px
- **Jalur Kanan**: 475 px

Posisi mobil disesuaikan dengan titik tengah jalur sehingga mobil tidak berhenti di antara dua jalur.

### 2. Kontrol dengan Deteksi Objek Biru

- Pemrosesan webcam dijalankan pada _background thread_ agar tidak menghambat rendering game.
- Frame webcam dibalik secara horizontal agar gerakan terasa seperti bercermin.
- Pemrosesan dilengkapi _morphological opening/closing_, perhitungan centroid, _temporal smoothing_, dan _cooldown_ untuk membantu mengurangi gangguan deteksi.
- Gerakan objek biru ke kiri atau kanan digunakan untuk memindahkan mobil satu jalur.

### 3. Gameplay dan Lalu Lintas

- Mobil NPC memiliki empat variasi sprite.
- NPC bergerak dari bagian atas ke bagian bawah layar.
- Algoritma _fair spawn_ dirancang agar tidak semua jalur tertutup secara bersamaan.
- Kepadatan dan kecepatan NPC meningkat seiring waktu dan skor.

### 4. Nyawa dan Efek Tabrakan

- Pemain memulai permainan dengan tiga nyawa.
- Tabrakan mengurangi satu nyawa dan memunculkan efek partikel serta suara benturan.
- Periode _invulnerability_ selama sekitar 1,3 detik membantu mencegah satu tabrakan mengurangi beberapa nyawa sekaligus.

### 5. Dashboard dan Preview Webcam

Panel di sisi kanan layar menampilkan preview webcam, pembagian zona, kontur objek biru, titik centroid, dan status deteksi. Tombol `M` digunakan untuk mengganti preview antara video asli dan _HSV binary mask_.

### 6. Keyboard Fallback dan Skor

- Jika webcam tidak tersedia, game menyediakan kontrol keyboard sebagai alternatif.
- Skor bertambah berdasarkan waktu bertahan dan NPC yang berhasil dilewati.
- _High score_ disimpan secara lokal di `assets/highscore.json`.

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

## Kontrol Permainan

- **Gerakkan objek biru ke kanan**: Pindah satu jalur ke kanan
- **Gerakkan objek biru ke kiri**: Pindah satu jalur ke kiri
- **`A` atau `←`**: Pindah satu jalur ke kiri (keyboard fallback)
- **`D` atau `→`**: Pindah satu jalur ke kanan (keyboard fallback)
- **`P` atau `Esc`**: Pause / resume permainan
- **`R`**: Restart permainan saat Game Over
- **`Enter` atau `Space`**: Mulai game saat berada di Menu Utama

Untuk kontrol berbasis warna, arahkan objek biru yang kontras—misalnya kartu, kain, atau sarung tangan—ke area yang terlihat oleh webcam. Gerakkan objek ke kiri atau kanan untuk berpindah jalur.

## Cara Kerja Deteksi HSV

Proses deteksi objek biru secara umum terdiri dari langkah berikut:

1. **Pengambilan frame:** Frame dibaca dari webcam menggunakan `cv2.VideoCapture`.
2. **Horizontal flip:** Frame dibalik dengan `cv2.flip(frame, 1)` agar gerakan terlihat seperti cermin.
3. **Konversi warna:** Frame diubah dari BGR ke HSV menggunakan `cv2.cvtColor`.
4. **Thresholding:** `cv2.inRange()` membuat _binary mask_ berdasarkan rentang HSV yang ditentukan.
5. **Operasi morfologi:** _Opening_ membantu mengurangi noise kecil, sedangkan _closing_ membantu menyambungkan bagian objek yang terputus.
6. **Penyaringan kontur:** Kontur dievaluasi berdasarkan luas minimum.
7. **Perhitungan centroid:** Titik pusat objek dihitung menggunakan momen spasial:

   \[
   c*x = \frac{M*{10}}{M*{00}}, \qquad
   c_y = \frac{M*{01}}{M\_{00}}
   \]

8. **Deteksi gerakan:** Perubahan posisi horizontal objek digunakan untuk menentukan arah perpindahan mobil. _Cooldown_ membantu mencegah satu gerakan terhitung berkali-kali.

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
2. Jika objek biru tampak terputus atau tidak terdeteksi penuh, coba turunkan batas minimum _saturation_ atau _value_ secara bertahap.
3. Jika latar belakang ikut terdeteksi, coba naikkan batas minimum _saturation_ atau sesuaikan rentang hue.
4. Gunakan objek biru yang kontras dengan lingkungan dan hindari pencahayaan yang berubah-ubah.

## Troubleshooting

- **Webcam tidak terbuka**
  - _Kemungkinan penyebab_: Webcam sedang digunakan oleh aplikasi lain atau indeks kamera di sistem tidak sesuai.
  - _Solusi_: Tutup aplikasi lain yang mengakses webcam, lalu periksa pengaturan indeks kamera (`WEBCAM_INDEX`) di `game/config.py`.

- **Tidak ada izin akses webcam di Linux**
  - _Kemungkinan penyebab_: Pengguna belum memiliki izin akses ke perangkat video.
  - _Solusi_: Tambahkan pengguna ke grup video dengan perintah `sudo usermod -aG video $USER`, lalu logout dan masuk kembali ke sesi sistem.

- **Mobil tidak berpindah jalur**
  - _Kemungkinan penyebab_: Objek biru tidak terdeteksi, pencahayaan kurang, atau luas kontur di bawah batas minimum.
  - _Solusi_: Dekatkan objek ke webcam, perbaiki pencahayaan ruangan, atau sesuaikan nilai `MIN_CONTOUR_AREA` dan rentang HSV di `game/config.py`.

- **Banyak objek lain ikut terdeteksi**
  - _Kemungkinan penyebab_: Warna latar belakang atau pakaian mirip dengan warna target.
  - _Solusi_: Gunakan objek biru yang lebih pekat dan kontras dengan latar belakang, atau persempit rentang warna HSV di `game/config.py`.

- **Dependensi gagal dipasang**
  - _Kemungkinan penyebab_: Versi Python tidak kompatibel atau virtual environment belum aktif.
  - _Solusi_: Pastikan virtual environment telah diaktifkan dan gunakan Python 3.12 dengan dependensi di `requirements.txt`.

---

## Author

**Muhammad Rasyha Syauqi Islam (5024241066)**  
