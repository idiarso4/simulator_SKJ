"""
Migration: Fix missing columns and add achievements
"""

def up(conn):
    """Apply the migration"""
    cursor = conn.cursor()
    
    # Check and add missing columns to users table
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    if "role" not in existing_columns:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'student'")
        except Exception as e:
            print(f"Warning: Could not add role column: {e}")
    
    if "email" not in existing_columns:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN email TEXT UNIQUE")
        except Exception as e:
            print(f"Warning: Could not add email column: {e}")
    
    # Add achievements if table is empty
    cursor.execute("SELECT COUNT(*) FROM achievements")
    if cursor.fetchone()[0] == 0:
        achievements = [
            ("First Steps", "Complete your first challenge", "🎯", "challenge", '{"challenges_completed": 1}', 10, "common"),
            ("Quick Learner", "Complete a challenge in under 5 minutes", "⚡", "challenge", '{"time_limit": 300}', 25, "rare"),
            ("Persistent", "Complete 10 challenges", "🏆", "milestone", '{"challenges_completed": 10}', 100, "epic"),
            ("Team Player", "Complete a team challenge", "🤝", "collaboration", '{"team_challenges": 1}', 50, "rare"),
            ("Streak Master", "Maintain a 7-day learning streak", "🔥", "streak", '{"streak_days": 7}', 75, "epic"),
        ]
        cursor.executemany("INSERT INTO achievements(name,description,icon,type,criteria,points,rarity) VALUES(?,?,?,?,?,?,?)", achievements)
    
    conn.commit()

def down(conn):
    """Rollback the migration (optional)"""
    pass