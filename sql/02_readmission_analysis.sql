-- ============================================================================
-- Hospital Readmission Analytics: SQL Queries
-- Written in standard ANSI SQL (tested on SQLite via sqlite3, fully compatible with MySQL 8.0+ and PostgreSQL)
-- Data Granularity: 99,343 valid encounters (post deceased/hospice exclusion)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- QUERY 1: Overall 30-Day Readmission Rate Benchmark
-- Calculates overall encounter-level 30-day readmission percentage.
-- ----------------------------------------------------------------------------
SELECT 
    COUNT(*) AS total_encounters,
    SUM(readmitted_30day) AS readmitted_30day_count,
    ROUND(AVG(readmitted_30day) * 100.0, 2) AS overall_30day_readmission_rate_pct
FROM cleaned_patient_encounters;


-- ----------------------------------------------------------------------------
-- QUERY 2: Readmission Rate by Age Group
-- Observes readmission rate distribution across age brackets.
-- ----------------------------------------------------------------------------
SELECT 
    age_clean AS age_group,
    COUNT(*) AS encounter_count,
    SUM(readmitted_30day) AS readmitted_count,
    ROUND(AVG(readmitted_30day) * 100.0, 2) AS readmission_rate_pct
FROM cleaned_patient_encounters
GROUP BY age_clean
ORDER BY MIN(age);


-- ----------------------------------------------------------------------------
-- QUERY 3: Readmission Rate by Prior Inpatient Visits
-- Compares readmission rate across prior inpatient visit history.
-- Note: Encounter-level rates include repeat patient visits.
-- ----------------------------------------------------------------------------
SELECT 
    prior_inpatient_bucket,
    COUNT(*) AS total_encounters,
    SUM(readmitted_30day) AS readmitted_30day_count,
    ROUND(AVG(readmitted_30day) * 100.0, 2) AS readmission_rate_pct
FROM cleaned_patient_encounters
GROUP BY prior_inpatient_bucket
ORDER BY 
    CASE prior_inpatient_bucket
        WHEN '0 Visits' THEN 1
        WHEN '1 Visit' THEN 2
        WHEN '2 Visits' THEN 3
        WHEN '3+ Visits' THEN 4
    END;


-- ----------------------------------------------------------------------------
-- QUERY 4: Readmission Rate by Length of Stay
-- Analyzes readmission rates across hospital stay duration buckets.
-- ----------------------------------------------------------------------------
SELECT 
    los_bucket AS length_of_stay,
    COUNT(*) AS total_encounters,
    SUM(readmitted_30day) AS readmitted_30day_count,
    ROUND(AVG(readmitted_30day) * 100.0, 2) AS readmission_rate_pct,
    ROUND(AVG(num_lab_procedures), 1) AS avg_lab_procedures
FROM cleaned_patient_encounters
GROUP BY los_bucket
ORDER BY MIN(time_in_hospital);


-- ----------------------------------------------------------------------------
-- QUERY 5: Readmission Rate by HbA1c Test Category
-- Observes readmission rate differences between tested and unmonitored patients.
-- (Observational data note: testing status is associated with rates, not causal)
-- ----------------------------------------------------------------------------
SELECT 
    COALESCE(A1Cresult, 'Not Tested') AS a1c_test_result,
    COUNT(*) AS total_encounters,
    SUM(readmitted_30day) AS readmitted_30day_count,
    ROUND(AVG(readmitted_30day) * 100.0, 2) AS readmission_rate_pct
FROM cleaned_patient_encounters
GROUP BY A1Cresult
ORDER BY readmission_rate_pct DESC;


-- ----------------------------------------------------------------------------
-- QUERY 6: Readmission Rate by Discharge Category
-- Compares observed rates across discharge care settings (Home vs SNF vs Transfer).
-- ----------------------------------------------------------------------------
SELECT 
    discharge_category,
    COUNT(*) AS total_encounters,
    SUM(readmitted_30day) AS readmitted_30day_count,
    ROUND(AVG(readmitted_30day) * 100.0, 2) AS readmission_rate_pct
FROM cleaned_patient_encounters
GROUP BY discharge_category
ORDER BY readmission_rate_pct DESC;


-- ----------------------------------------------------------------------------
-- QUERY 7: WINDOW FUNCTION - Patient Visit Rank & Cumulative Metrics
-- Uses ROW_NUMBER() OVER and COUNT() OVER to track visit sequence per patient.
-- ----------------------------------------------------------------------------
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
FROM cleaned_patient_encounters
LIMIT 20;


-- ----------------------------------------------------------------------------
-- QUERY 8: COMMON TABLE EXPRESSION (CTE) - Cohort Risk Ratio Benchmarking
-- Segments patients by prior inpatient visits (2+ visits = 14,114 encounters, 3,108 readmissions = 22.02%)
-- and compares observed rate against the baseline cohort (0-1 visits = 85,229 encounters, 8,206 readmissions = 9.63%).
-- ----------------------------------------------------------------------------
WITH patient_cohorts AS (
    SELECT 
        encounter_id,
        patient_nbr,
        readmitted_30day,
        number_inpatient,
        A1Cresult,
        CASE 
            WHEN number_inpatient >= 2 THEN '2+ Prior Inpatient Visits Cohort'
            ELSE 'Baseline Cohort (0-1 Prior Visits)'
        END AS risk_cohort
    FROM cleaned_patient_encounters
),
cohort_metrics AS (
    SELECT 
        risk_cohort,
        COUNT(*) AS total_encounters,
        SUM(readmitted_30day) AS readmissions_30day,
        AVG(readmitted_30day) AS readmission_rate
    FROM patient_cohorts
    GROUP BY risk_cohort
),
baseline AS (
    SELECT readmission_rate AS baseline_rate 
    FROM cohort_metrics 
    WHERE risk_cohort = 'Baseline Cohort (0-1 Prior Visits)'
)
SELECT 
    cm.risk_cohort,
    cm.total_encounters,
    cm.readmissions_30day,
    ROUND(cm.readmission_rate * 100.0, 2) AS readmission_rate_pct,
    ROUND(cm.readmission_rate / b.baseline_rate, 2) AS risk_multiplier_vs_baseline
FROM cohort_metrics cm
CROSS JOIN baseline b
ORDER BY cm.readmission_rate DESC;
