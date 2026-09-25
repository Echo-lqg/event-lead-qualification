import sqlite3
import pandas as pd

df = pd.read_csv("companies.csv")

conn = sqlite3.connect("event_leads.db")
#conn你和数据库之间的“连接”

cursor = conn.cursor()
#cursor= 通过这个连接，真正去执行 SQL 命令的“操作员”

cursor.execute("""
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    expected_event TEXT,
    case_type TEXT,
    company_size INTEGER,
    industry_fit INTEGER,
    past_event_engagement INTEGER,
    sponsorship_potential INTEGER
)
""")

#Insert CSV rows into the database

conn.commit()
conn.close()

print("Database connected successfully")



conn.close()