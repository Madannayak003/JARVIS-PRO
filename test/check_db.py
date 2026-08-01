import sqlite3

try:
    conn = sqlite3.connect("ai/memory.db")
    result = conn.execute("PRAGMA integrity_check;").fetchone()
    print(result)
    conn.close()
except Exception as e:
    print(e)