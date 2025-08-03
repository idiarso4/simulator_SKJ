import sqlite3
import os
from pathlib import Path
from datetime import datetime
import importlib.util

class MigrationManager:
    def __init__(self, db_path, migrations_dir):
        self.db_path = Path(db_path)
        self.migrations_dir = Path(migrations_dir)
        self.init_migrations_table()
    
    def init_migrations_table(self):
        """Initialize the migrations tracking table"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT UNIQUE NOT NULL,
                    applied_at TEXT NOT NULL
                )
            """)
            conn.commit()
    
    def get_applied_migrations(self):
        """Get list of already applied migrations"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT filename FROM migrations ORDER BY filename")
            return [row[0] for row in cursor.fetchall()]
    
    def get_pending_migrations(self):
        """Get list of migrations that need to be applied"""
        applied = set(self.get_applied_migrations())
        all_migrations = []
        
        if self.migrations_dir.exists():
            for file in sorted(self.migrations_dir.glob("*.py")):
                if file.name != "__init__.py" and file.name not in applied:
                    all_migrations.append(file.name)
        
        return all_migrations
    
    def apply_migration(self, filename):
        """Apply a single migration"""
        migration_path = self.migrations_dir / filename
        
        # Load the migration module
        spec = importlib.util.spec_from_file_location("migration", migration_path)
        migration_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration_module)
        
        # Apply the migration
        with sqlite3.connect(self.db_path) as conn:
            if hasattr(migration_module, 'up'):
                migration_module.up(conn)
            
            # Record the migration as applied
            conn.execute(
                "INSERT INTO migrations (filename, applied_at) VALUES (?, ?)",
                (filename, datetime.utcnow().isoformat())
            )
            conn.commit()
        
        print(f"Applied migration: {filename}")
    
    def run_migrations(self):
        """Run all pending migrations"""
        pending = self.get_pending_migrations()
        
        if not pending:
            print("No pending migrations")
            return
        
        print(f"Applying {len(pending)} migrations...")
        for migration in pending:
            self.apply_migration(migration)
        
        print("All migrations applied successfully")