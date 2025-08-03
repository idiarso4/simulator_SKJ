# SKJ Backend (Flask + SQLite)

API sederhana untuk modul & challenge dengan penyimpanan SQLite.

## Persiapan
1) Pastikan Python 3.x terpasang.
2) Buka terminal di folder backend lalu jalankan:

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python app.py
```

Server berjalan di http://127.0.0.1:5000

## Endpoint Utama
- POST /api/users {"name": "Nama"} -> buat/ambil user
- GET  /api/modules -> daftar modules + challenges
- GET  /api/progress/<user_id> -> progress user
- POST /api/progress {"user_id":1,"challenge_id":"c1","status":"completed","points":50}
- GET  /api/leaderboard -> leaderboard agregat

## Integrasi Frontend
Ubah script.js agar:
- Membuat user (POST /api/users)
- Memuat modules dari /api/modules
- Menyimpan progress challenge ke /api/progress
- Menarik leaderboard dari /api/leaderboard
