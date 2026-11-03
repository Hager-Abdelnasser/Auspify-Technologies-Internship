from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

BASE = Path(__file__).resolve().parent
OUT = BASE / "outputs" / "task2"
OUT.mkdir(parents=True, exist_ok=True)

RED, DARK = "#E50914", "#221F1F"
PALETTE = {"Movie": RED, "TV Show": DARK}
sns.set_theme(style="whitegrid", font_scale=1.0)

df = pd.read_csv(BASE / "data" / "netflix_cleaned.csv", parse_dates=["date_added"])

counts = df["type"].value_counts()
shares = (counts / counts.sum() * 100).round(1)
summary = pd.DataFrame({"titles": counts, "share_pct": shares})
print("CONTENT TYPE SUMMARY\n", summary.to_string(), f"\n\nTotal titles: {len(df):,}")
print(f"Movie to TV Show ratio: {counts['Movie'] / counts['TV Show']:.2f} : 1")

by_added = df.groupby(["year_added", "type"]).size().unstack(fill_value=0)
by_added = by_added[by_added.index >= 2015]
by_added["tv_share_pct"] = (by_added["TV Show"] / by_added[["Movie", "TV Show"]].sum(axis=1) * 100).round(1)
print("\nTitles added per year (2015+)\n", by_added.to_string())

by_rating = pd.crosstab(df["rating_group"], df["type"], normalize="index").mul(100).round(1)
print("\nType mix inside each audience group (%)\n", by_rating.to_string())

decade = (df["release_year"] // 10 * 10).where(df["release_year"] >= 1980, 1970)
by_decade = pd.crosstab(decade, df["type"], normalize="index").mul(100).round(1)
print("\nType mix by release decade (%)\n", by_decade.to_string())

fig, axes = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle("Netflix Content Type Analysis", fontsize=20, fontweight="bold", color=DARK, y=0.98)

ax = axes[0, 0]
_, _, pct_texts = ax.pie(counts, labels=counts.index, colors=[PALETTE[t] for t in counts.index],
                         autopct="%1.1f%%", startangle=90, wedgeprops=dict(width=0.42, edgecolor="white"),
                         textprops=dict(fontsize=12), pctdistance=0.79)
for t in pct_texts:
    t.set_color("white")
    t.set_fontweight("bold")
ax.text(0, 0, f"{len(df):,}\ntitles", ha="center", va="center", fontsize=15, fontweight="bold")
ax.set_title("Share of Movies vs TV Shows")

ax = axes[0, 1]
bars = sns.barplot(x=counts.index, y=counts.values, palette=PALETTE, ax=ax, hue=counts.index, legend=False)
for p in bars.patches:
    ax.annotate(f"{int(p.get_height()):,}", (p.get_x() + p.get_width() / 2, p.get_height()),
                ha="center", va="bottom", fontsize=12, fontweight="bold")
ax.set_title("Total Titles by Type")
ax.set_xlabel("")
ax.set_ylabel("Number of titles")

ax = axes[1, 0]
by_added[["Movie", "TV Show"]].plot(kind="bar", stacked=True, color=[RED, DARK], ax=ax, width=0.8)
ax.set_title("Titles Added per Year (stacked)")
ax.set_xlabel("Year added")
ax.set_ylabel("Number of titles")
ax.tick_params(axis="x", rotation=0)
ax.legend(title="")

ax = axes[1, 1]
by_rating.loc[["Kids", "Older Kids", "Teens", "Adults"]].plot(kind="barh", stacked=True, color=[RED, DARK], ax=ax, width=0.7)
ax.set_title("Type Mix by Audience Group (%)")
ax.set_xlabel("Share of titles (%)")
ax.set_ylabel("")
ax.legend(title="", loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False)

plt.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(OUT / "content_type_dashboard.png", dpi=160, bbox_inches="tight")
plt.close(fig)

summary.to_csv(OUT / "content_type_summary.csv")
by_added.to_csv(OUT / "titles_added_by_year_and_type.csv")

rated = by_rating.drop(index='Unrated')
peak_year = by_added[["Movie", "TV Show"]].sum(axis=1).idxmax()
tv_growth = by_added["tv_share_pct"].iloc[[0, -1]]
findings = [
    f"Movies make up {shares['Movie']}% of the catalogue ({counts['Movie']:,} titles) versus {shares['TV Show']}% TV Shows ({counts['TV Show']:,}).",
    f"There are about {counts['Movie'] / counts['TV Show']:.1f} movies for every TV show.",
    f"Peak addition year is {peak_year} with {int(by_added[['Movie', 'TV Show']].sum(axis=1).max()):,} new titles.",
    f"TV Show share of yearly additions moved from {tv_growth.iloc[0]}% in {tv_growth.index[0]} to {tv_growth.iloc[1]}% in {tv_growth.index[1]}.",
    f"{rated['TV Show'].idxmax()} content has the highest TV Show share ({rated['TV Show'].max()}%), while {rated['Movie'].idxmax()} content is the most movie-heavy ({rated['Movie'].max()}%).",
]
(OUT / "key_findings.txt").write_text("\n".join(f"- {f}" for f in findings), encoding="utf-8")
print("\nKEY FINDINGS")
for f in findings:
    print("-", f)
print(f"\nSaved to {OUT.relative_to(BASE)}")
