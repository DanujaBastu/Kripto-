"""
rsa.py - Implementasi RSA manual (tanpa library kriptografi).
Hanya memakai `random` untuk bilangan acak dan `hashlib` untuk SHA-256
(hash BUKAN bagian RSA; cek apakah dosen mengizinkan hashlib).
"""
import random
import hashlib


# ---------- 1. Operasi matematika dasar ----------
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def egcd(a, b):
    """Extended Euclidean: return (g, x, y) sehingga a*x + b*y = g."""
    if b == 0:
        return a, 1, 0
    g, x, y = egcd(b, a % b)
    return g, y, x - (a // b) * y


def mod_inverse(e, phi):
    g, x, _ = egcd(e, phi)
    if g != 1:
        raise ValueError("e tidak coprime dengan phi(n)")
    return x % phi


def mod_pow(base, exp, mod):
    """Fast modular exponentiation (square-and-multiply)."""
    result = 1
    base %= mod
    while exp > 0:
        if exp & 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp >>= 1
    return result


# ---------- 2. Bilangan prima ----------
def is_prime(n, k=40):
    """Tes primalitas Miller-Rabin."""
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
    while True:
        # bit paling atas & paling bawah di-set 1 (ukuran pas & ganjil)
        c = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(c):
            return c


# ---------- 3. Pembuatan kunci ----------
def generate_keys(bits=1024):
    """Return (n, e, d). Public key = (e, n), private key = (d, n)."""
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


# ---------- 4. Hash + Digital signature ----------
def hash_int(message: str) -> int:
    return int.from_bytes(hashlib.sha256(message.encode()).digest(), "big")


def sign(message: str, d: int, n: int) -> int:
    """Tanda tangan = hash(message)^d mod n  (pakai private key)."""
    return mod_pow(hash_int(message), d, n)


def verify(message: str, signature: int, e: int, n: int) -> bool:
    """Valid jika signature^e mod n == hash(message)  (pakai public key)."""
    return mod_pow(signature, e, n) == hash_int(message) % n


# ---------- 5. Enkripsi/dekripsi (opsional, untuk demo) ----------
def encrypt_int(m: int, e: int, n: int) -> int:
    return mod_pow(m, e, n)


def decrypt_int(c: int, d: int, n: int) -> int:
    return mod_pow(c, d, n)
