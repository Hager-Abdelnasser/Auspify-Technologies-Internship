from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
RAW_PATH = BASE / "data" / "Dataset.csv"
CLEAN_PATH = BASE / "data" / "netflix_cleaned.csv"

COUNTRY_FIX = {"West Germany": "Germany", "Soviet Union": "Russia"}
RATING_GROUP = {
    "TV-Y": "Kids", "TV-G": "Kids", "G": "Kids",
    "TV-Y7": "Older Kids", "TV-Y7-FV": "Older Kids", "TV-PG": "Older Kids", "PG": "Older Kids",
    "PG-13": "Teens", "TV-14": "Teens",
    "R": "Adults", "TV-MA": "Adults", "NC-17": "Adults",
    "NR": "Unrated", "UR": "Unrated",
}

df = pd.read_csv(RAW_PATH)
print("=" * 60, "\nSTEP 1 | Import\n" + "=" * 60)
print(f"Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
print(df.dtypes.to_string())
raw_rows = len(df)

print("\n" + "=" * 60, "\nSTEP 2 | Missing values\n" + "=" * 60)
placeholders = (df == "Not Given").sum()
print("Null values per column:\n", df.isna().sum().to_string())
print("\n'Not Given' placeholders per column:\n", placeholders[placeholders > 0].to_string())

text_cols = df.select_dtypes(include=["object", "string"]).columns
for col in text_cols:
    df[col] = df[col].str.strip()
df = df.replace({"Not Given": pd.NA, "": pd.NA})
df["director"] = df["director"].fillna("Unknown")
df["country"] = df["country"].fillna("Unknown")
print("\nPlaceholders converted to 'Unknown' in director and country")

print("\n" + "=" * 60, "\nSTEP 3 | Duplicates and formatting\n" + "=" * 60)
dup_id = df.duplicated().sum()
dup_content = df.duplicated(subset=["title", "type", "release_year", "duration"]).sum()
df = df.drop_duplicates(subset=["title", "type", "release_year", "duration"], keep="first")
print(f"Exact duplicates: {dup_id} | Duplicates by title/type/year/duration removed: {dup_content}")

df["date_added"] = pd.to_datetime(df["date_added"], format="%m/%d/%Y", errors="coerce")
df["year_added"] = df["date_added"].dt.year.astype("Int64")
df["month_added"] = df["date_added"].dt.month.astype("Int64")
print(f"date_added parsed: {df['date_added'].notna().sum():,} valid dates")

dur = df["duration"].str.extract(r"(?P<duration_value>\d+)\s*(?P<duration_unit>\D+)")
df["duration_value"] = dur["duration_value"].astype(int)
df["duration_unit"] = dur["duration_unit"].str.strip().str.replace("Seasons", "Season", regex=False)

print("\n" + "=" * 60, "\nSTEP 4 | Standardize Country, Rating, Type\n" + "=" * 60)
df["type"] = df["type"].str.strip().str.title().replace({"Tv Show": "TV Show"})
df["country"] = df["country"].str.title().replace(COUNTRY_FIX)
df["rating"] = df["rating"].str.upper()
df["rating_group"] = df["rating"].map(RATING_GROUP).fillna("Unrated")
df["primary_genre"] = df["listed_in"].str.split(",").str[0].str.strip()
df["genre_count"] = df["listed_in"].str.split(",").str.len()

print("Type:\n", df["type"].value_counts().to_string())
print("\nRating group:\n", df["rating_group"].value_counts().to_string())
print(f"\nUnique countries: {df['country'].nunique()}")

print("\n" + "=" * 60, "\nSTEP 5 | Export\n" + "=" * 60)
df = df.sort_values("date_added").reset_index(drop=True)
df.to_csv(CLEAN_PATH, index=False)
print(f"Rows: {raw_rows:,} -> {len(df):,} | Saved to: {CLEAN_PATH.relative_to(BASE)}")
print("\nFinal quality check:")
print(df.isna().sum().to_string())
