# AI-Assisted Event Lead Qualification Pipeline

An end-to-end prototype for classifying companies into technology events, scoring their business relevance, and prioritizing leads for outreach.

## Table of Contents

- [Project Overview](#project-overview)
- [Pipeline Architecture](#pipeline-architecture)
- [Project Structure](#project-structure)
- [Prompt Engineering](#prompt-engineering)
- [Prompt Evaluation Results](#prompt-evaluation-results)
- [Structured Output](#structured-output)
- [Database Design](#database-design)
- [Lead Scoring Model](#lead-scoring-model)
- [Example Output](#example-output)
- [Example Business Queries](#example-business-queries)
- [Running the Project](#running-the-project)
- [n8n Automation](#n8n-automation)
- [Power BI Dashboard](#power-bi-dashboard)
- [Data Limitations](#data-limitations)
- [Future Improvements](#future-improvements)
- [Tech Stack](#tech-stack)
- [Project Summary](#project-summary)

---

**Highlights**

- Classifies 20 companies into RAISE, Signal Week, MACHINA, or Other using OpenAI Structured Outputs
- Evaluates three prompt versions against expected labels: 90% → 95% → 100% agreement on the 20-company set
- Scores leads by combining `relevance_score` with simulated business features; the score definition was corrected after it distorted priorities ([details](#defining-the-relevance-score))
- Runs as a batch pipeline (Python, SQLite, pandas), a real-time n8n workflow, and a two-page Power BI dashboard

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
    ↓
Power BI dashboard
```

The project separates experimentation, production-style classification, database processing, and analysis into different modules.

---

## Project Structure

```text
event-lead-qualification/
├── docs/
│   ├── n8n_workflow.png
│   ├── powerbi_dashboard.png
│   └── powerbi_prompt_evaluation.png
├── n8n/
│   └── event_lead_qualification_workflow.json
├── powerbi/
│   └── event_lead_qualification_dashboard.pbix
├── companies.csv
├── openai_classifier.py
├── prompt_evaluation.py
├── database.py
├── lead_qualification.py
├── requirements.txt
├── .gitignore
└── README.md

Generated after running the scripts (gitignored, not committed):

event_leads.db                          ← database.py
lead_qualification_results.csv          ← lead_qualification.py
top_10_leads.csv
top_leads_by_event.csv
priority_leads.csv
event_summary.csv
priority_summary.csv
classification_errors.csv
lead_qualification_case_summary.csv
prompt_evaluation.csv                   ← prompt_evaluation.py
prompt_evaluation_case_summary.csv
fixed_by_v2.csv
experiment_summary.csv
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
- agreement by case type
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

### Defining the Relevance Score

The evaluation prompts (V1–V3) only decide which event a company belongs to. The production classifier also returns a `relevance_score`, and an early version of its prompt constrained the range but not the meaning.

The model read the score as classification confidence rather than event relevance. Companies classified as `Other` received scores as high as 10, while their own `reason` said that no event topic was central to the business. Because `relevance_score` carries 30% of the lead score, this pushed non-matching companies into the Medium priority band.

The production prompt now defines the score as relevance to the assigned event, not confidence in the classification:

```text
- 8-10: the event topic is the company's primary business
- 5-7:  the company fits the event, but the relevant technology is only
        one part of a broader business
- 2-4:  the company has only a marginal connection to the event topics
- 1:    the company has no meaningful connection to any event topic

If the event is Other, relevance_score must be 3 or lower.
```

The change altered scoring but not classification. All 20 companies kept the same predicted event, and every `Other` company is now in the Low priority band. Multi-domain companies such as NVIDIA and Tesla dropped from 9–10 to 7, because the event topic is only part of their business.

---

## Prompt Evaluation Results

The prompts were evaluated on a 20-company test set with hand-assigned expected labels.

| Prompt Version | Agreement with Expected Label |
|---------------|-------------------------------|
| V1 | 90% |
| V2 | 95% |
| V3 | 100% |

- V1 misclassified UiPath and Snowflake.
- V2 fixed both but introduced a new error on NVIDIA.
- V3 fixed NVIDIA and introduced no new errors on this set.

> The V3 rules were developed against these same 20 companies. The figures measure agreement with expected labels on this set and should not be interpreted as general model accuracy.

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

The lead score combines the AI-derived `relevance_score` with business features.

```text
Lead Score =
    relevance_score × 30%
  + industry_fit × 25%
  + sponsorship_potential × 20%
  + company_size × 10%
  + past_event_engagement × 10%
  + case_confidence × 5%
```

All six inputs use a 1–10 scale and the weights sum to 100%, so scores range from 10 to 100.

`relevance_score` is the only input produced by the classifier. Its definition is described under [Defining the Relevance Score](#defining-the-relevance-score), because an ill-defined scale distorts the whole ranking.

---

## Example Output

Example qualified leads:

| Company | Event | Relevance Score | Lead Score | Priority | Recommended Action |
|---|---|---:|---:|---|---|
| Binance | Signal Week | 10 | 95.0 | High | Contact sales / partnership team |
| Coinbase | Signal Week | 10 | 95.0 | High | Contact sales / partnership team |
| ABB Robotics | MACHINA | 10 | 93.0 | High | Contact sales / partnership team |
| Scale AI | RAISE | 10 | 93.0 | High | Contact sales / partnership team |
| NVIDIA | RAISE | 7 | 86.5 | High | Contact sales / partnership team |
| Tesla | MACHINA | 7 | 80.0 | Medium | Add to nurture campaign |
| PayPal | Other | 1 | 49.0 | Low | Low priority / monitor |

The last three rows show the relevance scale at work. NVIDIA and Tesla fit their events but serve several markets, so they score 7 rather than 10. PayPal is classified as `Other` and scores 1, which keeps it out of the outreach queue despite its high company size and sponsorship potential.

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
- classification agreement with expected labels
- high-priority lead selection

---

## Running the Project

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Set the OpenAI API Key

Store the API key in an environment variable. Never hardcode it or commit it to GitHub.

**Windows PowerShell**

```powershell
$env:OPENAI_API_KEY="your_api_key"
```

---

### Run the Database Pipeline

```bash
python database.py
```

The `RUN_CLASSIFICATION` flag in `database.py` controls whether the OpenAI classifier runs:

- `False` — reuses the classification results already stored in SQLite
- `True` — reruns the OpenAI classifier and refreshes the stored results

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

This script evaluates the V1, V2, and V3 prompts with live OpenAI API calls. The full 20-company run makes approximately 60 model requests (each company is evaluated with three prompt versions).

---

### Open the Dashboard

```text
powerbi/event_lead_qualification_dashboard.pbix
```

The report has its data embedded, so the scripts above are only needed to refresh it. See [Power BI Dashboard](#power-bi-dashboard).

---

## n8n Automation

In addition to the batch pipeline (`database.py` / `lead_qualification.py`), the project includes an n8n workflow (`n8n/event_lead_qualification_workflow.json`) that qualifies a single lead in real time when it is submitted through a webhook.

![n8n workflow](docs/n8n_workflow.png)

```text
Webhook (POST /event-lead)
    ↓
Edit Fields (map request body to fields)
    ↓
Validate Input (required fields + numeric ranges 1–10)
    ↓
Input Valid? ──No──→ Log Input Error (data table)
    │Yes
    ↓
OpenAI Classification (V3 decision-rules prompt)
    ↓
Parse Classification (parse + sanity-check JSON)
    ↓
Validate AI Output (event / relevance_score / reason)
    ↓
AI Output Valid? ──No──→ Log AI Error → Reject AI Output
    │Yes
    ↓
Calculate Lead Score (weighted formula → priority + recommended_action)
    ↓
IF Priority == High ──Yes──→ Discord Alert
    │No
    ↓
No Operation (do nothing)
```

Key design points:

- **Double validation.** Input data is validated before the OpenAI call, and the model output is validated again before scoring. Invalid inputs and invalid model outputs are written to the `error_logs` data table instead of entering the scoring pipeline.
- **Same scoring logic as Python.** The `Calculate Lead Score` node reimplements the identical weighted formula used in `database.py`, so batch and real-time results stay consistent.
- **Alerting on high-priority leads.** When `priority` is `High`, a Discord message is sent with the company name, event, lead score, relevance score, and reason; otherwise the run ends with a no-op.
- **Use case.** The workflow complements the batch pipeline: the batch scripts analyze an existing company list, while the webhook qualifies new leads as they arrive (e.g., from a signup form or CRM trigger).

---

## Power BI Dashboard

`powerbi/event_lead_qualification_dashboard.pbix` is a two-page report that turns the pipeline outputs into an actionable view for a business development team.

### Data Model

The report imports only the two detail-level exports:

| Table | Source | Grain |
|---|---|---|
| `lead_qualification_results` | `lead_qualification_results.csv` | one row per company |
| `prompt_evaluation_long` | `prompt_evaluation.csv`, unpivoted in Power Query | one row per company per prompt version |

The pre-aggregated exports (`top_10_leads.csv`, `event_summary.csv`, `priority_summary.csv`, `top_leads_by_event.csv`) are deliberately **not** imported. Every count, average, and ranking is a DAX measure over the detail tables, so slicers recalculate results instead of reading frozen ones. Importing both the detail and the summary of the same data would duplicate the aggregation logic in two places.

`prompt_evaluation.csv` is written in wide format (one column per prompt version). Power Query unpivots it into `prompt_version` / `prediction` / `is_correct` so the versions can be compared on a single axis.

### Page 1 — Lead Overview

![Power BI lead overview](docs/powerbi_dashboard.png)

Four KPI cards are driven by measures over the company table:

```dax
Total Leads =
COUNTROWS('lead_qualification_results')

Average Lead Score =
AVERAGE('lead_qualification_results'[lead_score])

High Priority Leads =
CALCULATE(
    [Total Leads],
    'lead_qualification_results'[priority] = "High"
)

Classification Agreement % =
DIVIDE(
    CALCULATE(
        [Total Leads],
        'lead_qualification_results'[correct] = 1
    ),
    [Total Leads]
)
```

The rest of the page has five visuals:

- **Lead Priority Distribution** — how the scoring model splits the 20 companies into High, Medium, and Low
- **Leads by Event** — where the classifier assigned each company, including `Other`
- **Average Lead Score by Event** — which event attracts the most commercially relevant companies, which a count alone cannot show
- **Top Qualified Leads** — the outreach shortlist, built with a Top N filter on `company` ranked by `lead_score` (not imported from `top_10_leads.csv`)
- **Sponsorship Potential vs Lead Score** — one bubble per company, colored by event and sized by `company_size`

`Event` and `Priority` slicers filter the whole page, so one report answers both "how is the pipeline performing overall" and "who should sales contact this week".

The scatter plot also makes the relevance-score fix visible: `Other` companies form a separate low cluster instead of mixing into the mid-range.

### Page 2 — Prompt Evaluation

![Power BI prompt evaluation](docs/powerbi_prompt_evaluation.png)

The second page covers prompt reliability rather than business value:

- **V1 / V2 / V3 Agreement %** cards — 90%, 95%, 100% on the evaluation set
- **Prompt Version Agreement** — the same three numbers as a column chart
- **Errors by Prompt Version** — error counts, which expose the V2 regression that the net agreement figures hide
- **Errors by Case Type and Prompt Version** — a matrix locating each error: V1 failed on `borderline_ai` and `keyword_trap`, V2 on `multi_domain`
- **Misclassified Cases** — the three individual errors with expected event, prompt version, and prediction

The cards use **Agreement** rather than **Accuracy** because the results are specific to the current 20-company evaluation set.

### Refreshing the Report

The `.pbix` embeds its data, so it opens without running the pipeline.

To refresh it, first regenerate the gitignored CSVs:

```bash
python database.py
python lead_qualification.py
python prompt_evaluation.py
```

Then use **Home → Refresh**. The data source paths are local, so a clone must repoint them to its own working directory.

---

## Data Limitations

The company descriptions and event labels are prototype data used for evaluation.

The following business features are simulated:

- company_size
- industry_fit
- past_event_engagement
- sponsorship_potential

In production, these fields would come from systems such as:

- CRM platforms
- historical event data
- company databases
- enrichment APIs

The lead-scoring weights are heuristic and are intended to demonstrate the business logic of the pipeline rather than represent an objectively validated scoring model.

---

## Future Improvements

Potential next steps:

- connecting CRM or enrichment APIs
- adding automated data ingestion with n8n
- storing classification timestamps and model metadata
- adding retry and rate-limit handling for API calls
- expanding the evaluation dataset
- adding automated tests
- scheduling the Power BI refresh against a hosted database instead of local CSV files
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
- n8n (workflow automation)
- Discord API (alerting)
- Power BI / DAX / Power Query
- Git / GitHub

---

## Project Summary

This project shows how an LLM classifier can be embedded in a sales and partnership workflow: event classification with validated structured output, database storage, lead scoring and prioritization, real-time automation, and BI reporting.
