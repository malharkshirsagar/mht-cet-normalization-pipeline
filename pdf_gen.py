import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
import os
import time

INPUT_CSV = r"C:\Users\OWNER\Documents\MHTCETPROJECT\stage8_cet_ranges.csv"
OUTPUT_PDF = (
    r"C:\Users\OWNER\Documents\MHTCETPROJECT\MHTCET_2026_Uncompressed_Raw_Ranks.pdf"
)

CREATOR_NAME = "Malhar Kshirsagar"
FOOTER_TITLE = f"MHT-CET 2026 Ranks v/s percentile | Created by {CREATOR_NAME}"


class NumberedCanvas(canvas.Canvas):
    """Custom canvas that injects headers and dynamic 'Page X of Y' footers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Footer divider line
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(40, 36, 572, 36)

        # Footer text
        self.drawString(40, 24, FOOTER_TITLE)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(572, 24, page_str)

        self.restoreState()


def build_pdf():
    start_time = time.time()
    print(f"[*] Reading '{INPUT_CSV}'...")
    df = pd.read_csv(INPUT_CSV, low_memory=False)

    print(f"[*] Total uncompressed percentile rows: {len(df):,}")

    # Build ReportLab Table Data
    # Header
    table_data = [["Percentile (Exact)", "Merit Rank Range", "Candidates"]]

    # Populate every exact decimal without grouping or dropping
    for _, row in df.iterrows():
        pct_val = row["total_percentile"]
        # Format cleanly keeping all 7 decimals
        try:
            pct_str = f"{float(pct_val):.7f}"
        except ValueError:
            pct_str = str(pct_val)

        rank_str = str(row["rank_range"])
        count_str = f"{int(row['count']):,}"

        table_data.append([pct_str, rank_str, count_str])

    print("[*] Compiling PDF layout...")

    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=45,
        bottomMargin=50,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "MainTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0f172a"),
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#64748b"),
    )

    story = [
        Paragraph(
            "MHT-CET 2026: UNCOMPRESSED PERCENTILE TO RANK MASTER DIRECTORY",
            title_style,
        ),
        Paragraph(
            "Complete raw decimal tiers (7 decimals) | 229,563 Pure PCM Aspirants (Diploma/D.Voc Excluded)",
            subtitle_style,
        ),
        Spacer(1, 10),
    ]

    # Configure Table Styles
    # Widths: 532 pt total (leftMargin=40, rightMargin=40 -> 612 - 80 = 532)
    col_widths = [190, 212, 130]

    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                # Header formatting
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0284c7")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8.5),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
                ("TOPPADDING", (0, 0), (-1, 0), 4),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                # Cell body formatting
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 7.5),
                ("ALIGN", (0, 1), (0, -1), "CENTER"),  # Percentile column
                ("ALIGN", (1, 1), (1, -1), "CENTER"),  # Rank range column
                ("ALIGN", (2, 1), (2, -1), "CENTER"),  # Count column
                ("BOTTOMPADDING", (0, 1), (-1, -1), 2.5),
                ("TOPPADDING", (0, 1), (-1, -1), 2.5),
                # Grid lines and alternating rows
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#e2e8f0")),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f8fafc")],
                ),
            ]
        )
    )

    story.append(t)

    print("[*] Writing document to disk (rendering pages)...")
    doc.build(story, canvasmaker=NumberedCanvas)

    elapsed = time.time() - start_time
    file_size_mb = os.path.getsize(OUTPUT_PDF) / (1024 * 1024)
    print(f"[✓] Generated: {OUTPUT_PDF}")
    print(f"[✓] Output size: {file_size_mb:.2f} MB in {elapsed:.2f} seconds!")


if __name__ == "__main__":
    build_pdf()
