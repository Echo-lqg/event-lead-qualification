# AI-Assisted Event Lead Qualification Pipeline

An end-to-end prototype for classifying companies into technology events, scoring their business relevance, and prioritizing leads for outreach.

The project combines:

- OpenAI API
- Prompt Engineering and Evaluation
- Structured Outputs
- Python
- pandas
- SQLite / SQL
- Lead Scoring and Business Analytics

---

## Project Overview

Event organizers may receive large lists of companies that need to be matched with the most relevant event and prioritized for business development.

This project automates part of that workflow.

Each company is classified into one of four event categories:

- **RAISE** — AI, generative AI, machine learning, AI infrastructure
- **Signal Week** — blockchain, crypto, Web3, digital assets
- **MACHINA** — robotics, physical AI, autonomous machines, embodied AI
- **Other** — companies that do not clearly fit the three event categories

The pipeline then combines the AI classification with simulated business features to calculate a lead score, assign a priority level, and recommend a follow-up action.

---

## Pipeline Architecture

```text
companies.csv
    ↓
SQLite companies table
    ↓
OpenAI API
    ↓
Structured classification output
    ↓
classifications table
    ↓
Business scoring logic
    ↓
lead_scores table
    ↓
SQL analytics + pandas analysis
    ↓
Lead qualification outputs
```

The project separates experimentation, production-style classification, database processing, and analysis into different modules.

---

## Project Structure

```text
event-lead-qualification/
├── n8n/
│   └── event_lead_qualification_workflow.json
├── companies.csv
├── openai_classifier.py
├── prompt_evaluation.py
├── database.py
├── lead_qualification.py
├── requirements.txt
├── .gitignore
├── README.md
└── output files / generated CSVs
```

### `openai_classifier.py`

Contains the production-style OpenAI classifier.

It:

- builds the final classification prompt
- calls the OpenAI API
- validates model output using Pydantic Structured Outputs

Returns:

- `event`
- `relevance_score`
- `reason`

---

### `prompt_evaluation.py`

Runs prompt experiments across three prompt versions.

The goal is to evaluate whether more explicit decision rules improve classification performance on ambiguous companies.

---

### `database.py`

Implements the main SQLite pipeline.

It:

- creates database tables
- imports company data
- optionally calls the OpenAI classifier
- stores classification results
- evaluates predictions against expected labels
- calculates lead scores
- assigns priority levels
- generates SQL-based business analytics

---

### `lead_qualification.py`

Loads the final SQLite results into pandas for further analysis and export.

It produces:

- classification evaluation
- classification errors
- accuracy by case type
- top 10 leads
- top 3 leads per event
- high-priority leads
- event summaries
- priority summaries

---

## Prompt Engineering

Three prompt versions were tested.

### V1 — Basic Classification Prompt

The first version provided only the event definitions and asked the model to select one category.

### V2 — Primary-Business Rules

The second version introduced stricter rules such as:

- classify based on the company's primary business
- avoid relying only on technology-related keywords
- use Other when no category clearly applies

### V3 — Explicit Decision Rules

The final version introduced more specific rules for ambiguous cases.

Examples:

- software-only robotic process automation should not be classified as MACHINA
- general fintech or payment companies should not automatically be classified as Signal Week
- AI capabilities should not automatically imply RAISE when AI is only an additional feature
- physical robotics takes priority over general AI when the company's core product is a robotic or autonomous system

The V3 decision rules are also used by the production classifier.

---

## Prompt Evaluation Results

The prompts were evaluated using a 20-company test set.

| Prompt Version | Accuracy |
|---------------|----------|
| V1 | 90% |
| V2 | 95% |
| V3 | 100% |

V1 misclassified examples such as UiPath and Snowflake.

V2 corrected those cases but introduced a new error for NVIDIA.

V3 corrected NVIDIA while introducing no additional errors on the current evaluation set.

> These results are specific to the current 20-company evaluation dataset and should not be interpreted as general model accuracy.

---

## Structured Output

The production classifier validates OpenAI responses with a Pydantic model.

```python
class ClassificationResult(BaseModel):
    event: Literal[
        "RAISE",
        "Signal Week",
        "MACHINA",
        "Other"
    ]

    relevance_score: int = Field(
        ge=1,
        le=10
    )

    reason: str
```

This ensures that downstream database and analytics steps receive predictable and validated data.

---

## Database Design

The SQLite database contains three main tables.

### `companies`

Stores source company data and business features.

Examples:

- name
- description
- expected_event
- case_type
- company_size
- industry_fit
- past_event_engagement
- sponsorship_potential

### `classifications`

Stores AI classification results.

- company_id
- predicted_event
- relevance_score
- reason
- correct

### `lead_scores`

Stores business qualification results.

- company_id
- lead_score
- priority
- recommended_action

The tables are connected through `company_id`.

---

## Lead Scoring Model

The lead score combines AI relevance with business-oriented features.

```text
Lead Score =
    relevance_score × 30%
  + industry_fit × 25%
  + sponsorship_potential × 20%
  + company_size × 10%
  + past_event_engagement × 10%
  + case_confidence × 5%
```

The weighted result is converted to a 0–100 score.

## Example Output

Example qualified leads:

| Company | Event | Relevance Score | Lead Score | Priority | Recommended Action |
|---|---|---:|---:|---|---|
| NVIDIA | RAISE | 10 | 95.5 | High | Contact sales / partnership team |
| Binance | Signal Week | 10 | 95.0 | High | Contact sales / partnership team |
| Scale AI | RAISE | 10 | 93.0 | High | Contact sales / partnership team |
| ABB Robotics | MACHINA | 10 | 93.0 | High | Contact sales / partnership team |

### Priority Rules

```text
85–100   → High
65–84.9  → Medium
<65      → Low
```

### Recommended Actions

```text
High    → Contact sales / partnership team
Medium  → Add to nurture campaign
Low     → Low priority / monitor
```

---

## Example Business Queries

The SQLite pipeline supports queries such as:

```sql
SELECT
    c.name,
    cl.predicted_event,
    ls.lead_score,
    ls.priority
FROM companies AS c
JOIN classifications AS cl
    ON c.id = cl.company_id
JOIN lead_scores AS ls
    ON c.id = ls.company_id
WHERE ls.priority = 'High'
ORDER BY ls.lead_score DESC;
```

Other analyses include:

- average lead score by event
- number of leads by priority level
- classification accuracy
- high-priority lead selection

---

## Running the Project

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Set the OpenAI API Key

The API key should be stored as an environment variable.

**Windows PowerShell**

```powershell
$env:OPENAI_API_KEY="your_api_key"
```

The API key should never be hardcoded in the source code or committed to GitHub.

---

### Run the Database Pipeline

```bash
python database.py
```

Inside `database.py`:

```python
RUN_CLASSIFICATION = False
```

Uses existing classification results stored in SQLite.

Setting:

```python
RUN_CLASSIFICATION = True
```

Runs the OpenAI classifier again and refreshes the classification results.

---

### Run pandas Analysis

```bash
python lead_qualification.py
```

---

### Run Prompt Experiments

```bash
python prompt_evaluation.py
```

This script evaluates V1, V2, and V3 prompts using live OpenAI API calls.

Running the full 20-company experiment results in approximately 60 model requests because each company is evaluated with three prompt versions.

---

## Data Limitations

The company descriptions and event labels are used for prototype evaluation.

Business features such as:

- company_size
- industry_fit
- past_event_engagement
- sponsorship_potential

are simulated for prototyping purposes.

In a production environment, these fields would be sourced from systems such as:

- CRM platforms
- historical event data
- company databases
- enrichment APIs

The lead-scoring weights are heuristic and are intended to demonstrate the business logic of the pipeline rather than represent an objectively validated scoring model.

---

## Future Improvements

Potential next steps include:

- connecting CRM or enrichment APIs
- adding automated data ingestion with n8n
- storing classification timestamps and model metadata
- adding retry and rate-limit handling for API calls
- expanding the evaluation dataset
- adding automated tests
- building a Power BI dashboard
- tracking prompt and model versions
- integrating lead results into a CRM workflow

---

## Tech Stack

- Python
- pandas
- OpenAI API
- Pydantic
- SQLite
- SQL
- Git / GitHub

---

## Project Summary

This project demonstrates how AI can support event lead qualification by combining:

- event classification
- structured output validation
- database storage
- lead scoring
- business prioritization

It is a useful prototype for understanding how LLMs can be applied in a sales and partnership workflow for event planning and acquisition.

---

## n8n Automation

The project includes an n8n workflow for automated lead processing.

```text
Webhook
→ Normalize Input
→ OpenAI Classification
→ Parse Classification
→ Calculate Lead Score
→ IF Priority == High
→ Discord Alert
