# 🎫 TiketKu - Aplikasi Tiket Konser Anti-Calo

Aplikasi web sederhana untuk penjualan tiket konser/event. Setiap tiket
ditandatangani secara digital menggunakan **RSA yang diimplementasikan manual**
(tanpa library kriptografi), sehingga tiket palsu atau tiket yang datanya
diubah akan langsung terdeteksi di pintu masuk.

Bagi pengguna, aplikasi ini hanya terlihat seperti situs beli tiket biasa.
Proses RSA berjalan di balik layar.

## Fitur

- **Beli tiket**: pengguna mengisi nama, memilih event dan kategori, lalu mendapat kode tiket.
- **Verifikasi di pintu masuk**: petugas memasukkan kode tiket, sistem menampilkan valid atau tidak.
- **Anti tiket palsu**: kode tiket yang dibuat sendiri atau diubah isinya (misalnya Regular menjadi VIP) ditolak.
- **Anti pemakaian ganda**: tiket yang sudah dipakai tidak bisa dipakai lagi.
- **Halaman admin (demo)**: menampilkan nilai n, e, dan d untuk keperluan presentasi.

## Cara Kerja

1. Saat pertama dijalankan, sistem membuat sepasang kunci RSA 1024-bit
   (public key dan private key panitia) dan menyimpannya di `keys.json`.
2. **Beli tiket**: data tiket (`ID|nama|event|kategori`) di-hash dengan SHA-256,
   lalu hash tersebut ditandatangani dengan **private key**:
   `signature = hash^d mod n`.
   Kode tiket = data tiket (base64) + tanda tangan.
3. **Verifikasi**: sistem menghitung `signature^e mod n` dengan **public key**
   dan membandingkannya dengan hash data tiket. Jika sama, tiket asli.
   Jika data diubah sedikit saja, hash berubah dan tiket ditolak.

## Struktur File

```
tiket-antic-calo/
├── app.py        # Web app Flask (halaman beli tiket, gate, admin)
├── rsa.py        # Implementasi RSA manual
├── keys.json     # Dibuat otomatis saat pertama dijalankan
└── README.md
```

### Isi `rsa.py`

| Fungsi | Kegunaan |
|---|---|
| `gcd`, `egcd`, `mod_inverse` | GCD dan Extended Euclidean untuk mencari kunci private `d` |
| `mod_pow` | Perpangkatan modular cepat (square-and-multiply) |
| `is_prime`, `generate_prime` | Tes primalitas Miller-Rabin dan pembuatan bilangan prima |
| `generate_keys` | Membuat kunci `(n, e, d)` |
| `sign`, `verify` | Tanda tangan digital dan verifikasinya |
| `encrypt_int`, `decrypt_int` | Enkripsi dan dekripsi RSA (untuk demo) |

> `hashlib` hanya dipakai untuk SHA-256 (fungsi hash, bukan RSA). Seluruh proses RSA ditulis manual.

## Cara Menjalankan

### Kebutuhan
- Python 3.8 atau lebih baru
- Flask

### Langkah-langkah (VS Code)

1. Buka folder `tiket-antic-calo` di VS Code (File > Open Folder).
2. Buka terminal (`Ctrl + ~`), lalu install Flask:
   ```
   pip install flask
   ```
3. Jalankan aplikasi:
   ```
   python app.py
   ```
4. Buka browser dan akses alamat berikut:

| Halaman | Alamat |
|---|---|
| Beli tiket | http://127.0.0.1:5000 |
| Pintu masuk (verifikasi) | http://127.0.0.1:5000/gate |
| Info RSA (demo) | http://127.0.0.1:5000/admin |

### Cara Mencoba

1. Buka halaman **Beli Tiket**, isi data, lalu klik **Beli Tiket**.
2. Salin kode tiket yang muncul.
3. Buka halaman **Pintu Masuk**, tempel kodenya, lalu klik **Verifikasi**. Hasilnya: tiket valid.
4. Tempel kode yang sama sekali lagi, hasilnya: tiket sudah pernah dipakai.
5. Ubah satu karakter pada kode tiket lalu verifikasi, hasilnya: tiket palsu.

### Mencoba dari HP (opsional)

Pastikan laptop dan HP terhubung ke WiFi yang sama. Ubah baris terakhir `app.py` menjadi:

```python
app.run(host="0.0.0.0", debug=True)
```

Lalu buka `http://IP-LAPTOP:5000` dari browser HP.

## Catatan

- Hapus `keys.json` jika ingin membuat pasangan kunci baru (tiket lama menjadi tidak valid).
- Daftar tiket yang sudah dipakai disimpan di memori, sehingga akan reset saat server di-restart.
- Aplikasi ini dibuat untuk keperluan tugas/pembelajaran. Untuk sistem produksi, gunakan library kriptografi standar dan padding seperti RSA-PSS.