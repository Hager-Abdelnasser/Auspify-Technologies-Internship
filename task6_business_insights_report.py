import base64
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
from plotly.subplots import make_subplots

BASE = Path(__file__).resolve().parent
OUT = BASE / "outputs" / "task6"
OUT.mkdir(parents=True, exist_ok=True)

RED, DARK, GREY = "#E50914", "#221F1F", "#B3B3B3"
sns.set_theme(style="whitegrid")

df = pd.read_csv(BASE / "data" / "netflix_cleaned.csv", parse_dates=["date_added"])
movies, shows = df[df["type"] == "Movie"], df[df["type"] == "TV Show"]
known_country = df[df["country"] != "Unknown"]
known_director = df[df["director"] != "Unknown"]
genres = df.assign(genre=df["listed_in"].str.split(",")).explode("genre")
genres["genre"] = genres["genre"].str.strip()

print("STEP 1 | EXPLORATORY DATA ANALYSIS")
print(f"Shape: {df.shape} | Date range added: {df['date_added'].min():%Y-%m-%d} to {df['date_added'].max():%Y-%m-%d}")
print("\nNumeric summary\n", df[["release_year", "duration_value", "genre_count"]].describe().round(1).to_string())
print("\nUnique values\n", df[["show_id", "title", "director", "country", "rating", "primary_genre"]].nunique().to_string())
print("\nData completeness (share of records with real value)")
completeness = pd.Series({
    "country": len(known_country) / len(df) * 100,
    "director": len(known_director) / len(df) * 100,
    "date_added": df["date_added"].notna().mean() * 100,
}).round(1)
print(completeness.to_string())

movie_median = movies["duration_value"].median()
movie_mean = movies["duration_value"].mean()
short_movies = (movies["duration_value"] < 90).mean() * 100
long_movies = (movies["duration_value"] > 120).mean() * 100
one_season = (shows["duration_value"] == 1).mean() * 100
three_plus = (shows["duration_value"] >= 3).mean() * 100
print(f"\nMovie runtime: median {movie_median:.0f} min, mean {movie_mean:.0f} min | under 90 min: {short_movies:.1f}% | over 120 min: {long_movies:.1f}%")
print(f"TV seasons: 1 season {one_season:.1f}% | 3+ seasons {three_plus:.1f}% | max {shows['duration_value'].max()} seasons")

top_directors = known_director.assign(d=known_director["director"].str.split(",")).explode("d")
top_directors["d"] = top_directors["d"].str.strip()
director_counts = top_directors["d"].value_counts().head(10)
print("\nTop 10 directors\n", director_counts.to_string())

print("\nSTEP 2 | KEY TRENDS AND PATTERNS")
country_counts = known_country["country"].value_counts()
top5 = country_counts.head(5)
top_genre_by_country = (genres[genres["country"].isin(top5.index)]
                        .groupby("country")["genre"].agg(lambda s: s.value_counts().index[0]).reindex(top5.index))
print("Leading genre tag in each top-5 country\n", top_genre_by_country.to_string())
added_year = df.groupby("year_added").size()
release_year = df.groupby("release_year").size()
peak_added, peak_release = int(added_year.idxmax()), int(release_year.idxmax())
print(f"Peak year titles were added: {peak_added} ({added_year.max():,}) | Peak release year: {peak_release} ({release_year.max():,})")
tv_share_by_year = df[df["year_added"] >= 2016].groupby("year_added")["type"].apply(lambda s: (s == "TV Show").mean() * 100).round(1)
print("TV Show share of additions by year (%)\n", tv_share_by_year.to_string())

print("\nSTEP 3 | DASHBOARDS")
fig = plt.figure(figsize=(18, 11))
gs = fig.add_gridspec(3, 4, height_ratios=[0.55, 1.6, 1.6], hspace=0.5, wspace=0.7)
fig.suptitle("Netflix Executive Dashboard", fontsize=22, fontweight="bold", color=DARK, y=0.99)

kpis = [("Total titles", f"{len(df):,}"), ("Movies", f"{len(movies):,}"), ("TV Shows", f"{len(shows):,}"),
        ("Countries", f"{known_country['country'].nunique()}")]
for i, (label, value) in enumerate(kpis):
    ax = fig.add_subplot(gs[0, i])
    ax.set_facecolor(RED if i == 0 else DARK)
    ax.set_xticks([]); ax.set_yticks([])
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.text(0.5, 0.58, value, ha="center", va="center", fontsize=26, fontweight="bold", color="white", transform=ax.transAxes)
    ax.text(0.5, 0.15, label, ha="center", va="center", fontsize=12, color="white", transform=ax.transAxes)

ax = fig.add_subplot(gs[1, 0:2])
added = df[df["year_added"] >= 2015].groupby(["year_added", "type"]).size().unstack(fill_value=0)
added.plot(kind="bar", stacked=True, color=[RED, DARK], ax=ax, width=0.8)
ax.set_title("Titles Added per Year")
ax.set_xlabel("")
ax.set_ylabel("Titles")
ax.tick_params(axis="x", rotation=0)
ax.legend(title="")

ax = fig.add_subplot(gs[1, 2:4])
c10 = country_counts.head(10).iloc[::-1]
ax.barh(c10.index, c10.values, color=[DARK] * 7 + [RED] * 3)
for y, v in enumerate(c10.values):
    ax.text(v + 25, y, f"{v:,}", va="center", fontsize=9, fontweight="bold")
ax.set_title("Top 10 Countries")
ax.set_xlim(0, c10.max() * 1.12)

ax = fig.add_subplot(gs[2, 0])
rg = df["rating_group"].value_counts().reindex(["Adults", "Teens", "Older Kids", "Kids", "Unrated"])
_, _, pcts = ax.pie(rg, labels=None, autopct=lambda v: f"{v:.0f}%" if v >= 3 else "", startangle=90, colors=[RED, "#B1060F", "#7A0A10", DARK, GREY],
                    wedgeprops=dict(width=0.45, edgecolor="white"), pctdistance=0.78, textprops=dict(fontsize=9))
for t in pcts:
    t.set_color("white")
    t.set_fontweight("bold")
ax.legend(rg.index, loc="upper center", bbox_to_anchor=(0.5, 0.02), ncol=3, fontsize=8, frameon=False, columnspacing=0.8)
ax.set_title("Audience Groups")

ax = fig.add_subplot(gs[2, 1:3])
g10 = genres["genre"].value_counts().head(10).iloc[::-1]
ax.barh(g10.index, g10.values, color=RED)
ax.set_title("Top 10 Genres")
ax.set_xlim(0, g10.max() * 1.1)

ax = fig.add_subplot(gs[2, 3])
sns.histplot(movies["duration_value"], bins=30, color=RED, ax=ax)
ax.axvline(movie_median, color=DARK, linestyle="--", linewidth=2)
ax.text(movie_median + 4, ax.get_ylim()[1] * 0.9, f"median {movie_median:.0f} min", fontsize=9, fontweight="bold")
ax.set_title("Movie Runtime")
ax.set_xlabel("Minutes")
ax.set_ylabel("")

fig.savefig(OUT / "dashboard_1_executive_overview.png", dpi=150, bbox_inches="tight")
plt.close(fig)

fig, axes = plt.subplots(2, 2, figsize=(17, 11))
fig.suptitle("Netflix Content Deep Dive", fontsize=22, fontweight="bold", color=DARK, y=0.98)

ax = axes[0, 0]
season_counts = shows["duration_value"].value_counts().sort_index()
season_counts = pd.concat([season_counts[season_counts.index <= 5], pd.Series({"6+": season_counts[season_counts.index > 5].sum()})])
season_counts.index = season_counts.index.astype(str)
ax.bar(season_counts.index, season_counts.values, color=DARK)
for x, v in zip(season_counts.index, season_counts.values):
    ax.text(x, v + 20, f"{v:,}", ha="center", fontsize=10, fontweight="bold")
ax.set_title("TV Shows by Number of Seasons")
ax.set_xlabel("Seasons")
ax.set_ylabel("Titles")

ax = axes[0, 1]
d10 = director_counts.iloc[::-1]
ax.barh(d10.index, d10.values, color=RED)
ax.set_title("Top 10 Directors (known directors only)")
ax.set_xlabel("Titles")

ax = axes[1, 0]
top8 = country_counts.head(8).index
ct = pd.crosstab(known_country[known_country["country"].isin(top8)]["country"], known_country[known_country["country"].isin(top8)]["rating_group"],
                 normalize="index").mul(100)[["Kids", "Older Kids", "Teens", "Adults"]].reindex(top8)
sns.heatmap(ct, annot=True, fmt=".0f", cmap=sns.light_palette(RED, as_cmap=True), linewidths=0.5, cbar_kws={"label": "% of titles"}, ax=ax)
ax.set_title("Audience Mix by Country (Top 8)")
ax.set_xlabel("")
ax.set_ylabel("")

ax = axes[1, 1]
lag = (df["year_added"] - df["release_year"]).clip(0, 10)
lag.value_counts().sort_index().plot(kind="bar", color=RED, ax=ax, width=0.8)
ax.set_xticklabels([f"{int(i)}" if i < 10 else "10+" for i in sorted(lag.unique())], rotation=0)
ax.set_title("Years Between Release and Netflix Addition")
ax.set_xlabel("Years")
ax.set_ylabel("Titles")

plt.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(OUT / "dashboard_2_content_deep_dive.png", dpi=150, bbox_inches="tight")
plt.close(fig)

panel = make_subplots(rows=2, cols=2, specs=[[{"type": "domain"}, {"type": "xy"}], [{"type": "xy"}, {"type": "xy"}]],
                      subplot_titles=("Content type", "Titles added per year", "Top 10 countries", "Top 10 genres"))
panel.add_trace(go.Pie(labels=df["type"].value_counts().index, values=df["type"].value_counts().values, hole=0.5,
                       marker=dict(colors=[RED, DARK])), row=1, col=1)
for t, color in (("Movie", RED), ("TV Show", DARK)):
    s = df[(df["type"] == t) & (df["year_added"] >= 2015)].groupby("year_added").size()
    panel.add_trace(go.Bar(x=s.index, y=s.values, name=t, marker_color=color), row=1, col=2)
panel.add_trace(go.Bar(x=country_counts.head(10).values[::-1], y=country_counts.head(10).index[::-1], orientation="h",
                       marker_color=RED, showlegend=False), row=2, col=1)
panel.add_trace(go.Bar(x=genres["genre"].value_counts().head(10).values[::-1], y=genres["genre"].value_counts().head(10).index[::-1],
                       orientation="h", marker_color=DARK, showlegend=False), row=2, col=2)
panel.update_layout(barmode="stack", title="Netflix Interactive Dashboard", height=850)
panel.write_html(OUT / "dashboard_3_interactive.html", include_plotlyjs="cdn")
print("Saved: dashboard_1_executive_overview.png, dashboard_2_content_deep_dive.png, dashboard_3_interactive.html")

print("\nSTEP 4 | ACTIONABLE BUSINESS INSIGHTS")
us_share = country_counts.iloc[0] / len(known_country) * 100
top5_share = top5.sum() / len(known_country) * 100
adult_share = (df["rating_group"] == "Adults").mean() * 100
family_share = df["rating_group"].isin(["Kids", "Older Kids"]).mean() * 100
india_tv = (known_country.loc[known_country["country"] == "India", "type"] == "TV Show").mean() * 100
pakistan_tv = (known_country.loc[known_country["country"] == "Pakistan", "type"] == "TV Show").mean() * 100
fresh_share = ((df["year_added"] - df["release_year"]) <= 1).mean() * 100
raw_rows = len(pd.read_csv(BASE / "data" / "Dataset.csv"))
removed_rows = raw_rows - len(df)
movies_2019 = int(df[(df["year_added"] == 2019) & (df["type"] == "Movie")].shape[0])
movies_2021 = int(df[(df["year_added"] == 2021) & (df["type"] == "Movie")].shape[0])

insights = [
    ("Catalogue mix", f"Movies are {len(movies) / len(df):.1%} of the catalogue. The TV Show share of yearly additions rose from {tv_share_by_year.iloc[1]}% in 2017 to {tv_share_by_year.iloc[-1]}% in 2021 while movie additions fell from {movies_2019:,} (2019) to {movies_2021:,} (2021, partial year)."),
    ("Geographic concentration", f"The United States alone holds {us_share:.1f}% of titles with a known country and the top 5 countries hold {top5_share:.1f}%. Diversification depends on a small set of markets."),
    ("Audience targeting", f"Adult-rated content is {adult_share:.1f}% of the catalogue versus {family_share:.1f}% for Kids and Older Kids. Family content is the smallest rated segment."),
    ("Market formats differ", f"Pakistan is series-led ({pakistan_tv:.0f}% TV Shows) while India is movie-led ({india_tv:.0f}% TV Shows), so the two largest South Asian markets need different content plans."),
    ("Content format", f"Median movie runtime is {movie_median:.0f} minutes and {one_season:.0f}% of TV Shows have a single season, so most series are short runs or limited series."),
    ("Freshness", f"{fresh_share:.0f}% of titles were added within a year of their release, and {(df['release_year'] >= 2010).mean():.0%} of the catalogue was released after 2009 (release-year peak: {peak_release}, {release_year.max():,} titles)."),
    ("Data quality", f"{100 - completeness['director']:.0f}% of titles have no director and {100 - completeness['country']:.0f}% have no country, which limits creator-level and market-level analysis."),
]
recommendations = [
    "Evaluate expanding family and kids programming, the smallest rated audience segment in the catalogue.",
    "Replicate the series-led approach seen in Pakistan, South Korea and Japan in other emerging markets.",
    "Reduce dependence on the US and India by growing mid-size markets such as Spain, Mexico, Egypt and Nigeria.",
    "Track TV Show seasons per title to measure retention and plan renewals for single-season series.",
    "Make country and director fields mandatory at ingestion to improve downstream analytics.",
]
for h, t in insights:
    print(f"- {h}: {t}")
print("\nRecommendations")
for r in recommendations:
    print("-", r)

print("\nSTEP 5 | FINAL ANALYTICAL REPORT")


def embed(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


def trend_image(name: str) -> str:
    p = BASE / "outputs" / name
    return embed(p) if p.exists() else ""


kpi_html = "".join(f'<div class="kpi"><span>{v}</span>{k}</div>' for k, v in [
    ("Titles", f"{len(df):,}"), ("Movies", f"{len(movies):,}"), ("TV Shows", f"{len(shows):,}"),
    ("Countries", f"{known_country['country'].nunique()}"), ("Release years", f"{df['release_year'].min()}-{df['release_year'].max()}")])
insight_html = "".join(f"<li><b>{h}.</b> {t}</li>" for h, t in insights)
rec_html = "".join(f"<li>{r}</li>" for r in recommendations)
extra_images = "".join(
    f'<h3>{title}</h3><img src="{trend_image(path)}" alt="{title}">'
    for title, path in [("Content type analysis", "task2/content_type_dashboard.png"),
                        ("Country analysis", "task3/top_countries.png"),
                        ("Release year trends", "task4/release_year_trends.png"),
                        ("Ratings and genres", "task5/rating_genre_dashboard.png")]
    if trend_image(path))

html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Netflix Business Insights Report</title>
<style>
body{{font-family:Segoe UI,Arial,sans-serif;margin:0;background:#f5f5f5;color:{DARK};line-height:1.6}}
header{{background:{DARK};color:#fff;padding:40px 6%}}
header h1{{margin:0;font-size:2rem;color:{RED}}}
main{{max-width:1100px;margin:auto;padding:24px 5%}}
.kpis{{display:flex;flex-wrap:wrap;gap:14px;margin:-30px 0 20px}}
.kpi{{flex:1 1 150px;background:#fff;border-top:4px solid {RED};padding:14px;text-align:center;border-radius:6px;box-shadow:0 2px 6px #0002}}
.kpi span{{display:block;font-size:1.7rem;font-weight:700;color:{RED}}}
h2{{border-left:5px solid {RED};padding-left:10px;margin-top:36px}}
img{{width:100%;border-radius:6px;box-shadow:0 2px 6px #0002;margin-bottom:18px}}
li{{margin-bottom:8px}}
footer{{text-align:center;color:#777;padding:30px;font-size:.85rem}}
</style></head><body>
<header><h1>Netflix Business Insights Report</h1>
<p>Data Analysis Using Python | Auspify Technologies Internship | {date.today():%B %Y}</p></header>
<main>
<div class="kpis">{kpi_html}</div>
<h2>Executive Summary</h2>
<p>This report analyses {len(df):,} Netflix titles after cleaning and standardisation. The catalogue is movie-heavy, concentrated in a handful of countries, oriented toward teen and adult audiences, and built mostly on content released after 2010.</p>
<h2>Key Insights</h2><ul>{insight_html}</ul>
<h2>Recommendations</h2><ol>{rec_html}</ol>
<h2>Dashboards</h2>
<img src="{embed(OUT / 'dashboard_1_executive_overview.png')}" alt="Executive overview">
<img src="{embed(OUT / 'dashboard_2_content_deep_dive.png')}" alt="Content deep dive">
<h2>Supporting Analysis</h2>{extra_images}
<h2>Method and Limitations</h2>
<ul><li>Cleaning: placeholders converted to Unknown, {removed_rows} duplicate records removed, dates parsed, types, ratings and countries standardised.</li>
<li>Data ends in {df['date_added'].max():%B %Y}; 2021 figures are partial.</li>
<li>Each title carries a single country value, so co-productions are not split.</li></ul>
</main><footer>Generated with Python, pandas, matplotlib, seaborn and plotly</footer>
</body></html>"""
(OUT / "Netflix_Business_Insights_Report.html").write_text(html, encoding="utf-8")
md = ["# Netflix Business Insights Report", "", "## Key Insights", *[f"- **{h}.** {t}" for h, t in insights], "", "## Recommendations", *[f"{i}. {r}" for i, r in enumerate(recommendations, 1)]]
(OUT / "executive_summary.md").write_text("\n".join(md), encoding="utf-8")
print(f"Report saved: {(OUT / 'Netflix_Business_Insights_Report.html').relative_to(BASE)}")
