"""
Migration: Enhance classes table with additional fields
"""

def up(conn):
    """Apply the migration"""
    cursor = conn.cursor()
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(classes)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    # Add new columns if they don't exist
    columns_to_add = [
        ("description", "TEXT"),
        ("max_students", "INTEGER"),
        ("class_code", "TEXT UNIQUE")
    ]
    
    for column_name, column_type in columns_to_add:
        if column_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE classes ADD COLUMN {column_name} {column_type}")
                print(f"Added {column_name} column to classes table")
            except Exception as e:
                print(f"Warning: Could not add column {column_name}: {e}")
    
    conn.commit()

def down(conn):
    """Rollback the migration (optional)"""
    pass