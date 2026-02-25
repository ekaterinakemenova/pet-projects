"""
Export aggregated tables for Tableau dashboard.

Run from project root: python scripts/export_tableau_tables.py

Output: CSV files in outputs/ folder.

Table → Visualization mapping:
  fact_job_postings           — KPI cards, filters, histogram (skills_count)
  agg_country                 — Bar / pie / donut (вакансии по странам)
  agg_experience              — Bar / pie (junior vs mid+)
  agg_remote                  — KPI (remote %)
  agg_top_skills              — Horizontal bar (top skills)
  agg_skills_by_country       — Heatmap skills × country
  agg_skills_by_experience    — Grouped bar / heatmap junior vs mid+
  agg_skills_gap              — Diverging bar (gap mid+ − junior)
  agg_skill_categories        — Treemap (категории навыков)
  agg_skill_categories_by_exp — Grouped bar категорий по experience
  agg_skills_count_dist       — Histogram (skills per posting)
  agg_skills_count_by_exp     — Box plot / сводка по experience
"""

import os
from pathlib import Path

import pandas as pd

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "jsearch_cleaned_with_skills.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

SKILL_CATEGORIES = {
    "Programming": ["sql", "python", "r"],
    "Spreadsheets": ["excel", "google_sheets"],
    "Databases": [
        "postgresql", "mysql", "oracle", "sql_server", "bigquery",
        "snowflake", "redshift", "vertica", "clickhouse", "databricks", "synapse"
    ],
    "Visualisation & BI Tools": [
        "dashboards", "data_visualization", "power_bi", "tableau", "looker",
        "qlik", "datalens", "superset"
    ],
    "Data Engineering": [
        "airflow", "hadoop", "spark", "kafka", "dbt",
        "talend", "informatica", "etl", "data_pipeline"
    ],
    "AI/ML Tools": ["chatgpt", "claude", "cursor", "copilot", "gemini"],
    "Statistics": [
        "statistics", "a_b_testing", "experimentation",
        "hypothesis_testing", "data_cleaning"
    ],
}


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DATA_PATH)
    df["posted_at_datetime_utc"] = pd.to_datetime(df["posted_at_datetime_utc"])

    skill_cols = [c for c in df.columns if c.startswith("skill_")]
    df["skills_count"] = df[skill_cols].sum(axis=1)
    n_total = len(df)

    # -------------------------------------------------------------------------
    # 1. fact_job_postings — базовая таблица для KPI, фильтров, drill-down
    # KPI cards, histogram skills per posting, фильтры по country/experience
    # -------------------------------------------------------------------------
    fact_cols = [
        "id", "title", "country_name", "country_code", "experience_group",
        "is_remote", "is_full_time", "is_part_time", "is_contractor", "is_internship",
        "skills_count", "posted_at_datetime_utc"
    ]
    fact_cols = [c for c in fact_cols if c in df.columns]
    fact_job_postings = df[fact_cols].copy()
    fact_job_postings.to_csv(OUTPUT_DIR / "fact_job_postings.csv", index=False)
    print(f"Saved: fact_job_postings.csv ({len(fact_job_postings)} rows)")

    # -------------------------------------------------------------------------
    # 2. agg_country — распределение по странам (bar, pie, donut)
    # -------------------------------------------------------------------------
    agg_country = (
        df["country_name"]
        .value_counts()
        .reset_index()
    )
    agg_country.columns = ["country_name", "count"]
    agg_country["share"] = agg_country["count"] / agg_country["count"].sum() * 100
    agg_country.to_csv(OUTPUT_DIR / "agg_country.csv", index=False)
    print(f"Saved: agg_country.csv")

    # -------------------------------------------------------------------------
    # 3. agg_experience — junior vs mid+ (bar, pie)
    # -------------------------------------------------------------------------
    agg_experience = (
        df["experience_group"]
        .value_counts()
        .reset_index()
    )
    agg_experience.columns = ["experience_group", "count"]
    agg_experience["share"] = agg_experience["count"] / agg_experience["count"].sum() * 100
    agg_experience.to_csv(OUTPUT_DIR / "agg_experience.csv", index=False)
    print(f"Saved: agg_experience.csv")

    # -------------------------------------------------------------------------
    # 4. agg_remote — remote vs on-site (для KPI)
    # -------------------------------------------------------------------------
    agg_remote = (
        df["is_remote"]
        .value_counts()
        .reset_index()
    )
    agg_remote.columns = ["is_remote", "count"]
    agg_remote["share"] = agg_remote["count"] / agg_remote["count"].sum() * 100
    agg_remote.to_csv(OUTPUT_DIR / "agg_remote.csv", index=False)
    print(f"Saved: agg_remote.csv")

    # -------------------------------------------------------------------------
    # 5. agg_top_skills — Top N skills (horizontal bar)
    # -------------------------------------------------------------------------
    top_skills = df[skill_cols].agg(["sum", "mean"]).T.reset_index()
    top_skills.columns = ["skill_name", "count", "share"]
    top_skills["share"] = top_skills["share"] * 100
    top_skills["skill"] = top_skills["skill_name"].str.replace("skill_", "", regex=False)
    top_skills = top_skills.sort_values("count", ascending=False).reset_index(drop=True)
    top_skills.to_csv(OUTPUT_DIR / "agg_top_skills.csv", index=False)
    print(f"Saved: agg_top_skills.csv ({len(top_skills)} skills)")

    # -------------------------------------------------------------------------
    # 6. agg_skills_by_country — heatmap skills × country (long format)
    # -------------------------------------------------------------------------
    skills_by_country = (
        df.groupby("country_name")[skill_cols]
        .sum()
        .T
    )
    skills_by_country = skills_by_country.reset_index().rename(columns={"index": "skill_name"})
    skills_by_country_long = skills_by_country.melt(
        id_vars="skill_name",
        var_name="country_name",
        value_name="count"
    )
    country_totals = df.groupby("country_name").size()
    skills_by_country_long["share"] = skills_by_country_long.apply(
        lambda r: r["count"] / country_totals[r["country_name"]] * 100
        if country_totals[r["country_name"]] > 0 else 0,
        axis=1
    )
    skills_by_country_long["skill"] = skills_by_country_long["skill_name"].str.replace(
        "skill_", "", regex=False
    )
    skills_by_country_long.to_csv(OUTPUT_DIR / "agg_skills_by_country.csv", index=False)
    print(f"Saved: agg_skills_by_country.csv")

    # -------------------------------------------------------------------------
    # 7. agg_skills_by_experience — grouped bar / heatmap junior vs mid+
    # -------------------------------------------------------------------------
    skills_by_exp = df.groupby("experience_group")[skill_cols].mean() * 100
    skills_by_exp = skills_by_exp.T.reset_index()
    skills_by_exp = skills_by_exp.rename(columns={"index": "skill_name"})
    skills_by_exp_long = skills_by_exp.melt(
        id_vars="skill_name",
        var_name="experience_group",
        value_name="share"
    )
    skills_by_exp_long["skill"] = skills_by_exp_long["skill_name"].str.replace(
        "skill_", "", regex=False
    )
    skills_by_exp_long.to_csv(OUTPUT_DIR / "agg_skills_by_experience.csv", index=False)
    print(f"Saved: agg_skills_by_experience.csv")

    # -------------------------------------------------------------------------
    # 8. agg_skills_gap — diverging bar (mid+ - junior)
    # -------------------------------------------------------------------------
    gap_df = skills_by_exp.copy()
    gap_df["gap"] = gap_df["mid_plus"] - gap_df["junior"]
    gap_df["skill"] = gap_df["skill_name"].str.replace("skill_", "", regex=False)
    gap_df = gap_df.rename(columns={"junior": "junior_share", "mid_plus": "mid_plus_share"})
    gap_df = gap_df.sort_values("gap", key=abs, ascending=False).reset_index(drop=True)
    gap_df.to_csv(OUTPUT_DIR / "agg_skills_gap.csv", index=False)
    print(f"Saved: agg_skills_gap.csv")

    # -------------------------------------------------------------------------
    # 9. agg_skill_categories — treemap категорий
    # -------------------------------------------------------------------------
    category_share = {}
    category_count = {}
    for category, skills in SKILL_CATEGORIES.items():
        cols = [f"skill_{s}" for s in skills if f"skill_{s}" in df.columns]
        if cols:
            mentioned = df[cols].max(axis=1)
            category_share[category] = mentioned.mean() * 100
            category_count[category] = int(mentioned.sum())

    agg_categories = (
        pd.Series(category_share)
        .sort_values(ascending=False)
        .reset_index()
    )
    agg_categories.columns = ["skill_category", "share"]
    agg_categories["count"] = agg_categories["skill_category"].map(category_count)
    agg_categories.to_csv(OUTPUT_DIR / "agg_skill_categories.csv", index=False)
    print(f"Saved: agg_skill_categories.csv")

    # -------------------------------------------------------------------------
    # 10. agg_skill_categories_by_experience — grouped bar категорий
    # -------------------------------------------------------------------------
    cat_exp_records = []
    for group in df["experience_group"].unique():
        subset = df[df["experience_group"] == group]
        for category, skills in SKILL_CATEGORIES.items():
            cols = [f"skill_{s}" for s in skills if f"skill_{s}" in df.columns]
            if cols:
                share = subset[cols].max(axis=1).mean() * 100
                cat_exp_records.append({
                    "experience_group": group,
                    "skill_category": category,
                    "share": share
                })

    agg_cat_exp = pd.DataFrame(cat_exp_records)
    agg_cat_exp.to_csv(OUTPUT_DIR / "agg_skill_categories_by_experience.csv", index=False)
    print(f"Saved: agg_skill_categories_by_experience.csv")

    # -------------------------------------------------------------------------
    # 11. agg_skills_count_dist — histogram (bins для skills per posting)
    # -------------------------------------------------------------------------
    skills_count_dist = (
        df["skills_count"]
        .value_counts()
        .sort_index()
        .reset_index()
    )
    skills_count_dist.columns = ["skills_count", "count"]
    skills_count_dist["share"] = skills_count_dist["count"] / n_total * 100
    skills_count_dist.to_csv(OUTPUT_DIR / "agg_skills_count_dist.csv", index=False)
    print(f"Saved: agg_skills_count_dist.csv")

    # -------------------------------------------------------------------------
    # 12. agg_skills_count_by_experience — box plot / сравнение median
    # -------------------------------------------------------------------------
    skills_count_by_exp = (
        df.groupby("experience_group")["skills_count"]
        .agg(["count", "mean", "median", "min", "max"])
        .reset_index()
    )
    skills_count_by_exp.to_csv(OUTPUT_DIR / "agg_skills_count_by_experience.csv", index=False)
    print(f"Saved: agg_skills_count_by_experience.csv")

    print("\nAll tables exported to outputs/")


if __name__ == "__main__":
    main()
