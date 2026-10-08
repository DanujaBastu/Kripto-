"""
rsa.py - Implementasi Algoritma RSA dan Hashing SHA-256 Murni dari Nol (Scratch).
Dibuat 100% tanpa menggunakan library/pustaka kriptografi atau hashing eksternal (ZERO LIBRARY).
Seluruh operasi modular, pembangkitan bilangan prima, dan hashing ditulis manual.
"""
import random


# ---------- 1. Operasi matematika dasar ----------
def gcd(a, b):
    """Algoritma Euclidean untuk menghitung Pembagi Bersama Terbesar (PBB/GCD)."""
    while b:
        a, b = b, a % b
    return a


def egcd(a, b):
    """Extended Euclidean: return (g, x, y) sehingga a*x + b*y = g (Identitas Bézout)."""
    if b == 0:
        return a, 1, 0
    g, x, y = egcd(b, a % b)
    return g, y, x - (a // b) * y


def mod_inverse(e, phi):
    """Mencari kunci privat d sebagai invers perkalian modular dari e mod phi."""
    g, x, _ = egcd(e, phi)
    if g != 1:
        raise ValueError("e tidak relatif prima dengan phi(n)")
    return x % phi


def mod_pow(base, exp, mod):
    """Pangkat Modulo Cepat (Square-and-Multiply bitwise) tanpa integer overflow."""
    result = 1
    base %= mod
    while exp > 0:
        if exp & 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp >>= 1
    return result


# ---------- 2. Bilangan prima & Uji Keprimaan ----------
def is_prime(n, k=40):
    """Uji keprimaan probabilistik Miller-Rabin."""
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29):
        if n == p:
            return True
        if n % p == 0:
            return False
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = mod_pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def generate_prime(bits):
    """Membangkitkan bilangan prima acak dengan ukuran bit tertentu."""
    while True:
        c = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(c):
            return c


# ---------- 3. Pembangkitan Pasangan Kunci RSA ----------
def generate_keys(bits=1024):
    """Membangkitkan Public Key (e, n) dan Private Key (d, n)."""
    e = 65537
    while True:
        p = generate_prime(bits // 2)
        q = generate_prime(bits // 2)
        if p == q:
            continue
        phi = (p - 1) * (q - 1)
        if gcd(e, phi) == 1:
            break
    n = p * q
    d = mod_inverse(e, phi)
    return n, e, d


# ---------- 4. Algoritma Hashing SHA-256 Murni dari Nol (Tanpa Hashlib) ----------
def _rotr(x, n):
    """Bitwise circular right rotation 32-bit."""
    return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF


def sha256_scratch(data: bytes) -> bytes:
    """Implementasi murni spesifikasi FIPS 180-4 SHA-256 tanpa modul hashlib."""
    # Nilai konstanta inisialisasi H (akar kuadrat dari 8 bilangan prima pertama)
    h = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    ]
    # Nilai konstanta putaran K (akar pangkat tiga dari 64 bilangan prima pertama)
    k = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    ]

    # Pre-processing (Padding bit '1' diikuti bit '0' hingga kelipatan 512-bit)
    padded = bytearray(data)
    orig_len_bits = len(data) * 8
    padded.append(0x80)
    while (len(padded) % 64) != 56:
        padded.append(0x00)
    padded.extend(orig_len_bits.to_bytes(8, "big"))

    # Proses pesan dalam blok 512-bit (64 byte)
    for i in range(0, len(padded), 64):
        chunk = padded[i:i+64]
        w = [int.from_bytes(chunk[j:j+4], "big") for j in range(0, 64, 4)] + [0] * 48
        for j in range(16, 64):
            s0 = _rotr(w[j-15], 7) ^ _rotr(w[j-15], 18) ^ (w[j-15] >> 3)
            s1 = _rotr(w[j-2], 17) ^ _rotr(w[j-2], 19) ^ (w[j-2] >> 10)
            w[j] = (w[j-16] + s0 + w[j-7] + s1) & 0xFFFFFFFF

        a, b, c, d, e, f, g, h_val = h
        for j in range(64):
            S1 = _rotr(e, 6) ^ _rotr(e, 11) ^ _rotr(e, 25)
            ch = (e & f) ^ ((~e) & g)
            temp1 = (h_val + S1 + ch + k[j] + w[j]) & 0xFFFFFFFF
            S0 = _rotr(a, 2) ^ _rotr(a, 13) ^ _rotr(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (S0 + maj) & 0xFFFFFFFF

            h_val = g
            g = f
            f = e
            e = (d + temp1) & 0xFFFFFFFF
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xFFFFFFFF

        h[0] = (h[0] + a) & 0xFFFFFFFF
        h[1] = (h[1] + b) & 0xFFFFFFFF
        h[2] = (h[2] + c) & 0xFFFFFFFF
        h[3] = (h[3] + d) & 0xFFFFFFFF
        h[4] = (h[4] + e) & 0xFFFFFFFF
        h[5] = (h[5] + f) & 0xFFFFFFFF
        h[6] = (h[6] + g) & 0xFFFFFFFF
        h[7] = (h[7] + h_val) & 0xFFFFFFFF

    return b"".join(val.to_bytes(4, "big") for val in h)


def hash_int(message: str) -> int:
    """Mengubah pesan menjadi integer hash 256-bit menggunakan fungsi SHA-256 manual."""
    return int.from_bytes(sha256_scratch(message.encode("utf-8")), "big")


# ---------- 5. Tanda Tangan Digital (Digital Signature) ----------
def sign(message: str, d: int, n: int) -> int:
    """Tanda tangan = hash(message)^d mod n  (enkripsi intisari data dengan private key)."""
    return mod_pow(hash_int(message), d, n)


def verify(message: str, signature: int, e: int, n: int) -> bool:
    """Verifikasi: dekripsi signature dengan public key e, lalu cocokkan dengan hash pesan asli."""
    return mod_pow(signature, e, n) == (hash_int(message) % n)


# ---------- 6. Enkripsi/Dekripsi Pesan Integer (Opsional Demo) ----------
def encrypt_int(m: int, e: int, n: int) -> int:
    return mod_pow(m, e, n)


def decrypt_int(c: int, d: int, n: int) -> int:
    return mod_pow(c, d, n)
