# Hospital Readmission Analytics: SQL + Python + Tableau

![Hospital Readmission Analytics Dashboard](assets/dashboard_screenshot.png)

## 📌 Executive Overview
30-Day Hospital Readmission is a critical quality and financial metric for healthcare providers (hospitals) and payers (insurers). Under the CMS **Hospital Readmissions Reduction Program (HRRP)**, health systems face severe financial penalties (up to 3% of total Medicare reimbursements) for higher-than-expected readmission rates.

This project delivers an end-to-end healthcare analytics solution built on the **UCI Diabetes 130-US Hospitals dataset (1999–2008)** (~100,000 patient encounters across 130 US hospitals). Designed to mirror real-world healthcare intelligence workflows (such as at **Innovaccer**), this project extracts actionable insights to identify high-risk patient cohorts, quantify readmission drivers, and recommend targeted care interventions.

---

## 🛠️ Tech Stack & Key Tools
- **Data Engineering & Cleaning**: Python (`pandas`, `numpy`)
- **Exploratory Data Analysis**: Jupyter Notebook (`notebooks/01_hospital_readmission_cleaning.ipynb`)
- **Database & Query Engine**: SQL (MySQL, PostgreSQL, SQLite) featuring **Window Functions** & **Common Table Expressions (CTEs)**
- **Interactive Visualizations**: HTML5, CSS3 Glassmorphism UI, Chart.js & Tableau Public
- **Version Control & Documentation**: Git, GitHub, Markdown

---

## 🧹 Data Cleaning & Audit Log
Healthcare EHR data contains real-world noise. The dataset was preprocessed using a rigorous audit pipeline to ensure analytical integrity:

1. **Missing Value Standardization**: String placeholder `'?'` converted to `NaN`. High-missing features (`weight` at 96.8% missing, `payer_code` at 39.5%, `medical_specialty` at 49.0%) were pruned.
2. **Exclusion of Non-Eligible Encounters**: Patients discharged to **Hospice** (`13`, `14`) or **Expired/Deceased** (`11`, `19`, `20`, `21`) were removed because 30-day readmission is clinically impossible for these patients.
3. **Patient Deduplication & Encounter Sequencing**: Patient encounters (`patient_nbr`) were indexed to maintain independent observation benchmarks and track repeat admissions.

### Data Cleaning Audit Trail
| Audit Step | Description | Records Impacted | Records Remaining |
| :--- | :--- | :---: | :---: |
| **Initial Raw Data** | Total patient encounters loaded | — | **101,766** |
| **Exclusion Filter** | Deceased or Hospice care discharges removed | -2,423 | **99,343** |
| **Deduplication** | Secondary visits removed for patient-level cohorting | -29,353 | **69,990** |
| **Final Clean Encounters** | Dataset for encounter-level 30-day readmission analysis | — | **99,343** |

---

## 📊 Core SQL Analytical Queries

The SQL analytical suite ([sql/02_readmission_analysis.sql](sql/02_readmission_analysis.sql)) includes 8 production-grade queries. Highlights include:

### 1. Window Function: Patient Visit Sequencing & Running Metrics
Tracks encounter rank per patient and calculates cumulative 30-day readmission flags across historical visits using `ROW_NUMBER() OVER` and `COUNT() OVER`.

```sql
SELECT 
    encounter_id,
    patient_nbr,
    age_clean,
    number_inpatient,
    readmitted_30day,
    ROW_NUMBER() OVER (
        PARTITION BY patient_nbr 
        ORDER BY encounter_id ASC
    ) AS patient_visit_sequence_num,
    COUNT(*) OVER (
        PARTITION BY patient_nbr
    ) AS total_patient_encounters
FROM cleaned_patient_encounters;
```

### 2. Multi-Stage CTE: High-Risk Cohort Risk Ratio Benchmarking
Uses a Common Table Expression to segment high-risk patients (2+ prior inpatient visits & high HbA1c) and calculate their risk multiplier relative to baseline.

```sql
WITH patient_cohorts AS (
    SELECT 
        encounter_id,
        patient_nbr,
        readmitted_30day,
        CASE 
            WHEN number_inpatient >= 2 AND A1Cresult IN ('>7', '>8') THEN 'High-Risk Cohort (2+ Inpatient & High A1C)'
            WHEN number_inpatient >= 2 THEN 'Moderate-Risk Cohort (2+ Inpatient)'
            ELSE 'Standard Baseline Cohort'
        END AS risk_cohort
    FROM cleaned_patient_encounters
),
cohort_metrics AS (
    SELECT 
        risk_cohort,
        COUNT(*) AS total_encounters,
        AVG(readmitted_30day) AS readmission_rate
    FROM patient_cohorts
    GROUP BY risk_cohort
),
baseline AS (
    SELECT readmission_rate AS baseline_rate 
    FROM cohort_metrics 
    WHERE risk_cohort = 'Standard Baseline Cohort'
)
SELECT 
    cm.risk_cohort,
    cm.total_encounters,
    ROUND(cm.readmission_rate * 100.0, 2) AS readmission_rate_pct,
    ROUND(cm.readmission_rate / b.baseline_rate, 2) AS risk_multiplier_vs_baseline
FROM cohort_metrics cm
CROSS JOIN baseline b
ORDER BY cm.readmission_rate DESC;
```

---

## 💡 Plain-English Business Insights & Takeaways

### 1. Prior Inpatient Visits are the #1 Driver of Readmission (2.3x Multiplier)
> **Insight:** Patients with zero prior inpatient visits in the preceding year have an **8.59%** 30-day readmission rate. This escalates to **13.25%** for 1 visit, **17.93%** for 2 visits, and **26.40%** for 3+ visits.  
> **Executive Takeaway:** *"Patients with 2+ prior inpatient visits are readmitted **2.3 times more often** than first-time patients (22.22% vs. 9.63%). For super-utilizers with 3+ prior visits, more than 1 in 4 returns to the hospital within 30 days."*

### 2. Inpatient Glycemic Testing Gap (83% Unmonitored Rate)
> **Insight:** **83.1% of hospital encounters** had no recorded HbA1c test during admission. However, tested patients who had medication adjustments saw readmission rates drop to **9.77%–10.15%**.  
> **Executive Takeaway:** *"More than 4 out of 5 diabetic encounters lack an HbA1c test, leaving care teams blind to long-term glycemic control. Implementing routine inpatient testing and medication adjustments drops readmission rates below the baseline."*

### 3. Care Transition Vulnerability at Rehab & Skilled Nursing Facilities (SNFs)
> **Insight:** Discharges to **Rehab/Transfers (21.88%)** and **Skilled Nursing Facilities (14.36%)** experience higher readmissions than direct home discharges (**9.30%**).  
> **Executive Takeaway:** *"Patients transferred to rehabilitation or step-down facilities are **2.35 times more likely to be readmitted** than home discharges, highlighting care coordination gaps during facility transitions."*

### 4. Extended Hospital Stay Risk
> **Insight:** Patients staying 8+ days in the hospital experience a **13.85%** readmission rate compared to **9.32%** for 1–2 day stays.  
> **Executive Takeaway:** *"Extended hospital stays do not safeguard against readmission; instead, they reflect high clinical complexity and carry a **48% higher readmission risk**."*

---

## 🖥️ Tableau Public & Interactive Dashboard Setup
- **Interactive Web Dashboard**: Open [`dashboard/index.html`](dashboard/index.html) directly in any web browser for a live UI preview with Chart.js visuals and dynamic filter controls.
- **Tableau Public Guide**: Detailed step-by-step instructions for publishing to Tableau Public are documented in [`dashboard/TABLEAU_GUIDE.md`](dashboard/TABLEAU_GUIDE.md).

---

## 📁 Repository Structure
```
Hospital Readmission Analytics/
│
├── data/
│   ├── raw/                           # Raw UCI dataset (diabetic_data.csv)
│   ├── cleaned_diabetic_data.csv      # Cleaned encounter-level dataset (99,343 rows)
│   ├── cleaned_patient_first_visits.csv# Deduplicated unique patient dataset (69,990 rows)
│   └── cleaning_audit_log.txt         # Automated cleaning audit trail text log
│
├── scripts/
│   ├── 00_download_data.py            # Automated UCI dataset downloader
│   ├── 01_data_cleaning.py            # Pandas cleaning & feature engineering script
│   ├── 02_execute_sql_queries.py      # SQLite SQL query execution & validation runner
│   ├── generate_charts.py             # Visual dashboard generator (PNG export)
│   └── generate_dashboard_screenshot.py # Playwright automated screenshot script
│
├── notebooks/
│   └── 01_hospital_readmission_cleaning.ipynb # Interactive Jupyter cleaning notebook
│
├── sql/
│   ├── 01_schema_and_import.sql       # DDL schema definition & import instructions
│   └── 02_readmission_analysis.sql    # 8 Analytical SQL queries (Window functions + CTEs)
│
├── dashboard/
│   ├── index.html                     # HTML5 Dashboard Interface
│   ├── styles.css                     # Glassmorphism CSS Design System
│   ├── app.js                         # Chart.js visual rendering & filter logic
│   └── TABLEAU_GUIDE.md               # Tableau Public setup & field mapping guide
│
├── assets/
│   └── dashboard_screenshot.png       # High-resolution dashboard screenshot
│
├── insights/
│   └── executive_insights.md          # Comprehensive executive briefing report
│
└── README.md                          # Project documentation
```

---

## ⚡ Quickstart & Replication Guide

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/Hospital-Readmission-Analytics.git
   cd Hospital-Readmission-Analytics
   ```

2. **Download Data & Run Cleaning Engine**:
   ```bash
   python scripts/00_download_data.py
   python scripts/01_data_cleaning.py
   ```

3. **Execute SQL Analytical Suite**:
   ```bash
   python scripts/02_execute_sql_queries.py
   ```

4. **Launch Interactive Web Dashboard**:
   Open `dashboard/index.html` in your browser.
