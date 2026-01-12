import sqlite3
from datetime import datetime

# Connect to the database (creates it if it doesn't exist)
conn = sqlite3.connect("nethogs_daily.db")
cursor = conn.cursor()

# Create the table
cursor.execute("""
CREATE TABLE IF NOT EXISTS days (
    name TEXT,
    day TEXT,  -- format: "YYYY-MM-DD"
    kbps_down FLOAT,
    kbps_up FLOAT,
    kbps_total FLOAT,
    last_update TEXT,
    PRIMARY KEY (name, day)
)
""")

conn.commit()

def add_process_data(name: str, kbps_down: float, kbps_up: float):
    kbps_total = kbps_down + kbps_up
    last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    day = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
    INSERT INTO days (name, day, kbps_down, kbps_up, kbps_total, last_update)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(name, day) DO UPDATE SET
        kbps_down = kbps_down + excluded.kbps_down,
        kbps_up = kbps_up + excluded.kbps_up,
        kbps_total = kbps_total + excluded.kbps_total,
        last_update = excluded.last_update
    """, (name, day, kbps_down, kbps_up, kbps_total, last_update))

    conn.commit()

def get_today_data():
    day = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT name, kbps_down, kbps_up, kbps_total, last_update FROM days WHERE day = ?", (day,))
    return cursor.fetchall()

def get_process_history(name: str):
    cursor.execute("SELECT day, kbps_down, kbps_up, kbps_total FROM days WHERE name = ? ORDER BY day", (name,))
    return cursor.fetchall()

def get_total_usage(name: str):
    cursor.execute("SELECT SUM(kbps_down), SUM(kbps_up), SUM(kbps_total) FROM days WHERE name = ?", (name,))
    return cursor.fetchone()
