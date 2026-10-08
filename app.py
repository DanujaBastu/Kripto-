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

EVENTS = {
    "Sound of Tomorrow": {
        "sub": "Konser Nusantara 2026",
        "date": "25 Okt 2026",
        "time": "19:00 WIB",
        "location": "Jakarta, Indonesia",
        "img": "/static/concert.png",
        "price_regular": "Rp 150.000",
        "price_vip": "Rp 350.000"
    },
    "Festival Musik Surabaya": {
        "sub": "East Java Live Fest",
        "date": "10 Nov 2026",
        "time": "18:30 WIB",
        "location": "Surabaya, Indonesia",
        "img": "/static/concert2.png",
        "price_regular": "Rp 120.000",
        "price_vip": "Rp 275.000"
    },
    "Konser Nusantara 2026": {
        "sub": "Gelora Senayan Tour",
        "date": "15 Des 2026",
        "time": "20:00 WIB",
        "location": "Bandung, Indonesia",
        "img": "/static/concert3.png",
        "price_regular": "Rp 175.000",
        "price_vip": "Rp 400.000"
    }
}


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
        return False, "Tiket tidak ditemukan di database", None
    payload = rec["payload"]
    if not rsa.verify(payload, int(rec["sig"], 16), E, N):  # public key
        return False, "Tanda tangan digital RSA tidak valid (data telah dimanipulasi)", None
    if rec["used"]:
        return False, "Tiket sudah pernah digunakan sebelumnya (Anti-Double Entry)", None
    rec["used"] = True
    save_tickets()
    _, nama, event, kategori = payload.split("|")
    return True, "Tiket sah dan terverifikasi oleh Public Key RSA", {"nama": nama, "event": event, "kategori": kategori}


# ---------- Tampilan (Web UI Modern) ----------
def get_page(body, active_tab="beli"):
    beli_cls = "bg-white text-slate-900 shadow-sm font-semibold" if active_tab == "beli" else "text-slate-500 hover:text-slate-900 font-medium"
    gate_cls = "bg-white text-slate-900 shadow-sm font-semibold" if active_tab == "gate" else "text-slate-500 hover:text-slate-900 font-medium"
    admin_cls = "bg-white text-slate-900 shadow-sm font-semibold" if active_tab == "admin" else "text-slate-500 hover:text-slate-900 font-medium"
    
    return f"""<!doctype html><html lang="id"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TiketKu - Anti Calo (RSA Digital Signature)</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<script src="/static/qrcode.min.js"></script>
<script src="/static/html5-qrcode.min.js"></script>
<style>
  body {{ font-family: 'Inter', sans-serif; }}
  #reader video {{ border-radius: 1rem; object-fit: cover; }}
</style>
</head>
<body class="min-h-screen bg-[linear-gradient(135deg,#dbeafe_0%,#f6f4ff_48%,#ede9fe_100%)] text-slate-900 antialiased">
    <!-- Header / Navbar -->
    <header class="sticky top-0 z-20 border-b border-slate-100/90 bg-white/70 backdrop-blur-xl">
      <nav class="mx-auto flex h-[76px] max-w-[1200px] items-center justify-between px-8" aria-label="Main navigation">
        <a href="/" class="flex items-center gap-2.5 text-[20px] font-bold tracking-[-0.03em] text-slate-900">
          <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-violet-600 to-indigo-600 text-white shadow-md shadow-violet-200">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" />
            </svg>
          </div>
          <span>tiketku</span>
        </a>
        <div class="absolute left-1/2 flex -translate-x-1/2 items-center gap-1 rounded-full bg-slate-100/80 p-1">
          <a href="/" class="rounded-full px-5 py-2 text-sm transition {beli_cls}">Beli Tiket</a>
          <a href="/gate" class="rounded-full px-5 py-2 text-sm transition {gate_cls}">Pintu Masuk</a>
          <a href="/admin" class="rounded-full px-5 py-2 text-sm transition {admin_cls}">Admin</a>
        </div>
        <div class="flex items-center gap-2 rounded-full border border-violet-200/80 bg-violet-50/80 px-3.5 py-1.5 text-xs font-semibold text-violet-700">
          <span class="h-1.5 w-1.5 rounded-full bg-violet-600 animate-pulse"></span>
          RSA Anti-Calo
        </div>
      </nav>
    </header>
    {body}
</body></html>"""


@app.route("/", methods=["GET", "POST"])
def beli():
    if request.method == "POST":
        nama = request.form.get("nama", "Tamu")
        event_name = request.form.get("event", "Sound of Tomorrow")
        kategori = request.form.get("kategori", "VIP")
        
        event_info = EVENTS.get(event_name, EVENTS["Sound of Tomorrow"])
        token = create_ticket(nama, event_name, kategori)
        
        body = f"""
        <main class="mx-auto grid min-h-[calc(100vh-76px)] max-w-[1100px] grid-cols-[1.1fr_.9fr] items-center gap-12 px-6 py-12">
            <section class="max-w-[520px]">
              <p class="mb-4 text-xs font-bold tracking-[.18em] text-violet-700 uppercase">E-Ticket Berhasil Diterbitkan</p>
              <h1 class="text-[42px] font-bold leading-[1.16] tracking-[-.035em] text-slate-900">Pembelian<br />Berhasil.</h1>
              <p class="mt-4 text-base text-slate-500">Tiket asli Anda telah ditandatangani secara digital dengan Private Key RSA panitia. Tunjukkan QR Code ini di Gate pintu masuk.</p>
              
              <div class="mt-7 rounded-2xl border border-violet-200/80 bg-white/80 p-5 shadow-sm space-y-2">
                <div class="flex items-center justify-between text-xs text-slate-500">
                  <span>Nama Pembeli</span>
                  <strong class="text-slate-800 text-sm">{nama}</strong>
                </div>
                <div class="flex items-center justify-between text-xs text-slate-500">
                  <span>Event</span>
                  <strong class="text-slate-800 text-sm">{event_name}</strong>
                </div>
                <div class="flex items-center justify-between text-xs text-slate-500">
                  <span>Kategori</span>
                  <span class="rounded-full bg-violet-100 px-2.5 py-0.5 text-xs font-bold text-violet-700">{kategori}</span>
                </div>
              </div>
              
              <div class="mt-7 flex gap-4">
                  <a href="/" class="flex-1"><button class="h-14 w-full rounded-full border border-violet-600 text-violet-600 text-sm font-bold bg-white transition hover:bg-violet-50 cursor-pointer">Beli Tiket Lain</button></a>
                  <a href="/gate" class="flex-1"><button class="h-14 w-full rounded-full bg-violet-600 text-white text-sm font-bold transition hover:bg-violet-700 shadow-lg shadow-violet-200 cursor-pointer flex items-center justify-center gap-2">Ke Pintu Masuk <span>→</span></button></a>
              </div>
            </section>
            
            <section class="relative py-9">
              <div class="absolute inset-0 m-auto h-[360px] w-[360px] rounded-full bg-violet-300/20 blur-3xl"></div>
              <div class="relative">
                <div class="relative mx-auto w-[330px] overflow-hidden rounded-[24px] bg-white shadow-[0_20px_60px_rgba(15,23,42,0.18)]">
                  <div class="relative h-[228px] overflow-hidden bg-cover bg-center px-6 pt-5 text-white" style="background-image: url('{event_info['img']}')">
                    <div class="absolute inset-0 bg-gradient-to-b from-violet-950/80 via-violet-950/50 to-slate-950/95"></div>
                    <div class="relative flex items-center justify-between">
                      <span class="text-[10px] font-bold tracking-[.18em] text-pink-200">LIVE CONCERT</span>
                      <span class="rounded-full border border-white/30 bg-white/20 px-2.5 py-1 text-[9px] font-bold tracking-wider">{kategori}</span>
                    </div>
                    <div class="absolute inset-x-0 bottom-0 bg-gradient-to-t from-slate-950/90 via-slate-950/45 to-transparent px-6 pb-5 pt-14">
                      <h2 class="text-[23px] font-bold leading-none tracking-[-0.04em]">{event_name}</h2>
                      <p class="mt-1 text-xs text-slate-200">{event_info['sub']}</p>
                      <div class="mt-4 grid grid-cols-2 gap-y-1 text-[10px] text-white/90">
                        <span class="flex items-center gap-1">
                          <svg class="h-3 w-3 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                          {event_info['date']}
                        </span>
                        <span class="flex items-center gap-1">
                          <svg class="h-3 w-3 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                          {event_info['time']}
                        </span>
                        <span class="col-span-2 flex items-center justify-between pt-0.5">
                          <span class="flex items-center gap-1">
                            <svg class="h-3 w-3 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                            {event_info['location']}
                          </span>
                          <span class="font-medium text-white">{nama}</span>
                        </span>
                      </div>
                    </div>
                  </div>
                  <div class="relative flex h-7 items-center"><span class="absolute -left-3 h-6 w-6 rounded-full bg-[#f0ecff]"></span><div class="mx-6 w-full border-t-2 border-dashed border-slate-200"></div><span class="absolute -right-3 h-6 w-6 rounded-full bg-[#f0ecff]"></span></div>
                  
                  <!-- Area QR Code Asli (Bisa Di-Scan Kamera) -->
                  <div class="px-6 pb-6 text-center">
                    <div id="realQrContainer" class="mx-auto flex items-center justify-center p-3 bg-white rounded-2xl shadow-sm border border-slate-100 w-[146px] h-[146px]"></div>
                    <p class="mt-3 font-mono text-[16px] font-bold tracking-[.08em] text-violet-700">{token}</p>
                    <p class="mt-1 text-[8px] font-bold tracking-[.14em] text-slate-400">RSA DIGITAL SIGNATURE VERIFIED</p>
                    <button onclick="navigator.clipboard.writeText('{token}'); alert('Kode tiket disalin: {token}')" class="mt-3 mx-auto flex items-center gap-1.5 rounded-full border border-violet-200 px-3.5 py-1.5 text-[11px] font-semibold text-violet-700 transition hover:bg-violet-50 cursor-pointer">
                      <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                      Salin Kode Tiket
                    </button>
                  </div>
                </div>
              </div>
            </section>
        </main>
        
        <script>
          // Render QR Code Nyata dengan qrcode.js
          new QRCode(document.getElementById("realQrContainer"), {{
            text: "{token}",
            width: 122,
            height: 122,
            colorDark : "#0f172a",
            colorLight : "#ffffff",
            correctLevel : QRCode.CorrectLevel.H
          }});
        </script>
        """
        return get_page(body, "beli")

    # GET Request: Form Pembelian Interaktif
    events_json = json.dumps(EVENTS)
    body = f"""
    <main class="mx-auto grid min-h-[calc(100vh-76px)] max-w-[1100px] grid-cols-[1.1fr_.9fr] items-center gap-12 px-6 py-12">
    <section class="max-w-[520px]">
      <p class="mb-4 text-xs font-bold tracking-[.18em] text-violet-700">YOUR NEXT GREAT MEMORY</p>
      <h1 class="text-[42px] font-bold leading-[1.16] tracking-[-.035em] text-slate-900">Konser impian.<br />Tiket di tangan.</h1>
      <p class="mt-4 text-base text-slate-500">Beli tiket konser asli, aman, dan terlindungi kriptografi RSA anti-calo.</p>
      
      <form method="post" id="ticketForm" class="mt-9 space-y-5">
        <!-- Input Nama -->
        <label class="block"><span class="mb-2 block text-sm font-semibold text-slate-700">Nama Lengkap</span>
          <input name="nama" id="namaInput" placeholder="Sesuai identitas asli" required class="h-13 w-full rounded-xl border border-slate-200 bg-white/80 p-4 text-sm outline-none transition placeholder:text-slate-400 focus:border-violet-500 focus:ring-4 focus:ring-violet-100" />
        </label>
        
        <!-- Pilih Event (Thumbnail Foto Nyata) -->
        <div class="relative"><span class="mb-2 block text-sm font-semibold text-slate-700">Pilih Event</span>
          <input type="hidden" name="event" id="eventInput" value="Sound of Tomorrow" />
          <button type="button" id="eventDropdownBtn" onclick="toggleEventDropdown()" class="flex h-[66px] w-full items-center gap-3.5 rounded-xl border border-slate-200 bg-white/80 p-2.5 text-left transition hover:border-violet-300 focus:ring-4 focus:ring-violet-100 cursor-pointer">
            <img id="selectedEventImg" src="/static/concert.png" class="h-11 w-11 rounded-lg object-cover shadow-sm ring-1 ring-slate-900/10" alt="Cover" />
            <span class="flex-1">
              <b id="selectedEventName" class="block text-sm font-bold text-slate-800">Sound of Tomorrow</b>
              <span id="selectedEventSub" class="text-xs text-slate-500">Konser Nusantara 2026 · Jakarta</span>
            </span>
            <svg id="eventChevron" class="h-4 w-4 text-slate-400 transition-transform duration-200 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" /></svg>
          </button>
          
          <!-- Dropdown List Event -->
          <div id="eventDropdownMenu" class="hidden absolute top-full left-0 right-0 mt-2 z-30 bg-white rounded-2xl shadow-xl border border-slate-100 p-2 space-y-1">
            <div onclick="selectEvent('Sound of Tomorrow')" class="flex items-center gap-3.5 p-2.5 rounded-xl hover:bg-violet-50 cursor-pointer transition">
              <img src="/static/concert.png" class="h-11 w-11 rounded-lg object-cover shadow-sm ring-1 ring-slate-900/10" alt="Sound of Tomorrow" />
              <div>
                <b class="block text-sm font-bold text-slate-800">Sound of Tomorrow</b>
                <span class="text-xs text-slate-500">Konser Nusantara 2026 · Jakarta (25 Okt)</span>
              </div>
            </div>
            <div onclick="selectEvent('Festival Musik Surabaya')" class="flex items-center gap-3.5 p-2.5 rounded-xl hover:bg-violet-50 cursor-pointer transition">
              <img src="/static/concert2.png" class="h-11 w-11 rounded-lg object-cover shadow-sm ring-1 ring-slate-900/10" alt="Festival Musik Surabaya" />
              <div>
                <b class="block text-sm font-bold text-slate-800">Festival Musik Surabaya</b>
                <span class="text-xs text-slate-500">East Java Live Fest · Surabaya (10 Nov)</span>
              </div>
            </div>
            <div onclick="selectEvent('Konser Nusantara 2026')" class="flex items-center gap-3.5 p-2.5 rounded-xl hover:bg-violet-50 cursor-pointer transition">
              <img src="/static/concert3.png" class="h-11 w-11 rounded-lg object-cover shadow-sm ring-1 ring-slate-900/10" alt="Konser Nusantara 2026" />
              <div>
                <b class="block text-sm font-bold text-slate-800">Konser Nusantara 2026</b>
                <span class="text-xs text-slate-500">Gelora Senayan Tour · Bandung (15 Des)</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Kategori Tiket (Regular / VIP) -->
        <div><span class="mb-2 block text-sm font-semibold text-slate-700">Kategori Tiket</span>
          <input type="hidden" name="kategori" id="kategoriInput" value="VIP" />
          <div class="flex gap-3">
            <button type="button" id="btnRegular" onclick="selectCategory('Regular')" class="h-12 flex-1 rounded-full border border-slate-200 bg-white/70 text-slate-600 text-sm font-semibold transition hover:bg-white cursor-pointer">Regular</button>
            <button type="button" id="btnVIP" onclick="selectCategory('VIP')" class="h-12 flex-1 rounded-full border border-violet-600 bg-violet-600 text-white shadow-[0_6px_16px_rgba(124,58,237,.32)] text-sm font-semibold transition cursor-pointer">VIP</button>
          </div>
        </div>
        
        <!-- Harga Dinamis -->
        <div class="flex items-center justify-between border-y border-slate-200/80 py-5 text-sm">
          <span class="text-slate-500">Harga / tiket</span><strong id="priceDisplay" class="text-base text-slate-900">Rp 350.000</strong>
        </div>
        
        <button type="submit" class="h-14 w-full rounded-full bg-gradient-to-r from-violet-600 to-purple-600 text-sm font-bold text-white shadow-[0_10px_20px_rgba(124,58,237,.2)] transition hover:-translate-y-0.5 hover:shadow-[0_14px_26px_rgba(124,58,237,.3)] cursor-pointer flex items-center justify-center gap-2">
          <span>Beli Tiket</span>
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
        </button>
        <div class="flex items-center justify-center gap-4 text-[11px] text-slate-500">
          <span class="flex items-center gap-1">
            <svg class="h-3.5 w-3.5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
            Tiket asli terverifikasi
          </span>
          <span class="flex items-center gap-1">
            <svg class="h-3.5 w-3.5 text-violet-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
            RSA Digital Signature
          </span>
        </div>
      </form>
    </section>
    
    <!-- Live Preview Tiket -->
    <section class="relative py-9">
      <div class="absolute inset-0 m-auto h-[360px] w-[360px] rounded-full bg-violet-300/20 blur-3xl"></div>
      <div class="relative">
        <div class="relative mx-auto w-[330px] overflow-hidden rounded-[24px] bg-white shadow-[0_20px_60px_rgba(15,23,42,0.18)]">
                  <div id="previewCardHero" class="relative h-[228px] overflow-hidden bg-cover bg-center px-6 pt-5 text-white transition-all duration-300" style="background-image: url('/static/concert.png')">
                    <div class="absolute inset-0 bg-gradient-to-b from-violet-950/40 via-violet-950/20 to-slate-950/95"></div>
                    <div class="relative flex items-center justify-between">
                      <span class="text-[10px] font-bold tracking-[.18em] text-pink-200">LIVE CONCERT</span>
                      <span id="previewKategoriBadge" class="rounded-full border border-white/30 bg-white/20 px-2.5 py-1 text-[9px] font-bold transition">VIP</span>
                    </div>
                    <div class="absolute inset-x-0 bottom-0 bg-gradient-to-t from-slate-950/90 via-slate-950/45 to-transparent px-6 pb-5 pt-14">
                      <h2 id="previewEventTitle" class="text-[23px] font-bold leading-none tracking-[-0.04em]">Sound of Tomorrow</h2>
                      <p id="previewEventSub" class="mt-1 text-xs text-slate-200">Konser Nusantara 2026</p>
                      <div class="mt-4 grid grid-cols-2 gap-y-1 text-[10px] text-white/90">
                        <span id="previewEventDate" class="flex items-center gap-1">
                          <svg class="h-3 w-3 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                          25 Okt 2026
                        </span>
                        <span id="previewEventTime" class="flex items-center gap-1">
                          <svg class="h-3 w-3 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                          19:00 WIB
                        </span>
                        <span class="col-span-2 flex items-center justify-between pt-0.5">
                          <span id="previewEventLocation" class="flex items-center gap-1">
                            <svg class="h-3 w-3 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                            Jakarta, Indonesia
                          </span>
                          <span id="previewNamaDisplay" class="font-medium text-white">Nama Pembeli</span>
                        </span>
                      </div>
                    </div>
                  </div>
                  <div class="relative flex h-7 items-center"><span class="absolute -left-3 h-6 w-6 rounded-full bg-[#f0ecff]"></span><div class="mx-6 w-full border-t-2 border-dashed border-slate-200"></div><span class="absolute -right-3 h-6 w-6 rounded-full bg-[#f0ecff]"></span></div>
                  
                  <!-- QR Code Preview Asli -->
                  <div class="px-6 pb-5 text-center">
                    <div id="previewQrContainer" class="mx-auto flex items-center justify-center p-3 bg-white rounded-2xl shadow-sm border border-slate-100 w-[146px] h-[146px]"></div>
                    <p class="mt-3 font-mono text-[15px] font-bold tracking-[.08em] text-violet-700">TKT-SAMPLE-PREVIEW</p>
                    <p class="mt-1 text-[8px] font-bold tracking-[.14em] text-slate-400">RSA DIGITAL SIGNATURE VERIFIED</p>
                    <div class="mt-4 flex items-center justify-center gap-1 text-[10px] font-semibold text-violet-600 bg-violet-50 rounded-full py-1 px-3">
                      <span>✓ Siap Diterbitkan</span>
                    </div>
                  </div>
        </div>
      </div>
    </section>
    </main>

    <!-- Client-side Logic untuk Interaktivitas Lengkap -->
    <script>
      const eventsData = {events_json};
      let currentEvent = "Sound of Tomorrow";
      let currentKategori = "VIP";

      // Inisialisasi QR Code Preview
      new QRCode(document.getElementById("previewQrContainer"), {{
        text: "TKT-PREVIEW-DEMO",
        width: 122,
        height: 122,
        colorDark : "#0f172a",
        colorLight : "#ffffff",
        correctLevel : QRCode.CorrectLevel.M
      }});

      function toggleEventDropdown() {{
        const menu = document.getElementById("eventDropdownMenu");
        const chevron = document.getElementById("eventChevron");
        menu.classList.toggle("hidden");
        chevron.classList.toggle("rotate-180");
      }}

      // Tutup dropdown jika klik di luar
      document.addEventListener("click", function(e) {{
        const btn = document.getElementById("eventDropdownBtn");
        const menu = document.getElementById("eventDropdownMenu");
        const chevron = document.getElementById("eventChevron");
        if (btn && menu && !btn.contains(e.target) && !menu.contains(e.target)) {{
          menu.classList.add("hidden");
          if (chevron) chevron.classList.remove("rotate-180");
        }}
      }});

      function selectEvent(eventName) {{
        currentEvent = eventName;
        document.getElementById("eventInput").value = eventName;
        const ev = eventsData[eventName];
        
        // Update Tampilan Tombol Dropdown
        document.getElementById("selectedEventImg").src = ev.img;
        document.getElementById("selectedEventName").textContent = eventName;
        document.getElementById("selectedEventSub").textContent = ev.sub + " · " + ev.location.split(",")[0];
        document.getElementById("eventDropdownMenu").classList.add("hidden");
        document.getElementById("eventChevron").classList.remove("rotate-180");

        // Update Live Preview Card
        document.getElementById("previewCardHero").style.backgroundImage = "url('" + ev.img + "')";
        document.getElementById("previewEventTitle").textContent = eventName;
        document.getElementById("previewEventSub").textContent = ev.sub;
        
        document.getElementById("previewEventDate").innerHTML = '<svg class="h-3 w-3 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>' + ev.date;
        document.getElementById("previewEventTime").innerHTML = '<svg class="h-3 w-3 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>' + ev.time;
        document.getElementById("previewEventLocation").innerHTML = '<svg class="h-3 w-3 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>' + ev.location;

        updatePrice();
      }}

      function selectCategory(cat) {{
        currentKategori = cat;
        document.getElementById("kategoriInput").value = cat;

        const btnReg = document.getElementById("btnRegular");
        const btnVip = document.getElementById("btnVIP");
        const badge = document.getElementById("previewKategoriBadge");

        if (cat === "Regular") {{
          btnReg.className = "h-12 flex-1 rounded-full border border-violet-600 bg-violet-600 text-white shadow-[0_6px_16px_rgba(124,58,237,.32)] text-sm font-semibold transition cursor-pointer";
          btnVip.className = "h-12 flex-1 rounded-full border border-slate-200 bg-white/70 text-slate-600 text-sm font-semibold transition hover:bg-white cursor-pointer";
          badge.textContent = "REGULAR";
        }} else {{
          btnVip.className = "h-12 flex-1 rounded-full border border-violet-600 bg-violet-600 text-white shadow-[0_6px_16px_rgba(124,58,237,.32)] text-sm font-semibold transition cursor-pointer";
          btnReg.className = "h-12 flex-1 rounded-full border border-slate-200 bg-white/70 text-slate-600 text-sm font-semibold transition hover:bg-white cursor-pointer";
          badge.textContent = "VIP";
        }}

        updatePrice();
      }}

      function updatePrice() {{
        const ev = eventsData[currentEvent];
        const price = currentKategori === "VIP" ? ev.price_vip : ev.price_regular;
        document.getElementById("priceDisplay").textContent = price;
      }}

      // Live update Nama
      document.getElementById("namaInput").addEventListener("input", function() {{
        const val = this.value.trim();
        document.getElementById("previewNamaDisplay").textContent = val ? val : "Nama Pembeli";
      }});
    </script>
    """
    return get_page(body, "beli")


@app.route("/gate", methods=["GET", "POST"])
def gate():
    result_html = ""
    if request.method == "POST":
        token = request.form.get("token", "").strip()
        ok, msg, info = check_ticket(token)
        if ok:
            result_html = f"""
            <div class="mt-8 border-l-4 border-emerald-500 bg-emerald-50/80 rounded-r-2xl p-5 text-left flex gap-4 shadow-sm animate-fade-in">
              <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-emerald-100 text-emerald-600 shadow-sm">
                <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
              </div>
              <div class="flex-1">
                <h2 class="font-bold text-emerald-800 text-base">Tiket Sah & Valid</h2>
                <p class="mt-0.5 text-xs text-emerald-700 leading-relaxed">{msg}</p>
                <div class="mt-3.5 rounded-xl bg-white/90 p-3.5 border border-emerald-200/70 text-xs text-slate-700 space-y-1">
                  <p class="flex items-center justify-between"><span>Nama:</span> <b class="text-slate-900">{info['nama']}</b></p>
                  <p class="flex items-center justify-between"><span>Event:</span> <b class="text-slate-900">{info['event']}</b></p>
                  <p class="flex items-center justify-between"><span>Kategori:</span> <span class="rounded-full bg-violet-100 px-2 py-0.5 font-bold text-violet-700 text-[11px]">{info['kategori']}</span></p>
                </div>
              </div>
            </div>
            """
        else:
            if "sudah pernah" in msg.lower():
                result_html = f"""
                <div class="mt-8 border-l-4 border-amber-500 bg-amber-50/80 rounded-r-2xl p-5 text-left flex gap-4 shadow-sm">
                  <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-amber-100 text-amber-600 shadow-sm">
                    <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
                  </div>
                  <div>
                    <h2 class="font-bold text-amber-800 text-base">Tiket Sudah Digunakan</h2>
                    <p class="mt-1 text-sm text-slate-600">{msg}</p>
                    <p class="mt-2 text-xs text-amber-700">Pencegahan manipulasi: tiket hanya dapat dipindai 1 kali di pintu masuk.</p>
                  </div>
                </div>
                """
            else:
                result_html = f"""
                <div class="mt-8 border-l-4 border-rose-500 bg-rose-50/80 rounded-r-2xl p-5 text-left flex gap-4 shadow-sm">
                  <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-rose-100 text-rose-600 shadow-sm">
                    <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                  </div>
                  <div>
                    <h2 class="font-bold text-rose-800 text-base">Tiket Ditolak (Tidak Sah)</h2>
                    <p class="mt-1 text-sm text-slate-600">{msg}</p>
                    <p class="mt-2 text-xs text-rose-700">Tanda tangan digital RSA tidak cocok dengan payload tiket atau kode tidak terdaftar.</p>
                  </div>
                </div>
                """

    body = f"""
    <main class="mx-auto max-w-[560px] px-6 py-14 text-center">
      <p class="text-xs font-bold tracking-[.18em] text-violet-700 uppercase">GATE CONTROL</p>
      <h1 class="mt-3 text-[34px] font-bold leading-tight tracking-[-.035em]">Pemeriksaan Tiket</h1>
      <p class="mx-auto mt-3 max-w-[470px] text-sm leading-6 text-slate-500">Pindai QR Code tiket menggunakan scanner kamera atau masukkan kode tiket secara manual.</p>
      
      <!-- Navigasi Mode: Scan Kamera vs Input Manual -->
      <div class="mt-8 flex justify-center gap-2 rounded-full bg-slate-200/70 p-1.5 max-w-[340px] mx-auto border border-slate-200/80">
        <button type="button" id="tabCameraBtn" onclick="switchMode('camera')" class="flex-1 flex items-center justify-center gap-2 rounded-full py-2.5 text-xs font-bold transition bg-white text-violet-700 shadow-sm cursor-pointer">
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/><path stroke-linecap="round" stroke-linejoin="round" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
          Scan Kamera
        </button>
        <button type="button" id="tabManualBtn" onclick="switchMode('manual')" class="flex-1 flex items-center justify-center gap-2 rounded-full py-2.5 text-xs font-semibold text-slate-500 hover:text-slate-900 transition cursor-pointer">
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
          Input Manual
        </button>
      </div>

      <!-- Mode 1: Kamera Scanner Asli -->
      <div id="cameraSection" class="mt-6">
        <div class="relative mx-auto w-full max-w-[400px] overflow-hidden rounded-3xl bg-slate-900 p-4 shadow-xl ring-1 ring-slate-800">
          <div class="relative w-full rounded-2xl overflow-hidden bg-black min-h-[300px] flex items-center justify-center">
            
            <!-- Video Reader Container (Terpisah dari placeholder agar bebas dari html5QrCode.clear()) -->
            <div id="reader" class="hidden w-full h-full min-h-[300px]"></div>

            <!-- Placeholder saat kamera mati (aman di DOM, tidak pernah terhapus) -->
            <div id="cameraPlaceholder" class="p-6 text-center space-y-4">
              <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-800 text-violet-400">
                <svg class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/><path stroke-linecap="round" stroke-linejoin="round" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
              </div>
              <div>
                <p class="text-sm font-semibold text-white">Scanner Kamera Siaga</p>
                <p class="mt-1 text-xs text-slate-400">Klik tombol untuk mengaktifkan pemindai kamera</p>
              </div>
              <button type="button" onclick="startScanner()" class="rounded-full bg-violet-600 px-6 py-3 text-xs font-bold text-white shadow-lg shadow-violet-500/40 hover:bg-violet-500 transition cursor-pointer flex items-center justify-center gap-2 mx-auto">
                <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/><path stroke-linecap="round" stroke-linejoin="round" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                Aktifkan Kamera Scanner
              </button>
            </div>

            <!-- Loading saat menghubungkan ke kamera -->
            <div id="cameraLoading" class="hidden p-6 text-center text-slate-300 space-y-3">
              <div class="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-violet-500 border-r-transparent"></div>
              <p class="text-xs">Menghubungkan ke kamera...</p>
            </div>
          </div>
          
          <div id="cameraActiveBar" class="hidden mt-3 flex items-center justify-between px-3 text-xs text-slate-300">
            <span class="flex items-center gap-2"><span class="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>Scanner Kamera Aktif</span>
            <button type="button" onclick="stopScanner()" class="text-rose-400 hover:text-rose-300 font-semibold cursor-pointer">Matikan Kamera</button>
          </div>
        </div>
        <p class="mt-3 text-xs text-slate-500">Arahkan kamera ke QR Code tiket e-ticket untuk verifikasi otomatis secara instan.</p>
      </div>

      <!-- Mode 2: Input Manual -->
      <div id="manualSection" class="hidden mt-6">
        <form method="post" id="gateManualForm" class="relative">
          <input name="token" id="tokenManualInput" class="h-16 w-full rounded-2xl border-2 border-slate-200 bg-white px-6 text-center font-mono text-xl outline-none transition placeholder:text-slate-400 focus:border-violet-500 focus:ring-4 focus:ring-violet-100" placeholder="TKT-XXXX-XXXX" required />
          <button type="submit" class="mt-4 h-14 w-full rounded-full bg-gradient-to-r from-violet-600 to-purple-600 text-sm font-bold text-white shadow-[0_10px_20px_rgba(124,58,237,.2)] transition hover:-translate-y-0.5 hover:shadow-[0_14px_26px_rgba(124,58,237,.3)] cursor-pointer flex items-center justify-center gap-2">
            <span>Verifikasi Tiket Sekarang</span>
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          </button>
        </form>
      </div>

      <!-- Form Hidden untuk Auto-Submit Hasil Scan Kamera -->
      <form method="post" id="autoScanForm" class="hidden">
        <input type="hidden" name="token" id="autoTokenInput" />
      </form>

      {result_html}
    </main>

    <script>
      let html5QrCode = null;
      let isScanning = false;

      function switchMode(mode) {{
        const camSec = document.getElementById("cameraSection");
        const manSec = document.getElementById("manualSection");
        const camBtn = document.getElementById("tabCameraBtn");
        const manBtn = document.getElementById("tabManualBtn");

        if (mode === "camera") {{
          camSec.classList.remove("hidden");
          manSec.classList.add("hidden");
          camBtn.className = "flex-1 flex items-center justify-center gap-2 rounded-full py-2.5 text-xs font-bold transition bg-white text-violet-700 shadow-sm cursor-pointer";
          manBtn.className = "flex-1 flex items-center justify-center gap-2 rounded-full py-2.5 text-xs font-semibold text-slate-500 hover:text-slate-900 transition cursor-pointer";
        }} else {{
          stopScanner();
          camSec.classList.add("hidden");
          manSec.classList.remove("hidden");
          manBtn.className = "flex-1 flex items-center justify-center gap-2 rounded-full py-2.5 text-xs font-bold transition bg-white text-violet-700 shadow-sm cursor-pointer";
          camBtn.className = "flex-1 flex items-center justify-center gap-2 rounded-full py-2.5 text-xs font-semibold text-slate-500 hover:text-slate-900 transition cursor-pointer";
        }}
      }}

      async function startScanner() {{
        const placeholder = document.getElementById("cameraPlaceholder");
        const loading = document.getElementById("cameraLoading");
        const reader = document.getElementById("reader");
        const activeBar = document.getElementById("cameraActiveBar");

        placeholder.classList.add("hidden");
        loading.classList.remove("hidden");
        reader.classList.add("hidden");
        activeBar.classList.add("hidden");

        try {{
          if (!html5QrCode) {{
            html5QrCode = new Html5Qrcode("reader");
          }}
          
          const config = {{ fps: 10, qrbox: {{ width: 230, height: 230 }} }};

          // Ambil daftar kamera yang tersedia di perangkat (laptop/hp)
          const devices = await Html5Qrcode.getCameras();
          if (devices && devices.length > 0) {{
            // Default pakai kamera pertama (biasanya webcam laptop)
            let cameraId = devices[0].id;
            
            // Jika ada kamera belakang (untuk HP), kita utamakan
            for (let i = 0; i < devices.length; i++) {{
              let label = devices[i].label.toLowerCase();
              if (label.includes("back") || label.includes("belakang") || label.includes("environment")) {{
                cameraId = devices[i].id;
                break;
              }}
            }}

            await html5QrCode.start(
              cameraId,
              config,
              (decodedText) => {{
                stopScanner();
                document.getElementById("autoTokenInput").value = decodedText.trim();
                document.getElementById("autoScanForm").submit();
              }},
              (errorMessage) => {{
                // Abaikan error per-frame (normal saat belum ada QR yang jelas)
              }}
            );

            isScanning = true;
            loading.classList.add("hidden");
            reader.classList.remove("hidden");
            activeBar.classList.remove("hidden");
          }} else {{
            throw new Error("Tidak ada kamera yang terdeteksi di perangkat ini.");
          }}
        }} catch (err) {{
          console.error("Camera Error:", err);
          alert("Gagal membuka kamera: " + err + "\\n\\nPastikan Anda memberikan izin kamera di browser. Mengalihkan ke mode Input Manual."); switchMode("manual");
          loading.classList.add("hidden");
          reader.classList.add("hidden");
          placeholder.classList.remove("hidden");
          activeBar.classList.add("hidden");
          isScanning = false;
        }}
      }}

      async function stopScanner() {{
        if (html5QrCode && isScanning) {{
          try {{
            await html5QrCode.stop();
          }} catch (e) {{
            console.log("Stop error:", e);
          }}
          isScanning = false;
        }}

        const placeholder = document.getElementById("cameraPlaceholder");
        const loading = document.getElementById("cameraLoading");
        const reader = document.getElementById("reader");
        const activeBar = document.getElementById("cameraActiveBar");

        if (reader) reader.classList.add("hidden");
        if (loading) loading.classList.add("hidden");
        if (placeholder) placeholder.classList.remove("hidden");
        if (activeBar) activeBar.classList.add("hidden");
      }}
    </script>
    """
    return get_page(body, "gate")


@app.route("/admin")
def admin():
    """Hanya untuk demo/presentasi: menampilkan komponen RSA."""
    body = f"""
    <main class="mx-auto max-w-[900px] px-6 py-14">
      <p class="text-xs font-bold tracking-[.18em] text-violet-700 uppercase">BEHIND THE SECURITY</p>
      <h1 class="mt-3 text-[34px] font-bold tracking-[-.035em]">Kontrol di balik setiap tiket.</h1>
      <p class="mt-3 text-sm text-slate-500">Informasi kunci RSA dan parameter kriptografi yang aktif di server.</p>
      
      <div class="mt-8 rounded-xl border border-violet-200 bg-violet-50/80 px-5 py-4 text-sm leading-6 text-violet-900/80">
        <b>Bagaimana RSA melindungi tiket ini?</b> Setiap tiket ditandatangani dengan <b>Private Key (d)</b> panitia saat pembelian. Pintu gerbang (Gate) hanya memverifikasi keaslian tanda tangan menggunakan <b>Public Key (e, n)</b>. Jika isi tiket diubah (misalnya status Regular diubah jadi VIP oleh calo), tanda tangan digital otomatis menjadi invalid.
      </div>
      
      <section class="mt-8 grid grid-cols-3 gap-5">
        <article class="relative rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-violet-100 text-violet-600">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/></svg>
          </div>
          <p class="mt-5 text-[11px] font-bold tracking-[.1em] text-slate-500 uppercase">PUBLIC KEY (e)</p>
          <p class="mt-1 text-[28px] font-bold tracking-[-.04em] text-slate-900">{E}</p>
          <p class="mt-4 text-xs text-slate-400">Ditanam di scanner gate</p>
        </article>
        
        <article class="relative rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-violet-100 text-violet-600">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/></svg>
          </div>
          <p class="mt-5 text-[11px] font-bold tracking-[.1em] text-slate-500 uppercase">MODULUS (n)</p>
          <p class="mt-1 text-[28px] font-bold tracking-[-.04em] text-slate-900">{str(N)[:10]}...</p>
          <p class="mt-4 text-xs text-slate-400">Panjang: {N.bit_length()} bit</p>
        </article>
        
        <article class="relative rounded-2xl border border-red-200 bg-red-50/75 p-6 shadow-sm">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-rose-100 text-rose-600">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
          </div>
          <p class="mt-5 text-[11px] font-bold tracking-[.1em] text-red-700 uppercase">PRIVATE KEY (d)</p>
          <p class="mt-1 text-[28px] font-bold tracking-[-.04em] text-red-900">{str(D)[:10]}...</p>
          <p class="mt-4 text-xs text-red-600/80">RAHASIA — hanya panitia.</p>
        </article>
      </section>
    </main>
    """
    return get_page(body, "admin")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)