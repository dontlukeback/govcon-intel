# DOL OFLC Data Inventory — Complete Reference

*Compiled: 2026-03-18*
*Sources: dol.gov/agencies/eta/foreign-labor/performance, flag.dol.gov, foreignlaborcert.doleta.gov (redirects to dol.gov)*

---

## Executive Summary

The DOL Office of Foreign Labor Certification (OFLC) publishes **six program datasets** with full disclosure data, updated **quarterly**, covering **FY2008 through FY2026 Q1**. All files are free, public, and downloadable as Excel (.xlsx) with PDF record layouts describing every column. The old flcdatacenter.com now redirects to flag.dol.gov (the FLAG system), and the old foreignlaborcert.doleta.gov redirects to the main DOL performance page.

**Base URL for all files:**
`https://www.dol.gov/sites/dolgov/files/ETA/oflc/pdfs/`

---

## 1. LCA Program (H-1B, H-1B1, E-3) — PRIMARY DATASET

This is the core H-1B dataset. Every Labor Condition Application filed by employers is disclosed.

### Files Per Quarter

| File | Naming Pattern | FY2026 Q1 Size | FY2025 Q4 Size |
|------|---------------|----------------|----------------|
| Main Disclosure | `LCA_Disclosure_Data_FY{YEAR}_Q{Q}.xlsx` | 72.1 MB | 75.4 MB |
| Worksites | `LCA_Worksites_FY{YEAR}_Q{Q}.xlsx` | — | 88.3 MB |
| Appendix A | `LCA_Appendix_A_FY{YEAR}_Q{Q}.xlsx` | — | — |
| Record Layout | `LCA_Record_Layout_FY{YEAR}_Q{Q}.pdf` | ~168 KB | ~168 KB |
| Worksites Layout | `LCA_Worksites_Record_Layout_FY{YEAR}_Q{Q}.pdf` | ~137 KB | — |
| Appendix A Layout | `LCA_Appendix_A_Record_Layout_FY{YEAR}_Q{Q}.pdf` | ~130 KB | — |

### Date Range
- FY2008 through FY2026 Q1 (current)
- Fiscal year = Oct 1 - Sep 30
- Updated quarterly

### Main Disclosure Fields (67 columns)

**Case Metadata:**
- `CASE_NUMBER` — Unique identifier for each application
- `CASE_STATUS` — "Certified", "Certified-Withdrawn", "Denied", "Withdrawn"
- `RECEIVED_DATE` — Date application received at OFLC
- `DECISION_DATE` — Date of last significant event/determination
- `ORIGINAL_CERT_DATE` — Original certification date (for Certified-Withdrawn)
- `VISA_CLASS` — H-1B, E-3 Australian, H-1B1 Chile, H-1B1 Singapore

**Job Information:**
- `JOB_TITLE` — Free-text title of the job
- `SOC_CODE` — Standard Occupational Classification code
- `SOC_TITLE` — Occupational title for the SOC code
- `FULL_TIME_POSITION` — Y/N
- `BEGIN_DATE` — Requested employment start date
- `END_DATE` — Requested employment end date
- `TOTAL_WORKER_POSITIONS` — Number of foreign workers requested

**Employment Type (petition basis):**
- `NEW_EMPLOYMENT` — New employer
- `CONTINUED_EMPLOYMENT` — Same employer continuation
- `CHANGE_PREVIOUS_EMPLOYMENT` — Same employer, no material change
- `NEW_CONCURRENT_EMPLOYMENT` — Additional employer
- `CHANGE_EMPLOYER` — New employer, same classification
- `AMENDED_PETITION` — Same employer, material change

**Employer Information:**
- `EMPLOYER_NAME` — Legal business name
- `TRADE_NAME_DBA` — DBA name
- `EMPLOYER_ADDRESS1`, `EMPLOYER_ADDRESS2`
- `EMPLOYER_CITY`, `EMPLOYER_STATE`, `EMPLOYER_POSTAL_CODE`
- `EMPLOYER_COUNTRY`, `EMPLOYER_PROVINCE`
- `EMPLOYER_PHONE`, `EMPLOYER_PHONE_EXT`
- `EMPLOYER_FEIN` — Federal Employer ID Number
- `NAICS_CODE` — North American Industry Classification System code

**Employer Point of Contact:**
- `EMPLOYER_POC_LAST_NAME`, `EMPLOYER_POC_FIRST_NAME`, `EMPLOYER_POC_MIDDLE_NAME`
- `EMPLOYER_POC_JOB_TITLE`
- `EMPLOYER_POC_ADDRESS1` through `EMPLOYER_POC_EMAIL` (full address block)

**Attorney/Agent Information:**
- `AGENT_REPRESENTING_EMPLOYER` — Y/N
- `AGENT_ATTORNEY_LAST_NAME`, `AGENT_ATTORNEY_FIRST_NAME`, `AGENT_ATTORNEY_MIDDLE_NAME`
- `AGENT_ATTORNEY_ADDRESS1` through `AGENT_ATTORNEY_EMAIL_ADDRESS` (full address block)
- `LAWFIRM_NAME_BUSINESS_NAME`
- `LAWFIRM_BUSINESS_FEIN`
- `STATE_OF_HIGHEST_COURT`
- `NAME_OF_HIGHEST_STATE_COURT`

**Primary Worksite (wages and location):**
- `WORKSITE_WORKERS` — Number at first worksite
- `SECONDARY_ENTITY` — Y/N, placed with another company
- `SECONDARY_ENTITY_BUSINESS_NAME` — Name of that company
- `WORKSITE_ADDRESS1`, `WORKSITE_ADDRESS2`
- `WORKSITE_CITY`, `WORKSITE_COUNTY`, `WORKSITE_STATE`, `WORKSITE_POSTAL_CODE`
- `WAGE_RATE_OF_PAY_FROM` — Minimum offered wage
- `WAGE_RATE_OF_PAY_TO` — Maximum offered wage
- `WAGE_UNIT_OF_PAY` — Hour/Week/Bi-Weekly/Month/Year
- `PREVAILING_WAGE` — Prevailing wage for the position
- `PW_UNIT_OF_PAY` — Unit of prevailing wage
- `PW_TRACKING_NUMBER` — Links to PW determination
- `PW_WAGE_LEVEL` — OES Level I/II/III/IV or N/A
- `PW_OES_YEAR` — Year of OES data used
- `PW_OTHER_SOURCE` — CBA/DBA/SCA/Other/PW Survey
- `PW_OTHER_YEAR`
- `PW_SURVEY_PUBLISHER`
- `PW_SURVEY_NAME`
- `TOTAL_WORKSITE_LOCATIONS` — Count of all worksites

**Compliance & Attestation:**
- `AGREE_TO_LC_STATEMENT` — Y/N
- `H-1B_DEPENDENT` — Y/N, employer is H-1B dependent
- `WILLFUL_VIOLATOR` — Y/N
- `SUPPORT_H1B` — Y/N/N/A, exempt workers only
- `STATUTORY_BASIS` — Wage/Degree/Both (exemption basis)
- `APPENDIX_A_ATTACHED` — Y/N/N/A
- `PUBLIC_DISCLOSURE` — Where public access file is posted

**Preparer:**
- `PREPARER_LAST_NAME`, `PREPARER_FIRST_NAME`, `PREPARER_MIDDLE_INITIAL`
- `PREPARER_BUSINESS_NAME`, `PREPARER_EMAIL`

### Worksites File Fields (20 columns)
For applications with multiple worksites (up to 10). One row per worksite, joined by `CASE_NUMBER`.

- `CASE_NUMBER` — Join key to main disclosure
- `WORKSITE_WORKERS`
- `SECONDARY_ENTITY` (Y/N)
- `SECONDARY_ENTITY_BUSINESS_NAME`
- `WORKSITE_ADDRESS1`, `WORKSITE_ADDRESS2`
- `WORKSITE_CITY`, `WORKSITE_COUNTY`, `WORKSITE_STATE`, `WORKSITE_POSTAL_CODE`
- `WAGE_RATE_OF_PAY_FROM`, `WAGE_RATE_OF_PAY_TO`, `WAGE_UNIT_OF_PAY`
- `PREVAILING_WAGE`, `PW_UNIT_OF_PAY`
- `PW_TRACKING_NUMBER`, `PW_WAGE_LEVEL`, `PW_OES_YEAR`
- `PW_OTHER_SOURCE`, `PW_OTHER_YEAR`
- `PW_SURVEY_PUBLISHER`, `PW_SURVEY_NAME`

### Appendix A File Fields (5 columns)
For H-1B dependent/willful violator employers claiming Master's degree exemption. Multiple rows per case.

- `CASE_NUMBER`
- `APPX_A_NO_OF_EXEMPT_WORKERS`
- `APPX_A_NAME_OF_INSTITUTION`
- `APPX_A_FIELD_OF_STUDY`
- `APPX_A_DATE_OF_DEGREE`

---

## 2. PERM Program (Permanent Labor Certification)

Employers seeking to sponsor foreign workers for green cards. Richer data than LCA — includes recruitment steps, job requirements, education levels.

### Files Per Quarter

| File | Pattern | FY2026 Q1 Size |
|------|---------|----------------|
| Main Disclosure | `PERM_Disclosure_Data_FY{YEAR}_Q{Q}.xlsx` | 11.3 MB |
| Record Layout | `PERM_Record_Layout_FY{YEAR}_Q{Q}.pdf` | ~187 KB |

### Date Range
- FY2008 through FY2026 Q1
- Note: New ETA-9089 form took effect June 1, 2023, changing field structure

### PERM Fields (100+ columns)

**Case Metadata:**
- `CASE_NUMBER`, `CASE_STATUS` (Certified/Certified-Expired/Denied/Withdrawn)
- `RECEIVED_DATE`, `DECISION_DATE`

**Occupation:**
- `OCCUPATION_TYPE` — Professional/Non-professional/College-University Teacher/Schedule A/None-Professional Athlete
- `JOB_TITLE`, `PWD_SOC_CODE`, `PWD_SOC_TITLE`

**Employer Info:**
- `EMP_BUSINESS_NAME`, `EMP_TRADE_NAME`
- Full address block: `EMP_ADDR1` through `EMP_PHONEEXT`
- `EMP_FEIN`, `EMP_NAICS`
- `EMP_NUM_PAYROLL` — Total employees on payroll
- `EMP_YEAR_COMMENCED` — Year business started
- `EMP_WORKER_INTEREST` — Foreign worker has ownership interest? Y/N
- `EMP_RELATIONSHIP_WORKER` — Familial relationship? Y/N

**Employer Point of Contact:**
- `EMP_POC_LAST_NAME` through `EMP_POC_EMAIL`

**Attorney/Agent:**
- `ATTY_AG_REP_TYPE` — Attorney/Agent/None
- Full name and address block
- `ATTY_AG_LAW_FIRM_NAME`, `ATTY_AG_FEIN`, `ATTY_AG_STATE_BAR_NUMBER`
- `ATTY_AG_GOOD_STANDING_STATE`, `ATTY_AG_GOOD_STANDING_COURT`

**Foreign Worker Info:**
- `FW_INFO_APPX_A_ATTACHED` — Appendix A identifying the worker
- `FW_INFO_ATTY_OR_AGENT` — Same attorney represents both employer and worker?

**Job Opportunity / Prevailing Wage:**
- `JOB_OPP_PWD_NUMBER` — PW Determination tracking number
- `JOB_OPP_PWD_ATTACHED` — Y/N/N/A
- `JOB_OPP_WAGE_FROM`, `JOB_OPP_WAGE_TO`, `JOB_OPP_WAGE_PER`
- `JOB_OPP_WAGE_CONDITIONS` — Bonus/benefits details

**Primary Worksite:**
- `PRIMARY_WORKSITE_TYPE`
- Full address: `PRIMARY_WORKSITE_ADDR1` through `PRIMARY_WORKSITE_POSTAL_CODE`
- `PRIMARY_WORKSITE_BLS_AREA` — MSA/OES area title
- `IS_MULTIPLE_LOCATIONS`, `IS_APPENDIX_B_ATTACHED`

**Other Job Requirements (rich data):**
- `OTHER_REQ_IS_FULLTIME_EMP`
- `OTHER_REQ_IS_LIVEIN_HOUSEHOLD` — Live-in domestic worker
- `OTHER_REQ_IS_PAID_EXPERIENCE`, `OTHER_REQ_IS_FW_EXECUTED_CONT`, `OTHER_REQ_IS_EMP_PROVIDED_CONT`
- `OTHER_REQ_ACCEPT_DIPLOMA_PWD` — Accept foreign degree equivalent?
- `OTHER_REQ_IS_FW_CURRENTLY_WRK` — Foreign worker currently employed?
- `OTHER_REQ_IS_FW_QUALIFY` — Qualifies only via alternative requirements?
- `OTHER_REQ_EMP_WILL_ACCEPT` — Accept combo of education/experience/training?
- `OTHER_REQ_EMP_RELY_EXP` — Relying solely on experience gained with this employer?
- `OTHER_REQ_FW_GAIN_EXP` — Experience in comparable position?
- `OTHER_REQ_EMP_PAY_EDUCATION` — Employer paid for worker's education?
- `OTHER_REQ_JOB_EMP_PREMISES` — Must live on employer premises?
- `OTHER_REQ_JOB_COMBO_OCCUP` — Combination of occupations?
- `OTHER_REQ_JOB_FOREIGN_LANGUAGE` — Foreign language required?
- `OTHER_REQ_JOB_REQ_EXCEED` — Requirements exceed SVP level?
- `OTHER_REQ_EMP_USE_CREDENTIAL` — Credentialing service used?
- `OTHER_REQ_EMP_REC_PAYMENT` — Employer received payment for filing?
- `OTHER_REQ_EMP_LAYOFF` — Layoff in past 6 months?

**Recruitment Information:**
- `RECR_INFO_RECRUIT_SUPERVISED_REQ` — Supervised recruitment required?
- `RECR_INFO_JOB_START_DATE`, `RECR_INFO_JOB_END_DATE` — SWA job order dates
- `RECR_INFO_IS_NEWSPAPER_SUNDAY`, `RECR_INFO_NEWSPAPER_NAME`, `RECR_INFO_AD_DATE1`
- `RECR_INFO_RECRUIT_AD_TYPE` — Newspaper of general circulation / Professional journal
- `RECR_INFO_NEWSPAPER_NAME2`, `RECR_INFO_AD_DATE2`
- Job fair dates: `RECR_OCC_JOB_FAIR_FROM/TO`
- Employer website dates: `RECR_OCC_EMP_WEBSITE_FROM/TO`
- Job search website dates: `RECR_OCC_JOB_SEARCH_FROM/TO`
- On-campus dates: `RECR_OCC_ON_CAMPUS_FROM/TO`
- Trade org dates: `RECR_OCC_TRADE_ORG_FROM/TO`
- Private employment firm dates: `RECR_OCC_PRIVATE_EMP_FROM/TO`
- Employee referral dates: `RECR_OCC_EMP_REFERRAL_FROM/TO`
- Campus placement dates: `RECR_OCC_CAMPUS_PLACEMENT_FROM/TO`
- Local/ethnic newspaper dates: `RECR_OCC_LOCAL_NEWSPAPER_FROM/TO`
- Radio/TV ad dates: `RECR_OCC_RADIO_AD_FROM/TO`

**Notice/Posting:**
- `NOTICE_POST_BARGAIN_REP` — Notice to bargaining representative
- `NOTICE_POST_BARGAIN_REP_PHYSICAL` — Physical posting for 10 days
- `NOTICE_POST_BARGAIN_REP_ELECTRONIC` — Electronic dissemination
- `NOTICE_POST_BARGAIN_REP_INHOUSE` — In-house media
- `NOTICE_POST_BARGAIN_REP_PRIVATE` — Private household posting
- `NOTICE_POST_EMP_NOT_POSTED` — DID NOT post notice

**Compliance:**
- `EMP_CERTIFY_COMPLIANCE`
- `DECL_PREP_LAST_NAME` through `DECL_PREP_EMAIL`

---

## 3. Prevailing Wage Program (Form ETA-9141)

Every prevailing wage determination request — covers ALL visa classes (H-1B, H-2B, PERM, CW-1, E-3). This is the richest wage dataset with education requirements, job duties context, and OES wage levels.

### Files Per Quarter

| File | Pattern | FY2026 Q1 Size |
|------|---------|----------------|
| Main Disclosure | `PW_Disclosure_Data_FY{YEAR}_Q{Q}.xlsx` | 78.0 MB |
| Worksites | `PW_Worksites_FY{YEAR}_Q{Q}.xlsx` | varies |
| Record Layout | `PW_Record_Layout_FY{YEAR}_Q{Q}.pdf` | ~184 KB |

### Date Range
- FY2010 through FY2026 Q1

### PW Fields (75+ columns)

**Case Metadata:**
- `CASE_NUMBER`, `CASE_STATUS` (Determination Issued / Redetermination Affirmed / Redetermination Modified / Center Director Review Affirmed / Center Director Review Modified / Withdrawn)
- `RECEIVED_DATE`, `DETERMINATION_DATE`, `REDETERMINATION_DATE`
- `CENTER_DIRECTOR_REVIEW_DATE`, `WITHDRAWAL_DATE`
- `VISA_CLASS` — CW-1/H-2B/H-1B/H-1B1 Chile/H-1B1 Singapore/E-3 Australian/PERM

**Employer & Contact Info:**
- Full POC block: `EMPLOYER_POC_LAST_NAME` through `EMPLOYER_POC_EMAIL`
- `EMPLOYER_LEGAL_BUSINESS_NAME`, `TRADE_NAME_DBA`
- Full employer address block
- `EMPLOYER_FEIN`, `NAICS_CODE`

**Attorney/Agent:**
- `TYPE_OF_REPRESENTATION` — Attorney/Agent/None
- Full name and address block
- `LAWFIRM_NAME_BUSINESS_NAME`

**ACWIA Coverage (H-1B specific):**
- `COVERED_BY_ACWIA` — Y/N/N/A
- `ACWIA_INST_HIGHER_EDUCATION`
- `ACWIA_AFFILIATED_NON_PROFIT`
- `ACWIA_RESEARCH_ORG`
- `ACWIA_STATUS_CHANGED`

**Special Classifications:**
- `PROF_SPORTS_LEAGUE` — Professional sports position?
- `CBA` — Covered by Collective Bargaining Agreement?
- `WAGE_SOURCE_REQUESTED` — DBA/SCA/Survey
- `SURVEY_NAME`, `SURVEY_PUBLICATION_DATE`

**Job Requirements (extremely detailed):**
- `JOB_TITLE`
- `SUPERVISE_OTHER_EMP`, `EMP_SOC_CODES`, `EMP_SOC_TITLES`
- `REQUIRED_EDUCATION_LEVEL` — None/High School/Associate's/Bachelor's/Master's/Doctorate/Other
- `REQUIRED_OTHER_DEGREE`, `REQUIRED_EDUCATION_MAJOR`
- `SECOND_EDUCATION`, `SECOND_EDUCATION_MAJOR`
- `REQUIRED_TRAINING` (Y/N), `REQUIRED_TRAINING_MONTHS`, `REQUIRED_TRAINING_NAME`
- `REQUIRED_EXPERIENCE` (Y/N), `REQUIRED_EXPERIENCE_MONTHS`, `REQUIRED_OCCUPATION`
- `SPECIAL_SKILLS_REQUIREMENTS` (Y/N)
- `SPEC_REQ_LICENSE_CERT`, `SPEC_REQ_FOREIGN_LANG`, `SPEC_REQ_RES_FELLOW`, `SPEC_REQ_OTHER`

**Alternative Requirements:**
- `ALTERNATIVE_REQUIREMENTS` (Y/N)
- `ALT_EDUCATION_LEVEL`, `ALT_OTHER_DEGREE`, `ALT_EDUCATION_MAJOR`
- `ALT_TRAINING` (Y/N), `ALT_TRAINING_MONTHS`, `ALT_TRAINING_NAME`
- `ALT_EXPERIENCE` (Y/N), `ALT_EXPERIENCE_MONTHS`
- `ALT_SPECIAL_SKILLS`, `ALT_LICENSE_CERT`, `ALT_FOREIGN_LANGUAGE`, `ALT_RES_FELLOWSHIP`, `ALT_OTHER_REQ`

**SOC / O*NET Codes:**
- `SUGGESTED_SOC_CODE`, `SUGGESTED_SOC_TITLE`
- `PWD_SOC_CODE`, `PWD_SOC_TITLE`
- `O_NET_CODE`, `O_NET_TITLE`
- `O_NET_CODE_COMBO`, `O_NET_TITLE_COMBO` (combination occupations)
- `SUPERVISOR_JOB_TITLE`

**Travel:**
- `TRAVEL_REQUIRED` (Y/N), `TRAVEL_DETAILS`

**Worksite:**
- Full primary worksite address block
- `OTHER_WORKSITE_LOCATION` (Y/N)

**Wage Determination (primary):**
- `PWD_WAGE_RATE` — The actual prevailing wage
- `PWD_UNIT_OF_PAY` — Hour/Week/Bi-Weekly/Month/Year
- `PWD_OES_WAGE_LEVEL` — I/II/III/IV/OES Mean/N/A
- `PWD_WAGE_SOURCE` — OES (All Industries)/OES (ACWIA)/CBA/DBA/SCA/Alternate Survey/etc.
- `PWD_SURVEY_NAME`
- `BLS_AREA` — Metropolitan/Non-Metropolitan Statistical Area

**Wage Determination (alternative requirements):**
- `ALT_PWD_WAGE_RATE`, `ALT_PWD_UNIT_OF_PAY`, `ALT_PWD_OES_WAGE_LEVEL`
- `ALT_PWD_WAGE_SOURCE`, `ALT_PWD_SURVEY_NAME`

**H-2B Specific:**
- `H2B_HIGHEST_PWD` — Highest PW across all H-2B worksites

**Other:**
- `WAGE_DET_NOTES` — Additional notes
- `PREVAIL_WAGE_DETERM_DATE`, `PWD_WAGE_EXPIRATION_DATE`

---

## 4. H-2A Program (Temporary Agricultural Workers)

### Files Per Quarter

| File | Pattern | FY2026 Q1 Size |
|------|---------|----------------|
| Main Disclosure | `H-2A_Disclosure_Data_FY{YEAR}_Q{Q}.xlsx` | 60.4 MB |
| Addendum (old form) | `H-2A_Disclosure_Data_Addendum_FY{YEAR}_Q{Q}.xlsx` | varies |
| Addendum (new form) | `H-2A_Disclosure_Data_New_Addendum_FY{YEAR}_Q{Q}.xlsx` | varies |
| Employment Records | `H-2A_Employment_FY{YEAR}_Q{Q}.xlsx` | varies |
| Housing Records | `H-2A_Housing_FY{YEAR}_Q{Q}.xlsx` | varies |
| Record Layout | `H-2A_Record_Layout_FY{YEAR}_Q{Q}.pdf` | varies |

### Date Range
- FY2008 through FY2026 Q1

### Additional Data Available
- Adverse Effect Wage Rates (AEWRs) — via flag.dol.gov
- Labor Supply State Determinations
- Meals & Subsistence Rates

---

## 5. H-2B Program (Temporary Non-Agricultural Workers)

### Files Per Quarter

| File | Pattern | FY2026 Q1 Size |
|------|---------|----------------|
| Main Disclosure | `H-2B_Disclosure_Data_FY{YEAR}_Q{Q}.xlsx` | 10.5 MB |
| Appendix A | `H-2B_Appendix_A_FY{YEAR}_Q{Q}.xlsx` | varies |
| Appendix C | `H-2B_Appendix_C_FY{YEAR}_Q{Q}.xlsx` | varies |
| Appendix D | `H-2B_Appendix_D_FY{YEAR}_Q{Q}.xlsx` | varies |
| Record Layout | `H-2B_Record_Layout_FY{YEAR}_Q{Q}.pdf` | varies |

### Date Range
- FY2008 through FY2026 Q1

---

## 6. CW-1 Program (CNMI Transitional Workers)

### Files Per Quarter

| File | Pattern | Size |
|------|---------|------|
| Main Disclosure | `CW-1_Disclosure_Data_FY{YEAR}_Q{Q}.xlsx` | Small |
| Appendix A | `CW-1_Appendix_A_FY{YEAR}_Q{Q}.xlsx` | Small |
| Appendix B | `CW-1_Appendix_B_FY{YEAR}_Q{Q}.xlsx` | Small |
| Record Layout | `CW-1_Record_Layout_FY{YEAR}_Q{Q}.pdf` | varies |

### Date Range
- FY2019 through FY2026 Q1

---

## 7. FLAG System Tools (flag.dol.gov)

The Foreign Labor Application Gateway (FLAG) replaced flcdatacenter.com and provides:

### OFLC Wage Search Tool
- Interactive search for prevailing wages by occupation and location
- Uses reCAPTCHA v3 (no simple API)
- Returns OES wage data by SOC code and geographic area

### OFLC Wage Data Downloads
- Bulk OES wage data files
- H-2A Adverse Effect Wage Rates
- H-2A Labor Supply State Determinations
- H-2A Meals & Subsistence Rates

### Case Status Search
- Look up individual application status by case number

### Processing Times
- Current processing times by program

### Other Resources
- Foreign Labor Recruiter Directory
- Program Debarment Lists (employers barred from programs)
- State Workforce Agency Locator

---

## Data Architecture Notes

### Important Structural Change: FY2020
Beginning FY2020, OFLC migrated to the FLAG system. This substantially changed field availability and data structure. Pre-FY2020 and post-FY2020 data may require different parsing logic.

### New PERM Form: June 2023
The ETA-9089 form was revised effective June 1, 2023. FY2024+ PERM data uses the new field structure. Earlier data may have different/fewer columns.

### PII Exclusions
The following are explicitly excluded from public disclosure:
- Attorney's FEIN and State Bar Number (LCA files)
- Job Duties free-text field (PW files)

### Joining Datasets
- `CASE_NUMBER` joins main disclosure to worksites/appendix files within the same program
- `PW_TRACKING_NUMBER` in LCA links to `CASE_NUMBER` in PW disclosure data (cross-program join)
- `JOB_OPP_PWD_NUMBER` in PERM links to `CASE_NUMBER` in PW disclosure data

### Estimated Record Volumes (per full fiscal year)
- LCA (H-1B): ~800K-1M+ applications per year (based on 75 MB file size)
- PERM: ~100K-150K applications per year
- PW: ~500K-700K determinations per year
- H-2A: ~300K-500K applications per year
- H-2B: ~50K-100K applications per year
- CW-1: Small volume (CNMI only)

### File Size Summary

| Dataset | Quarterly Size Range | Annual Estimate |
|---------|---------------------|-----------------|
| LCA Main | 70-80 MB | ~300 MB |
| LCA Worksites | ~88 MB | ~350 MB |
| PERM | 11-83 MB | ~200 MB |
| PW | ~78 MB | ~300 MB |
| H-2A | 60-77 MB | ~275 MB |
| H-2B | ~10 MB | ~40 MB |

---

## Key Fields for H-1B Career Intelligence Product

The most valuable columns for a career intelligence / employer sponsorship product:

### Employer Identification
- `EMPLOYER_NAME` + `EMPLOYER_FEIN` — Unique employer identification
- `NAICS_CODE` — Industry classification
- `EMPLOYER_CITY`, `EMPLOYER_STATE` — HQ location

### Job & Compensation
- `JOB_TITLE` — Free-text, needs NLP normalization
- `SOC_CODE` + `SOC_TITLE` — Standardized occupation
- `WAGE_RATE_OF_PAY_FROM` / `WAGE_RATE_OF_PAY_TO` — Offered salary range
- `WAGE_UNIT_OF_PAY` — Normalize to annual
- `PREVAILING_WAGE` + `PW_UNIT_OF_PAY` — Market benchmark
- `PW_WAGE_LEVEL` — OES Level I-IV (proxy for seniority)
- `FULL_TIME_POSITION` — Full/part time

### Location
- `WORKSITE_CITY`, `WORKSITE_STATE`, `WORKSITE_COUNTY` — Actual work location
- Worksites file for multi-location applications

### Timing & Status
- `CASE_STATUS` — Approval outcome
- `RECEIVED_DATE`, `DECISION_DATE` — Processing timeline
- `BEGIN_DATE`, `END_DATE` — Employment period

### Sponsorship Pattern
- `NEW_EMPLOYMENT` / `CONTINUED_EMPLOYMENT` / `CHANGE_EMPLOYER` — Type of petition
- `H-1B_DEPENDENT` — Employer heavily uses H-1B
- `TOTAL_WORKER_POSITIONS` — Volume per application

### Placement
- `SECONDARY_ENTITY` — Consulting/staffing indicator
- `SECONDARY_ENTITY_BUSINESS_NAME` — Actual client company

### Legal Representation
- `LAWFIRM_NAME_BUSINESS_NAME` — Immigration law firm
- `AGENT_REPRESENTING_EMPLOYER` — Has representation

---

## Download Strategy for MVP

**Phase 1 — Core H-1B data:**
Download LCA Disclosure Data for FY2020-FY2026 (post-FLAG, consistent schema). ~6 years x 4 quarters x ~75 MB = ~1.8 GB of Excel files.

**Phase 2 — Enrich with wages:**
Download PW Disclosure Data for same period. Join on PW_TRACKING_NUMBER for detailed education/experience requirements.

**Phase 3 — Green card pipeline:**
Download PERM data for same period. Shows which employers are sponsoring for permanent residency.

**Phase 4 — Historical depth:**
Backfill FY2008-FY2019. Different schema requires mapping work.
