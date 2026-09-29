import csv
import re
import time

INPUT_FILE = "C:/Users/OWNER/Documents/MHTCETPROJECT/stage6.txt"
OUTPUT_CSV = "stage7.csv"

# 1-Line Master CSV Header
CSV_COLUMNS = [
    "merit_no",
    "application_id",
    "candidate_name",
    "category",
    "gender",
    "special_reservation_flags",
    "merit_exam",
    "total_percentile",
    "math_percentile",
    "physics_percentile",
    "chemistry_percentile",
    "hsc_pcm_pct",
    "hsc_math_pct",
    "hsc_physics_pct",
    "hsc_diploma_total_pct",
    "ssc_total_pct",
    "ssc_math_pct",
    "ssc_science_pct",
    "ssc_english_pct",
]

CATEGORIES = {
    "OPEN",
    "OBC",
    "SC",
    "ST",
    "SEBC",
    "VJ",
    "NT-A",
    "NT-B",
    "NT-C",
    "NT-D",
    "NT1",
    "NT2",
    "NT3",
    "SBC",
    "EWS",
}


def convert_to_csv(input_path: str, output_path: str):
    start = time.time()
    print(f"[*] Reading '{input_path}' and converting to CSV...")

    parsed_rows = []
    skipped_count = 0

    with open(input_path, "r", encoding="utf-8") as infile:
        for line in infile:
            stripped = line.strip()
            if not stripped:
                continue

            # Must start with a merit rank and EN Application ID (skips the multi-line text header)
            if not re.match(r"^\d+\s+EN\d+", stripped):
                skipped_count += 1
                continue

            tokens = stripped.split()

            # Expecting at least 16 tokens (Rank, AppID, Name, Cat, Gender, Exam + 12 numeric scores)
            if len(tokens) < 16:
                skipped_count += 1
                continue

            merit_no = tokens[0]
            app_id = tokens[1]

            # The trailing 12 tokens are always the exact numeric scores
            scores = tokens[-12:]

            # The token directly preceding the 12 scores is the Exam
            merit_exam = tokens[-13]

            # Middle tokens: Name, Category, Gender, and special reservation flags (-/-)
            middle_tokens = tokens[2:-13]

            # Identify category and gender positions
            cat_idx = None
            gender_idx = None

            for i, token in enumerate(middle_tokens):
                clean_tok = token.replace(" ", "").upper()
                if clean_tok in CATEGORIES and cat_idx is None:
                    cat_idx = i
                elif clean_tok in ("MALE", "FEMALE") and gender_idx is None:
                    gender_idx = i

            # If layout is standard, slice cleanly
            if cat_idx is not None and gender_idx is not None and cat_idx < gender_idx:
                candidate_name = " ".join(middle_tokens[:cat_idx])
                category = middle_tokens[cat_idx].upper()
                gender = middle_tokens[gender_idx].capitalize()
                flags = " ".join(middle_tokens[gender_idx + 1 :])
            else:
                # Fallback for irregular spacing
                candidate_name = " ".join(middle_tokens)
                category = "UNKNOWN"
                gender = "UNKNOWN"
                flags = "-/-"

            row = [
                merit_no,
                app_id,
                candidate_name,
                category,
                gender,
                flags,
                merit_exam,
            ] + scores

            parsed_rows.append(row)

    print(f"[*] Writing {len(parsed_rows):,} rows to '{output_path}'...")

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(CSV_COLUMNS)
        writer.writerows(parsed_rows)

    elapsed = time.time() - start
    print(f"\n[✓] Successfully generated '{output_path}' in {elapsed:.2f} seconds!")
    print(
        f"[✓] Converted {len(parsed_rows):,} candidates (Skipped {skipped_count} header lines)."
    )


if __name__ == "__main__":
    convert_to_csv(INPUT_FILE, OUTPUT_CSV)
