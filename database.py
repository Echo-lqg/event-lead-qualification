# =========================================================
# 1. Imports and configuration
# =========================================================

from openai_classifier import classify_company

import sqlite3
import pandas as pd

RUN_CLASSIFICATION = False

# =========================================================
# 2. Load source company data
# =========================================================

df = pd.read_csv("companies.csv")

# =========================================================
# 3. Connect to SQLite database
# =========================================================

conn = sqlite3.connect("event_leads.db")

cursor = conn.cursor()

# =========================================================
# 4. Create database tables
# =========================================================

# Companies table
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

# AI classification results
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

# Lead qualification results
cursor.execute("""
CREATE TABLE IF NOT EXISTS lead_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    lead_score REAL NOT NULL,
    priority TEXT NOT NULL,
    recommended_action TEXT,
    FOREIGN KEY (company_id)
        REFERENCES companies(id)    
)
""")

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

conn.commit()

# =========================================================
# 6. Run OpenAI classification (optional)
# =========================================================

if RUN_CLASSIFICATION:

    #Clear previous classification results
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

    #Save database changes
    conn.commit()

# =========================================================
# 7. Evaluate classification results
# =========================================================

cursor.execute("""
SELECT *
FROM companies
""")

company_rows = cursor.fetchall()

print("\n===== Companies =====")

for row in company_rows:
    print(row)

#Print stored classifications
cursor.execute("""
SELECT *
FROM classifications
""")

classification_rows = cursor.fetchall()

print("\n===== Classifications =====")

for row in classification_rows:
    print(row)

#Compare predicted vs expected
cursor.execute("""
SELECT
    c.name,
    c.expected_event,
    cl.predicted_event,
    cl.relevance_score,
    cl.correct
FROM companies AS c
JOIN classifications AS cl
    on c.id = cl.company_id
""")

joined_rows = cursor.fetchall()

print("\n===== Joined Classification Results =====")

for row in joined_rows :
     print(row)

#Calculate accuracy
cursor.execute("""
SELECT
    AVG(correct)
FROM classifications
""")

accuracy = cursor.fetchone()[0]
if accuracy is not None:
    print(
        f"\nClassification accuracy: "
        f"{accuracy:.2%}"
    )
else:
    print("\nNo classification data available.")


# =========================================================
# 8. Calculate lead qualification scores
# =========================================================

case_confidence_map = {
    "clear_case": 10,
    "multi_domain": 7,
    "borderline_fintech": 6,
    "borderline_ai": 6,
    "borderline_autonomy": 7,
    "keyword_trap": 5
}

cursor.execute("""
DELETE FROM lead_scores
""")

cursor.execute("""
SELECT
    c.id,
    c.name,
    c.case_type,
    c.company_size,
    c.industry_fit,
    c.past_event_engagement,
    c.sponsorship_potential,
    cl.relevance_score
FROM companies AS c
JOIN classifications AS cl
    ON c.id = cl.company_id
""")

lead_data = cursor.fetchall()

for (
    company_id,
    name,
    case_type,
    company_size,
    industry_fit,
    past_event_engagement,
    sponsorship_potential,
    relevance_score
) in lead_data:

    case_confidence = case_confidence_map[case_type]

    lead_score = (
        relevance_score * 0.30
        + industry_fit * 0.25
        + sponsorship_potential * 0.20
        + company_size * 0.10
        + past_event_engagement * 0.10
        + case_confidence * 0.05
    ) * 10

    lead_score = round(lead_score, 1)

    if lead_score >= 85:
        priority = "High"
    elif lead_score >= 65:
        priority = "Medium"
    else:
        priority = "Low"

    if priority == "High":
        recommended_action = "Contact sales / partnership team"
    elif priority == "Medium":
        recommended_action = "Add to nurture campaign"
    else:
        recommended_action = "Low priority / monitor"

    cursor.execute("""
    INSERT INTO lead_scores (
        company_id,
        lead_score,
        priority,
        recommended_action
    )
    VALUES (?, ?, ?, ?)
    """, (
            company_id,
            lead_score,
            priority,
            recommended_action
    ))

    conn.commit()

cursor.execute("""
SELECT *
FROM lead_scores
""")

lead_score_rows = cursor.fetchall()
print("\n===== Lead Scores =====")

for row in lead_score_rows:
    print(row)

# =========================================================
# 9. Build final lead qualification results
# =========================================================

cursor.execute("""
SELECT
    c.name,
    cl.predicted_event,
    cl.relevance_score,
    ls.lead_score,
    ls.priority,
    ls.recommended_action
FROM companies AS c
JOIN classifications AS cl
    ON c.id = cl.company_id
JOIN lead_scores AS ls
    ON c.id = ls.company_id
ORDER BY ls.lead_score DESC
""")

final_results = cursor.fetchall()

print("\n===== Final Lead Qualification Results =====")

for row in final_results:
    print(row)

# =========================================================
# 10. Business analytics
# =========================================================

#High priority leads
cursor.execute("""
SELECT
    c.name,
    cl.predicted_event,
    ls.lead_score,
    ls.priority,
    ls.recommended_action
FROM companies AS c
JOIN classifications AS cl
    ON c.id = cl.company_id
JOIN lead_scores AS ls
    ON c.id = ls.company_id
WHERE ls.priority = 'High'
ORDER BY ls.lead_score DESC
""")

high_priority_leads = cursor.fetchall()

print("\n===== High Priority Leads =====")

for row in high_priority_leads:
    print(row)

# Lead summary by event
cursor.execute("""
SELECT
    cl.predicted_event,
    COUNT(*) AS company_count,
    ROUND(AVG(ls.lead_score),1) AS average_lead_score
FROM classifications AS cl
JOIN lead_scores AS ls
    on cl.company_id = ls.company_id
GROUP BY cl.predicted_event
ORDER BY average_lead_score DESC
""")

event_summary = cursor.fetchall()

print("\n===== Event Summary =====")

for row in event_summary:
    print(row)

# Lead priority distribution
cursor.execute("""
SELECT
    priority,
    COUNT(*) AS lead_count
FROM lead_scores
GROUP BY priority
ORDER BY lead_count DESC
""")

priority_summary = cursor.fetchall()

print("\n===== Priority Summary =====")

for row in priority_summary:
    print(row)

# =========================================================
# 11. Close database connection
# =========================================================

conn.close()
print("\nDatabase pipeline completed successfully.")
