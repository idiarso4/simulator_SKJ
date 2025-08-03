"""
Migration: Enhance user system with authentication and roles
"""

def up(conn):
    """Apply the migration"""
    cursor = conn.cursor()
    
    # Add new columns to users table
    columns_to_add = [
        ("email", "TEXT UNIQUE"),
        ("password_hash", "TEXT"),
        ("class_id", "INTEGER"),
        ("profile_picture", "TEXT"),
        ("preferences", "TEXT"),
        ("last_active", "TEXT")
    ]
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    for column_name, column_type in columns_to_add:
        if column_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")
            except Exception as e:
                print(f"Warning: Could not add column {column_name}: {e}")
    
    # Ensure role column exists (it should from original schema)
    if "role" not in existing_columns:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'student'")
        except Exception as e:
            print(f"Warning: Could not add role column: {e}")
    
    # Create classes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            teacher_id INTEGER NOT NULL,
            semester INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (teacher_id) REFERENCES users(id)
        )
    """)
    
    # Create achievements table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            icon TEXT,
            type TEXT NOT NULL,
            criteria TEXT,
            points INTEGER DEFAULT 0,
            rarity TEXT DEFAULT 'common'
        )
    """)
    
    # Create user_achievements table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            achievement_id INTEGER NOT NULL,
            earned_at TEXT NOT NULL,
            progress REAL DEFAULT 1.0,
            UNIQUE(user_id, achievement_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (achievement_id) REFERENCES achievements(id)
        )
    """)
    
    conn.commit()

def down(conn):
    """Rollback the migration (optional)"""
    # This would remove the changes, but we'll keep it simple for now
    pass