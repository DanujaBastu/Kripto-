"""
app.py - Aplikasi Tiket Konser Anti-Calo
Jalankan:  pip install flask   lalu   python app.py
Buka:      http://127.0.0.1:5000        (beli tiket)
           http://127.0.0.1:5000/gate   (pintu masuk / scan)
           http://127.0.0.1:5000/admin  (khusus demo: lihat kunci RSA)
"""
import json
import os
import secrets

from flask import Flask, request, render_template_string

import rsa

app = Flask(__name__)
KEY_FILE = "keys.json"
TICKET_FILE = "tickets.json"
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # tanpa O/0/I/1 biar tidak membingungkan


def load_tickets():
    if os.path.exists(TICKET_FILE):
        with open(TICKET_FILE) as f:
            return json.load(f)
    return {}


def save_tickets():
    with open(TICKET_FILE, "w") as f:
        json.dump(tickets, f)


# { "7K3M9QXA": {"payload": "...", "sig": "hex...", "used": False} }
tickets = load_tickets()


# ---------- Kunci RSA panitia (dibuat sekali, disimpan ke file) ----------
def load_keys():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE) as f:
            k = json.load(f)
        return k["n"], k["e"], k["d"]
    n, e, d = rsa.generate_keys(1024)
    with open(KEY_FILE, "w") as f:
        json.dump({"n": n, "e": e, "d": d}, f)
    return n, e, d


N, E, D = load_keys()


# ---------- Buat & cek tiket ----------
def create_ticket(nama, event, kategori):
    tid = "".join(secrets.choice(ALPHABET) for _ in range(8))
    payload = f"{tid}|{nama}|{event}|{kategori}"
    signature = rsa.sign(payload, D, N)  # private key panitia
    tickets[tid] = {"payload": payload, "sig": hex(signature)[2:], "used": False}
    save_tickets()
    return f"TKT-{tid[:4]}-{tid[4:]}"  # kode pendek untuk user


def check_ticket(code):
    tid = code.upper().replace("TKT", "").replace("-", "").replace(" ", "")
    rec = tickets.get(tid)
    if not rec:
        return False, "Tiket tidak ditemukan", None
    payload = rec["payload"]
    if not rsa.verify(payload, int(rec["sig"], 16), E, N):  # public key
        return False, "Data tiket tidak valid / sudah diubah", None
    if rec["used"]:
        return False, "Tiket sudah pernah dipakai", None
    rec["used"] = True
    save_tickets()
    _, nama, event, kategori = payload.split("|")
# ---------- Tampilan (Web UI Modern) ----------
PAGE = """
<!doctype html><html lang="id"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TiketKu - Anti Calo</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  body { font-family: 'Inter', sans-serif; }
</style>
</head>
<body class="min-h-screen bg-[linear-gradient(135deg,#dbeafe_0%,#f6f4ff_48%,#ede9fe_100%)] text-slate-900">
    <header class="sticky top-0 z-20 border-b border-slate-100/90 bg-white/60 backdrop-blur-xl">
      <nav class="mx-auto flex h-[76px] max-w-[1200px] items-center justify-between px-8" aria-label="Main navigation">
        <a href="/" class="text-[21px] font-bold tracking-[-0.04em] text-slate-900"><span class="mr-1.5">🎫</span>tiketku</a>
        <div class="absolute left-1/2 flex -translate-x-1/2 items-center gap-1 rounded-full bg-slate-100/70 p-1">
          <a href="/" class="rounded-full px-5 py-2 text-sm font-medium transition text-slate-500 hover:text-slate-900">Beli Tiket</a>
          <a href="/gate" class="rounded-full px-5 py-2 text-sm font-medium transition text-slate-500 hover:text-slate-900">Pintu Masuk</a>
          <a href="/admin" class="rounded-full px-5 py-2 text-sm font-medium transition text-slate-500 hover:text-slate-900">Admin</a>
        </div>
        <p class="text-xs font-medium tracking-wide text-slate-500">RSA Anti-Calo</p>
      </nav>
    </header>
    {{ body|safe }}
</body></html>
"""


@app.route("/", methods=["GET", "POST"])
def beli():
    if request.method == "POST":
        token = create_ticket(request.form["nama"], request.form["event"], request.form["kategori"])
        body = f"""
        <main class="mx-auto grid min-h-[calc(100vh-76px)] max-w-[1100px] grid-cols-[1.1fr_.9fr] items-center gap-12 px-6 py-12">
            <section class="max-w-[520px]">
              <p class="mb-4 text-xs font-bold tracking-[.18em] text-violet-700">YOUR NEXT GREAT MEMORY</p>
              <h1 class="text-[42px] font-bold leading-[1.16] tracking-[-.035em] text-slate-900">Pembelian<br />Berhasil.</h1>
              <p class="mt-4 text-base text-slate-500">Tiket impian Anda sudah di tangan. Tunjukkan tiket ini di pintu masuk.</p>
              <div class="mt-9">
                  <a href="/"><button class="h-14 w-full rounded-full border border-violet-600 text-violet-600 text-sm font-bold bg-white transition hover:bg-violet-50">Beli Tiket Lain</button></a>
              </div>
            </section>
            
            <section class="relative py-9">
              <div class="absolute inset-0 m-auto h-[360px] w-[360px] rounded-full bg-violet-300/20 blur-3xl"></div>
              <div class="relative">
                <div class="relative mx-auto w-[330px] overflow-hidden rounded-[24px] bg-white shadow-[0_20px_60px_rgba(15,23,42,0.18)]">
                  <div class="relative h-[228px] overflow-hidden bg-cover bg-center px-6 pt-5 text-white" style="background-image: url('/static/concert.png')">
                    <div class="absolute inset-0 bg-gradient-to-b from-violet-950/80 via-violet-950/50 to-slate-950/95"></div>
                    <div class="relative flex items-center justify-between"><span class="text-[10px] font-bold tracking-[.18em] text-pink-200">LIVE CONCERT</span><span class="rounded-full border border-white/30 bg-white/15 px-2.5 py-1 text-[9px] font-bold">{request.form['kategori']}</span></div>
                    <div class="absolute inset-x-0 bottom-0 bg-gradient-to-t from-slate-950/90 via-slate-950/45 to-transparent px-6 pb-5 pt-14">
                      <h2 class="text-[25px] font-bold leading-none tracking-[-0.04em]">{request.form['event']}</h2>
                      <p class="mt-1 text-xs text-slate-200">Konser Nusantara 2026</p>
                      <div class="mt-4 grid grid-cols-2 gap-y-1 text-[10px] text-white/90">
                        <span>📅 25 Okt 2026</span><span>⏰ 19:00 WIB</span>
                        <span class="col-span-2">📍 Jakarta, Indonesia <span class="float-right">{request.form['nama']}</span></span>
                      </div>
                    </div>
                  </div>
                  <div class="relative flex h-7 items-center"><span class="absolute -left-3 h-6 w-6 rounded-full bg-[#f0ecff]"></span><div class="mx-6 w-full border-t-2 border-dashed border-slate-200"></div><span class="absolute -right-3 h-6 w-6 rounded-full bg-[#f0ecff]"></span></div>
                  <div class="px-6 pb-5 text-center">
                    <div class="mx-auto grid h-[120px] w-[120px] grid-cols-7 gap-[3px] bg-white p-2">
                       <span class="bg-slate-900"></span><span class="bg-slate-900"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-slate-900"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-slate-900"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-slate-900"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span>
                    </div>
                    <p class="mt-3 font-mono text-[15px] font-bold tracking-[.08em] text-violet-700">{token}</p>
                    <p class="mt-1 text-[8px] font-bold tracking-[.14em] text-slate-400">RSA DIGITAL SIGNATURE VERIFIED</p>
                    <button class="mt-4 ml-auto flex items-center gap-1 rounded-full border border-violet-200 px-3 py-1.5 text-[10px] font-semibold text-violet-700 transition hover:bg-violet-50">📥 Unduh Tiket</button>
                  </div>
                </div>
              </div>
            </section>
        </main>
        """
        return render_template_string(PAGE, body=body)

    body = """
    <main class="mx-auto grid min-h-[calc(100vh-76px)] max-w-[1100px] grid-cols-[1.1fr_.9fr] items-center gap-12 px-6 py-12">
    <section class="max-w-[520px]">
      <p class="mb-4 text-xs font-bold tracking-[.18em] text-violet-700">YOUR NEXT GREAT MEMORY</p>
      <h1 class="text-[42px] font-bold leading-[1.16] tracking-[-.035em] text-slate-900">Konser impian.<br />Tiket di tangan.</h1>
      <p class="mt-4 text-base text-slate-500">Beli tiket konser asli, aman, dan anti-calo.</p>
      
      <form method="post" class="mt-9 space-y-5">
        <label class="block"><span class="mb-2 block text-sm font-semibold text-slate-700">Nama Lengkap</span>
          <input name="nama" placeholder="Sesuai identitas asli" required class="h-13 w-full rounded-xl border border-slate-200 bg-white/80 p-4 text-sm outline-none transition placeholder:text-slate-400 focus:border-violet-500 focus:ring-4 focus:ring-violet-100" />
        </label>
        
        <div class="block"><span class="mb-2 block text-sm font-semibold text-slate-700">Pilih Event</span>
          <input type="hidden" name="event" value="Sound of Tomorrow" />
          <button type="button" class="flex h-[62px] w-full items-center gap-3 rounded-xl border border-slate-200 bg-white/80 px-3 text-left transition hover:border-violet-300">
            <span class="grid h-9 w-9 place-items-center rounded-full bg-gradient-to-br from-pink-300 via-violet-400 to-sky-300 text-sm">♫</span>
            <span><b class="block text-sm text-slate-800">Sound of Tomorrow</b><span class="text-xs text-slate-500">Multi-venue • 2026</span></span>
            <span class="ml-auto text-slate-400">⌄</span>
          </button>
        </div>
        
        <div><span class="mb-2 block text-sm font-semibold text-slate-700">Kategori Tiket</span>
          <input type="hidden" name="kategori" value="VIP" />
          <div class="flex gap-3">
            <button type="button" class="h-12 flex-1 rounded-full border border-slate-200 bg-white/70 text-slate-600 text-sm font-semibold transition hover:bg-white">Regular</button>
            <button type="button" class="h-12 flex-1 rounded-full border border-violet-600 bg-violet-600 text-white shadow-[0_6px_16px_rgba(124,58,237,.32)] text-sm font-semibold transition">VIP</button>
          </div>
        </div>
        
        <div class="flex items-center justify-between border-y border-slate-200/80 py-5 text-sm">
          <span class="text-slate-500">Harga / tiket</span><strong class="text-base text-slate-900">Rp 350.000</strong>
        </div>
        
        <button type="submit" class="h-14 w-full rounded-full bg-gradient-to-r from-violet-600 to-purple-600 text-sm font-bold text-white shadow-[0_10px_20px_rgba(124,58,237,.2)] transition hover:-translate-y-0.5 hover:shadow-[0_14px_26px_rgba(124,58,237,.3)]">Beli Tiket <span class="ml-1">→</span></button>
        <div class="flex items-center justify-center gap-4 text-[11px] text-slate-500">
          <span>✓ Tiket asli dijamin</span><span>🔒 Dilindungi RSA Encryption</span>
        </div>
      </form>
    </section>
    
    <section class="relative py-9">
      <div class="absolute inset-0 m-auto h-[360px] w-[360px] rounded-full bg-violet-300/20 blur-3xl"></div>
      <div class="relative">
        <div class="relative mx-auto w-[330px] overflow-hidden rounded-[24px] bg-white shadow-[0_20px_60px_rgba(15,23,42,0.18)]">
                  <div class="relative h-[228px] overflow-hidden bg-cover bg-center px-6 pt-5 text-white" style="background-image: url('/static/concert.png')">
                    <div class="absolute inset-0 bg-gradient-to-b from-violet-950/25 via-violet-950/10 to-slate-950/95"></div>
                    <div class="relative flex items-center justify-between"><span class="text-[10px] font-bold tracking-[.18em] text-pink-200">LIVE CONCERT</span><span class="rounded-full border border-white/30 bg-white/15 px-2.5 py-1 text-[9px] font-bold">VIP</span></div>
                    <div class="absolute inset-x-0 bottom-0 bg-gradient-to-t from-slate-950/90 via-slate-950/45 to-transparent px-6 pb-5 pt-14">
                      <h2 class="text-[25px] font-bold leading-none tracking-[-0.04em]">Sound of Tomorrow</h2>
                      <p class="mt-1 text-xs text-slate-200">Konser Nusantara 2026</p>
                      <div class="mt-4 grid grid-cols-2 gap-y-1 text-[10px] text-white/90">
                        <span>📅 25 Okt 2026</span><span>⏰ 19:00 WIB</span>
                        <span class="col-span-2">📍 Jakarta, Indonesia <span class="float-right">Aditya Pratama</span></span>
                      </div>
                    </div>
                  </div>
                  <div class="relative flex h-7 items-center"><span class="absolute -left-3 h-6 w-6 rounded-full bg-[#f0ecff]"></span><div class="mx-6 w-full border-t-2 border-dashed border-slate-200"></div><span class="absolute -right-3 h-6 w-6 rounded-full bg-[#f0ecff]"></span></div>
                  <div class="px-6 pb-5 text-center">
                    <div class="mx-auto grid h-[120px] w-[120px] grid-cols-7 gap-[3px] bg-white p-2">
                       <span class="bg-slate-900"></span><span class="bg-slate-900"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-slate-900"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-slate-900"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-slate-900"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span><span class="bg-transparent"></span><span class="bg-slate-900"></span>
                    </div>
                    <p class="mt-3 font-mono text-[15px] font-bold tracking-[.08em] text-violet-700">TKT-7K3M-9QXA</p>
                    <p class="mt-1 text-[8px] font-bold tracking-[.14em] text-slate-400">RSA DIGITAL SIGNATURE VERIFIED</p>
                    <button class="mt-4 ml-auto flex items-center gap-1 rounded-full border border-violet-200 px-3 py-1.5 text-[10px] font-semibold text-violet-700 transition hover:bg-violet-50">📥 Unduh Tiket</button>
                  </div>
        </div>
      </div>
    </section>
    </main>
    """
    return render_template_string(PAGE, body=body)


@app.route("/gate", methods=["GET", "POST"])
def gate():
    body = """
    <main class="mx-auto max-w-[560px] px-6 py-16 text-center">
      <p class="text-xs font-bold tracking-[.18em] text-violet-700">GATE CONTROL</p>
      <h1 class="mt-3 text-[34px] font-bold leading-tight tracking-[-.035em]">Pengalaman seru<br />dimulai di sini.</h1>
      <p class="mx-auto mt-4 max-w-[470px] text-sm leading-6 text-slate-500">Verifikasi tiket pengunjung untuk memastikan keaslian sebelum masuk.</p>
      
      <form method="post" class="relative mt-9">
        <input name="token" class="h-16 w-full rounded-xl border-2 border-slate-200 bg-white px-6 text-center font-mono text-xl outline-none transition placeholder:text-slate-400 focus:border-violet-500 focus:ring-4 focus:ring-violet-100" placeholder="TKT-7K3M-9QXA" required />
        <button type="submit" class="mt-4 h-14 w-full rounded-full bg-gradient-to-r from-violet-600 to-purple-600 text-sm font-bold text-white shadow-[0_10px_20px_rgba(124,58,237,.2)]">Verifikasi Tiket</button>
      </form>
    """
    if request.method == "POST":
        ok, msg, info = check_ticket(request.form["token"])
        if ok:
            body += f"""
            <div class="mt-9 border-l-4 border-green-500 bg-green-50 rounded-r-xl p-5 text-left flex gap-4">
              <span class="text-3xl">✅</span>
              <div>
                <h2 class="font-bold text-green-700">Tiket Valid</h2>
                <p class="mt-1 text-sm leading-5 text-slate-600">{msg}</p>
                <p class="mt-4 text-xs leading-5 text-slate-600"><b>{info['nama']}</b> · {info['event']}<br />Kategori: <b>{info['kategori']}</b></p>
              </div>
            </div>
            """
        else:
            if "sudah pernah dipakai" in msg.lower():
                body += f"""
                <div class="mt-9 border-l-4 border-yellow-500 bg-yellow-50 rounded-r-xl p-5 text-left flex gap-4">
                  <span class="text-3xl">⚠️</span>
                  <div>
                    <h2 class="font-bold text-yellow-700">Tiket Sudah Digunakan</h2>
                    <p class="mt-1 text-sm leading-5 text-slate-600">{msg}</p>
                  </div>
                </div>
                """
            else:
                body += f"""
                <div class="mt-9 border-l-4 border-rose-500 bg-rose-50 rounded-r-xl p-5 text-left flex gap-4">
                  <span class="text-3xl">❌</span>
                  <div>
                    <h2 class="font-bold text-rose-700">Tiket Tidak Valid</h2>
                    <p class="mt-1 text-sm leading-5 text-slate-600">{msg}</p>
                  </div>
                </div>
                """
    body += "</main>"
    return render_template_string(PAGE, body=body)


@app.route("/admin")
def admin():
    """Hanya untuk demo/presentasi: menampilkan komponen RSA."""
    body = f"""
    <main class="mx-auto max-w-[900px] px-6 py-14">
      <p class="text-xs font-bold tracking-[.18em] text-violet-700">BEHIND THE SECURITY</p>
      <h1 class="mt-3 text-[34px] font-bold tracking-[-.035em]">Kontrol di balik setiap tiket.</h1>
      <p class="mt-3 text-sm text-slate-500">Informasi kunci RSA dan daftar tiket yang diterbitkan.</p>
      
      <div class="mt-8 rounded-xl border border-violet-200 bg-violet-50 px-5 py-4 text-sm leading-6 text-violet-900/80">
        <b>Bagaimana RSA melindungi tiket ini?</b> Setiap tiket ditandatangani dengan Private Key (d). Pemindai hanya menerima tandatangan yang bisa diverifikasi dengan Public Key (e) dan (n). Data tiket tidak bisa dipalsukan.
      </div>
      
      <section class="mt-8 grid grid-cols-3 gap-5">
        <article class="relative rounded-2xl border border-slate-200 bg-white p-6">
          <span class="grid h-10 w-10 place-items-center rounded-full text-lg bg-violet-100">🔑</span>
          <p class="mt-5 text-[11px] font-bold tracking-[.1em] text-slate-500">PUBLIC KEY (e)</p>
          <p class="mt-1 text-[28px] font-bold tracking-[-.04em] text-slate-900">{E}</p>
          <p class="mt-4 text-xs italic text-slate-500">Ditanam di scanner gate</p>
        </article>
        
        <article class="relative rounded-2xl border border-slate-200 bg-white p-6">
          <span class="grid h-10 w-10 place-items-center rounded-full text-lg bg-violet-100">🔢</span>
          <p class="mt-5 text-[11px] font-bold tracking-[.1em] text-slate-500">MODULUS (n)</p>
          <p class="mt-1 text-[28px] font-bold tracking-[-.04em] text-slate-900">{str(N)[:10]}...</p>
          <p class="mt-4 text-xs italic text-slate-500">Panjang: {N.bit_length()} bit</p>
        </article>
        
        <article class="relative rounded-2xl border border-red-200 bg-red-50/75 p-6">
          <span class="grid h-10 w-10 place-items-center rounded-full text-lg bg-red-100">🔒</span>
          <p class="mt-5 text-[11px] font-bold tracking-[.1em] text-red-700">PRIVATE KEY (d)</p>
          <p class="mt-1 text-[28px] font-bold tracking-[-.04em] text-red-900">{str(D)[:10]}...</p>
          <p class="mt-4 text-xs italic text-red-700/70">RAHASIA — hanya untuk panitia.</p>
        </article>
      </section>
    </main>
    """
    return render_template_string(PAGE, body=body)


if __name__ == "__main__":
    app.run(debug=True)