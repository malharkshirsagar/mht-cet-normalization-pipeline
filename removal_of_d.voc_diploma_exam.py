import pandas as pd
import time

INPUT_CSV = r"C:\Users\OWNER\Documents\MHTCETPROJECT\stage7_fix.csv"
OUTPUT_CLEAN_CSV = r"C:\Users\OWNER\Documents\MHTCETPROJECT\stage7_cet_only.csv"
OUTPUT_RANGES_CSV = r"C:\Users\OWNER\Documents\MHTCETPROJECT\stage8_cet_ranges.csv"


def filter_and_aggregate():
    start = time.time()
    print(f"[*] Reading '{INPUT_CSV}'...")
    df = pd.read_csv(INPUT_CSV, low_memory=False)
    initial_count = len(df)

    # 1. Filter strictly for MHT-CET-PCM records
    # Keeps records where merit_exam contains 'MHT-CET' or 'PCM'
    cet_mask = (
        df["merit_exam"].astype(str).str.contains(r"MHT-CET|PCM", case=False, na=False)
    )
    clean_df = df[cet_mask].copy()

    # Exclude any explicit Diploma / D.Voc leakage
    clean_df = clean_df[
        ~clean_df["merit_exam"]
        .astype(str)
        .str.contains(r"Diploma|D\.Voc|Vocational", case=False, na=False)
    ]

    dropped_count = initial_count - len(clean_df)
    print(f"[✓] Removed {dropped_count:,} non-CET (Diploma/D.Voc) records.")
    print(f"[✓] Pure MHT-CET candidates remaining: {len(clean_df):,}")

    # Ensure numeric percentiles and ranks
    clean_df["merit_no"] = pd.to_numeric(clean_df["merit_no"], errors="coerce")
    clean_df["total_percentile"] = pd.to_numeric(
        clean_df["total_percentile"], errors="coerce"
    )
    clean_df = (
        clean_df.dropna(subset=["merit_no", "total_percentile"])
        .sort_values("merit_no")
        .reset_index(drop=True)
    )
    clean_df["merit_no"] = clean_df["merit_no"].astype(int)

    # Format percentile back to exact 7-decimal string
    clean_df["total_percentile_str"] = clean_df["total_percentile"].apply(
        lambda x: f"{x:.7f}"
    )

    # Save cleaned CET-only master dataset
    clean_df.drop(columns=["total_percentile_str"]).to_csv(
        OUTPUT_CLEAN_CSV, index=False
    )
    print(f"[✓] Saved clean CET master to: '{OUTPUT_CLEAN_CSV}'")

    # 2. Generate clean Stage 8 Ranges for CET only
    print("[*] Generating rank ranges and tie density...")
    grouped = (
        clean_df.groupby("total_percentile_str", sort=False)
        .agg(
            start_rank=("merit_no", "min"),
            end_rank=("merit_no", "max"),
            count=("merit_no", "count"),
        )
        .reset_index()
    )

    grouped.rename(columns={"total_percentile_str": "total_percentile"}, inplace=True)
    grouped["rank_range"] = grouped.apply(
        lambda r: (
            f"{r['start_rank']} - {r['end_rank']}"
            if r["count"] > 1
            else str(r["start_rank"])
        ),
        axis=1,
    )

    final_ranges = grouped[
        ["total_percentile", "rank_range", "start_rank", "end_rank", "count"]
    ]
    final_ranges.to_csv(OUTPUT_RANGES_CSV, index=False)

    print(f"[✓] Saved pure CET rank ranges to: '{OUTPUT_RANGES_CSV}'")
    print(f"[✓] Total unique percentile tiers: {len(final_ranges):,}")
    print(f"\nExecution finished in {time.time() - start:.2f}s")
    print("\n--- TOP 5 CET BANDS ---")
    print(final_ranges.head(5).to_string(index=False))


if __name__ == "__main__":
    filter_and_aggregate()
