"""
Migration: Enhance challenges with advanced properties
"""

def up(conn):
    """Apply the migration"""
    cursor = conn.cursor()
    
    # Add new columns to challenges table
    try:
        cursor.execute("ALTER TABLE challenges ADD COLUMN description TEXT")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE challenges ADD COLUMN difficulty TEXT DEFAULT 'beginner'")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE challenges ADD COLUMN simulation_type TEXT DEFAULT 'visual'")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE challenges ADD COLUMN simulation_config TEXT")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE challenges ADD COLUMN hints TEXT")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE challenges ADD COLUMN solution TEXT")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE challenges ADD COLUMN points INTEGER DEFAULT 50")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE challenges ADD COLUMN time_limit INTEGER")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE challenges ADD COLUMN prerequisites TEXT")
    except:
        pass
    
    conn.commit()

def down(conn):
    """Rollback the migration (optional)"""
    pass