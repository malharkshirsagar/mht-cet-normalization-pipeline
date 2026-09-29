import pandas as pd
import time

INPUT_CSV = "C:/Users/OWNER/Documents/MHTCETPROJECT/stage8.csv"
OUTPUT_CSV = "stage9"


def generate_percentile_ranges(input_path: str, output_path: str):
    start = time.time()
    print(f"[*] Reading '{input_path}'...")

    # Read the 2-column file (keep percentile as string to preserve exact 7 decimals)
    df = pd.read_csv(input_path, dtype={"merit_no": int, "total_percentile": str})

    # Sort strictly by merit_no
    df = df.sort_values("merit_no").reset_index(drop=True)

    print("[*] Grouping by percentile and calculating rank spans...")

    # Group by percentile preserving order of appearance (highest rank to lowest rank)
    grouped = (
        df.groupby("total_percentile", sort=False)
        .agg(
            start_rank=("merit_no", "min"),
            end_rank=("merit_no", "max"),
            count=("merit_no", "count"),
        )
        .reset_index()
    )

    # Create a clean readable rank range string: "1 - 22" or just "1" if only 1 student
    grouped["rank_range"] = grouped.apply(
        lambda r: (
            f"{r['start_rank']} - {r['end_rank']}"
            if r["count"] > 1
            else str(r["start_rank"])
        ),
        axis=1,
    )

    # Reorder columns cleanly
    final_df = grouped[
        ["total_percentile", "rank_range", "start_rank", "end_rank", "count"]
    ]

    print(f"[*] Saving {len(final_df):,} unique percentile bands to '{output_path}'...")
    final_df.to_csv(output_path, index=False)

    elapsed = time.time() - start
    print(f"\n[✓] Done in {elapsed:.2f} seconds!")
    print(f"[✓] File size reduced from 4 MB to ~{len(final_df) * 45 // 1024} KB!")

    print("\n--- SAMPLE PREVIEW (Top 10 Percentile Tiers) ---")
    print(final_df.head(10).to_string(index=False))

    print("\n--- MAXIMUM TIE DENSITY (Single percentile with most students) ---")
    densest = final_df.loc[final_df["count"].idxmax()]
    print(
        f"Percentile: {densest['total_percentile']} | Count: {densest['count']} students | Ranks: {densest['rank_range']}"
    )


if __name__ == "__main__":
    generate_percentile_ranges(INPUT_CSV, OUTPUT_CSV)
