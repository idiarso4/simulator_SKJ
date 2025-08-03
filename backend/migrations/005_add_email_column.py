"""
Migration: Add email column to users table properly
"""

def up(conn):
    """Apply the migration"""
    cursor = conn.cursor()
    
    # Check if email column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "email" not in columns:
        # Since we can't add UNIQUE constraint to existing table, we'll add without it
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
        print("Added email column to users table")
    
    conn.commit()

def down(conn):
    """Rollback the migration (optional)"""
    pass