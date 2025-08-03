"""
Migration: Add class_code column to classes table
"""

def up(conn):
    """Apply the migration"""
    cursor = conn.cursor()
    
    # Check if class_code column exists
    cursor.execute("PRAGMA table_info(classes)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "class_code" not in columns:
        cursor.execute("ALTER TABLE classes ADD COLUMN class_code TEXT")
        print("Added class_code column to classes table")
    
    conn.commit()

def down(conn):
    """Rollback the migration (optional)"""
    pass