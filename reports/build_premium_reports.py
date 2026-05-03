"""
Build Poverty 360 premium (McKinsey-style) annual report PDFs.

Outputs (letter size):
  - 2019-annual-report.pdf
  - 2020-annual-report.pdf
  - 2021-annual-report.pdf

Requires: pip install reportlab

Figures align with poverty360.org / index.html Foundation Years section.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.pdfgen import canvas


# Brand (aligned with site tokens + portfolio navy/gold)
NAVY = colors.HexColor("#0B1F3A")
NAVY_MID = colors.HexColor("#163A63")
GOLD = colors.HexColor("#C9A227")
INK = colors.HexColor("#1A1A1A")
BODY = colors.HexColor("#3D3D3D")
MUTED = colors.HexColor("#5C5C52")
RULE = colors.HexColor("#D8D2C4")
OFF_WHITE = colors.HexColor("#FDFCF9")
FOREST = colors.HexColor("#2D4A3E")


@dataclass(frozen=True)
class YearReport:
    year: int
    governing: str
    revenue_label: str
    revenue_note: str
    theme: str
    program_title: str
    program_body: str
    kpis: list[tuple[str, str]]
    program_use: str
    risk_implication_action: tuple[str, str, str]


DATA: dict[int, YearReport] = {
    2019: YearReport(
        year=2019,
        governing=(
            "USADF-backed dairy resilience kept nutrition and livelihoods "
            "stable through the first COVID-19 shock in Ghana."
        ),
        revenue_label="$56,443",
        revenue_note="Baseline year · total revenue (audited basis as filed).",
        theme="COVID response · Ghana",
        program_title="Dairy resilience and nutrition",
        program_body=(
            "With USADF C.A.R.E.S. support, Poverty 360 equipped dairy farmers to survive COVID-19, "
            "keeping milk on tables and livelihoods intact across Ghana while expanding hygiene access."
        ),
        kpis=[
            ("Children fed dairy nutrition", "5,000"),
            ("Dairy farmers supported", "330"),
            ("Handwashing stations", "450"),
            ("Farmer revenue increase", "+60%"),
        ],
        program_use="97 cents of every dollar directed to programme delivery",
        risk_implication_action=(
            "Risk: supply chain and price shocks could erode smallholder margins faster than aid cycles refresh.",
            "Implication: without predictable offtake and inputs, nutrition gains reverse within one season.",
            "Action: lock multi-year buyer commitments and pre-position veterinary and feed support.",
        ),
    ),
    2020: YearReport(
        year=2020,
        governing=(
            "Cross-border energy, food security, and livelihood pilots scaled "
            "with disciplined unit economics across Ghana, Mali, and Burkina Faso."
        ),
        revenue_label="$71,448",
        revenue_note="Up 27% year over year.",
        theme="Multi-country · Ghana · Mali · Burkina Faso",
        program_title="Light, food, and livelihoods",
        program_body=(
            "Solar lamps transformed nighttime study in Mali. Hermetically sealed crop storage lifted margins in Ghana. "
            "Market skills programming supported women entrepreneurs in Burkina Faso."
        ),
        kpis=[
            ("Solar lamps to Mali students", "5,000"),
            ("Increase in study hours", "700%"),
            ("PICS crop storage sacks", "10,000"),
            ("Farmer margin increase (Ghana)", "+80%"),
            ("Women trained (Burkina Faso)", "600"),
            ("Vegetable farmer profits", "+60%"),
        ],
        program_use="94 cents of every dollar directed to programme delivery",
        risk_implication_action=(
            "Risk: currency and logistics volatility compresses margins on imported components.",
            "Implication: field teams need scenario-based procurement, not single-vendor dependence.",
            "Action: diversify suppliers and pre-fund six months of lamp and sack inventory.",
        ),
    ),
    2021: YearReport(
        year=2021,
        governing=(
            "Climate year investments linked clean energy, reforestation, and coastal waste removal "
            "to measurable household savings and student leadership."
        ),
        revenue_label="$467,744",
        revenue_note="Up 554% year over year · climate and scale year.",
        theme="Climate year · Ghana",
        program_title="Trees, clean stoves, and clean shores",
        program_body=(
            "Ten thousand seedlings planted, clean cookstoves to three thousand households, "
            "and plastic waste cleared from coastal communities with student peer educators leading outreach."
        ),
        kpis=[
            ("Seedlings planted", "10,000"),
            ("Student peer educators", "300"),
            ("Clean stoves distributed", "6,000"),
            ("Households using clean cooking", "3,000"),
            ("Estimated CO2 saved per household / month", "0.2 t"),
            ("Monthly fuel savings / household", "$8"),
        ],
        program_use="96 cents of every dollar directed to programme delivery",
        risk_implication_action=(
            "Risk: adoption curves flatten if maintenance and fuel access are not bundled.",
            "Implication: stove distribution without behaviour support undercounts sustained use.",
            "Action: pair distribution with village maintenance networks and savings groups.",
        ),
    ),
}


def _cover_page(year: int, governing: str) -> bytes:
    buf = BytesIO()
    w, h = letter
    c = canvas.Canvas(buf, pagesize=letter)
    c.setFillColor(NAVY)
    c.rect(0, 0, w, h, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(0, h - 0.35 * inch, w, 0.12 * inch, fill=1, stroke=0)
    c.rect(0, 0.22 * inch, w, 0.06 * inch, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 42)
    c.drawString(0.75 * inch, h - 1.35 * inch, str(year))
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.HexColor("#E2E8F0"))
    c.drawString(0.75 * inch, h - 1.62 * inch, "POVERTY 360 · ANNUAL REPORT")
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.white)
    c.drawString(0.75 * inch, h - 2.15 * inch, "Foundation years memorandum")
    c.setFont("Helvetica", 10.5)
    c.setFillColor(colors.HexColor("#CBD5E1"))
    text = c.beginText(0.75 * inch, h - 2.55 * inch)
    text.setLeading(14)
    for line in _wrap(governing, 95):
        text.textLine(line)
    c.drawText(text)
    c.setFillColor(GOLD)
    c.setFont("Helvetica", 9)
    c.drawString(0.75 * inch, 0.65 * inch, "Evidence-based analytics and social impact · Registered in Ghana")
    c.setFillColor(colors.HexColor("#94A3B8"))
    c.drawString(0.75 * inch, 0.48 * inch, f"Prepared for board and donor circulation · {date.today().isoformat()}")
    c.showPage()
    c.save()
    return buf.getvalue()


def _wrap(text: str, max_chars: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur: list[str] = []
    for w in words:
        trial = (" ".join(cur + [w])).strip()
        if len(trial) <= max_chars:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def _footer(canv: canvas.Canvas, doc) -> None:
    canv.saveState()
    w, _ = letter
    canv.setStrokeColor(GOLD)
    canv.setLineWidth(1.2)
    canv.line(0.75 * inch, 0.55 * inch, w - 0.75 * inch, 0.55 * inch)
    canv.setFillColor(MUTED)
    canv.setFont("Helvetica", 8)
    canv.drawString(0.75 * inch, 0.38 * inch, "Poverty 360 · Annual memorandum · Board and donor circulation")
    canv.restoreState()


def _body_pdf(yr: YearReport) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.72 * inch,
        title=f"Poverty 360 {yr.year} Annual Report",
        onFirstPage=_footer,
        onLaterPages=_footer,
    )
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle(
        "H1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        textColor=FOREST,
        spaceAfter=10,
    )
    h2 = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11.5,
        textColor=NAVY_MID,
        spaceBefore=14,
        spaceAfter=8,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=BODY,
    )
    small = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=MUTED,
    )
    story: list = []

    story.append(Paragraph("Executive summary", h1))
    story.append(Paragraph(f"<b>Governing thought.</b> {yr.governing}", body))
    story.append(Spacer(1, 10))
    story.append(
        Paragraph(
            "<b>Scope.</b> This memorandum summarises verified programme outcomes published in the "
            "Poverty 360 Foundation Years narrative. It is not a substitute for full audited statements.",
            body,
        )
    )
    story.append(Spacer(1, 14))

    story.append(Paragraph("Financial snapshot", h2))
    fin_data = [
        ["Metric", "Value"],
        ["Reporting year", str(yr.year)],
        ["Total revenue (as published)", yr.revenue_label],
        ["Context", yr.revenue_note],
        ["Programme use efficiency", yr.program_use],
    ]
    t = Table(fin_data, colWidths=[2.6 * inch, 3.5 * inch])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [OFF_WHITE, colors.HexColor("#F4F1EA")]),
                ("TEXTCOLOR", (0, 1), (-1, -1), INK),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, RULE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Programme narrative", h2))
    story.append(Paragraph(f"<b>{yr.theme}</b> · <i>{yr.program_title}</i>", body))
    story.append(Spacer(1, 6))
    story.append(Paragraph(yr.program_body, body))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Impact at a glance", h2))
    kpi_rows = [["Indicator", "Outcome"]] + [[a, b] for a, b in yr.kpis]
    kt = Table(kpi_rows, colWidths=[3.4 * inch, 2.7 * inch])
    kt.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8F0EC")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("TEXTCOLOR", (0, 0), (-1, 0), FOREST),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, OFF_WHITE]),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("TEXTCOLOR", (0, 1), (-1, -1), INK),
                ("GRID", (0, 0), (-1, -1), 0.5, RULE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(kt)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Policy brief · Risk · Implication · Action", h2))
    r, im, ac = yr.risk_implication_action
    story.append(Paragraph(f"<b>Risk.</b> {r}", body))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<b>Implication.</b> {im}", body))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<b>Action.</b> {ac}", body))
    story.append(Spacer(1, 16))

    story.append(
        Paragraph(
            "Partners and validators referenced in the public Poverty 360 narrative include USADF, Citibank, "
            "national and local government entities in West Africa, and community implementing partners. "
            "Request underlying monitoring data through formal due diligence channels.",
            small,
        )
    )
    story.append(Spacer(1, 10))
    story.append(
        Paragraph(
            "<b>Disclaimer.</b> This document is a decision-support memorandum. It does not constitute "
            "legal, tax, or investment advice. All figures are as stated in the Foundation Years public materials "
            "unless separately audited schedules are provided.",
            small,
        )
    )

    doc.build(story)
    return buf.getvalue()


def _merge_pdfs(*parts: bytes) -> bytes:
    try:
        from pypdf import PdfWriter, PdfReader
    except ImportError:
        from PyPDF2 import PdfWriter, PdfReader  # type: ignore
    writer = PdfWriter()
    for blob in parts:
        reader = PdfReader(BytesIO(blob))
        for page in reader.pages:
            writer.add_page(page)
    out = BytesIO()
    writer.write(out)
    return out.getvalue()


def build(year: int, out_path: Path) -> None:
    yr = DATA[year]
    cover = _cover_page(yr.year, yr.governing)
    body = _body_pdf(yr)
    merged = _merge_pdfs(cover, body)
    out_path.write_bytes(merged)


def main() -> None:
    root = Path(__file__).resolve().parent
    archive = root / "archive" / "legacy_uploads"
    archive.mkdir(parents=True, exist_ok=True)
    for fname in ("2019.pdf", "2020.pdf", "2021.pdf"):
        p = root / fname
        if p.exists():
            dest = archive / fname
            if not dest.exists():
                p.replace(dest)
    for y in (2019, 2020, 2021):
        out = root / f"{y}-annual-report.pdf"
        build(y, out)
        print("Wrote", out, "size", out.stat().st_size)


if __name__ == "__main__":
    main()
