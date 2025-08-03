"""
Migration: Enhance progress tracking with detailed analytics
"""

def up(conn):
    """Apply the migration"""
    cursor = conn.cursor()
    
    # Enhance detailed_progress table
    try:
        cursor.execute("ALTER TABLE detailed_progress ADD COLUMN session_id TEXT")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE detailed_progress ADD COLUMN start_time TEXT")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE detailed_progress ADD COLUMN end_time TEXT")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE detailed_progress ADD COLUMN actions TEXT")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE detailed_progress ADD COLUMN hints_used INTEGER DEFAULT 0")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE detailed_progress ADD COLUMN attempts INTEGER DEFAULT 1")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE detailed_progress ADD COLUMN final_score INTEGER DEFAULT 0")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE detailed_progress ADD COLUMN time_spent INTEGER DEFAULT 0")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE detailed_progress ADD COLUMN completion_rate REAL DEFAULT 0.0")
    except:
        pass
    
    # Create team_challenges table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS team_challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challenge_id TEXT NOT NULL,
            team_members TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            shared_state TEXT,
            created_at TEXT NOT NULL,
            completed_at TEXT,
            FOREIGN KEY (challenge_id) REFERENCES challenges(id)
        )
    """)
    
    # Create content management table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            content_data TEXT,
            file_attachments TEXT,
            version INTEGER DEFAULT 1,
            created_by INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            is_published BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    """)
    
    conn.commit()

def down(conn):
    """Rollback the migration (optional)"""
    pass