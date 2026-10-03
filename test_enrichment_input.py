import pandas as pd

df = pd.read_csv("companies_enrichment_test.csv")

required_columns = [
    "name",
    "website",
    "expected_event"
]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(
            f"""Missing required column: {column}"""
        )

for _, row in df.iterrows():
    name = row["name"],
    website = row["website"]

    if pd.isna(name):
        raise ValueError("Company name is missing")
    
    if pd.isna(website):
        raise ValueError(
            f"Website is missing for {name}"
        )

    if not str(website).startswith(
        ("http://", "https://")
    ):
        raise ValueError(
            f"Invalid website for {name}: {website}"
        )

print("Input validation passed.")
print(df)