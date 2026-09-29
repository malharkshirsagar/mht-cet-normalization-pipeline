import pandas as pd

# Load master CSV
df = pd.read_csv("stage7.csv")

# Slice only Merit No and Total Percentile
rank_percentile_df = df[["merit_no", "total_percentile"]]

# Save to a lightweight CSV
rank_percentile_df.to_csv("mht_cet_2026_rank_vs_percentile.csv", index=False)

print(f"[✓] Created dataset with {len(rank_percentile_df):,} rows!")
print(rank_percentile_df.head(10))
