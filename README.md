# LAPORAN TUGAS KRIPTOGRAFI: IMPLEMENTASI ALGORITMA RSA
## STUDI KASUS: APLIKASI TIKET KONSER ANTI-CALO (DIGITAL SIGNATURE)

---

### IDENTITAS KELOMPOK
* **Mata Kuliah:** Kriptografi
* **Semester:** 5 (Tahun Ajaran 2024/2025)
* **Kelompok:** Kelompok [Nomor Kelompok]
* **Anggota Kelompok:**
  1. Mohamad Arkan (NRP: [Isi NRP Anda])
  2. [Nama Anggota 2] (NRP: [Isi NRP Anggota 2])
* **Departemen/Program Studi:** S-1 Teknologi Informasi
* **Fakultas:** Fakultas Teknologi Elektro dan Informatika Cerdas (FTEIC)
* **Institusi:** Institut Teknologi Sepuluh Nopember (ITS) Surabaya

---

## BAB I: PENDAHULUAN

### 1.1 Latar Belakang
Dalam perkembangan keamanan informasi dan komunikasi digital modern, teknik kriptografi memegang peranan fundamental dalam menjaga kerahasiaan (*confidentiality*), integritas data (*integrity*), autentikasi (*authentication*), dan nirpenyangkalan (*non-repudiation*). Salah satu tonggak terpenting dalam sejarah kriptografi modern adalah penemuan sistem kriptografi kunci-publik (*asymmetric-key cryptography*) oleh Ron Rivest, Adi Shamir, dan Leonard Adleman pada tahun 1977 di Massachusetts Institute of Technology (MIT), yang dikenal secara luas dengan nama **Algoritma RSA**.

Berbeda dengan kriptografi simetris (seperti DES atau AES) yang menggunakan kunci yang sama untuk proses enkripsi dan dekripsi sehingga rentan pada tahap distribusi kunci, RSA menggunakan pasangan kunci: **kunci publik (*public key*)** yang diumumkan secara terbuka untuk melakukan enkripsi, dan **kunci privat (*private key*)** yang disimpan secara rahasia oleh pemilik untuk melakukan dekripsi. Keamanan algoritma RSA bertumpu pada kesulitan komputasi pemfaktoran bilangan bulat yang sangat besar menjadi faktor-faktor prima penyusunnya (*prime factorization problem*).

Sesuai dengan instruksi penugasan untuk membuat sebuah studi kasus (*Study Case*) dunia nyata, tugas ini mengimplementasikan algoritma RSA pada skenario **Aplikasi Tiket Konser Anti-Calo (Digital Signature)**. Implementasi dilakukan secara **murni dari nol (*scratch*) tanpa menggunakan pustaka (*library*) atau kerangka kerja (*framework*) kriptografi eksternal**, guna menunjukkan secara transparan fungsi setiap tahapan RSA dalam memvalidasi keaslian dokumen.

### 1.2 Tujuan Tugas
Tujuan dari pelaksanaan tugas dan pembuatan aplikasi studi kasus ini adalah:
1. Mengimplementasikan algoritma RSA murni dari nol dalam sebuah Studi Kasus dunia nyata, yaitu penerapan Tanda Tangan Digital (Digital Signature) pada penerbitan tiket elektronik konser (E-Ticket) guna mencegah pemalsuan oleh calo.
2. Membuktikan kebenaran matematis dari algoritma RSA melalui perhitungan aritmatika modular, fungsi totient Euler, identitas Bézout, dan Teorema Euler yang beroperasi dalam mode autentikasi (Enkripsi dengan *Private Key*, Dekripsi dengan *Public Key*).
3. Menyediakan antarmuka pengguna (UI) yang mensimulasikan arsitektur terdistribusi: Sisi Admin Panitia (Pembuat Kunci & Penandatangan Tiket), Media Distribusi (QR Code/Teks), dan Sisi Scanner *Gate* (Verifikasi Tiket).
4. Menunjukkan keunggulan RSA dalam menjamin integritas dan autentikasi data, di mana tiket yang isinya dimanipulasi sekecil apapun akan langsung gagal diverifikasi oleh sistem pembaca di pintu masuk.

---

## BAB II: LANDASAN TEORI MATEMATIKA RSA

Algoritma RSA dibangun di atas pondasi teori bilangan (*number theory*) dan aritmatika modular. Berikut adalah konsep-konsep kunci yang digunakan:

### 2.1 Bilangan Prima dan Uji Keprimaan (*Primality Test*)
Bilangan prima adalah bilangan bulat positif lebih besar dari 1 yang hanya memiliki dua pembagi positif, yaitu 1 dan dirinya sendiri. Pada implementasi mandiri ini, dilakukan uji keprimaan menggunakan metode *Trial Division* teroptimasi dengan menguji faktor pembagi hingga $\sqrt{n}$ dengan pola lompatan $6k \pm 1$.

### 2.2 Pembagi Bersama Terbesar (PBB / GCD) & Algoritma Euclidean
Pembagi Bersama Terbesar (*Greatest Common Divisor* / GCD) dari dua bilangan bulat $a$ dan $b$ adalah bilangan bulat terbesar $d$ sedemikian rupa sehingga $d \mid a$ dan $d \mid b$. Algoritma Euclidean menghitung GCD secara iteratif:
$$\text{gcd}(a, b) = \text{gcd}(b, a \pmod b)$$
Iterasi berhenti saat sisa bagi bernilai 0, dan pembagi terakhir merupakan nilai $\text{PBB}(a, b)$.

### 2.3 Relatif Prima & Identitas Bézout
Dua bilangan bulat $a$ dan $b$ dikatakan relatif prima (koprima) jika dan hanya jika:
$$\text{PBB}(a, b) = 1$$
Berdasarkan identitas Bézout, jika $\text{PBB}(a, b) = 1$, maka terdapat bilangan bulat $x$ dan $y$ sedemikian sehingga:
$$a \cdot x + b \cdot y = 1$$

### 2.4 Fungsi Totient Euler ($\phi(n)$)
Fungsi Euler $\phi(n)$ menyatakan banyaknya bilangan bulat positif $1 \le k < n$ yang relatif prima terhadap $n$. Jika $n = p \times q$ dengan $p$ dan $q$ adalah dua bilangan prima berbeda, maka sifat multiplikatif fungsi totient menghasilkan:
$$\phi(n) = \phi(p) \times \phi(q) = (p - 1)(q - 1)$$

### 2.5 Teorema Euler
Teorema Euler menyatakan bahwa jika $a$ dan $n$ relatif prima ($\text{PBB}(a, n) = 1$), maka:
$$a^{\phi(n)} \equiv 1 \pmod n$$
Teorema ini adalah dasar matematis yang menjamin bahwa proses dekripsi pada RSA dapat mengembalikan plainteks awal.

### 2.6 Algoritma Euclidean Diperluas (*Extended Euclidean Algorithm*)
Kunci privat $d$ merupakan invers perkalian modular dari $e$ modulo $\phi(n)$:
$$e \cdot d \equiv 1 \pmod{\phi(n)}$$
Persamaan tersebut setara dengan mencari pasangan bilangan bulat $d$ dan $k'$ pada:
$$e \cdot d + \phi(n) \cdot k' = 1$$
Algoritma Euclidean Diperluas menelusuri kembali koefisien pembagian modular untuk memperoleh nilai $d = (s \pmod{\phi(n)} + \phi(n)) \pmod{\phi(n)}$.

### 2.7 Pangkat Modulo Cepat (*Modular Exponentiation / Square-and-Multiply*)
Perhitungan nilai $m^e \pmod n$ dan $c^d \pmod n$ untuk bilangan besar tidak dapat dilakukan dengan pemangkatan biasa karena akan menimbulkan *integer overflow*. Algoritma *Square-and-Multiply* merepresentasikan eksponen dalam bentuk biner dan mengevaluasi sisa bagi pada setiap langkah pengkuadratan dan perkalian dengan kompleksitas waktu efisien $O(\log \text{eksponen})$.

---

## BAB III: PERANCANGAN DAN IMPLEMENTASI SISTEM

Aplikasi dirancang menggunakan teknologi **Python Flask** sebagai *backend* web server dan **Tailwind CSS** untuk antarmuka pengguna (UI) modern. Seluruh komputasi kriptografi berjalan murni menggunakan fungsi matematika Python bawaan tanpa menggunakan library kriptografi eksternal seperti `pycryptodome`.

### 3.1 Struktur Direktori Proyek
```text
Kripto-/
├── app.py          # Web app Flask (Routing web, rendering UI Tailwind, endpoint gate/admin)
├── rsa.py          # Implementasi inti matematika RSA murni (Tanpa Library eksternal)
├── keys.json       # Penyimpanan sepasang kunci RSA (Public & Private Key)
├── tickets.json    # Database penyimpanan payload tiket dan Tanda Tangan Digital (Signature)
├── static/         # Direktori aset statis (contoh: foto konser)
└── README.md       # Laporan dan petunjuk instalasi
```

### 3.2 Fungsi-Fungsi Inti Matematika (`rsa.py`)
Berikut adalah implementasi fungsi kunci tanpa library yang ditulis secara manual:
1. **`is_prime(n)` & `generate_prime(bits)`**: Menghasilkan bilangan prima besar dan melakukan uji keprimaan menggunakan metode *Miller-Rabin Primality Test*.
2. **`gcd(a, b)`**: Menghitung $\text{PBB}(a, b)$ dengan algoritma Euclidean.
3. **`egcd(a, b)` & `mod_inverse(e, phi)`**: Mencari kunci privat $d$ menggunakan *Extended Euclidean Algorithm*.
4. **`mod_pow(base, exp, mod)`**: Menghitung eksponensial modulo secara sangat cepat menggunakan metode *Square-and-Multiply* bitwise untuk mencegah overflow.
5. **`generate_keys(bits)`**: Membangkitkan pasangan kunci publik $(e, n)$ dan kunci privat $(d, n)$.
6. **`sign(message, private_key)`**: Melakukan hashing SHA-256 pada pesan, kemudian dienkripsi (ditandatangani) menggunakan $d$ dan $n$.
7. **`verify(message, signature, public_key)`**: Menghash ulang pesan dan mencocokkannya dengan dekripsi signature menggunakan $e$ dan $n$.

### 3.3 Fitur Antarmuka Pengguna (UI)
* **Halaman Beli Tiket (`/`)**: 
  - Pengguna mengisi nama, event, dan kategori tiket.
  - Server membuat ID unik, memformat *payload* data, lalu menandatanganinya menggunakan fungsi `sign` (Private Key).
  - Tanda tangan digital beserta data tiket disimpan ke `tickets.json`. Pengguna mendapatkan visual E-Ticket estetik.
* **Halaman Gate Control (`/gate`)**:
  - Petugas memasukkan ID tiket pengunjung.
  - Server mencari tiket di database, lalu memverifikasi tanda tangannya menggunakan fungsi `verify` (Public Key).
  - Jika isi tiket dimanipulasi sekecil apa pun di dalam *database* (misal: "Regular" diubah paksa jadi "VIP"), sistem akan otomatis menolak tiket tersebut (*Digital Signature Invalid*).
* **Halaman Admin Control (`/admin`)**:
  - Halaman khusus demonstrasi untuk menampilkan nilai komponen matematis $e$, $n$, dan $d$ secara *real-time*.

---

## BAB IV: HASIL PENGUJIAN DAN ANALISIS

### 4.1 Uji Kasus 1: Sesuai Slide Perkuliahan (Kasus Alice & Pesan "HELLOALICE")
* **Parameter Kunci:**
  - $p = 47$ (Prima)
  - $q = 71$ (Prima)
  - $n = 47 \times 71 = 3337$
  - $\phi(n) = (47 - 1) \times (71 - 1) = 46 \times 70 = 3220$
  - Dipilih $e = 79$ ($\text{PBB}(79, 3220) = 1$)
  - Invers modular: Untuk $k = 25$, diperoleh $d = \frac{1 + 25 \times 3220}{79} = \frac{80501}{79} = 1019$.
  - Kunci Publik: $(e=79, n=3337)$
  - Kunci Privat: $(d=1019, n=3337)$

* **Proses Enkripsi:**
  - Plainteks $m = \text{"HELLOALICE"}$
  - Kode huruf 2 digit:
    $H=07, E=04, L=11, L=11, O=14, A=00, L=11, I=08, C=02, E=04$
    $\rightarrow m = 07041111140011080204$
  - Pemecahan blok 4 digit:
    $m_1 = 0704, m_2 = 1111, m_3 = 1400, m_4 = 1108, m_5 = 0204$
  - Perhitungan per blok:
    - $c_1 = 704^{79} \pmod{3337} = 328 \rightarrow 0328$
    - $c_2 = 1111^{79} \pmod{3337} = 301 \rightarrow 0301$
    - $c_3 = 1400^{79} \pmod{3337} = 2653$
    - $c_4 = 1108^{79} \pmod{3337} = 2986$
    - $c_5 = 204^{79} \pmod{3337} = 1164$
  - **Cipherteks Dihasilkan:** `0328 0301 2653 2986 1164` (Sesuai 100% dengan slide).

* **Proses Dekripsi:**
  - $m_1 = 328^{1019} \pmod{3337} = 704 \rightarrow 0704 \rightarrow \text{"HE"}$
  - $m_2 = 301^{1019} \pmod{3337} = 1111 \rightarrow \text{"LL"}$
  - $m_3 = 2653^{1019} \pmod{3337} = 1400 \rightarrow \text{"OA"}$
  - $m_4 = 2986^{1019} \pmod{3337} = 1108 \rightarrow \text{"LI"}$
  - $m_5 = 1164^{1019} \pmod{3337} = 204 \rightarrow 0204 \rightarrow \text{"CE"}$
  - **Plainteks Hasil Rekonstruksi:** $\text{"HELLOALICE"}$ (**COCOK SEMPURNA / MATCH VERIFIED**).

### 4.2 Uji Kasus 2: Sesuai Slide Perkuliahan (Kasus Bob)
* $p = 83, q = 61 \Rightarrow n = 5063, \phi(n) = 82 \times 60 = 4920$.
* Kunci publik $e = 187$ ($\text{PBB}(187, 4920) = 1$).
* Kunci privat $d = 763$.
* Hasil pengujian program: Nilai yang dihasilkan identik dengan contoh di slide kuliah.

### 4.3 Analisis Aspek Keamanan
Pada contoh praktikum, bilangan prima $p$ dan $q$ yang digunakan berukuran relatif kecil (2 digit hingga 3 digit) untuk kemudahan demonstrasi perhitungan manual. Namun dalam implementasi nyata standar industri (misal RSA-2048 atau RSA-4096), ukuran bilangan prima mencapai ratusan hingga ribuan bit sehingga faktorisasi nilai $n$ mustahil dilakukan dalam waktu wajar dengan daya komputasi saat ini.

---

## BAB V: KESIMPULAN

1. Algoritma kriptografi kunci-publik RSA telah berhasil diimplementasikan secara **murni dari nol tanpa melibatkan pustaka (*library*) atau kerangka kerja (*framework*) kriptografi pihak ketiga**.
2. Seluruh tahapan mulai dari verifikasi bilangan prima, pembentukan modulus $n$, totient $\phi(n)$, pemilihan kunci publik $e$, pencarian kunci privat $d$ melalui Algoritma Euclidean Diperluas, hingga operasi enkripsi dan dekripsi modular berjalan dengan akurat dan presisi.
3. Hasil pengujian pada aplikasi terbukti **100% identik dengan hasil perhitungan manual pada materi slide perkuliahan Kriptografi**, baik pada kasus Alice maupun kasus Bob.
4. Antarmuka pengguna (UI) yang dirancang memberikan kemudahan visualisasi proses matematis per langkah, memudahkan pengujian parameter, serta siap digunakan untuk demonstrasi praktikum dan video presentasi tugas.

---

## DAFTAR PUSTAKA
1. Munir, Rinaldi. (2019). *Kriptografi* (Edisi Kedua). Bandung: Informatika.
2. Aumasson, Jean-Philippe. (2017). *Serious Cryptography: A Practical Introduction to Modern Encryption*. San Francisco: No Starch Press, Inc.
3. Rivest, R. L., Shamir, A., & Adleman, L. (1978). A method for obtaining digital signatures and public-key cryptosystems. *Communications of the ACM*, 21(2), 120-126.
4. Slide Kuliah: *Kriptografi Part 5 - Asymmetric-key Cryptography: RSA*. Departemen Teknologi Informasi, Institut Teknologi Sepuluh Nopember.


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

