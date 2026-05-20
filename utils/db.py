import sqlite3

# -----------------------------------
# DATABASE CONNECTION
# -----------------------------------
conn = sqlite3.connect(
    "database/expense.db",
    check_same_thread=False
)

cursor = conn.cursor()

# -----------------------------------
# CREATE USERS TABLE
# -----------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    email TEXT UNIQUE,
    password BLOB
)
""")

conn.commit()