"""
Migration: Add advanced properties to challenges table
"""

def up(conn):
    """Apply the migration"""
    cursor = conn.cursor()
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(challenges)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    # Add new columns if they don't exist
    columns_to_add = [
        ("created_at", "TEXT"),
        ("updated_at", "TEXT"),
        ("is_active", "BOOLEAN DEFAULT 1"),
        ("tags", "TEXT"),
        ("estimated_duration", "INTEGER")
    ]
    
    for column_name, column_type in columns_to_add:
        if column_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE challenges ADD COLUMN {column_name} {column_type}")
                print(f"Added {column_name} column to challenges table")
            except Exception as e:
                print(f"Warning: Could not add column {column_name}: {e}")
    
    # Update existing challenges with default values
    cursor.execute("""
        UPDATE challenges 
        SET created_at = datetime('now'), 
            updated_at = datetime('now'),
            is_active = 1
        WHERE created_at IS NULL
    """)
    
    conn.commit()

def down(conn):
    """Rollback the migration (optional)"""
    pass