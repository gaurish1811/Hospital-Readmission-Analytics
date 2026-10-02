# Executive Insights: 30-Day Hospital Readmission Analytics
**Context:** Provider & Payer Value-Based Care Analysis (Innovaccer Case Study)  
**Dataset:** UCI Diabetes 130-US Hospitals (1999–2008)  
**Primary Analytical Cohort:** 99,343 valid post-discharge encounters (deceased & hospice excluded)  
**Secondary Benchmark Cohort:** 69,990 deduplicated first-visit unique patients  
**Overall Encounter Readmission Benchmark:** 11.39% (11,314 / 99,343 encounters)

---

## 1. Prior Inpatient Visits Pattern (2.3x Baseline Risk)
* **The Data:**
  * **0 Prior Visits:** 8.59% readmission rate (5,690 / 66,245 encounters)
  * **1 Prior Visit:** 13.25% readmission rate (2,516 / 18,984 encounters)
  * **2 Prior Visits:** 17.93% readmission rate (1,309 / 7,300 encounters)
  * **3+ Prior Visits:** 26.40% readmission rate (1,799 / 6,814 encounters)
  * **Combined 2+ Prior Visits Cohort:** **22.02%** readmission rate (**3,108 / 14,114 encounters**) vs **9.63%** for baseline patients (0-1 prior visits).
* **Observational Insight:** Patients with 2+ prior inpatient visits exhibited a **22.02% 30-day readmission rate**, representing a **2.29x (2.3x) multiplier** compared to baseline patients (9.63%). For patients with 3+ prior visits, observed readmissions reached **26.40%** (>1 in 4 encounters).
* **Methodological Note on Repeat Patients:** Rates are reported per encounter (99,343 encounters), so repeat patients contribute multiple visits. To verify whether this pattern holds without repeat-patient bias, we also evaluated the deduplicated 69,990 first-visit index cohort, where prior inpatient history remained the strongest single risk predictor.

---

## 2. Inpatient HbA1c Glycemic Monitoring Pattern
* **The Data:**
  * **Not Tested:** **83.05% of encounters (82,509 / 99,343)** had no HbA1c test recorded, showing an **11.68%** readmission rate.
  * **Tested Patients:** Encounters where HbA1c was tested exhibited lower overall readmission rates (**9.77%–10.15%**).
* **Observational Insight (Non-Causal):** As this is observational EHR data, we cannot claim that HbA1c testing directly *causes* a reduction in readmissions. However, tested patients **had lower observed readmission rates** than unmonitored patients. This association suggests that clinical monitoring of glycemic status is correlated with overall care management quality during admission.

---

## 3. Care Transition Setting Breakdown
* **The Data:**
  * **Discharged Home:** 9.30% readmission rate (5,602 / 60,234 encounters)
  * **SNF / Nursing Facility:** 14.36% readmission rate (2,187 / 15,229 encounters)
  * **Rehab / Hospital Transfer:** **21.88%** readmission rate (**1,192 / 5,449 encounters**)
* **Observational Insight:** Encounters resulting in transfers to rehabilitation or medical facilities exhibited **21.88% 30-day readmissions**—more than double the rate observed for direct home discharges (9.30%).

---

## 4. Length of Hospital Stay & Age Distribution
* **The Data:** Encounters lasting 8+ days showed a **13.85%** readmission rate (vs 9.32% for 1–2 day stays). Patients aged 60–90 accounted for **58.9%** of total hospitalizations.
* **Observational Insight:** Extended hospital stays were associated with elevated readmission rates (13.85%), reflecting higher underlying clinical complexity and comorbidity burden.

---

## Summary Matrix

| Patient Cohort | Encounters | Readmissions | Observed Rate | Risk vs Baseline | Key Observation |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Baseline Cohort (0-1 Visits)** | 85,229 | 8,206 | 9.63% | 1.00x | Standard acute encounters |
| **2+ Prior Visits Cohort** | 14,114 | 3,108 | **22.02%** | **2.29x (2.3x)** | Strongest observed risk driver |
| **Rehab / Transfer Setting** | 5,449 | 1,192 | **21.88%** | **2.27x** | High rate during care transitions |
| **HbA1c Tested Cohort** | 16,834 | 1,673 | **9.94%** | **0.87x** | Tested group had lower observed rates |
