import sqlite3
conn = sqlite3.connect('D:/diceiq/diceiq.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", tables)
for table in tables:
    tname = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {tname}")
    count = cursor.fetchone()[0]
    cursor.execute(f"PRAGMA table_info({tname})")
    cols = cursor.fetchall()
    print(f"\n{tname} ({count} rows)")
    print("Columns:", [c[1] for c in cols])
    if count > 0:
        cursor.execute(f"SELECT * FROM {tname} LIMIT 2")
        print("Sample:", cursor.fetchall())
conn.close()
