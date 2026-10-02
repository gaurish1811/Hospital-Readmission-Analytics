-- ============================================================================
-- Hospital Readmission Analytics: Database Schema & Data Import
-- Database Engine: Compatible with MySQL, PostgreSQL, SQLite
-- ============================================================================

-- Drop tables if they already exist
DROP TABLE IF EXISTS cleaned_patient_encounters;
DROP TABLE IF EXISTS raw_diabetic_data;

-- 1. Create Raw Data Table Schema
CREATE TABLE raw_diabetic_data (
    encounter_id BIGINT PRIMARY KEY,
    patient_nbr BIGINT,
    race VARCHAR(50),
    gender VARCHAR(20),
    age VARCHAR(20),
    weight VARCHAR(50),
    admission_type_id INT,
    discharge_disposition_id INT,
    admission_source_id INT,
    time_in_hospital INT,
    payer_code VARCHAR(50),
    medical_specialty VARCHAR(100),
    num_lab_procedures INT,
    num_procedures INT,
    num_medications INT,
    number_outpatient INT,
    number_emergency INT,
    number_inpatient INT,
    diag_1 VARCHAR(50),
    diag_2 VARCHAR(50),
    diag_3 VARCHAR(50),
    number_diagnoses INT,
    max_glu_serum VARCHAR(20),
    A1Cresult VARCHAR(20),
    metformin VARCHAR(20),
    repaglinide VARCHAR(20),
    nateglinide VARCHAR(20),
    chlorpropamide VARCHAR(20),
    glimepiride VARCHAR(20),
    acetohexamide VARCHAR(20),
    glipizide VARCHAR(20),
    gliquidone VARCHAR(20),
    glimepiride_pioglitazone VARCHAR(20),
    metformin_rosiglitazone VARCHAR(20),
    metformin_pioglitazone VARCHAR(20),
    change VARCHAR(20),
    diabetesMed VARCHAR(20),
    readmitted VARCHAR(20)
);

-- 2. Create Cleaned Patient Encounters Schema (Post-Cleaning Pipeline)
CREATE TABLE cleaned_patient_encounters (
    encounter_id BIGINT PRIMARY KEY,
    patient_nbr BIGINT,
    race VARCHAR(50),
    gender VARCHAR(20),
    age VARCHAR(20),
    age_clean VARCHAR(20),
    admission_type_id INT,
    discharge_disposition_id INT,
    discharge_category VARCHAR(50),
    admission_source_id INT,
    time_in_hospital INT,
    los_bucket VARCHAR(20),
    num_lab_procedures INT,
    num_procedures INT,
    num_medications INT,
    number_outpatient INT,
    number_emergency INT,
    number_inpatient INT,
    prior_inpatient_bucket VARCHAR(20),
    diag_1 VARCHAR(50),
    diag_2 VARCHAR(50),
    diag_3 VARCHAR(50),
    number_diagnoses INT,
    max_glu_serum VARCHAR(20),
    A1Cresult VARCHAR(20),
    change VARCHAR(20),
    diabetesMed VARCHAR(20),
    readmitted VARCHAR(20),
    readmitted_30day INT,
    readmitted_any INT
);

-- MySQL Data Import Instructions:
-- LOAD DATA INFILE '/path/to/cleaned_diabetic_data.csv'
-- INTO TABLE cleaned_patient_encounters
-- FIELDS TERMINATED BY ',' ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 1 ROWS;
