# Unconventional Data Sources for Career Intelligence / Workforce Analytics

## Research Date: 2026-03-18

---

## TIER 1: HIGH-VALUE, ACCESSIBLE APIs (Can build with today)

### 1. DOL Foreign Labor Certification Data (LCA/H-1B, PERM)
- **URL**: https://www.dol.gov/agencies/eta/foreign-labor/performance
- **Access**: Free bulk Excel downloads, FY2008-FY2026
- **Datasets**:
  - **LCA (H-1B, H-1B1, E-3)**: Quarterly + annual. Employer name, job title, SOC code, wage offered, prevailing wage, worksite city/state, case status, decision date
  - **PERM**: Annual. Employer, job title, wage, education requirements, experience needed, country of citizenship
  - **H-2A/H-2B**: Agricultural and temp non-ag workers
- **Key fields**: Employer name, NAICS code, SOC code, wage level, worksite, visa class
- **Combination potential**: THIS IS THE CORE DATASET. Everything else enriches it.

### 2. USCIS H-1B Employer Data Hub
- **URL**: https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub
- **Access**: Free, downloadable Excel/CSV, FY2009-FY2026 Q1
- **Fields**: Employer name, city, state, zip, NAICS code, tax ID (last 4), initial/continuing employment, approvals, denials
- **Combination potential**: Approval RATES by employer — combine with LCA data to see which employers file lots of applications but get denied. Red flags for workers.

### 3. USAspending.gov API (Federal Contracts)
- **URL**: https://api.usaspending.gov/
- **Access**: Free, no API key needed, REST API v2
- **Tested endpoints**:
  - `POST /api/v2/search/spending_by_award/` — search contracts by keyword, recipient, time period, agency
  - `POST /api/v2/recipient/` — search contractor entities by name
  - Returns: Award ID, recipient name, award amount, description, awarding agency
- **Companies found**: Infosys Public Services ($200K HHS contract), General Dynamics IT, BAE Systems
- **KILLER COMBINATION**: Cross-reference H-1B sponsor list with federal contract recipients.
  - Which companies that sponsor H-1Bs also get government contracts?
  - Are they required to hire American first? (They are under certain rules)
  - Revenue stability signal: companies with federal contracts = stable sponsors
  - Could identify companies growing their government business (more hiring coming)

### 4. GitHub API (Company Tech Stack Profiling)
- **URL**: https://api.github.com
- **Access**: Free (60 req/hr unauthenticated, 5000/hr with token)
- **Tested endpoints**:
  - `/orgs/{org}/repos` — repos with language, stars, activity
  - `/search/users?q=type:org+location:...` — find company orgs by location
- **What we confirmed**:
  - Can identify company engineering presence: Infosys has Python, Java, C#, Go, TypeScript repos
  - Can detect tech stacks at scale: Google repos show C++, Python, Go, HTML
  - Can find companies by location (San Francisco: Netlify, Cloudflare, HashiCorp, Discord)
- **COMBINATION IDEAS**:
  - Map H-1B sponsor tech stacks from GitHub repos → predict which job titles they'll sponsor next
  - Companies with active open-source = engineering-first culture = better for tech workers
  - Detect technology shifts (company adding Rust/Go repos = hiring for those skills soon)
  - Company engineering team size proxy via contributor counts

### 5. FRED API (Federal Reserve Economic Data)
- **URL**: https://fred.stlouisfed.org/docs/api/fred/
- **Access**: Free with API key registration
- **Endpoints**: Categories, releases, series, observations, search, tags, maps
- **Relevant series**: Unemployment rates (metro-level), job postings (Indeed data), labor force participation, wage growth
- **COMBINATION IDEAS**:
  - Overlay H-1B filing volumes against unemployment rates by metro area
  - "Is this city's labor market tight?" → more H-1B sponsorship likely
  - Economic leading indicators → predict hiring/sponsorship cycles
  - Wage growth data vs. H-1B prevailing wages → are companies underpaying?

### 6. Senate Lobbying Disclosure API
- **URL**: https://lda.senate.gov/api/v1/
- **Access**: Free, REST API, JSON responses
- **Data**: All lobbying filings under the Lobbying Disclosure Act
- **Fields**: Registrant, client, lobbying activities, issue codes, descriptions
- **Issue code "IMM"** = Immigration filings
- **Note**: API search filtering appears limited — may need to bulk download and filter locally
- **COMBINATION IDEAS**:
  - WHO is lobbying for/against H-1B expansion? (Tech companies, staffing firms, unions)
  - Match lobbying clients to H-1B sponsors → companies investing in policy change = dependent on program
  - Track lobbying spend trends → predict policy changes before they happen
  - Identify industry coalitions forming around immigration reform

### 7. SEC EDGAR Full-Text Search
- **URL**: https://efts.sec.gov/LATEST/search-index?q=%22h-1b%22
- **Access**: Free API, no key needed
- **What we found**: 40 10-K filings mentioning "H-1B" in 2024-2025, including:
  - **Staffing firms**: Kforce (KFRC), Kelly Services (KELYA), Resources Connection (RGP)
  - **IT services**: Cognizant (CTSH), Accenture (ACN), Genpact (G)
  - **Tech companies**: GoDaddy (GDDY), NetApp (NTAP), Juniper Networks (JNPR), Skyworks (SWKS), RingCentral (RNG), Etsy (ETSY), SoFi (SOFI), Axon (AXON)
  - **Biotech/pharma**: Pacific Biosciences, ZyVersa, Lantern Pharma, Fate Therapeutics
- **COMBINATION IDEAS**:
  - Companies that discuss H-1B as a RISK FACTOR in 10-K = heavily dependent on program
  - Cross-reference with actual H-1B filing volumes
  - Sentiment analysis of SEC language about immigration → bullish vs. defensive
  - Track year-over-year changes in immigration risk language
  - Public company financial health + H-1B dependency = sponsor reliability score

---

## TIER 2: VALUABLE BUT REQUIRES MORE WORK

### 8. O*NET (Occupational Data)
- **URL**: https://services.onetcenter.org/
- **Access**: Free REST API (requires registration), bulk database downloads available
- **Data**: 900+ occupations with skills, education, outlook, wages, tasks, knowledge areas, technology skills
- **COMBINATION IDEAS**:
  - Map H-1B SOC codes to O*NET skills profiles → "What skills does this visa job actually require?"
  - Identify which occupations have the highest H-1B sponsorship rates vs. labor supply
  - Education requirements from O*NET vs. what's listed on LCA filings → discrepancy detection
  - Career pathway mapping: "You have X skills → these H-1B-friendly occupations match"
  - Automation risk scores from O*NET → which H-1B jobs are at risk of being automated?

### 9. BLS JOLTS Data (Job Openings and Labor Turnover)
- **URL**: https://download.bls.gov/pub/time.series/jt/
- **Access**: Free bulk download, time series format
- **Series**: Job openings, hires, separations, quits, layoffs by industry
- **COMBINATION IDEAS**:
  - Industries with highest job openings but lowest quits = talent gaps = H-1B sponsorship hotspots
  - Quits rate by industry → worker leverage → wage negotiation power for H-1B holders
  - Layoff rates → "Is this industry volatile?" Risk signal for visa holders
  - Leading indicator: job openings rising in an industry → predict H-1B filing surge next quarter

### 10. BLS Occupational Employment and Wage Statistics (OEWS)
- **URL**: https://www.bls.gov/oes/tables.htm
- **Access**: Free downloads
- **Granularity**: By occupation, industry, state, metro area
- **COMBINATION IDEAS**:
  - Compare H-1B prevailing wages vs. actual market wages from OEWS
  - Identify metros where H-1B wages significantly trail market → exploitation signal
  - Wage percentile data → "Is this H-1B offer at the 25th or 75th percentile?"

### 11. NSF Survey of Earned Doctorates
- **URL**: https://ncses.nsf.gov/surveys/earned-doctorates
- **Access**: Free data tables, restricted microdata available
- **Key fields**: Citizenship status (US native, naturalized, permanent resident, temporary visa), field of study, institution, post-graduation plans
- **Annual census since 1958**, 58K+ doctorate recipients per year
- **COMBINATION IDEAS**:
  - Pipeline analysis: Which fields produce the most temporary visa holders → future H-1B demand
  - Country-of-origin patterns for STEM doctorates → predict which nationalities will file H-1Bs
  - Track "intent to stay in US" by field → which disciplines lose talent?
  - University → employer pipeline mapping for international graduates

### 12. SAM.gov Entity Registration + Contract Awards API
- **URL**: https://open.gsa.gov/api/ (multiple APIs)
- **Access**: Free, API key required
- **APIs confirmed**:
  - Entity Management API — search registered federal contractors
  - Contract Awards API — federal contract data
  - CALC API — labor rate data for GSA professional services
  - Exclusions API — debarred/excluded entities
- **COMBINATION IDEAS**:
  - Cross-reference SAM.gov registered contractors with H-1B sponsors
  - Labor rate data from CALC → what does the government pay for the same roles H-1B workers fill?
  - Excluded entities → "Has this H-1B sponsor ever been debarred from government contracts?"

### 13. Data.gov Datasets
- **URL**: https://catalog.data.gov/
- **Access**: Free, CKAN API at /api/3
- **H-1B related datasets found**:
  - DOL H-1B investigative case data (enforcement actions)
  - Nonimmigrant visa issuances by category and nationality (State Dept, FY1997-2014)
  - DHS ELIS visa data
  - CW-1 program data
- **COMBINATION IDEAS**:
  - Enforcement/investigation data → which employers have been investigated for H-1B violations?
  - Visa issuance by nationality → demand forecasting by country

---

## TIER 3: CREATIVE / UNCONVENTIONAL SOURCES (Nobody is combining these)

### 14. Layoffs.fyi / WARN Act Data
- **URL**: https://layoffs.fyi (Airtable-based tracker)
- **Data**: Company name, employees affected, date, public/private status
- **Tracked 165K+ layoffs in 2026 alone across 1,000+ companies**
- **WARN Act**: Federal law requires 60-day notice for mass layoffs. State labor departments publish these.
  - Each state publishes separately (CA, NY, TX are most useful)
  - Fields: Company, location, number affected, layoff date, reason
- **COMBINATION IDEAS**:
  - H-1B holders at companies announcing layoffs have 60 days to find new sponsor
  - "ALERT: Your employer just filed a WARN notice — here are companies in your field actively sponsoring"
  - Track which H-1B-heavy employers are laying off → immigration crisis early warning
  - Layoff volume at IT staffing companies (Cognizant, Infosys, Wipro) → systemic risk signal

### 15. Court Records (CourtListener API)
- **URL**: https://www.courtlistener.com/api/rest/v4/
- **Access**: Free API
- **Data**: Dockets, opinions, parties, attorneys, judges, RECAP documents
- **COMBINATION IDEAS**:
  - Immigration court outcomes by employer (were they sued for visa fraud?)
  - Wage theft lawsuits against H-1B sponsors
  - Class action suits involving foreign workers
  - Track which immigration attorneys have highest success rates

### 16. BuiltWith (Technology Profiling)
- **URL**: https://builtwith.com/
- **Access**: Paid API (pricing not publicly listed), free basic lookups
- **Data**: Technology stack of any website — frameworks, analytics, hosting, CMS, etc.
- **COMBINATION IDEAS**:
  - Profile H-1B sponsor companies' tech stacks → what skills are they hiring for?
  - Detect technology migration (company moving from Java to Python → hiring Python developers)
  - Correlate tech stack complexity with H-1B sponsorship volume
  - Alternative to GitHub for non-open-source companies

### 17. Crunchbase (Startup Funding)
- **URL**: https://www.crunchbase.com/
- **Access**: Paid API ($149-499/mo), free basic search
- **Data**: Company funding rounds, investors, founding date, employee count, industry
- **COMBINATION IDEAS**:
  - Recently funded startups → predict new H-1B sponsorship (they need to hire fast)
  - Series B+ companies → established enough to handle sponsorship paperwork
  - Investor patterns → VCs that fund companies which heavily sponsor H-1Bs
  - "Companies that just raised $50M+ in your field" → likely starting to sponsor

### 18. SEC EDGAR — Deeper Analysis
- **Already confirmed 40+ companies mention H-1B in 10-K filings**
- Companies by SIC code:
  - 7389 (Services): 5 filings (staffing/consulting)
  - 2834 (Pharma): 4 filings
  - 7374 (Data Processing): 4 filings
  - 7363 (Temp Staffing): 3 filings
  - 7371 (Computer Programming): 2 filings (Cognizant)
- **States**: CA (14), AZ (4), NJ (4), NY (4), MI (3)
- **DEEPER COMBINATION IDEAS**:
  - Parse proxy statements (DEF 14A) for executive compensation tied to diversity/inclusion metrics → companies incentivized to maintain international workforce
  - 10-K risk factor analysis over time → is H-1B dependency growing or shrinking?
  - Correlate company revenue growth with H-1B filing volumes

### 19. PatentsView (USPTO Patent Data)
- **URL**: https://patentsview.org/
- **Note**: Legacy API discontinued, new API requires authentication
- **Data**: Patents by assignee (company), inventor, technology class, citations
- **COMBINATION IDEAS**:
  - Which H-1B sponsors are the most innovative? (patent volume)
  - Inventor nationality data → track foreign-born innovation contributions
  - Technology class → predict which technical skills are in demand
  - Patent → product → revenue pipeline analysis

### 20. OpenSecrets (Campaign Finance + Lobbying)
- **URL**: https://www.opensecrets.org/api
- **Access**: Free API key required (403 on initial fetch — needs registration)
- **Data**: Campaign contributions, lobbying expenditures, industry totals
- **COMBINATION IDEAS**:
  - Which industries spend the most lobbying on immigration? → follow the money
  - Individual company lobbying spend on immigration issues
  - Campaign contributions to members of immigration committees
  - Predict policy changes based on lobbying spend trends

---

## TIER 4: HIGH-CREATIVITY SOURCES (Untapped by competitors)

### 21. App Store / Product Data
- Apple App Store and Google Play rankings
- **Idea**: Company app success → growth → hiring → sponsorship
- Companies whose apps are growing rapidly will need to scale engineering teams
- App store revenue estimates (from Sensor Tower / App Annie) correlate with hiring

### 22. Glassdoor / Indeed Reviews
- No public API, but scraping/data partnerships possible
- **Ideas**:
  - Sentiment analysis of H-1B worker reviews vs. domestic workers at same company
  - "Visa sponsorship" mentioned in reviews → ground truth on sponsorship culture
  - Interview difficulty scores → how hard is it to get hired at top sponsors?
  - Company rating trends → declining ratings at H-1B-heavy firms = retention risk

### 23. LinkedIn Company Data
- No public API (LinkedIn restricts heavily)
- **Ideas**:
  - Employee growth rate → predict H-1B filings
  - Job posting volume with "visa sponsorship" in description
  - Department growth (engineering growing faster than sales = tech hiring)
  - Employee origin countries → international workforce composition

### 24. Corporate Diversity/ESG Reports
- **Access**: Published annually by most public companies, available on corporate websites
- **Ideas**:
  - Track international workforce percentages
  - Companies with strong D&I commitments → more likely to maintain sponsorship
  - ESG scores correlated with immigration friendliness

### 25. University International Student Data (SEVIS/ICE)
- **URL**: https://www.ice.gov/sevis/data
- **Access**: Free annual reports
- **Data**: International student counts by school, field, country, degree level
- **COMBINATION IDEAS**:
  - University → OPT → H-1B pipeline mapping
  - Which schools produce the most H-1B workers?
  - Field of study trends → predict future H-1B demand by occupation
  - Geographic clustering: schools near tech hubs → local employer sponsorship patterns

### 26. State Workforce Agency Data
- Each state publishes employment data, wage data, and industry projections
- **Ideas**:
  - State-level H-1B concentration vs. local unemployment → political risk assessment
  - Which states are adding/losing H-1B-friendly industries?
  - State prevailing wage determinations vs. actual offers

### 27. Census Bureau — American Community Survey
- **URL**: https://www.census.gov/programs-surveys/acs
- **Access**: Free API + bulk downloads
- **Data**: Foreign-born population, citizenship status, occupation, income, education, language by geography
- **COMBINATION IDEAS**:
  - Existing immigrant community presence → predict which metros attract H-1B workers
  - Education levels of foreign-born workers by metro → skills supply analysis
  - Occupation × citizenship status → which jobs are immigrant-heavy?

### 28. EEOC Employer Information Reports (EEO-1)
- **Access**: Limited — aggregated data published, individual employer data via FOIA
- **Data**: Workforce demographics by job category, race, gender
- **Ideas**: Diversity composition at H-1B sponsors → how international is their workforce really?

---

## UNIQUE COMBINATION STRATEGIES (The Real Competitive Advantage)

### Strategy 1: "Sponsor Reliability Score"
Combine: USCIS approval rates + SEC financial health + USAspending contracts + WARN layoff data + Glassdoor ratings
- Score = How reliable is this employer as an H-1B sponsor?
- Factors: approval rate, revenue stability, layoff history, employee satisfaction

### Strategy 2: "H-1B Market Predictor"
Combine: JOLTS job openings + FRED economic indicators + Crunchbase funding + GitHub activity
- Predict which industries/companies will increase sponsorship next quarter
- Leading indicators before LCA filings appear

### Strategy 3: "Wage Fairness Index"
Combine: DOL LCA wages + BLS OEWS market wages + FRED wage growth + Glassdoor salary data
- "Is this H-1B offer fair?" with percentile ranking
- Track wage progression over multiple LCA filings for same employer

### Strategy 4: "Policy Risk Dashboard"
Combine: Senate lobbying data + OpenSecrets spend + SEC risk factor language + USCIS denial trends
- Predict immigration policy changes
- Score companies by policy exposure risk

### Strategy 5: "Talent Pipeline Intelligence"
Combine: NSF doctorate data + SEVIS/ICE student data + University rankings + H-1B filings by employer
- Map the full pipeline: university → OPT → H-1B → green card
- Identify which schools feed which employers
- Country-of-origin pipeline analysis

### Strategy 6: "Federal Contractor + H-1B Crosswalk"
Combine: USAspending contracts + SAM.gov entities + DOL LCA data + USCIS approvals
- Unique dataset: companies getting taxpayer money AND sponsoring foreign workers
- Political sensitivity analysis
- Revenue stability signal for workers choosing employers

### Strategy 7: "Technology Demand Forecaster"
Combine: GitHub tech stacks + BuiltWith profiles + H-1B job titles/SOC codes + O*NET skills + Patent data
- Predict which technical skills will be in highest H-1B demand
- "Learn Rust — companies sponsoring H-1Bs are adopting it fastest"
- Skills gap analysis by geography

---

## SUMMARY: API ACCESS MATRIX

| Source | Free API | Bulk Download | Auth Required | Rate Limit |
|--------|----------|---------------|---------------|------------|
| DOL LCA/PERM | No (files) | Yes (Excel) | No | N/A |
| USCIS Employer Hub | No | Yes (Excel/CSV) | No | N/A |
| USAspending | Yes | Yes | No | Generous |
| GitHub | Yes | Via API | Optional | 60/5000 req/hr |
| FRED | Yes | Via API | API key | Moderate |
| Senate Lobbying | Yes | Via API | No | Unknown |
| SEC EDGAR | Yes | Yes | No | 10 req/sec |
| O*NET | Yes | Yes | Registration | Unknown |
| BLS JOLTS/OEWS | No | Yes (text/Excel) | No | N/A |
| NSF Doctorates | No | Yes (Excel) | No | N/A |
| SAM.gov | Yes | Yes | API key | Unknown |
| Data.gov | Yes (CKAN) | Varies | No | Unknown |
| CourtListener | Yes | Yes | No | Unknown |
| Crunchbase | Paid | No | Yes | Paid tier |
| BuiltWith | Paid | No | Yes | Paid tier |
| PatentsView | Yes (new) | Yes | Registration | Unknown |
| Census ACS | Yes | Yes | API key | Generous |

---

## RECOMMENDED BUILD ORDER

1. **Week 1-2**: DOL LCA + USCIS Hub (core H-1B data, free, downloadable)
2. **Week 3-4**: USAspending crosswalk (federal contractor overlay)
3. **Week 5-6**: SEC EDGAR H-1B mentions + BLS wage data (fair wage analysis)
4. **Week 7-8**: GitHub tech stack profiling (technology demand signals)
5. **Month 3**: FRED economic indicators + JOLTS (market prediction layer)
6. **Month 4**: Lobbying data + layoff trackers (policy/risk layer)
7. **Month 5+**: NSF/SEVIS pipeline data, O*NET skills mapping, patent data
