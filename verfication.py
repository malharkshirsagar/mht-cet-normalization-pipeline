import csv
import re
import time

INPUT_FILE = r"C:\Users\OWNER\Documents\MHTCETPROJECT\stage5.txt"
OUTPUT_CSV = r"C:\Users\OWNER\Documents\MHTCETPROJECT\stage7_fix.csv"

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


def is_number(val: str) -> bool:
    try:
        float(val)
        return True
    except ValueError:
        return False


def parse_line(line: str):
    tokens = line.strip().split()
    if len(tokens) < 5 or not tokens[0].isdigit() or not tokens[1].startswith("EN"):
        return None

    merit_no = int(tokens[0])
    app_id = tokens[1]

    # Find where the trailing numeric scores begin
    score_start_idx = len(tokens)
    while score_start_idx > 2 and is_number(tokens[score_start_idx - 1]):
        score_start_idx -= 1

    scores = tokens[score_start_idx:]
    # The exam token is right before the scores (e.g. MHT-CET-PCM, Diploma)
    exam_idx = score_start_idx - 1
    merit_exam = tokens[exam_idx] if exam_idx >= 2 else "UNKNOWN"

    total_percentile = scores[0] if scores else "0.0000000"

    # Middle section: Name, Category, Gender, Reservation flags
    middle = tokens[2:exam_idx]

    cat_idx = None
    gender_idx = None

    for i, tok in enumerate(middle):
        clean_tok = tok.upper()
        if clean_tok in CATEGORIES and cat_idx is None:
            cat_idx = i
        elif clean_tok in ("MALE", "FEMALE") and gender_idx is None:
            gender_idx = i

    if cat_idx is not None:
        name = " ".join(middle[:cat_idx])
        category = middle[cat_idx].upper()
    else:
        name = " ".join(middle)
        category = "UNKNOWN"

    gender = middle[gender_idx].capitalize() if gender_idx is not None else "UNKNOWN"

    return {
        "merit_no": merit_no,
        "application_id": app_id,
        "candidate_name": name,
        "category": category,
        "gender": gender,
        "merit_exam": merit_exam,
        "total_percentile": total_percentile,
    }


def run():
    start = time.time()
    print(f"[*] Reading and parsing from '{INPUT_FILE}'...")

    rows = []
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            parsed = parse_line(line)
            if parsed:
                rows.append(parsed)

    print(f"[*] Successfully parsed {len(rows):,} candidate records.")

    # Write clean stage7.csv
    fieldnames = [
        "merit_no",
        "application_id",
        "candidate_name",
        "category",
        "gender",
        "merit_exam",
        "total_percentile",
    ]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[✓] stage7.csv generated in {time.time() - start:.2f} seconds!")


if __name__ == "__main__":
    run()
