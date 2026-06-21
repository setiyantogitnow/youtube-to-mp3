# Under the Hood: YouTube-to-MP3 Downloader

Dokumentasi ini menjelaskan bagaimana komponen-komponen aplikasi bekerja secara terintegrasi, mulai dari interaksi pengguna di frontend hingga file MP3 tersimpan di penyimpanan lokal.

## 🛠️ Komponen Utama
- **Frontend:** `/static/index.html` (HTML/Vanilla JS)
- **Backend Orchestrator:** `main.py` (Flask)
- **Core Engine:** `app/downloader.py` (yt-dlp & FFmpeg)

---

## 🗺️ Mapping Alur Kerja

### Tahap 1: Trigger & Request (Frontend)
**Lokasi:** `/static/index.html`
- **Aksi:** Pengguna menginput URL, memilih mode/kualitas, dan mengklik tombol "Mulai Unduh".
- **Baris Kode Kunci:** 
  - `line 85-104`: Fungsi `downloadBtn.onclick` menggunakan `fetch('/download', ...)` untuk mengirim data dalam format JSON (URL, mode, kualitas) melalui HTTP POST ke server.
- **Hasil:** Request terkirim ke backend.

### Tahap 2: Penerimaan & Instruksi (Backend Orchestrator)
**Lokasi:** `main.py`
- **Aksi:** Server menerima request dan mengarahkan proses ke fungsi yang tepat.
- **Baris Kode Kunci:**
  - `line 15-20`: `@app.route('/download', methods=['POST'])` menangkap request dari frontend.
  - `line 25`: `result = download_media(...)` meneruskan parameter input ke modul downloader untuk diproses lebih lanjut.
- **Hasil:** Instruksi pengunduhan diteruskan ke Core Engine.

### Tahap 3: Pengunduhan & Konversi (Core Engine)
**Lokasi:** `app/downloader.py`
- **Aksi:** Pengambilan data stream dari YouTube dan konversi menjadi format audio/video.
- **Baris Kode Kunci:**
  - `line 15-25`: `ydl_opts` menentukan "resep" konversi. Penggunaan `FFmpegExtractAudio` sangat krusial karena YouTube tidak menyediakan file .mp3 asli. FFmpeg akan melakukan transcoding dari format stream (.webm/.m4a) menjadi .mp3.
  - `line 45`: `ydl.extract_info(url, download=True)` adalah eksekusi utama yang melakukan koneksi ke server YouTube dan menarik data binary.
  - `line 50`: `re.sub(r'\.[^.]+$', '.mp3', filename)` memastikan hasil akhir memiliki ekstensi file yang benar.
- **Hasil:** File `.mp3` atau `.mp4` fisik tersimpan di folder `/home/hika/youtube-to-mp3/downloads`.

### Tahap 4: Pengiriman File (Delivery)
**Lokasi:** `main.py` $\rightarrow$ Browser
- **Aksi:** Memberikan akses download file yang telah selesai diproses.
- **Baris Kode Kunci:**
  - `main.py (line 32)`: Mengirimkan link unik `/download_file/{filename}` kembali ke frontend.
  - `main.py (line 38-40)`: `@app.route('/download_file/<filename>')` menggunakan `send_from_directory` dengan `as_attachment=True` untuk memicu dialog "Save As" di browser pengguna.
- **Hasil:** File berpindah dari server ke penyimpanan lokal pengguna.

---

## ⚡ Analisis Proses Kompleks: Transcoding Audio
Salah satu bagian paling rumit adalah penggunaan **Post-Processor FFmpeg** di `app/downloader.py`:
```python
'postprocessors': [{
    'key': 'FFmpegExtractAudio',
    'preferredcodec': 'mp3',
    'preferredquality': quality,
}],
```
**Proses di balik layar:**
1. `yt-dlp` mengunduh file audio dalam format asli YouTube (misal: WebM).
2. `yt-dlp` memanggil software eksternal **FFmpeg**.
3. FFmpeg mengekstrak audio dari kontainer WebM.
4. FFmpeg melakukan kompresi ulang (transcoding) menjadi format MP3 dengan bitrate yang ditentukan (128/192/320kbps).
5. File asli yang mentah dihapus, menyisakan file `.mp3` yang kompatibel dengan berbagai perangkat.
