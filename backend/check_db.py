import sqlite3

conn = sqlite3.connect('skj.db')
cursor = conn.cursor()

print("Tables in database:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f"  - {table[0]}")

print("\nColumns in users table:")
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

print("\nColumns in challenges table:")
cursor.execute("PRAGMA table_info(challenges)")
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

print("\nAchievements:")
cursor.execute("SELECT name, description FROM achievements")
achievements = cursor.fetchall()
for ach in achievements:
    print(f"  - {ach[0]}: {ach[1]}")

conn.close()