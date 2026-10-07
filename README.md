# 🎫 TiketKu - Aplikasi Tiket Konser Anti-Calo

Aplikasi web sederhana untuk penjualan tiket konser/event. Setiap tiket
ditandatangani secara digital menggunakan **RSA yang diimplementasikan manual**
(tanpa library kriptografi), sehingga data tiket yang diubah atau dipalsukan
akan langsung terdeteksi di pintu masuk.

Bagi pengguna, aplikasi ini hanya terlihat seperti situs beli tiket biasa:
mereka cuma menerima kode pendek seperti `TKT-7K3M-9QXA`. Proses RSA berjalan
di balik layar.

## Fitur

- **Beli tiket**: pengguna mengisi nama, memilih event dan kategori, lalu mendapat kode tiket pendek.
- **Verifikasi di pintu masuk**: petugas memasukkan kode tiket, sistem menampilkan valid atau tidak.
- **Anti tiket palsu**: kode yang ditebak/dibuat sendiri tidak ditemukan, dan data tiket yang dimanipulasi (misalnya Regular menjadi VIP) gagal verifikasi tanda tangan.
- **Anti pemakaian ganda**: tiket yang sudah dipakai tidak bisa dipakai lagi.
- **Halaman admin (demo)**: menampilkan nilai n, e, dan d untuk keperluan presentasi.

## Alur Aplikasi

1. **Beli tiket**: server membuat ID acak 8 karakter, menyusun data
   `ID|nama|event|kategori`, menandatanganinya dengan private key RSA, lalu
   menyimpan data + tanda tangan di `tickets.json`. User hanya menerima kode
   pendek dari ID tersebut.
2. **Pintu masuk**: server mencari tiket berdasarkan kode, memverifikasi tanda
   tangan dengan public key RSA, lalu menandai tiket sebagai sudah dipakai.

---

## Penjelasan RSA Secara Bertahap

RSA adalah algoritma kriptografi **asimetris**: ada dua kunci yang saling
berpasangan.

- **Public key** `(e, n)`: boleh diketahui siapa saja, dipakai untuk **verifikasi**.
- **Private key** `(d, n)`: hanya dipegang panitia, dipakai untuk **menandatangani**.

Keamanannya bertumpu pada fakta bahwa mengalikan dua bilangan prima besar itu
mudah, tetapi memfaktorkan hasilnya kembali menjadi `p` dan `q` itu sangat sulit.

### Bagian A - Pembuatan Kunci (`generate_keys` di `rsa.py`)

**Langkah 1 - Pilih dua bilangan prima besar `p` dan `q`.**
Program membuat bilangan acak 512-bit lalu mengujinya dengan **tes Miller-Rabin**
(`is_prime`) sampai ketemu bilangan prima (`generate_prime`).

**Langkah 2 - Hitung modulus `n`.**

```
n = p × q
```

`n` adalah bagian dari public key maupun private key. Dengan p dan q masing-masing
512-bit, `n` berukuran 1024-bit.

**Langkah 3 - Hitung `φ(n)` (Euler's totient).**

```
φ(n) = (p − 1) × (q − 1)
```

**Langkah 4 - Pilih eksponen publik `e`.**
Program memakai `e = 65537`, lalu memastikan `gcd(e, φ(n)) = 1` (fungsi `gcd`).
Jika tidak, `p` dan `q` dibuat ulang.

**Langkah 5 - Hitung eksponen privat `d`.**
`d` adalah invers modular dari `e` terhadap `φ(n)`:

```
d × e ≡ 1 (mod φ(n))
```

Dihitung dengan **Extended Euclidean Algorithm** (`egcd` dan `mod_inverse`).

**Hasil:**

```
Public key  = (e, n)
Private key = (d, n)     ← p, q, φ(n) dibuang/dirahasiakan
```

### Bagian B - Operasi Inti: Perpangkatan Modular (`mod_pow`)

Semua proses RSA berujung pada satu operasi:

```
hasil = basis ^ eksponen mod n
```

Karena eksponennya bisa sangat besar (ratusan digit), program memakai
**square-and-multiply**: eksponen dibaca bit demi bit, sehingga cukup ~1024 kali
kuadrat dan perkalian, bukan triliunan perkalian. Fungsi `pow()` bawaan Python tidak dipakai.

### Bagian C - Menandatangani Tiket (`sign`, dipanggil saat beli tiket)

**Langkah 1 - Susun data tiket.**

```
payload = "K7M3Q9XA|Budi|Konser Nusantara 2026|VIP"
```

**Langkah 2 - Hash data tiket dengan SHA-256.**

```
h = SHA256(payload)      → bilangan 256-bit
```

Hash membuat data berapa pun panjangnya menjadi bilangan kecil yang pasti
lebih kecil dari `n`. Mengubah satu karakter saja pada data menghasilkan hash yang sama sekali berbeda.

**Langkah 3 - "Enkripsi" hash dengan private key.**

```
signature = h ^ d mod n
```

Hanya pemegang `d` (panitia) yang bisa menghasilkan nilai ini.

**Langkah 4 - Simpan.**
`payload` dan `signature` disimpan di `tickets.json`. User hanya mendapat ID pendek.

### Bagian D - Memverifikasi Tiket (`verify`, dipanggil di pintu masuk)

**Langkah 1 - Cari tiket** berdasarkan kode yang dimasukkan petugas, lalu ambil `payload` dan `signature`-nya.

**Langkah 2 - Hash ulang `payload`:**

```
h_baru = SHA256(payload)
```

**Langkah 3 - Buka tanda tangan dengan public key:**

```
h_asli = signature ^ e mod n
```

**Langkah 4 - Bandingkan.**

```
h_asli == h_baru  →  tiket valid
h_asli != h_baru  →  data diubah / tanda tangan palsu, tiket ditolak
```

Jika seseorang mengubah `VIP` menjadi `Regular` (atau sebaliknya) di `tickets.json`,
`h_baru` berubah sedangkan `signature` tetap, sehingga keduanya tidak cocok.
Orang tersebut juga tidak bisa membuat tanda tangan baru karena tidak punya `d`.

### Mengapa Cara Ini Berhasil (Bukti Singkat)

Karena `d × e ≡ 1 (mod φ(n))`, maka:

```
(h ^ d) ^ e mod n  =  h ^ (d×e) mod n  =  h
```

Artinya apa yang "dikunci" dengan `d` bisa "dibuka" dengan `e`, dan sebaliknya.

### Contoh Angka Kecil

Kunci kecil agar mudah dihitung manual (aplikasi asli memakai 1024-bit):

| Langkah | Perhitungan | Hasil |
|---|---|---|
| Pilih prima | p = 61, q = 53 | |
| Hitung n | 61 × 53 | **n = 3233** |
| Hitung φ(n) | 60 × 52 | **φ(n) = 3120** |
| Pilih e | gcd(17, 3120) = 1 | **e = 17** |
| Hitung d | 17 × d ≡ 1 (mod 3120) | **d = 2753** (cek: 17 × 2753 = 46801 = 15 × 3120 + 1) |

Misalkan hash data tiket bernilai `h = 65`:

```
Sign    : signature = 65 ^ 2753 mod 3233 = 588
Verify  : 588 ^ 17 mod 3233             = 65   ✔ sama dengan h → VALID
```

Kalau data diubah sehingga hash-nya menjadi, misalnya, 66, maka `66 ≠ 65` → **DITOLAK**.

Untuk enkripsi pesan (bukan tanda tangan), arahnya dibalik:

```
Enkripsi : 65 ^ 17 mod 3233   = 2790   (pakai public key)
Dekripsi : 2790 ^ 2753 mod 3233 = 65   (pakai private key)
```

Fungsi `encrypt_int` dan `decrypt_int` di `rsa.py` mengimplementasikan ini untuk demo.

---

## Struktur File

```
tiket-antic-calo/
├── app.py          # Web app Flask (halaman beli tiket, gate, admin)
├── rsa.py          # Implementasi RSA manual
├── keys.json       # Kunci RSA, dibuat otomatis saat pertama dijalankan
├── tickets.json    # Data tiket + tanda tangan, dibuat otomatis
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

1. Buka halaman **Beli Tiket**, isi data, lalu klik **Beli Tiket**. Akan muncul kode seperti `TKT-7K3M-9QXA`.
2. Buka halaman **Pintu Masuk**, masukkan kodenya, lalu klik **Verifikasi**. Hasilnya: tiket valid.
3. Masukkan kode yang sama sekali lagi, hasilnya: tiket sudah pernah dipakai.
4. Masukkan kode asal-asalan, hasilnya: tiket tidak ditemukan.
5. **Uji manipulasi data:** beli tiket baru, buka `tickets.json`, ubah `Regular` menjadi `VIP` pada `payload`, lalu verifikasi tiket tersebut. Hasilnya: data tiket tidak valid / sudah diubah.

### Mencoba dari HP (opsional)

Pastikan laptop dan HP terhubung ke WiFi yang sama. Ubah baris terakhir `app.py` menjadi:

```python
app.run(host="0.0.0.0", debug=True)
```

Lalu buka `http://IP-LAPTOP:5000` dari browser HP.

## Catatan

- Hapus `keys.json` dan `tickets.json` jika ingin mulai dari awal (kunci baru, tiket lama hilang).
- Verifikasi bergantung pada data di server, sehingga tiket tidak bisa dicek offline hanya dari kodenya.
- Aplikasi ini dibuat untuk keperluan tugas/pembelajaran. Untuk sistem produksi, gunakan library kriptografi standar dan padding seperti RSA-PSS.
