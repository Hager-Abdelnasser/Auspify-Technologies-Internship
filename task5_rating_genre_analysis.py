from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from plotly.subplots import make_subplots

BASE = Path(__file__).resolve().parent
OUT = BASE / "outputs" / "task5"
OUT.mkdir(parents=True, exist_ok=True)

RED, DARK = "#E50914", "#221F1F"
sns.set_theme(style="whitegrid")

df = pd.read_csv(BASE / "data" / "netflix_cleaned.csv")
GROUP_ORDER = ["Kids", "Older Kids", "Teens", "Adults", "Unrated"]
RATING_ORDER = ["TV-Y", "TV-G", "G", "TV-Y7", "TV-Y7-FV", "TV-PG", "PG", "TV-14", "PG-13", "TV-MA", "R", "NC-17", "NR", "UR"]

rating_counts = df["rating"].value_counts().reindex(RATING_ORDER).dropna().astype(int)
rating_tbl = pd.DataFrame({"titles": rating_counts, "share_pct": (rating_counts / len(df) * 100).round(1)})
print("STEP 1 | RATING CATEGORIES\n", rating_tbl.to_string())
group_tbl = df["rating_group"].value_counts().reindex(GROUP_ORDER)
print("\nAudience groups\n", (group_tbl / len(df) * 100).round(1).to_string())

genres = df.assign(genre=df["listed_in"].str.split(",")).explode("genre")
genres["genre"] = genres["genre"].str.strip()
genre_counts = genres["genre"].value_counts()
print(f"\nSTEP 2 | MOST COMMON GENRES (of {genre_counts.size} distinct)\n", genre_counts.head(15).to_string())

type_rating = pd.crosstab(df["rating"], df["type"]).reindex(RATING_ORDER).dropna(how="all")
type_rating_pct = type_rating.div(type_rating.sum(axis=0), axis=1).mul(100).round(1)
print("\nSTEP 3 | RATING SHARE WITHIN EACH TYPE (%)\n", type_rating_pct.to_string())

top_genres = genre_counts.head(12).index
genre_group = (genres[genres["genre"].isin(top_genres)]
               .pivot_table(index="genre", columns="rating_group", values="show_id", aggfunc="count", fill_value=0)
               .reindex(columns=[g for g in GROUP_ORDER if g != "Unrated"]))
genre_group_pct = genre_group.div(genre_group.sum(axis=1), axis=0).mul(100).round(1)
genre_group_pct = genre_group_pct.loc[genre_group.sum(axis=1).sort_values(ascending=False).index]
print("\nAudience mix of top genres (%)\n", genre_group_pct.to_string())

genre_type = genres.groupby(["genre", "type"]).size().unstack(fill_value=0)

fig, axes = plt.subplots(2, 2, figsize=(17, 12))
fig.suptitle("Netflix Ratings and Genres: Audience Targeting", fontsize=20, fontweight="bold", color=DARK, y=0.98)

ax = axes[0, 0]
colors = [RED if r in ("TV-MA", "TV-14", "R", "PG-13") else DARK for r in rating_counts.index]
sns.barplot(x=rating_counts.index, y=rating_counts.values, hue=rating_counts.index, palette=colors, legend=False, ax=ax)
ax.set_title("Titles by Rating")
ax.set_xlabel("")
ax.set_ylabel("Number of titles")
ax.tick_params(axis="x", rotation=45)

ax = axes[0, 1]
top15 = genre_counts.head(15).iloc[::-1]
ax.barh(top15.index, top15.values, color=RED)
for y, v in enumerate(top15.values):
    ax.text(v + 20, y, f"{v:,}", va="center", fontsize=9, fontweight="bold")
ax.set_title("Top 15 Genres")
ax.set_xlabel("Number of titles")
ax.set_xlim(0, top15.max() * 1.1)

ax = axes[1, 0]
sns.heatmap(type_rating_pct, annot=True, fmt=".1f", cmap=sns.light_palette(RED, as_cmap=True), linewidths=0.5,
            cbar_kws={"label": "% of type"}, ax=ax)
ax.set_title("Rating Share within Movies vs TV Shows (%)")
ax.set_xlabel("")
ax.set_ylabel("")

ax = axes[1, 1]
sns.heatmap(genre_group_pct, annot=True, fmt=".0f", cmap=sns.light_palette(DARK, as_cmap=True), linewidths=0.5,
            cbar_kws={"label": "% of genre"}, ax=ax)
ax.set_title("Audience Mix of Top 12 Genres (%)")
ax.set_xlabel("")
ax.set_ylabel("")

plt.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(OUT / "rating_genre_dashboard.png", dpi=160, bbox_inches="tight")
plt.close(fig)

print("\nSTEP 4 | INTERACTIVE VISUALIZATIONS")
sun = px.sunburst(df, path=["type", "rating_group", "rating"], color="type",
                  color_discrete_map={"Movie": RED, "TV Show": DARK, "(?)": "#888888"},
                  title="Content Type > Audience Group > Rating")
sun.update_traces(textinfo="label+percent parent", insidetextorientation="radial")
sun.update_layout(margin=dict(l=10, r=10, t=60, b=10), height=650)
sun.write_html(OUT / "sunburst_type_audience_rating.html", include_plotlyjs="cdn")

gt = genre_type.loc[genre_counts.head(20).index].reset_index().melt(id_vars="genre", var_name="type", value_name="titles")
gbar = px.bar(gt, y="genre", x="titles", color="type", orientation="h", barmode="stack",
              color_discrete_map={"Movie": RED, "TV Show": DARK}, title="Top 20 Genres by Content Type")
gbar.update_layout(yaxis=dict(autorange="reversed"), height=700, legend_title_text="")
gbar.write_html(OUT / "top_genres_interactive.html", include_plotlyjs="cdn")

heat = px.imshow(genre_group_pct, text_auto=".0f", aspect="auto", color_continuous_scale=["#fde0dd", RED, "#400004"],
                 labels=dict(color="% of genre"), title="Audience Mix of Top 12 Genres (%)")
heat.write_html(OUT / "genre_audience_heatmap.html", include_plotlyjs="cdn")

trend = (genres[genres["genre"].isin(genre_counts.head(6).index) & (genres["release_year"] >= 2010)]
         .groupby(["release_year", "genre"]).size().reset_index(name="titles"))
tl = px.line(trend, x="release_year", y="titles", color="genre", markers=True, title="Top 6 Genres Over Time (release year)")
tl.update_layout(height=520)
tl.write_html(OUT / "genre_trend_interactive.html", include_plotlyjs="cdn")

panel = make_subplots(rows=1, cols=2, specs=[[{"type": "domain"}, {"type": "xy"}]],
                      subplot_titles=("Audience group share", "Titles by rating"))
panel.add_trace(go.Pie(labels=group_tbl.index, values=group_tbl.values, hole=0.5,
                       marker=dict(colors=[RED, "#B1060F", "#7A0A10", DARK, "#888888"])), row=1, col=1)
panel.add_trace(go.Bar(x=rating_counts.index, y=rating_counts.values, marker_color=RED), row=1, col=2)
panel.update_layout(title="Rating Overview", showlegend=True, height=480)
panel.write_html(OUT / "rating_overview_interactive.html", include_plotlyjs="cdn")
print("Saved 5 interactive HTML charts")

rating_tbl.to_csv(OUT / "rating_distribution.csv")
genre_counts.rename("titles").to_csv(OUT / "genre_counts.csv")
genre_group_pct.to_csv(OUT / "genre_audience_mix.csv")

adult_share = group_tbl["Adults"] / len(df) * 100
kids_share = (group_tbl["Kids"] + group_tbl["Older Kids"]) / len(df) * 100
mature_movie = type_rating_pct.loc["TV-MA", "Movie"]
mature_tv = type_rating_pct.loc["TV-MA", "TV Show"]
adult_heavy = genre_group_pct["Adults"].idxmax()
family_heavy = (genre_group_pct["Kids"] + genre_group_pct["Older Kids"]).idxmax()
intl_share = genre_counts["International Movies"] + genre_counts["International TV Shows"]
multi = (df["genre_count"] > 1).mean() * 100
insights = [
    f"{df['rating'].value_counts().idxmax()} is the most common rating ({rating_tbl.loc[df['rating'].value_counts().idxmax(), 'share_pct']}% of titles); mature-oriented content (Adults group) is {adult_share:.1f}% of the catalogue.",
    f"Family-oriented content (Kids and Older Kids) is {kids_share:.1f}% of the catalogue, so Netflix leans toward teen and adult audiences.",
    f"TV-MA covers {mature_tv:.1f}% of TV Shows versus {mature_movie:.1f}% of Movies, showing that series are targeted more at mature viewers.",
    f"{genre_counts.index[0]} ({genre_counts.iloc[0]:,}) and {genre_counts.index[1]} ({genre_counts.iloc[1]:,}) are the two largest genre tags; international tags together reach {intl_share:,} listings.",
    f"{adult_heavy} is the most adult-skewed top genre ({genre_group_pct.loc[adult_heavy, 'Adults']:.0f}% Adults), while {family_heavy} is the most family-oriented.",
    f"{multi:.0f}% of titles carry more than one genre tag, which supports cross-genre recommendation and bundling.",
]
(OUT / "audience_insights.txt").write_text("\n".join(f"- {i}" for i in insights), encoding="utf-8")
print("\nSTEP 5 | AUDIENCE INSIGHTS")
for i in insights:
    print("-", i)
print(f"\nSaved to {OUT.relative_to(BASE)}")
