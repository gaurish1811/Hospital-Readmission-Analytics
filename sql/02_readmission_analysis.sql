-- ============================================================================
-- Hospital Readmission Analytics: Analytical Queries
-- Focus: Provider/Payer 30-Day Readmission Risk & Cohort Segmentation
-- Engine: Standard SQL (Compatible with MySQL 8.0+, PostgreSQL, SQLite 3.25+)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- QUERY 1: Overall 30-Day Readmission Rate KPI
-- Calculates total valid encounters, 30-day readmissions, and overall percentage.
-- ----------------------------------------------------------------------------
SELECT 
    COUNT(*) AS total_encounters,
    SUM(readmitted_30day) AS readmitted_30day_count,
    ROUND(AVG(readmitted_30day) * 100.0, 2) AS overall_30day_readmission_rate_pct
FROM cleaned_patient_encounters;


-- ----------------------------------------------------------------------------
-- QUERY 2: Readmission Rate by Age Group
-- Evaluates how readmission risk shifts across age brackets (e.g. 70-80, 80-90).
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
-- Demonstrates the exponential risk increase based on prior inpatient history.
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
-- QUERY 4: Readmission Rate by Length of Stay (Hospital Days)
-- Analyzes whether longer hospital stay correlates with higher readmission risk.
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
-- QUERY 5: Readmission Rate by HbA1c Test Result
-- Measures the impact of glycemic control monitoring (None, Norm, >7, >8).
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
-- QUERY 6: Readmission Rate by Discharge Disposition Category
-- Compares readmission risks across care transitions (Home vs SNF vs Transfer).
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
-- QUERY 7: WINDOW FUNCTION - Patient Visit Sequence Rank & Prior Visit Running Total
-- Uses ROW_NUMBER() OVER and SUM() OVER to track visit sequence per patient.
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
    ) AS total_patient_encounters,
    SUM(readmitted_30day) OVER (
        PARTITION BY patient_nbr
    ) AS total_patient_30day_readmissions
FROM cleaned_patient_encounters
LIMIT 20;


-- ----------------------------------------------------------------------------
-- QUERY 8: COMMON TABLE EXPRESSION (CTE) - High-Risk Cohort Risk Ratio Analysis
-- Multi-stage CTE benchmarking high-risk patients (2+ prior inpatient visits & high HbA1c) 
-- against standard baseline patients.
-- ----------------------------------------------------------------------------
WITH patient_cohorts AS (
    SELECT 
        encounter_id,
        patient_nbr,
        readmitted_30day,
        number_inpatient,
        A1Cresult,
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
        SUM(readmitted_30day) AS readmissions_30day,
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
    cm.readmissions_30day,
    ROUND(cm.readmission_rate * 100.0, 2) AS readmission_rate_pct,
    ROUND(cm.readmission_rate / b.baseline_rate, 2) AS risk_multiplier_vs_baseline
FROM cohort_metrics cm
CROSS JOIN baseline b
ORDER BY cm.readmission_rate DESC;
