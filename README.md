# File program berada di branch master.

# Deskripsi 

Proyek ini merupakan aplikasi berbasis Flask yang menggunakan kamera/webcam sebagai alat untuk mendeteksi tingkat fokus dari penggunanya. Aplikasi ini memanfaatkan dlib untuk mendeteksi wajah dan fitur landmark, serta menghitung durasi pengguna dalam keadaan focus atau tidak berdasarkan Eye Aspect Ratio (EAR).

# Fitur:
1. Deteksi Wajah
Program akan mendeteksi wajah pengguna apakah sedang fokus atau tidak.
2. Deteksi mata
Program akan mendeteksi mata pengguna apakah tertutup atau tidak. Jika tertutup lebih dari 5 detik maka pengguna tidak fokus.
3. Menampilkan statistik hasil dari tingkat fokus pengguna seperti: 
    - Jumlah kejadian tidak fokus.
    - Tingkat fokus pengguna.
    - Rata-rata durasi tidak fokus.
    - Ringkasan performa fokus pengguna.
    - Rekomendasi peningkatan untuk pengguna.
    - Log Waktu tidak fokus.

# Teknologi yang digunakan:
- Flask: Framework Python untuk aplikasi web.
- OpenCV: untuk pengolahan gambar dan video.
- dlib: Untuk deteksi wajah dan landmark.
- HTML/CSS/Javascripts: Untuk antarmuka pengguna.

# Instalasi:
1. Pastikan anda telah mendownload python, OpenCV, dlib dan framework flask.
2. Masuk ke direktori proyek.
3. cd fokus-deteksi.
4. Download file dari model shape_predictor_68_face_landmarks.dat dari GitHub.
5. Kemudian jalankan server Flask dan akses http://127.0.0.1:5000.

# File:
- app.py logika Utama dari aplikasi.
- templates/index.html: Halaman Utama untuk focus detector.
- templates/result.html : halaman untuk statistik hasil deteksi fokus pengguna.
- static/style.css : CSS untuk halaman website.
- Javascripts: program javascripts untuk html dan css.

Maaf pak karena filenya berada di branch master, saya tidak mengerti memindahkannya ke branch main.
