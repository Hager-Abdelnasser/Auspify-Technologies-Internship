# Netflix Data Analysis Using Python

Auspify Technologies - Data Analysis Using Python Internship

Six tasks on the Netflix catalogue (8,790 raw records, 8,786 after cleaning). Each task has its own script.

## Structure

```
Auspify_Netflix_Project/
├── data/
│   ├── Dataset.csv                  raw data
│   └── netflix_cleaned.csv          output of Task 1
├── task1_data_cleaning.py
├── task2_content_type_dashboard.py
├── task3_country_analysis.py
├── task4_release_year_trends.py
├── task5_rating_genre_analysis.py
├── task6_business_insights_report.py
├── run_all.py                       runs all tasks in order
├── requirements.txt
└── outputs/
    ├── task2 ... task6              charts, tables, insights
    └── console_logs                 printed output of every script
```

## Run

```bash
pip install -r requirements.txt
python run_all.py
```

Or run one task: `python task3_country_analysis.py` (Task 1 must run first because it creates the cleaned dataset).

## Tasks

| Task | Level | Main outputs |
|------|-------|--------------|
| 1. Data Cleaning & Preparation | Easy | `data/netflix_cleaned.csv` |
| 2. Content Type Analysis Dashboard | Easy | dashboard PNG, summary tables, key findings |
| 3. Country-Wise Content Analysis | Medium | ranking CSV, charts, interactive world map |
| 4. Trend Analysis by Release Year | Medium | trend dashboard, heatmap, yearly table |
| 5. Content Rating & Genre Analysis | Advanced | dashboard PNG, 5 interactive HTML charts |
| 6. Business Insights Report | Advanced | 3 dashboards, HTML report, executive summary |

## Cleaning decisions

- `Not Given` in `director` and `country` converted to `Unknown` (2,588 and 287 records).
- 4 duplicate records (same title, type, release year and duration under different IDs) removed.
- `date_added` parsed to datetime; `year_added` and `month_added` created.
- `duration` split into `duration_value` and `duration_unit`.
- Country names standardised (West Germany to Germany, Soviet Union to Russia); ratings grouped into Kids, Older Kids, Teens, Adults, Unrated.

## Notes

- The data ends in September 2021, so 2021 figures are partial.
- Each title has one country value; co-productions are not split.
