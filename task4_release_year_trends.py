from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pandas as pd
import seaborn as sns

BASE = Path(__file__).resolve().parent
OUT = BASE / "outputs" / "task4"
OUT.mkdir(parents=True, exist_ok=True)

RED, DARK, GREY = "#E50914", "#221F1F", "#B3B3B3"
sns.set_theme(style="whitegrid")

df = pd.read_csv(BASE / "data" / "netflix_cleaned.csv", parse_dates=["date_added"])
last_date = df["date_added"].max()
print(f"Release years span {df['release_year'].min()} to {df['release_year'].max()} | Latest date_added: {last_date:%Y-%m-%d}")

yearly = df.groupby("release_year").size().rename("titles").to_frame()
yearly = yearly.reindex(range(yearly.index.min(), yearly.index.max() + 1), fill_value=0)
yearly["yoy_pct"] = yearly["titles"].pct_change().mul(100).round(1)
yearly["ma3"] = yearly["titles"].rolling(3, center=True, min_periods=1).mean().round(1)
by_type = df.groupby(["release_year", "type"]).size().unstack(fill_value=0).reindex(yearly.index, fill_value=0)
yearly = yearly.join(by_type)
yearly.to_csv(OUT / "titles_by_release_year.csv")

recent = yearly.loc[2000:]
print("\nTITLES BY RELEASE YEAR (2000 onward)\n", recent[["titles", "Movie", "TV Show", "yoy_pct"]].to_string())

peak_year = int(yearly["titles"].idxmax())
peak_val = int(yearly["titles"].max())
last_year = int(yearly.index.max())
growth_window = yearly.loc[2008:peak_year]
cagr = ((yearly.loc[peak_year, "titles"] / yearly.loc[2008, "titles"]) ** (1 / (peak_year - 2008)) - 1) * 100
post_peak = yearly.loc[peak_year:]
decline_years = int((post_peak["yoy_pct"].dropna() < 0).sum())

decades = (yearly.index // 10 * 10)
by_decade = yearly.groupby(decades)[["titles", "Movie", "TV Show"]].sum()
by_decade["share_pct"] = (by_decade["titles"] / by_decade["titles"].sum() * 100).round(1)
print("\nTITLES BY DECADE OF RELEASE\n", by_decade.to_string())

added = df.groupby("year_added").size().rename("titles_added").to_frame()
added["yoy_pct"] = added["titles_added"].pct_change().mul(100).round(1)
print("\nTITLES ADDED TO NETFLIX BY YEAR\n", added.loc[2015:].to_string())

df["lag_years"] = df["year_added"] - df["release_year"]
lag_median = df["lag_years"].median()
fresh_share = (df["lag_years"] <= 1).mean() * 100
print(f"\nMedian gap between release and Netflix addition: {lag_median:.0f} year(s) | Added within 1 year of release: {fresh_share:.1f}%")

fig, axes = plt.subplots(2, 2, figsize=(16, 11))
fig.suptitle("Netflix Content Production by Release Year", fontsize=20, fontweight="bold", color=DARK, y=0.98)

ax = axes[0, 0]
ax.fill_between(recent.index, recent["titles"], color=RED, alpha=0.18)
ax.plot(recent.index, recent["titles"], color=RED, linewidth=2.5, marker="o", markersize=4, label="Titles released")
ax.plot(recent.index, recent["ma3"], color=DARK, linewidth=2, linestyle="--", label="3-year moving average")
ax.annotate(f"Peak {peak_year}: {peak_val:,}", (peak_year, peak_val), xytext=(-150, -40), textcoords="offset points",
            arrowprops=dict(arrowstyle="->", color=DARK), fontsize=11, fontweight="bold")
ax.set_title("Titles Released per Year (2000 onward)")
ax.set_xlabel("Release year")
ax.set_ylabel("Number of titles")
ax.legend()

ax = axes[0, 1]
yoy = recent["yoy_pct"].loc[2005:]
ax.bar(yoy.index, yoy.values, color=[RED if v >= 0 else DARK for v in yoy.values])
ax.axhline(0, color=GREY, linewidth=1)
ax.xaxis.set_major_locator(MaxNLocator(integer=True))
ax.set_title("Year-over-Year Change in Releases (%)")
ax.set_xlabel("Release year")
ax.set_ylabel("Change vs previous year (%)")

ax = axes[1, 0]
ax.plot(recent.index, recent["Movie"], color=RED, linewidth=2.5, label="Movie")
ax.plot(recent.index, recent["TV Show"], color=DARK, linewidth=2.5, label="TV Show")
ax.set_title("Movies vs TV Shows by Release Year")
ax.set_xlabel("Release year")
ax.set_ylabel("Number of titles")
ax.legend()

ax = axes[1, 1]
dec = by_decade.loc[1940:, ["Movie", "TV Show"]]
dec.index = [f"{d}s" for d in dec.index]
dec.plot(kind="bar", stacked=True, color=[RED, DARK], ax=ax, width=0.75)
ax.set_title("Titles by Decade of Release")
ax.set_xlabel("")
ax.set_ylabel("Number of titles")
ax.tick_params(axis="x", rotation=0)
ax.legend(title="")

plt.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(OUT / "release_year_trends.png", dpi=160, bbox_inches="tight")
plt.close(fig)

heat = df[df["year_added"] >= 2016].pivot_table(index="year_added", columns="month_added", values="show_id", aggfunc="count", fill_value=0)
heat.columns = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][: len(heat.columns)]
fig, ax = plt.subplots(figsize=(13, 5))
sns.heatmap(heat, annot=True, fmt="d", cmap=sns.light_palette(RED, as_cmap=True), linewidths=0.5, cbar_kws={"label": "Titles added"}, ax=ax)
ax.set_title("When Titles Were Added to Netflix (Year x Month)", fontweight="bold")
ax.set_xlabel("")
ax.set_ylabel("")
fig.savefig(OUT / "added_year_month_heatmap.png", dpi=160, bbox_inches="tight")
plt.close(fig)

best_month = df[df["year_added"] < 2021]["month_added"].value_counts().idxmax()
month_name = pd.Timestamp(2000, int(best_month), 1).strftime("%B")
peak_yoy = recent["yoy_pct"].loc[2005:].idxmax()
insights = [
    f"Release volume grew from {int(yearly.loc[2008, 'titles'])} titles in 2008 to a peak of {peak_val:,} in {peak_year}, a compound growth of {cagr:.1f}% per year.",
    f"The sharpest jump was in {peak_yoy} ({recent.loc[peak_yoy, 'yoy_pct']:+.0f}% vs the previous year).",
    f"After the {peak_year} peak, releases fell in {decline_years} of the {last_year - peak_year} following years; {last_year} stands at {int(yearly.loc[last_year, 'titles']):,} titles ({yearly.loc[last_year, 'yoy_pct']:+.1f}% YoY).",
    f"The 2010s hold {by_decade.loc[2010, 'share_pct']}% of the whole catalogue, confirming a catalogue weighted toward recent content.",
    f"TV Shows grew faster than Movies between 2010 and {peak_year}: {yearly.loc[peak_year, 'TV Show'] / yearly.loc[2010, 'TV Show']:.1f}x versus {yearly.loc[peak_year, 'Movie'] / yearly.loc[2010, 'Movie']:.1f}x.",
    f"The median gap between release and Netflix addition is {lag_median:.0f} year, and {fresh_share:.0f}% of titles were added within a year of release.",
    f"{month_name} is the most common month for additions before 2021.",
    f"The data ends in {last_date:%B %Y}, so {last_year} is a partial year and its drop should not be read as a real decline.",
]
(OUT / "trend_insights.txt").write_text("\n".join(f"- {i}" for i in insights), encoding="utf-8")
print("\nBUSINESS PATTERNS")
for i in insights:
    print("-", i)
print(f"\nSaved to {OUT.relative_to(BASE)}")
