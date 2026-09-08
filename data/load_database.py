import sqlite3
import pandas as pd

CSV_PATH = "data/alerts (2).csv"
DB_PATH = "data/alerts.db"

# Read CSV
df = pd.read_csv(CSV_PATH)

# Connect to SQLite
conn = sqlite3.connect(DB_PATH)

# Load dataframe into SQLite
df.to_sql(
    "alerts",
    conn,
    if_exists="replace",
    index=False
)

# Create an index for commonly filtered columns
cursor = conn.cursor()

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_facility
ON alerts(facility_id)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_severity
ON alerts(severity)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_ward
ON alerts(ward)
""")

conn.commit()

# Verify
count = cursor.execute(
    "SELECT COUNT(*) FROM alerts"
).fetchone()[0]

print(f"Successfully loaded {count:,} alerts into SQLite.")

conn.close()