"""
sha256_manual.py - Implementasi SHA-256 manual (tanpa hashlib).
Mengikuti standar FIPS 180-4.
"""

# 64 konstanta K: 32 bit pertama dari pecahan akar pangkat tiga 64 prima pertama
K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]

# Nilai awal hash H0..H7: akar kuadrat 8 prima pertama
H_AWAL = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
          0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]

MASK = 0xFFFFFFFF  # supaya hasil tetap 32-bit


def rotr(x, n):
    """Rotate right 32-bit."""
    return ((x >> n) | (x << (32 - n))) & MASK


def sha256(data: bytes) -> bytes:
    # 1. PADDING: tambah bit 1, lalu 0 sampai panjang = 56 (mod 64), lalu panjang asli 64-bit
    panjang_bit = len(data) * 8
    data += b"\x80"
    while len(data) % 64 != 56:
        data += b"\x00"
    data += panjang_bit.to_bytes(8, "big")

    h = H_AWAL[:]

    # 2. Proses tiap blok 64 byte (512 bit)
    for i in range(0, len(data), 64):
        blok = data[i:i + 64]

        # 2a. Message schedule: 16 word dari blok + 48 word turunan
        w = [int.from_bytes(blok[j:j + 4], "big") for j in range(0, 64, 4)]
        for t in range(16, 64):
            s0 = rotr(w[t - 15], 7) ^ rotr(w[t - 15], 18) ^ (w[t - 15] >> 3)
            s1 = rotr(w[t - 2], 17) ^ rotr(w[t - 2], 19) ^ (w[t - 2] >> 10)
            w.append((w[t - 16] + s0 + w[t - 7] + s1) & MASK)

        # 2b. Compression: 64 putaran
        a, b, c, d, e, f, g, hh = h
        for t in range(64):
            S1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25)
            ch = (e & f) ^ (~e & MASK & g)
            temp1 = (hh + S1 + ch + K[t] + w[t]) & MASK
            S0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (S0 + maj) & MASK
            hh, g, f, e = g, f, e, (d + temp1) & MASK
            d, c, b, a = c, b, a, (temp1 + temp2) & MASK

        # 2c. Tambahkan hasil blok ke hash sementara
        h = [(x + y) & MASK for x, y in zip(h, [a, b, c, d, e, f, g, hh])]

    # 3. Gabungkan 8 word jadi 32 byte
    return b"".join(x.to_bytes(4, "big") for x in h)