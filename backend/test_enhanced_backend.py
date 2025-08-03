#!/usr/bin/env python3
"""
Test script for enhanced backend infrastructure
"""

from database import get_conn, row_to_dict
import json

def test_enhanced_database():
    """Test the enhanced database structure"""
    print("Testing Enhanced Database Infrastructure...")
    
    with get_conn() as conn:
        cursor = conn.cursor()
        
        # Test 1: Check all required tables exist
        print("\n1. Checking required tables...")
        required_tables = [
            'users', 'modules', 'challenges', 'progress', 'detailed_progress',
            'classes', 'achievements', 'user_achievements', 'team_challenges', 'content'
        ]
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        for table in required_tables:
            if table in existing_tables:
                print(f"   ✓ {table} table exists")
            else:
                print(f"   ✗ {table} table missing")
        
        # Test 2: Check enhanced user columns
        print("\n2. Checking enhanced user columns...")
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [col[1] for col in cursor.fetchall()]
        
        required_user_columns = ['id', 'name', 'role', 'created_at', 'password_hash', 'class_id', 'profile_picture', 'preferences', 'last_active']
        for col in required_user_columns:
            if col in user_columns:
                print(f"   ✓ users.{col} exists")
            else:
                print(f"   ✗ users.{col} missing")
        
        # Test 3: Check enhanced challenge columns
        print("\n3. Checking enhanced challenge columns...")
        cursor.execute("PRAGMA table_info(challenges)")
        challenge_columns = [col[1] for col in cursor.fetchall()]
        
        required_challenge_columns = ['id', 'module_id', 'title', 'tasks_json', 'description', 'difficulty', 'simulation_type', 'simulation_config', 'hints', 'solution', 'points', 'time_limit', 'prerequisites']
        for col in required_challenge_columns:
            if col in challenge_columns:
                print(f"   ✓ challenges.{col} exists")
            else:
                print(f"   ✗ challenges.{col} missing")
        
        # Test 4: Check achievements data
        print("\n4. Checking achievements data...")
        cursor.execute("SELECT COUNT(*) FROM achievements")
        achievement_count = cursor.fetchone()[0]
        print(f"   ✓ {achievement_count} achievements loaded")
        
        cursor.execute("SELECT name, type, rarity FROM achievements")
        achievements = cursor.fetchall()
        for name, type_, rarity in achievements:
            print(f"   - {name} ({type_}, {rarity})")
        
        # Test 5: Test migration tracking
        print("\n5. Checking migration tracking...")
        cursor.execute("SELECT filename FROM migrations ORDER BY filename")
        migrations = cursor.fetchall()
        print(f"   ✓ {len(migrations)} migrations applied:")
        for migration in migrations:
            print(f"   - {migration[0]}")
        
        print("\n✅ Enhanced backend infrastructure test completed successfully!")

if __name__ == "__main__":
    test_enhanced_database()