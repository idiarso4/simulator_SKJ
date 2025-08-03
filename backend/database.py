import sqlite3
from pathlib import Path
from datetime import datetime
from migrations.migration_manager import MigrationManager

DB_PATH = Path(__file__).parent / "skj.db"
MIGRATIONS_DIR = Path(__file__).parent / "migrations"

def get_conn():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with basic tables"""
    with get_conn() as conn:
        cur = conn.cursor()
        
        # Create basic tables (existing structure)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            role TEXT DEFAULT 'student',
            created_at TEXT NOT NULL
        )
        """)
        
        cur.execute("""
        CREATE TABLE IF NOT EXISTS modules (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            semester INTEGER NOT NULL
        )
        """)
        
        cur.execute("""
        CREATE TABLE IF NOT EXISTS challenges (
            id TEXT PRIMARY KEY,
            module_id TEXT NOT NULL,
            title TEXT NOT NULL,
            tasks_json TEXT NOT NULL,
            FOREIGN KEY (module_id) REFERENCES modules(id)
        )
        """)
        
        cur.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            challenge_id TEXT NOT NULL,
            status TEXT NOT NULL,
            points INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL,
            UNIQUE(user_id, challenge_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (challenge_id) REFERENCES challenges(id)
        )
        """)
        
        cur.execute("""
        CREATE TABLE IF NOT EXISTS detailed_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            challenge_id TEXT NOT NULL,
            action TEXT NOT NULL,
            payload TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (challenge_id) REFERENCES challenges(id)
        )
        """)
        
        conn.commit()

def run_migrations():
    """Run database migrations"""
    migration_manager = MigrationManager(DB_PATH, MIGRATIONS_DIR)
    migration_manager.run_migrations()

def setup_database():
    """Complete database setup including migrations"""
    init_db()
    run_migrations()

def seed_if_empty():
    """Seed database with initial data if empty"""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS c FROM modules")
        if cur.fetchone()["c"] == 0:
            modules = [
                ("m1", "Modul 1: Pengenalan Ancaman", 1),
                ("m2", "Modul 2: Enkripsi Dasar", 1),
                ("m3", "Modul 3: Firewall & Keamanan", 1),
                ("m4", "Modul 4: Konfigurasi Firewall", 2),
                ("m5", "Modul 5: Scanning & Monitoring", 2),
                ("m6", "Modul 6: Autentikasi & AAA", 2),
                ("m7", "Modul 7: Penetration Testing", 3),
                ("m8", "Modul 8: IDS/IPS & SIEM", 3),
                ("m9", "Modul 9: PKI & Sertifikat", 3),
                ("m10","Modul 10: Desain Keamanan", 4),
                ("m11","Modul 11: Cyber Attack Simulation", 4),
                ("m12","Modul 12: Laporan Teknis", 4),
            ]
            cur.executemany("INSERT INTO modules(id,title,semester) VALUES(?,?,?)", modules)

            challenges = [
                ("c1", "m1", "Phishing Email Attack", '["Baca email mencurigakan","Identifikasi indikator","Laporkan"]'),
                ("c2", "m1", "DDoS Attack Visualization", '["Amati trafik","Aktifkan rate-limit","Verifikasi"]'),
                ("c3", "m2", "Caesar Cipher", '["Masukkan pesan","Geser kunci","Bandingkan"]'),
                ("c4", "m3", "Packet Filtering", '["Tentukan rule","Blokir port 23","Uji paket"]'),
                ("c5", "m4", "NAT & Port Forwarding", '["Tambah rule NAT","Port forward 8080->80","Verifikasi"]'),
                ("c6", "m5", "Nmap Scan Virtual", '["Pilih target","Scan","Analisis hasil"]'),
                ("c7", "m6", "Simulasi MFA", '["Password","OTP","Akses diberikan"]'),
                ("c8", "m7", "Eksploitasi Dasar", '["Enumerasi","Temukan CVE","Eksploitasi aman"]'),
                ("c9", "m8", "Snort Rule Basics", '["Aktifkan rule","Picu alert","Analisis log"]'),
                ("c10","m9", "TLS Handshake Visual", '["Client hello","Verifikasi sertifikat","Negosiasi kunci"]'),
                ("c11","m10","Security Zone Planning", '["Buat DMZ","Pisahkan VLAN","Redundansi"]'),
                ("c12","m11","Ransomware Scenario", '["Isolasi host","Pulihkan backup","Review kebijakan"]'),
                ("c13","m12","Template Reporting", '["Isi temuan","Tambah bukti","Ekspor"]'),
            ]
            cur.executemany("INSERT INTO challenges(id,module_id,title,tasks_json) VALUES(?,?,?,?)", challenges)
            
            # Seed some basic achievements
            achievements = [
                ("First Steps", "Complete your first challenge", "🎯", "challenge", '{"challenges_completed": 1}', 10, "common"),
                ("Quick Learner", "Complete a challenge in under 5 minutes", "⚡", "challenge", '{"time_limit": 300}', 25, "rare"),
                ("Persistent", "Complete 10 challenges", "🏆", "milestone", '{"challenges_completed": 10}', 100, "epic"),
                ("Team Player", "Complete a team challenge", "🤝", "collaboration", '{"team_challenges": 1}', 50, "rare"),
                ("Streak Master", "Maintain a 7-day learning streak", "🔥", "streak", '{"streak_days": 7}', 75, "epic"),
            ]
            cur.executemany("INSERT INTO achievements(name,description,icon,type,criteria,points,rarity) VALUES(?,?,?,?,?,?,?)", achievements)
            
            conn.commit()

# Helper function for row to dict conversion
def row_to_dict(row):
    """Convert SQLite row to dictionary"""
    return {k: row[k] for k in row.keys()}