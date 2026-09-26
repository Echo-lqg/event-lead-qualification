from openai_classifier import classify_company

import sqlite3
import pandas as pd

df = pd.read_csv("companies.csv")

conn = sqlite3.connect("event_leads.db")
#conn你和数据库之间的“连接”

cursor = conn.cursor()
#cursor= 通过这个连接，真正去执行 SQL 命令的“操作员”

# Create companies table
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

for _, row in df.iterrows():
    cursor.execute("""
    INSERT OR IGNORE INTO companies ( 
    name,
    description,
    expected_event,
    case_type,
    company_size,
    industry_fit,
    past_event_engagement,
    sponsorship_potential
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row["name"],
        row["description"],
        row["expected_event"],
        row["case_type"],
        row["company_size"],
        row["industry_fit"],
        row["past_event_engagement"],
        row["sponsorship_potential"]
    ))

# Create classifications table
cursor.execute("""
CREATE TABLE IF NOT EXISTS classifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    predicted_event TEXT NOT NULL,
    relevance_score INTEGER NOT NULL,
    reason TEXT,
    correct INTEGER,
    FOREIGN KEY (company_id)
        REFERENCES companies(id)
)
""")

# Clear previous classification results
cursor.execute("""
DELETE FROM classifications
""")

cursor.execute("""
SELECT
    id,
    name,
    description,
    expected_event
FROM companies
""")

companies = cursor.fetchall()

for company_id, name, description, expected_event in companies:

    try:
        result = classify_company(
            name,
            description
        )

        predicted_event = result.event
        relevance_score = result.relevance_score
        reason = result.reason

        correct = int(
            predicted_event == expected_event
        )

        cursor.execute("""
        INSERT INTO classifications (
            company_id,
            predicted_event,
            relevance_score,
            reason,
            correct
        )
        VALUES (?, ?, ?, ?, ?)
        """, (
            company_id,
            predicted_event,
            relevance_score,
            reason,
            correct
        ))

        print(
            f"✓ {name} ->"
            f"{predicted_event} "
            f"({relevance_score}/10)"
        )
    except Exception as error:
            print(
                f"✗ Failed to classify {name}: {error}"
            )

# Save database changes
conn.commit()


# Check classification data
cursor.execute("""
SELECT *
FROM classifications
""")

classification_rows = cursor.fetchall()

print("\n===== Classifications =====")

for row in classification_rows:
    print(row)


# Check company data
cursor.execute("""
SELECT *
FROM companies
""")

company_rows = cursor.fetchall()

print("\n===== Companies =====")

for row in company_rows:
    print(row)

conn.close()
print("\nDatabase setup completed successfully.")

