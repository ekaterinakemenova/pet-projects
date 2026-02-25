# Data Analyst Skills: In-Demand Skills & Market Analysis

## Goal
Conduct an exploratory analysis of job posting data for *data analyst* and *junior data analyst* roles across major English-speaking markets in order to identify the most in-demand technical skills, compare skill requirements across experience levels and countries, and support career planning.

## Tools & Stack
**Languages:** Python  
**Libraries:** pandas, numpy, requests, python-dotenv, matplotlib, seaborn  
**BI tool:** Tableau  
**Format:** Jupyter Notebooks + interactive dashboard

## Data
Job posting data sourced via JSearch API (RapidAPI), which aggregates Google for Jobs listings across LinkedIn, Indeed, Glassdoor, ZipRecruiter, and others.
- **Period:** 18 January - 17 February 2026 (one-month snapshot)
- **Markets:** USA, United Kingdom, Canada
- **Roles:** data analyst, junior data analyst
- **Coverage:** ~1,200 raw postings; ~1,140 postings after deduplication and country validation.

## Key Steps

**1. Data collection** (`notebooks/01_jsearch_data_collection.ipynb`)
- Reusable function to fetch jobs from JSearch API with pagination and rate-limit handling

**2. Data cleaning & skill extraction** (`notebooks/02_cleaning_and_skills.ipynb`)
- Column standardisation, data type conversion, deduplication, missing value handling, categorical validation
- Deriving `experience_group` (junior vs mid_plus) from job titles
- Job description cleaning (lowercase, HTML removal, whitespace normalisation) for keyword-based skill extraction
- Skills dictionary with 43 skills and regex patterns; binary indicators extracted from job description text

**3. EDA & visualisation** (`notebooks/03_eda_and_plots.ipynb`)
- Sample breakdown by country, experience level, employment type, remote status
- Skill demand analysis: top skills, skills by category, skills by country, average skills per posting
- Junior vs middle+ skill comparison and gap analysis

**4. Dashboard creation**
- [Data Analyst Skills Analysis (Jan–Feb 2026)](https://public.tableau.com/app/profile/ekaterina.kemenova/viz/DataAnalystSkillsAnalysisJan-Feb2026/DataAnalystSkillsAnalysisJan-Feb2026) — published on Tableau Public

## Main Findings
- **Core skill set:** SQL is the most in-demand skill (~55% of postings), with Python and Excel close behind (~36% each). BI tools (20-36% of postings) and statistics (28%) round out the core stack.
- **Experience-level differences:** Junior roles focus on core skills (Excel, Python, statistics, data visualisation, data cleaning). Middle+ roles add cloud databases (Snowflake, Databricks) and data engineering tools (ETL, pipelines, dbt).
- **Skill categories:** Programming (62%) and BI tools (56%) are the top categories at both experience levels. Data engineering rises from 15% in junior to 23% in middle+ postings.
- **Geographic variation:** USA makes up ~60% of postings. The core stack is consistent across all three markets, with Canada showing higher demand for data engineering skills and the USA leading on Excel and Tableau.

## Recommendations
- **Master the core stack first**: SQL, Python, and at least one BI tool (Power BI or Tableau) appear in the majority of postings across all markets and seniority levels - these should be the foundation before investing time in niche tools.
- **Add data engineering skills to progress to middle+**: The clearest gap between junior and middle+ postings is in ETL, pipelines, and cloud tools (Snowflake, Databricks, dbt) - these are the skills to build once the core stack is solid.
