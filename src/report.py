"""Executive PDF brief generation using ReportLab."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


NAVY = colors.HexColor("#132238")
BLUE = colors.HexColor("#2F6BFF")
TEAL = colors.HexColor("#11A7A0")
GOLD = colors.HexColor("#F2B134")
RED = colors.HexColor("#D9534F")
LIGHT = colors.HexColor("#EEF2F7")
GRAY = colors.HexColor("#687385")

FONT_REGULAR = "GapReportSans"
FONT_BOLD = "GapReportSans-Bold"


def _register_fonts() -> None:
    if {
        FONT_REGULAR,
        FONT_BOLD,
    }.issubset(pdfmetrics.getRegisteredFontNames()):
        return

    reportlab_font_dir = Path(reportlab.__file__).resolve().parent / "fonts"
    windows_font_dir = Path.home().anchor + "Windows/Fonts"
    candidate_pairs = [
        # ReportLab includes Bitstream Vera on supported platforms. This is the
        # preferred project font because it travels with the Python dependency.
        (reportlab_font_dir / "Vera.ttf", reportlab_font_dir / "VeraBd.ttf"),
        # Common Windows, Linux, and macOS fallbacks.
        (Path(windows_font_dir) / "arial.ttf", Path(windows_font_dir) / "arialbd.ttf"),
        (
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ),
        (
            Path("/Library/Fonts/Arial.ttf"),
            Path("/Library/Fonts/Arial Bold.ttf"),
        ),
    ]

    for regular_path, bold_path in candidate_pairs:
        if regular_path.is_file() and bold_path.is_file():
            pdfmetrics.registerFont(TTFont(FONT_REGULAR, str(regular_path)))
            pdfmetrics.registerFont(TTFont(FONT_BOLD, str(bold_path)))
            return

    raise FileNotFoundError(
        "No compatible TrueType report font was found. Reinstall reportlab "
        "to restore its bundled Vera.ttf and VeraBd.ttf files."
    )


def _styles() -> dict[str, ParagraphStyle]:
    _register_fonts()
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName=FONT_BOLD,
            fontSize=24,
            leading=28,
            textColor=NAVY,
            alignment=TA_LEFT,
            spaceAfter=10,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName=FONT_REGULAR,
            fontSize=10,
            leading=14,
            textColor=GRAY,
            spaceAfter=16,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName=FONT_BOLD,
            fontSize=16,
            leading=19,
            textColor=NAVY,
            spaceBefore=8,
            spaceAfter=9,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName=FONT_BOLD,
            fontSize=11,
            leading=14,
            textColor=BLUE,
            spaceBefore=7,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=8.7,
            leading=12.2,
            textColor=NAVY,
            spaceAfter=6,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=7,
            leading=9.2,
            textColor=GRAY,
        ),
        "kpi": ParagraphStyle(
            "KPI",
            parent=base["Normal"],
            fontName=FONT_BOLD,
            fontSize=14,
            leading=17,
            textColor=NAVY,
            alignment=TA_CENTER,
        ),
        "kpi_label": ParagraphStyle(
            "KPI Label",
            parent=base["Normal"],
            fontName=FONT_REGULAR,
            fontSize=6.8,
            leading=8.5,
            textColor=GRAY,
            alignment=TA_CENTER,
        ),
        "table": ParagraphStyle(
            "Table",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=7.4,
            leading=9.2,
            textColor=NAVY,
        ),
    }


def _page_frame(canvas, doc) -> None:
    canvas.saveState()
    width, height = letter
    canvas.setStrokeColor(LIGHT)
    canvas.line(0.55 * inch, 0.47 * inch, width - 0.55 * inch, 0.47 * inch)
    canvas.setFont(FONT_REGULAR, 6.7)
    canvas.setFillColor(GRAY)
    canvas.drawString(0.55 * inch, 0.28 * inch, "Gap Equity and Operational Risk Model")
    canvas.drawRightString(
        width - 0.55 * inch,
        0.28 * inch,
        f"Page {doc.page} | Research use only",
    )
    canvas.restoreState()


def _styled_table(
    data: list[list[object]],
    col_widths: list[float],
    header: bool = True,
) -> Table:
    table = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    style = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 1 if header else 0), (-1, -1), FONT_REGULAR),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.white),
        ("ROWBACKGROUNDS", (0, 1 if header else 0), (-1, -1), [colors.white, LIGHT]),
    ]
    if header:
        style.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
            ]
        )
    table.setStyle(TableStyle(style))
    return table


def build_executive_report(
    output_path: Path,
    reference_price: float,
    data_status: str,
    forward_pe: float,
    composite_risk_score: float,
    risk_weighted_value: float,
    valuations: pd.DataFrame,
    scored_risks: pd.DataFrame,
    brands: pd.DataFrame,
    sourcing: pd.DataFrame,
    mc_summary: dict[str, float],
    materiality: dict[str, float],
    chart_paths: dict[str, Path],
    sources: pd.DataFrame,
    as_of: str,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    styles = _styles()
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.58 * inch,
        title="Gap Equity and Operational Risk Model",
        author="Jason Keen",
        subject="Equity valuation, operational risk, and scenario analysis for Gap Inc.",
    )
    story: list[object] = []

    story.append(Paragraph("Gap Equity and<br/>Operational Risk Model", styles["title"]))
    story.append(
        Paragraph(
            f"Executive research brief | NYSE: GAP | Financial data through {as_of} | "
            f"Market-data mode: {data_status}",
            styles["subtitle"],
        )
    )

    kpis = [
        [Paragraph(f"${reference_price:.2f}", styles["kpi"]), Paragraph(f"{forward_pe:.1f}x", styles["kpi"]), Paragraph(f"{composite_risk_score:.0f}/100", styles["kpi"]), Paragraph(f"${risk_weighted_value:.2f}", styles["kpi"])],
        [Paragraph("Reference price", styles["kpi_label"]), Paragraph("Forward P/E", styles["kpi_label"]), Paragraph("Composite risk", styles["kpi_label"]), Paragraph("Risk-weighted value", styles["kpi_label"])],
    ]
    kpi_table = Table(kpis, colWidths=[1.65 * inch] * 4)
    kpi_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.white),
                ("INNERGRID", (0, 0), (-1, -1), 3, colors.white),
                ("TOPPADDING", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 9),
            ]
        )
    )
    story.extend([kpi_table, Spacer(1, 10)])

    story.append(Paragraph("Investment conclusion", styles["h1"]))
    story.append(
        Paragraph(
            "Gap is an inexpensive but operationally sensitive turnaround. The Gap brand has "
            "regained cultural and commercial momentum, liquidity is strong, and current "
            "valuation leaves room for upside if guided earnings persist. The discount is "
            "partly justified by tariff-sensitive margins, Old Navy concentration, Athleta's "
            "continued contraction, lease commitments, and high earnings-event volatility.",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            f"The model's risk-weighted blended value is <b>${risk_weighted_value:.2f}</b>. "
            f"The Monte Carlo median is <b>${mc_summary['median']:.2f}</b>, with a "
            f"<b>{mc_summary['probability_above_reference']:.0%}</b> probability of exceeding "
            "the reference price. This is a decision-support estimate, not a recommendation.",
            styles["body"],
        )
    )

    story.append(Paragraph("What the market is pricing", styles["h2"]))
    story.append(
        Paragraph(
            "At roughly the high-single-digit forward earnings multiple, the stock price implies "
            "that recent brand momentum and cash generation may not be durable. The key analytical "
            "question is therefore not whether the shares look optically cheap, but whether a "
            "7%+ operating margin can survive tariff, promotion, and consumer-demand pressure.",
            styles["body"],
        )
    )
    story.append(Image(str(chart_paths["scenario"]), width=6.7 * inch, height=3.55 * inch))

    story.append(PageBreak())
    story.append(Paragraph("Scenario valuation", styles["h1"]))
    scenario_rows: list[list[object]] = [
        ["Scenario", "Probability", "EPS", "P/E value", "DCF value", "Blended"]
    ]
    for row in valuations.itertuples(index=False):
        scenario_rows.append(
            [
                row.scenario,
                f"{row.probability:.0%}",
                f"${row.estimated_eps:.2f}",
                f"${row.earnings_value:.2f}",
                f"${row.dcf_value:.2f}",
                f"${row.blended_value:.2f}",
            ]
        )
    story.append(
        _styled_table(
            scenario_rows,
            [1.45 * inch, 0.85 * inch, 0.72 * inch, 0.95 * inch, 0.95 * inch, 0.95 * inch],
        )
    )
    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "The earnings method receives a 70% weight and DCF receives 30%. This keeps the "
            "valuation anchored to observable retail-sector earnings while still recognizing "
            "Gap's free-cash-flow and balance-sheet value.",
            styles["small"],
        )
    )
    story.append(Image(str(chart_paths["sensitivity"]), width=6.45 * inch, height=3.85 * inch))
    story.append(
        Paragraph(
            f"<b>Margin materiality:</b> A 100-basis-point operating-margin change corresponds "
            f"to approximately ${materiality['pre_tax_impact_m']:.0f} million of pre-tax income, "
            f"${materiality['eps_impact']:.2f} of EPS, and ${materiality['price_impact']:.2f} "
            "per share at a 9.5x multiple.",
            styles["body"],
        )
    )

    story.append(PageBreak())
    story.append(Paragraph("Operational risk intelligence", styles["h1"]))
    risk_rows: list[list[object]] = [["Risk", "Category", "Score", "Weight", "Direction"]]
    for row in scored_risks.head(8).itertuples(index=False):
        risk_rows.append(
            [
                Paragraph(str(row.risk), styles["table"]),
                row.category,
                f"{row.adjusted_score:.0f}",
                f"{row.normalized_weight:.0%}",
                row.direction,
            ]
        )
    story.append(
        _styled_table(
            risk_rows,
            [2.4 * inch, 1.0 * inch, 0.55 * inch, 0.65 * inch, 1.0 * inch],
        )
    )
    story.append(Spacer(1, 5))
    story.append(Image(str(chart_paths["risk"]), width=6.5 * inch, height=3.9 * inch))

    story.append(PageBreak())
    story.append(Paragraph("Brand and sourcing diagnostics", styles["h1"]))
    story.append(
        Paragraph(
            "The strongest signal is the Gap brand's double-digit comparable-sales growth. "
            "The largest vulnerability is the combination of Old Navy's revenue weight and "
            "Athleta's prolonged contraction. Portfolio-level results can weaken even while "
            "the namesake brand continues to improve.",
            styles["body"],
        )
    )
    story.append(Image(str(chart_paths["brands"]), width=6.6 * inch, height=3.45 * inch))
    story.append(
        Paragraph(
            "Sourcing concentration turns trade policy and geopolitical disruption into direct "
            "gross-margin variables. Vietnam and Indonesia represented 48% of fiscal 2025 "
            "merchandise purchases by value.",
            styles["body"],
        )
    )
    story.append(Image(str(chart_paths["sourcing"]), width=6.35 * inch, height=3.35 * inch))

    story.append(PageBreak())
    story.append(Paragraph("Monte Carlo price-risk distribution", styles["h1"]))
    story.append(Image(str(chart_paths["monte_carlo"]), width=6.65 * inch, height=3.55 * inch))
    mc_rows = [
        ["Metric", "Result", "Interpretation"],
        ["5th percentile", f"${mc_summary['p05']:.2f}", "Severe downside tail"],
        ["Median", f"${mc_summary['median']:.2f}", "Central simulated outcome"],
        ["95th percentile", f"${mc_summary['p95']:.2f}", "Strong execution outcome"],
        ["P(value below $15)", f"{mc_summary['probability_below_15']:.1%}", "Material drawdown risk"],
        ["P(value above $27)", f"{mc_summary['probability_above_27']:.1%}", "Turnaround upside"],
    ]
    story.append(_styled_table(mc_rows, [1.45 * inch, 1.05 * inch, 3.55 * inch]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Quarterly monitoring framework", styles["h2"]))
    monitoring_items = [
        "Old Navy and Gap comparable-sales spread",
        "Athleta comparable-sales and revenue direction",
        "Merchandise margin excluding tariff effects",
        "Inventory growth relative to net-sales growth",
        "Promotional intensity and average unit retail",
        "Tariff rates affecting Vietnam and Indonesia sourcing",
        "Operating cash flow, capital expenditures, and repurchase pace",
        "Online-sales growth and channel mix",
    ]
    for item in monitoring_items:
        story.append(Paragraph(f"- {item}", styles["body"]))

    story.append(PageBreak())
    story.append(Paragraph("Methodology and source register", styles["h1"]))
    story.append(
        Paragraph(
            "The model combines three valuation scenarios, a five-year DCF, operating-margin "
            "sensitivity, an eight-factor operational-risk score, and a seeded Monte Carlo "
            "simulation. Monte Carlo trials vary revenue growth, operating margin, taxes, "
            "share count, valuation multiple, and discrete tariff, consumer, and brand events. "
            "Pinned inputs make the result reproducible; optional live mode refreshes only the "
            "market price and safely falls back to pinned data.",
            styles["body"],
        )
    )
    source_rows: list[list[object]] = [["Source", "Purpose", "As of"]]
    for row in sources.itertuples(index=False):
        source_rows.append(
            [
                Paragraph(f'<link href="{row.url}" color="#2F6BFF">{row.source}</link>', styles["table"]),
                Paragraph(str(row.purpose), styles["table"]),
                str(row.as_of),
            ]
        )
    story.append(_styled_table(source_rows, [2.05 * inch, 3.45 * inch, 0.8 * inch]))
    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "<b>Limitations:</b> The model does not forecast daily trading prices, does not "
            "capture every tax or accounting adjustment, and does not constitute investment "
            "advice. Scenario probabilities and shock distributions are transparent analyst "
            "assumptions and should be updated after each earnings release or material trade-policy change.",
            styles["small"],
        )
    )
    story.append(
        Paragraph(
            f"Generated {date.today().isoformat()} | Model version 1.0.1",
            styles["small"],
        )
    )

    doc.build(story, onFirstPage=_page_frame, onLaterPages=_page_frame)
    return output_path
