<div align="center">

# Netflix Data Analysis Using Python

**End-to-end analysis of the Netflix catalogue: cleaning, exploration, dashboards and business insights**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C)
![Seaborn](https://img.shields.io/badge/Seaborn-4C72B0)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?logo=plotly&logoColor=white)
![Status](https://img.shields.io/badge/Tasks-6%2F6%20completed-E50914)

Auspify Technologies | Data Analysis Using Python Internship

`#Auspify` `#AuspifyTechnologies` `#AuspifyInternship` `#AuspifyProjects`

</div>

---

## Overview

This repository contains six analysis tasks built on a Netflix titles dataset (8,790 raw records, 8,786 after cleaning). Each task is a standalone Python script that reads the cleaned dataset, produces charts and tables, and prints its findings.

| Task | Level | Focus | Script |
|------|-------|-------|--------|
| 1 | Easy | Data cleaning and preparation | `task1_data_cleaning.py` |
| 2 | Easy | Content type analysis dashboard | `task2_content_type_dashboard.py` |
| 3 | Medium | Country-wise content analysis | `task3_country_analysis.py` |
| 4 | Medium | Trend analysis by release year | `task4_release_year_trends.py` |
| 5 | Advanced | Content rating and genre analysis | `task5_rating_genre_analysis.py` |
| 6 | Advanced | Business insights report | `task6_business_insights_report.py` |

## Key Findings

- **Catalogue mix:** 69.7% Movies (6,123) and 30.3% TV Shows (2,663).
- **Geography:** the United States holds 38.1% of titles with a known country; the top 5 countries hold 66.2%.
- **Audience:** Adult-rated content is 45.6% of the catalogue, while Kids and Older Kids together are 23.4%.
- **Trends:** yearly releases peaked in 2018 (1,144 titles), and 85% of the catalogue was released after 2009.
- **Formats:** median movie runtime is 98 minutes, and 67% of TV Shows have a single season.
- **Market differences:** Pakistan is series-led (83% TV Shows) while India is movie-led (8% TV Shows).

The data ends in September 2021, so 2021 figures are partial.

## Dashboards

### Executive overview (Task 6)
![Executive Dashboard](outputs/task6/dashboard_1_executive_overview.png)

### Content type analysis (Task 2)
![Content Type](outputs/task2/content_type_dashboard.png)

### Country analysis (Task 3)
![Countries](outputs/task3/top_countries.png)

### Release year trends (Task 4)
![Trends](outputs/task4/release_year_trends.png)

### Ratings and genres (Task 5)
![Ratings and Genres](outputs/task5/rating_genre_dashboard.png)

### Content deep dive (Task 6)
![Deep Dive](outputs/task6/dashboard_2_content_deep_dive.png)

### Interactive outputs

GitHub does not render HTML files, so download the repository and open these in a browser:

- `outputs/task3/world_map.html`
- `outputs/task5/sunburst_type_audience_rating.html`
- `outputs/task5/top_genres_interactive.html`
- `outputs/task6/dashboard_3_interactive.html`
- `outputs/task6/Netflix_Business_Insights_Report.html` (full report)

## Cleaning Decisions

- `Not Given` in `director` (2,588) and `country` (287) converted to `Unknown`.
- 4 duplicate records removed (same title, type, release year and duration under different IDs).
- `date_added` parsed to datetime; `year_added` and `month_added` created.
- `duration` split into `duration_value` and `duration_unit`.
- Countries standardised (West Germany to Germany, Soviet Union to Russia).
- Ratings grouped into Kids, Older Kids, Teens, Adults and Unrated.

## Project Structure

```
.
├── data/
│   ├── Dataset.csv
│   └── netflix_cleaned.csv
├── outputs/
│   ├── console_logs/
│   └── task2 ... task6/
├── task1_data_cleaning.py
├── task2_content_type_dashboard.py
├── task3_country_analysis.py
├── task4_release_year_trends.py
├── task5_rating_genre_analysis.py
├── task6_business_insights_report.py
├── run_all.py
└── requirements.txt
├── Screenshots/                  screenshots of completed tasks
```

## How to Run

```bash
git clone https://github.com/Hager-Abdelnasser/<repo-name>.git
cd <repo-name>
pip install -r requirements.txt
python run_all.py
```

To run a single task: `python task3_country_analysis.py`. Run Task 1 first, because it creates `data/netflix_cleaned.csv`.

## Tech Stack

Python, Pandas, Matplotlib, Seaborn, Plotly

## Limitations

- Each title has one country value, so co-productions are not split.
- Business recommendations in Task 6 are suggestions based on patterns in this dataset, not verified facts.

## Author

**Hager Abdelnasser**
Data Engineering and Data Analytics | Faculty of Computers and Information, Ain Shams University

[GitHub](https://github.com/Hager-Abdelnasser) | [LinkedIn](https://www.linkedin.com/in/hager-abdelnasser9/)
