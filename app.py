"""
app.py - Aplikasi Tiket Konser Anti-Calo
Jalankan:  pip install flask   lalu   python app.py
Buka:      http://127.0.0.1:5000        (beli tiket)
           http://127.0.0.1:5000/gate   (pintu masuk / scan)
           http://127.0.0.1:5000/admin  (khusus demo: lihat kunci RSA)
"""
import base64
import json
import os
import uuid

from flask import Flask, request, render_template_string

import rsa

app = Flask(__name__)
KEY_FILE = "keys.json"
used_tickets = set()  # tiket yang sudah masuk (anti dipakai 2x)


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
    payload = f"{uuid.uuid4().hex[:10]}|{nama}|{event}|{kategori}"
    signature = rsa.sign(payload, D, N)  # private key panitia
    token = base64.urlsafe_b64encode(payload.encode()).decode() + "." + hex(signature)[2:]
    return token


def check_ticket(token):
    try:
        b64, sig_hex = token.strip().split(".")
        payload = base64.urlsafe_b64decode(b64.encode()).decode()
        signature = int(sig_hex, 16)
    except Exception:
        return False, "Tiket tidak valid", None
    if not rsa.verify(payload, signature, E, N):  # public key
        return False, "Tiket PALSU / sudah diubah", None
    tid, nama, event, kategori = payload.split("|")
    if tid in used_tickets:
        return False, "Tiket sudah pernah dipakai", None
    used_tickets.add(tid)
    return True, "Tiket valid, silakan masuk", {"nama": nama, "event": event, "kategori": kategori}


# ---------- Tampilan (tidak ada istilah RSA untuk user) ----------
PAGE = """
<!doctype html><html lang="id"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TiketKu</title>
<style>
 body{font-family:system-ui,sans-serif;background:#f3f0ff;margin:0;padding:24px}
 .card{max-width:480px;margin:auto;background:#fff;border-radius:16px;padding:24px;box-shadow:0 4px 20px #0001}
 input,select,textarea,button{width:100%;padding:12px;margin:6px 0;border-radius:8px;border:1px solid #ccc;box-sizing:border-box;font-size:15px}
 button{background:#6c3ef4;color:#fff;border:0;cursor:pointer;font-weight:600}
 .ok{background:#d9f7e4;padding:12px;border-radius:8px}.bad{background:#fde0e0;padding:12px;border-radius:8px}
 code,textarea{word-break:break-all;font-size:12px}nav a{margin-right:12px}
</style></head><body><div class="card">
<nav><a href="/">Beli Tiket</a><a href="/gate">Pintu Masuk</a></nav>
{{ body|safe }}
</div></body></html>
"""


@app.route("/", methods=["GET", "POST"])
def beli():
    body = """<h2>🎫 Beli Tiket</h2>
    <form method="post">
      <input name="nama" placeholder="Nama lengkap" required>
      <select name="event"><option>Konser Nusantara 2026</option><option>Festival Musik Surabaya</option></select>
      <select name="kategori"><option>Regular</option><option>VIP</option></select>
      <button>Beli Tiket</button></form>"""
    if request.method == "POST":
        token = create_ticket(request.form["nama"], request.form["event"], request.form["kategori"])
        body = f"""<h2>✅ Pembelian berhasil</h2>
        <p>Tunjukkan kode tiket ini di pintu masuk:</p>
        <textarea rows="6" readonly>{token}</textarea>"""
    return render_template_string(PAGE, body=body)


@app.route("/gate", methods=["GET", "POST"])
def gate():
    body = """<h2>🚪 Pintu Masuk</h2>
    <form method="post"><textarea name="token" rows="5" placeholder="Tempel kode tiket (hasil scan)" required></textarea>
    <button>Verifikasi</button></form>"""
    if request.method == "POST":
        ok, msg, info = check_ticket(request.form["token"])
        detail = f"<br>{info['nama']} - {info['event']} ({info['kategori']})" if info else ""
        body += f'<div class="{"ok" if ok else "bad"}">{"✅" if ok else "❌"} {msg}{detail}</div>'
    return render_template_string(PAGE, body=body)


@app.route("/admin")
def admin():
    """Hanya untuk demo/presentasi: menampilkan komponen RSA."""
    body = f"""<h2>🔧 Info RSA (demo)</h2>
    <p><b>n</b> ({N.bit_length()} bit):<br><code>{N}</code></p>
    <p><b>e</b> (public):<br><code>{E}</code></p>
    <p><b>d</b> (private):<br><code>{D}</code></p>"""
    return render_template_string(PAGE, body=body)


if __name__ == "__main__":
    app.run(debug=True)
