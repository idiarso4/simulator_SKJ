# 🧪 Testing SKJ Simulator Pro - Enhanced Backend

## 📋 Prerequisites

Pastikan Anda sudah menginstall dependencies:
```bash
cd backend
pip install -r requirements.txt
```

## 🚀 Menjalankan Aplikasi

### 1. Start Backend (Terminal 1)
```bash
cd backend
python app.py
```

Backend akan berjalan di: `http://127.0.0.1:5001`

### 2. Start Frontend (Terminal 2)
```bash
python start_frontend.py
```

Frontend akan berjalan di: `http://localhost:8000`

## 🔍 Testing Enhanced Features

### 1. **Enhanced Authentication**
- Buka browser ke `http://localhost:8000`
- Klik tab "Profile" 
- Masukkan nama dan simpan
- Sistem akan otomatis membuat user dengan enhanced authentication

### 2. **Role-Based Access Control**
Test dengan berbagai role:

**Create Admin User:**
```bash
curl -X POST http://127.0.0.1:5001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"admin","email":"admin@test.com","password":"admin123","role":"admin"}'
```

**Create Teacher:**
```bash
curl -X POST http://127.0.0.1:5001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"teacher","email":"teacher@test.com","password":"teacher123","role":"teacher"}'
```

**Login dan dapatkan token:**
```bash
curl -X POST http://127.0.0.1:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"name":"admin","password":"admin123"}'
```

### 3. **Class Management**
**Create Class (Teacher/Admin only):**
```bash
curl -X POST http://127.0.0.1:5001/api/classes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"name":"Keamanan Jaringan 101","semester":1,"description":"Kelas pengenalan keamanan jaringan","max_students":30}'
```

**List Classes:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://127.0.0.1:5001/api/classes
```

### 4. **Enhanced Challenges**
**Get Challenges with Advanced Properties:**
```bash
curl http://127.0.0.1:5001/api/modules
```

**Create Advanced Challenge:**
```bash
curl -X POST http://127.0.0.1:5001/api/challenges \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "id": "advanced_network_sim",
    "module_id": "m1", 
    "title": "Advanced Network Simulation",
    "description": "Interactive network topology challenge",
    "difficulty": "intermediate",
    "simulation_type": "network",
    "simulation_config": {
      "max_devices": 10,
      "device_types": ["router", "switch", "firewall"],
      "packet_simulation": true
    },
    "points": 150,
    "time_limit": 1800,
    "tags": ["networking", "simulation", "intermediate"]
  }'
```

### 5. **Role-Specific Dashboards**
**Student Dashboard:**
```bash
curl -H "Authorization: Bearer STUDENT_TOKEN" http://127.0.0.1:5001/api/dashboard/student
```

**Teacher Dashboard:**
```bash
curl -H "Authorization: Bearer TEACHER_TOKEN" http://127.0.0.1:5001/api/dashboard/teacher
```

**Admin Dashboard:**
```bash
curl -H "Authorization: Bearer ADMIN_TOKEN" http://127.0.0.1:5001/api/dashboard/admin
```

## 🎯 Frontend Testing

1. **Dashboard**: Lihat statistik dan progress pembelajaran
2. **Rooms**: Pilih semester dan modul pembelajaran  
3. **Challenges**: Coba challenge interaktif (Phishing, Caesar Cipher, Firewall)
4. **Leaderboard**: Lihat ranking berdasarkan poin
5. **Profile**: Kelola profil pengguna

## 🔧 Enhanced Features yang Bisa Ditest

### ✅ **Completed Features:**
1. **Enhanced Backend Infrastructure** - Database migrations, dependencies
2. **Enhanced User Management** - JWT auth, password hashing, user roles
3. **Role-Based Access Control** - 28 permissions, 3 roles, fine-grained access
4. **Class Management** - Create classes, student enrollment, class codes
5. **Enhanced Challenge Model** - 6 simulation types, 4 difficulty levels, prerequisites

### 🚧 **Next Features (Coming Soon):**
- Network simulation components
- Terminal simulation system  
- Real-time collaboration
- Advanced analytics
- Gamification system
- PWA features

## 🐛 Troubleshooting

**Backend tidak bisa diakses:**
- Pastikan backend berjalan di port 5001
- Check console untuk error messages
- Pastikan database migrations berhasil

**Frontend tidak connect ke backend:**
- Frontend akan auto-detect backend di port 5000-5100
- Check browser console untuk connection errors
- Pastikan CORS enabled di backend

**Database issues:**
- Delete `backend/skj.db` dan restart backend untuk fresh database
- Check migration logs untuk errors

## 📊 Database Structure

Enhanced database sekarang memiliki:
- **users**: Enhanced dengan email, password_hash, class_id, preferences
- **classes**: Class management dengan teacher assignment dan student limits  
- **challenges**: Advanced properties dengan simulation configs dan prerequisites
- **achievements**: Gamification system dengan badges dan points
- **progress**: Detailed tracking dengan analytics data

## 🎉 Success Indicators

Jika semuanya berjalan dengan baik, Anda akan melihat:
- ✅ Backend starts without errors
- ✅ Frontend connects dan load data dari backend
- ✅ User registration/login works
- ✅ Challenges dapat dimainkan dan progress tersimpan
- ✅ Leaderboard menampilkan ranking yang benar
- ✅ Role-based features bekerja sesuai permissions

Happy testing! 🚀