from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import seaborn as sns

BASE = Path(__file__).resolve().parent
OUT = BASE / "outputs" / "task3"
OUT.mkdir(parents=True, exist_ok=True)

RED, DARK = "#E50914", "#221F1F"
sns.set_theme(style="whitegrid")

df = pd.read_csv(BASE / "data" / "netflix_cleaned.csv")

known = df[df["country"] != "Unknown"].copy()
print(f"Titles with a known country: {len(known):,} of {len(df):,} ({len(known) / len(df):.1%})")
print(f"Countries represented: {known['country'].nunique()}")

by_country = (
    known.groupby("country")
    .agg(titles=("show_id", "count"),
         movies=("type", lambda s: (s == "Movie").sum()),
         tv_shows=("type", lambda s: (s == "TV Show").sum()),
         first_release=("release_year", "min"),
         latest_release=("release_year", "max"))
    .sort_values("titles", ascending=False)
)
by_country["share_pct"] = (by_country["titles"] / len(known) * 100).round(2)
by_country["cumulative_share_pct"] = by_country["share_pct"].cumsum().round(2)
by_country["rank"] = range(1, len(by_country) + 1)
by_country["tv_share_pct"] = (by_country["tv_shows"] / by_country["titles"] * 100).round(1)

TOP_N = 15
top = by_country.head(TOP_N)
print(f"\nTOP {TOP_N} CONTENT-PRODUCING COUNTRIES\n",
      top[["rank", "titles", "movies", "tv_shows", "share_pct", "cumulative_share_pct"]].to_string())

top5_share = by_country["share_pct"].head(5).sum()
top10_share = by_country["share_pct"].head(10).sum()
single_title = (by_country["titles"] == 1).sum()
print(f"\nTop 5 share: {top5_share:.1f}% | Top 10 share: {top10_share:.1f}% | Countries with a single title: {single_title}")

fig, axes = plt.subplots(1, 2, figsize=(18, 8), gridspec_kw={"width_ratios": [1.1, 1]})
fig.suptitle("Netflix Content by Country", fontsize=20, fontweight="bold", color=DARK)

ax = axes[0]
palette = [RED] * 3 + ["#B1060F"] * 3 + [DARK] * (TOP_N - 6)
sns.barplot(data=top.reset_index(), y="country", x="titles", hue="country", palette=palette, legend=False, ax=ax)
for p, v in zip(ax.patches, top["titles"]):
    ax.text(p.get_width() + 20, p.get_y() + p.get_height() / 2, f"{v:,}", va="center", fontsize=10, fontweight="bold")
ax.set_title(f"Top {TOP_N} Countries by Number of Titles")
ax.set_xlabel("Number of titles")
ax.set_ylabel("")
ax.set_xlim(0, top["titles"].max() * 1.12)

ax = axes[1]
top10 = by_country.head(10)[["movies", "tv_shows"]].iloc[::-1]
top10.rename(columns={"movies": "Movie", "tv_shows": "TV Show"}).plot(
    kind="barh", stacked=True, color=[RED, DARK], ax=ax, width=0.75)
ax.set_title("Movie vs TV Show Mix (Top 10)")
ax.set_xlabel("Number of titles")
ax.set_ylabel("")
ax.legend(title="", loc="lower right")

plt.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(OUT / "top_countries.png", dpi=160, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(by_country["rank"], by_country["cumulative_share_pct"], color=RED, linewidth=2.5)
for k in (5, 10, 20):
    v = by_country["cumulative_share_pct"].iloc[k - 1]
    ax.scatter(k, v, color=DARK, zorder=3)
    ax.annotate(f"Top {k}: {v:.1f}%", (k, v), textcoords="offset points", xytext=(10, -14), fontsize=11, fontweight="bold")
ax.set_title("Catalogue Concentration (Cumulative Share by Country Rank)", fontweight="bold")
ax.set_xlabel("Country rank")
ax.set_ylabel("Cumulative share of titles (%)")
ax.set_ylim(0, 102)
fig.savefig(OUT / "concentration_curve.png", dpi=160, bbox_inches="tight")
plt.close(fig)

fig_map = px.choropleth(by_country.reset_index(), locations="country", locationmode="country names",
                        color="titles", hover_name="country",
                        hover_data={"movies": True, "tv_shows": True, "share_pct": True, "titles": True},
                        color_continuous_scale=["#fde0dd", RED, "#400004"],
                        title="Netflix Titles by Country")
fig_map.update_layout(geo=dict(showframe=False, showcoastlines=False), margin=dict(l=0, r=0, t=60, b=0))
fig_map.write_html(OUT / "world_map.html", include_plotlyjs="cdn")

by_country.to_csv(OUT / "country_ranking.csv")

regional = {
    "North America": ["United States", "Canada", "Mexico"],
    "Europe": ["United Kingdom", "France", "Spain", "Germany", "Italy", "Turkey", "Netherlands", "Belgium", "Sweden", "Ireland", "Poland", "Denmark", "Norway", "Switzerland"],
    "Asia": ["India", "Japan", "South Korea", "Pakistan", "Philippines", "Thailand", "Indonesia", "China", "Hong Kong", "Taiwan", "Singapore", "Malaysia", "Vietnam"],
    "MENA": ["Egypt", "Saudi Arabia", "United Arab Emirates", "Lebanon", "Jordan", "Kuwait", "Syria", "Iran", "Israel"],
}
region_totals = {r: int(by_country.loc[by_country.index.intersection(c), "titles"].sum()) for r, c in regional.items()}
print("\nTitles by selected regions:", region_totals)

leader, runner = by_country.iloc[0], by_country.iloc[1]
tv_leader = by_country[by_country["titles"] >= 100]["tv_share_pct"].idxmax()
insights = [
    f"{by_country.index[0]} leads with {int(leader['titles']):,} titles ({leader['share_pct']}% of titles with a known country), about {leader['titles'] / runner['titles']:.1f}x the runner-up, {by_country.index[1]}.",
    f"The top 5 countries ({', '.join(by_country.index[:5])}) account for {top5_share:.1f}% of the catalogue and the top 10 for {top10_share:.1f}%.",
    f"{single_title} of {len(by_country)} countries have only one title, showing a long tail of low-volume markets.",
    f"Among countries with 100+ titles, {tv_leader} has the highest TV Show share ({by_country.loc[tv_leader, 'tv_share_pct']}%), so its local catalogue is series-led.",
    f"North America ({region_totals['North America']:,} titles) is followed by Asia ({region_totals['Asia']:,}) and Europe ({region_totals['Europe']:,}); the MENA group stands at {region_totals['MENA']:,} titles.",
    f"{(df['country'] == 'Unknown').sum()} titles have no country recorded, which is a data-quality gap worth fixing at ingestion.",
]
(OUT / "business_insights.txt").write_text("\n".join(f"- {i}" for i in insights), encoding="utf-8")
print("\nBUSINESS INSIGHTS")
for i in insights:
    print("-", i)
print(f"\nSaved to {OUT.relative_to(BASE)}")
