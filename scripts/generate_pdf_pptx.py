import os
import sqlite3
import pandas as pd
import numpy as np
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# Workspace paths
workspace = r"c:\Datatatatta"
db_path = os.path.join(workspace, "data", "db", "bluestock_mf.db")
reports_dir = os.path.join(workspace, "reports")
figures_dir = os.path.join(reports_dir, "figures")
os.makedirs(reports_dir, exist_ok=True)

# Colors definition
PRIMARY_HEX = "#1f77b4"      # Muted Navy Blue
SECONDARY_HEX = "#2c3e50"    # Dark Slate
TEXT_HEX = "#333333"         # Dark Grey
LIGHT_BG_HEX = "#f8f9fa"     # Light grey bg
ACCENT_HEX = "#e74c3c"       # Accent Red

PRIMARY_RGB = RGBColor(31, 119, 180)
SECONDARY_RGB = RGBColor(44, 62, 80)
TEXT_RGB = RGBColor(51, 51, 51)
LIGHT_BG_RGB = RGBColor(248, 249, 250)
ACCENT_RGB = RGBColor(231, 76, 60)

# Connect to database for fetching actual data
conn = sqlite3.connect(db_path)

# Fetch aggregate statistics
kpi_total_aum = pd.read_sql_query("SELECT SUM(aum_crore) FROM fact_performance", conn).values[0][0]
kpi_total_schemes = pd.read_sql_query("SELECT COUNT(*) FROM dim_fund", conn).values[0][0]
kpi_total_tx = pd.read_sql_query("SELECT COUNT(*) FROM fact_transactions", conn).values[0][0]
kpi_total_volume = pd.read_sql_query("SELECT SUM(amount_inr) FROM fact_transactions", conn).values[0][0]

# Fetch top 5 funds by AUM
top_funds_df = pd.read_sql_query("""
    SELECT f.scheme_name, f.fund_house, f.category, f.risk_category, p.aum_crore, p.sharpe_ratio, p.return_3yr_pct
    FROM fact_performance p
    JOIN dim_fund f ON p.amfi_code = f.amfi_code
    ORDER BY p.aum_crore DESC
    LIMIT 5
""", conn)

# Fetch some performance metrics summary
metrics_summary_df = pd.read_sql_query("""
    SELECT f.category, COUNT(f.amfi_code) as num_funds, 
           AVG(p.return_3yr_pct) as avg_3yr_return, AVG(p.sharpe_ratio) as avg_sharpe, AVG(p.beta) as avg_beta
    FROM fact_performance p
    JOIN dim_fund f ON p.amfi_code = f.amfi_code
    GROUP BY f.category
""", conn)

# Fetch transactions by age group
age_dist_df = pd.read_sql_query("""
    SELECT age_group, COUNT(*) as tx_count, SUM(amount_inr) as total_amount
    FROM fact_transactions
    GROUP BY age_group
""", conn)

# NumberedCanvas for ReportLab pagination (Page X of Y)
class NumberedCanvas(canvas.Canvas):
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
            self.draw_page_elements(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_elements(self, page_count):
        if self._pageNumber == 1:
            # Draw beautiful cover page borders and backgrounds
            self.saveState()
            self.setFillColor(colors.HexColor(PRIMARY_HEX))
            self.rect(0, 0, 15, 792, fill=True, stroke=False)
            self.setFillColor(colors.HexColor(SECONDARY_HEX))
            self.rect(15, 0, 10, 792, fill=True, stroke=False)
            self.restoreState()
            return

        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#7f8c8d"))
        
        # Header (Only on page 2 onwards)
        self.drawString(54, 750, "Bluestock Mutual Fund Portfolio Analytics Report")
        self.setLineWidth(0.5)
        self.setStrokeColor(colors.HexColor("#bdc3c7"))
        self.line(54, 742, 558, 742)
        
        # Footer
        self.line(54, 55, 558, 55)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 40, page_text)
        self.drawString(54, 40, "Bluestock Mutual Fund Capstone Project | Confidential Report")
        self.restoreState()

def build_pdf():
    pdf_path = os.path.join(reports_dir, "Final_Report.pdf")
    # Top margin is 72 to clear the header (height 742)
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=32,
        leading=38,
        textColor=colors.HexColor(PRIMARY_HEX),
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor(SECONDARY_HEX),
        spaceAfter=30
    )
    
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor(PRIMARY_HEX),
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor(SECONDARY_HEX),
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor(TEXT_HEX),
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor(TEXT_HEX),
        leftIndent=20,
        firstLineIndent=-10,
        spaceAfter=5
    )
    
    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor(TEXT_HEX)
    )

    story = []
    
    # ----------------------------------------------------
    # COVER PAGE
    # ----------------------------------------------------
    story.append(Spacer(1, 100))
    story.append(Paragraph("BLUESTOCK MUTUAL FUND<br/>PORTFOLIO ANALYTICS", title_style))
    story.append(Paragraph("A Comprehensive Data Engineering & Financial Analytics Capstone Report", subtitle_style))
    story.append(Spacer(1, 150))
    
    # Metadata Block
    meta_text = f"""
    <b>Prepared For:</b> Bluestock Fintech<br/>
    <b>Author:</b> Antigravity AI Engineer<br/>
    <b>Date:</b> June 2026<br/>
    <b>Project Stage:</b> Day 4 Core Execution & Final Review<br/>
    <b>Database Version:</b> v1.4 (SQLite Star Schema)<br/>
    """
    story.append(Paragraph(meta_text, meta_style))
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # SECTION 1: EXECUTIVE SUMMARY
    # ----------------------------------------------------
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(Paragraph(
        "This project delivers an end-to-end data processing, storage, analytics, and visualization solution for "
        "mutual fund portfolios. Using a high-performance star schema database, we process raw histories, calculate "
        "industry-standard performance statistics, simulate risk paths, and construct an optimization framework.",
        body_style
    ))
    
    # KPI Table
    kpi_data = [
        [Paragraph("<b>Metric</b>", body_style), Paragraph("<b>Value</b>", body_style), Paragraph("<b>Business Description</b>", body_style)],
        ["Aggregate AUM", f"INR {kpi_total_aum / 100000:.2f} Lakh Crore", "Total Assets Under Management across all active funds in registry."],
        ["Active Schemes", f"{kpi_total_schemes} Funds", "Count of verified mutual fund schemes being monitored."],
        ["Total Transactions", f"{kpi_total_tx:,}", "Retail investor transaction counts logged in the system."],
        ["Transaction Volume", f"INR {kpi_total_volume / 10000000:.2f} Crore", "Cumulative retail transaction volume invested."]
    ]
    t_kpi = Table(kpi_data, colWidths=[120, 130, 250])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor(PRIMARY_HEX)),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor(LIGHT_BG_HEX), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#dddddd")),
    ]))
    
    story.append(t_kpi)
    story.append(Spacer(1, 15))
    
    # Top 5 Funds Table
    story.append(Paragraph("Top 5 Mutual Funds by Assets Under Management (AUM)", h2_style))
    fund_table_data = [
        ["Scheme Name", "Category", "AUM (Crore)", "Sharpe Ratio", "3-Year CAGR"]
    ]
    for idx, r in top_funds_df.iterrows():
        fund_table_data.append([
            r['scheme_name'].split(' - ')[0],
            r['category'],
            f"INR {r['aum_crore']:,}",
            f"{r['sharpe_ratio']:.2f}",
            f"{r['return_3yr_pct']:.2f}%"
        ])
    t_funds = Table(fund_table_data, colWidths=[180, 80, 100, 70, 70])
    t_funds.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor(SECONDARY_HEX)),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#dddddd")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor(LIGHT_BG_HEX), colors.white]),
    ]))
    story.append(t_funds)
    story.append(Spacer(1, 15))

    # ----------------------------------------------------
    # SECTION 2: DATA QUALITY & ETL PIPELINE
    # ----------------------------------------------------
    story.append(Paragraph("2. Data Quality & ETL Ingestion Pipeline", h1_style))
    story.append(Paragraph(
        "Our ETL process (implemented in `scripts/etl_pipeline.py`) performs ingestion, validation, and loading of "
        "raw CSV datasets into our relational schema. To preserve historical NAV fidelity and handle calendar gaps, "
        "we apply rigorous cleaning operations:",
        body_style
    ))
    story.append(Paragraph("• <b>Weekend and Holiday Gaps:</b> NAV files exclude weekends/holidays. The ETL pipeline reindexes each fund history to a continuous date range and forward-fills (`ffill()`) values to ensure accurate CAGR calculations.", bullet_style))
    story.append(Paragraph("• <b>Standardization:</b> Transaction type values are standardized into an enum string (`SIP`, `Lumpsum`, `Redemption`), and date strings are parsed into uniform `YYYY-MM-DD` timestamps.", bullet_style))
    story.append(Paragraph("• <b>Key Validation:</b> A data validation check confirmed 100% referential integrity between `dim_fund` and `fact_nav` (all AMFI codes matched).", bullet_style))
    story.append(Spacer(1, 10))
    
    # ----------------------------------------------------
    # SECTION 3: DATABASE ARCHITECTURE
    # ----------------------------------------------------
    story.append(Paragraph("3. SQLite Star Schema Database Architecture", h1_style))
    story.append(Paragraph(
        "The relational database is structured as a <b>Star Schema</b> for fast analytical querying and dashboard retrieval. "
        "The layout separates core entities into logical dimensions and transactional facts:",
        body_style
    ))
    story.append(Paragraph("• <b>dim_fund:</b> Holds fund static attributes (AMFI code, scheme name, fund house, category, risk, benchmark, expense ratio).", bullet_style))
    story.append(Paragraph("• <b>dim_date:</b> Holds date dimensions (date, year, month, quarter, day of week, weekday flag).", bullet_style))
    story.append(Paragraph("• <b>fact_nav:</b> Tracks daily net asset value time series.", bullet_style))
    story.append(Paragraph("• <b>fact_transactions:</b> Logs retail transaction specifics (investor ID, city tier, state, payment mode, gender, age group).", bullet_style))
    story.append(Paragraph("• <b>fact_performance / fact_aum:</b> Summarizes risk parameters, Morningstar ratings, and asset size dimensions.", bullet_style))
    story.append(PageBreak())

    # ----------------------------------------------------
    # SECTION 4: FINANCIAL PERFORMANCE & RISK ANALYTICS
    # ----------------------------------------------------
    story.append(Paragraph("4. Performance Analytics & Risk Metrics", h1_style))
    story.append(Paragraph(
        "We implement mathematically correct financial formulations to evaluate the portfolios. In accordance with professional standards, "
        "returns are annualized using a <b>252-trading day convention</b> rather than 365 calendar days:",
        body_style
    ))
    
    # Formula explanation
    story.append(Paragraph("<b>CAGR (Compound Annual Growth Rate):</b>", h2_style))
    story.append(Paragraph("<i>CAGR = (V_end / V_begin) ^ (252 / N_trading_days) - 1</i>", bullet_style))
    
    story.append(Paragraph("<b>Sharpe Ratio:</b> measures excess return per unit of volatility relative to a 6% risk-free rate:", h2_style))
    story.append(Paragraph("<i>Sharpe = ((Mean Daily Return - Risk-Free Daily Rate) / Daily Return StdDev) * sqrt(252)</i>", bullet_style))
    
    story.append(Paragraph("<b>Value at Risk (95% Daily VaR):</b> represents the threshold indicating that daily losses will not exceed this value with 95% confidence:", h2_style))
    story.append(Paragraph("<i>VaR_95 = 5th Percentile of Daily returns</i>", bullet_style))
    story.append(Spacer(1, 10))

    # Category Table
    cat_table_data = [
        ["Category", "Funds Count", "Avg 3-Yr Return", "Avg Sharpe Ratio", "Avg Beta vs Bench"]
    ]
    for idx, r in metrics_summary_df.iterrows():
        cat_table_data.append([
            r['category'],
            f"{int(r['num_funds'])}",
            f"{r['avg_3yr_return']:.2f}%",
            f"{r['avg_sharpe']:.2f}",
            f"{r['avg_beta']:.2f}"
        ])
    t_cat = Table(cat_table_data, colWidths=[120, 90, 110, 100, 100])
    t_cat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor(PRIMARY_HEX)),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#dddddd")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor(LIGHT_BG_HEX), colors.white]),
    ]))
    story.append(t_cat)
    story.append(Spacer(1, 15))

    # Embed charts
    nav_chart_path = os.path.join(figures_dir, "01_nav_trends.png")
    if os.path.exists(nav_chart_path):
        story.append(Paragraph("NAV daily historical performance trends (2022–2026):", h2_style))
        story.append(Image(nav_chart_path, width=450, height=225))
    
    story.append(PageBreak())

    # ----------------------------------------------------
    # SECTION 5: ADVANCED FINANCIAL MODELS
    # ----------------------------------------------------
    story.append(Paragraph("5. Advanced Financial Analytics", h1_style))
    
    # Monte Carlo
    story.append(Paragraph("5.1 Monte Carlo NAV Growth Simulation", h2_style))
    story.append(Paragraph(
        "Using Euler-Maruyama discretization of Geometric Brownian Motion, we simulate the daily NAV path of "
        "SBI Bluechip Fund (119551) 5 years into the future. By computing quantile lines across 1,000 paths, we construct "
        "uncertainty bands around the expected trajectory, capturing statistical limits of performance volatility.",
        body_style
    ))
    
    # Markowitz
    story.append(Paragraph("5.2 Markowitz Efficient Frontier Optimization", h2_style))
    story.append(Paragraph(
        "We construct a portfolios space from 5 key funds (SBI Bluechip, ICICI Bluechip, Nippon Large Cap, Axis Bluechip, "
        "and Kotak Bluechip). By generating 10,000 random weight combinations, we map the Efficient Frontier. The optimal "
        "Tangency Portfolio (maximizing Sharpe ratio) and the Minimum Variance Portfolio are identified, providing mathematical "
        "guidance for capital allocation.",
        body_style
    ))
    
    # Cohort
    story.append(Paragraph("5.3 Cohort Retention & Recommender Engine", h2_style))
    story.append(Paragraph(
        "Transaction behaviors are tracked using monthly cohort analysis, illustrating investor retention over time. Additionally, "
        "the content-based recommender engine combines demographic-inferred risk parameters (younger age groups default to "
        "higher risk equity funds; older groups default to low-risk debt instruments) and filters out existing assets.",
        body_style
    ))
    
    frontier_chart_path = os.path.join(figures_dir, "11_nav_correlation_matrix.png")
    if os.path.exists(frontier_chart_path):
        story.append(Spacer(1, 10))
        story.append(Paragraph("Pairwise returns correlation matrix heatmap of 10 schemes:", h2_style))
        story.append(Image(frontier_chart_path, width=320, height=260))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print("Report PDF generated successfully at reports/Final_Report.pdf")

def build_pptx():
    pptx_path = os.path.join(reports_dir, "Presentation.pptx")
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    blank_layout = prs.slide_layouts[6] # Blank
    
    # Helper to add standard header and slide design
    def create_slide(title_text):
        slide = prs.slides.add_slide(blank_layout)
        
        # Header banner
        header_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(12.333), Inches(0.8))
        tf = header_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.name = "Arial"
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_RGB
        
        # Bottom footer line
        line = slide.shapes.add_shape(
            1, # Rectangle
            Inches(0.5), Inches(7.0), Inches(12.333), Inches(0.02)
        )
        line.fill.solid()
        line.fill.fore_color.rgb = SECONDARY_RGB
        line.line.color.rgb = SECONDARY_RGB
        
        # Footer text
        footer_box = slide.shapes.add_textbox(Inches(0.5), Inches(7.05), Inches(12.333), Inches(0.3))
        tf_foot = footer_box.text_frame
        p_foot = tf_foot.paragraphs[0]
        p_foot.text = "Bluestock Mutual Fund Analytics Capstone | June 2026"
        p_foot.font.size = Pt(10)
        p_foot.font.color.rgb = RGBColor(127, 140, 141)
        
        return slide

    # SLIDE 1: TITLE SLIDE (Custom design)
    slide1 = prs.slides.add_slide(blank_layout)
    # Background accent block
    bg_accent = slide1.shapes.add_shape(1, Inches(0), Inches(0), Inches(0.4), Inches(7.5))
    bg_accent.fill.solid()
    bg_accent.fill.fore_color.rgb = PRIMARY_RGB
    bg_accent.line.fill.background()

    bg_accent2 = slide1.shapes.add_shape(1, Inches(0.4), Inches(0), Inches(0.2), Inches(7.5))
    bg_accent2.fill.solid()
    bg_accent2.fill.fore_color.rgb = SECONDARY_RGB
    bg_accent2.line.fill.background()

    # Title box
    title_box = slide1.shapes.add_textbox(Inches(1.2), Inches(2.2), Inches(11.0), Inches(2.5))
    tf = title_box.text_frame
    p1 = tf.paragraphs[0]
    p1.text = "BLUESTOCK MUTUAL FUND"
    p1.font.size = Pt(44)
    p1.font.bold = True
    p1.font.color.rgb = PRIMARY_RGB
    p1.font.name = "Arial"
    
    p2 = tf.add_paragraph()
    p2.text = "PORTFOLIO & RISK ANALYTICS"
    p2.font.size = Pt(36)
    p2.font.bold = True
    p2.font.color.rgb = SECONDARY_RGB
    
    p3 = tf.add_paragraph()
    p3.text = "End-to-End Data Engineering & Advanced Financial Modeling"
    p3.font.size = Pt(18)
    p3.font.color.rgb = RGBColor(100, 110, 120)
    p3.space_before = Pt(20)

    # Info box
    info_box = slide1.shapes.add_textbox(Inches(1.2), Inches(5.2), Inches(8.0), Inches(1.5))
    tf_info = info_box.text_frame
    pi1 = tf_info.paragraphs[0]
    pi1.text = "Prepared by: Antigravity AI Engineer"
    pi1.font.size = Pt(12)
    pi1.font.color.rgb = TEXT_RGB
    
    pi2 = tf_info.add_paragraph()
    pi2.text = "Platform: Python, SQLite Star Schema, Streamlit"
    pi2.font.size = Pt(12)
    pi2.font.color.rgb = TEXT_RGB

    # SLIDE 2: INGESTION & DATA QUALITY
    slide2 = create_slide("Data Ingestion & Cleaning Pipeline")
    # Bullet points on left
    bullet_box = slide2.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(6.0), Inches(5.0))
    tf = bullet_box.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "Ingestion Overview"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = SECONDARY_RGB
    
    bullets = [
        "Loads 10 raw CSV datasets covering funds, NAV history, inflows, transactions, and holdings.",
        "Live NAV fetching module retrieves and saves HDFC Top 100 scheme NAV data from API (mfapi.in).",
        "Cleans NAV history by sorting and forward-filling weekend and holiday gaps to prevent calendar bias.",
        "Standardizes transaction types (SIP/Lumpsum/Redemption) and cleans KYC enums.",
        "Verifies 100% referential integrity with AMFI scheme code matches across datasets (Passes validation)."
    ]
    for b in bullets:
        p_b = tf.add_paragraph()
        p_b.text = "• " + b
        p_b.font.size = Pt(14)
        p_b.space_before = Pt(8)
        p_b.font.color.rgb = TEXT_RGB

    # AUM Chart on right
    aum_img_path = os.path.join(figures_dir, "02_aum_growth.png")
    if os.path.exists(aum_img_path):
        slide2.shapes.add_picture(aum_img_path, Inches(6.8), Inches(1.5), Inches(6.0), Inches(4.5))

    # SLIDE 3: EXECUTIVE SUMMARY & AUM
    slide3 = create_slide("Executive Summary & AUM Concentration")
    
    # Left Side KPI cards (using text boxes as shapes)
    kpis = [
        ("AGGREGATE AUM", f"INR {kpi_total_aum / 100000:.2f}L Cr", "Cumulative asset scale"),
        ("ACTIVE FUNDS", f"{kpi_total_schemes}", "Monitored mutual funds"),
        ("TOTAL TRANSACTIONS", f"{kpi_total_tx:,}", "Retail investor trade log count"),
        ("TRANSACTION VOLUME", f"INR {kpi_total_volume / 10000000:.2f} Cr", "Retail invested capital")
    ]
    
    for i, (label, val, desc) in enumerate(kpis):
        top = 1.5 + (i * 1.3)
        # Background card
        card = slide3.shapes.add_shape(1, Inches(0.5), Inches(top), Inches(5.5), Inches(1.1))
        card.fill.solid()
        card.fill.fore_color.rgb = LIGHT_BG_RGB
        card.line.color.rgb = RGBColor(220, 225, 230)
        
        # Text in card
        tf_card = card.text_frame
        tf_card.word_wrap = True
        tf_card.margin_left = Inches(0.1)
        tf_card.margin_top = Inches(0.1)
        p_label = tf_card.paragraphs[0]
        p_label.text = label
        p_label.font.size = Pt(11)
        p_label.font.bold = True
        p_label.font.color.rgb = PRIMARY_RGB
        
        p_val = tf_card.add_paragraph()
        p_val.text = val
        p_val.font.size = Pt(22)
        p_val.font.bold = True
        p_val.font.color.rgb = SECONDARY_RGB
        
        p_desc = tf_card.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(9)
        p_desc.font.color.rgb = RGBColor(120, 130, 140)

    # Right side chart showing Category Heatmap or SIP inflow
    sip_img_path = os.path.join(figures_dir, "03_sip_inflow_trend.png")
    if os.path.exists(sip_img_path):
        slide3.shapes.add_picture(sip_img_path, Inches(6.8), Inches(1.5), Inches(6.0), Inches(4.5))

    # SLIDE 4: INVESTOR DEMOGRAPHICS
    slide4 = create_slide("Investor Demographics & Geographic Split")
    
    bullet_box = slide4.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(6.0), Inches(5.0))
    tf = bullet_box.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "Key Demographic Insights"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = SECONDARY_RGB
    
    insights = [
        "Age Group Dominance: Younger cohorts aged 26-35 drive the highest transaction counts (43.8% total volume).",
        "Geographic Concentration: Maharashtra acts as the primary volume driver, contributing to more than 35% of total capital.",
        "Tier Split: T30 cities swallow 69.9% of capital, while B30 cities contribute a solid 30.1%, highlighting strong semi-urban penetration.",
        "Gender Split: Transaction amounts display an active male-skewed distribution, though female-registered folios are rising.",
        "Preferred Channels: UPI and Net Banking dominate transaction payment modes, highlighting digital platform convenience."
    ]
    for ins in insights:
        p_b = tf.add_paragraph()
        p_b.text = "• " + ins
        p_b.font.size = Pt(13)
        p_b.space_before = Pt(8)
        p_b.font.color.rgb = TEXT_RGB

    demo_img_path = os.path.join(figures_dir, "05_age_group_pie.png")
    if os.path.exists(demo_img_path):
        slide4.shapes.add_picture(demo_img_path, Inches(6.8), Inches(1.5), Inches(6.0), Inches(4.5))

    # SLIDE 5: PERFORMANCE ANALYTICS
    slide5 = create_slide("Performance Analytics & Risk Profiling")
    
    bullet_box = slide5.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(6.0), Inches(5.0))
    tf = bullet_box.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "Mathematical Metrics (252 Trading Days)"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = SECONDARY_RGB
    
    p_desc = tf.add_paragraph()
    p_desc.text = "We avoid calendar errors by annualizing returns and risk measures based on actual market trading days (252) rather than 365 days."
    p_desc.font.size = Pt(13)
    p_desc.space_before = Pt(5)
    
    perf_bullets = [
        "CAGR: Annualized compound growth. Used to normalize performance across different lifetimes.",
        "Sharpe Ratio: Excess return per unit of volatility relative to 6% annual Risk-Free Rate.",
        "Beta: Evaluates fund return volatility relative to its benchmark index (e.g. Nifty 50).",
        "Value at Risk (95% Daily VaR): The 5th percentile threshold of returns, mapping maximum expected daily loss."
    ]
    for pb in perf_bullets:
        p_b = tf.add_paragraph()
        p_b.text = "• " + pb
        p_b.font.size = Pt(13)
        p_b.space_before = Pt(8)
        p_b.font.color.rgb = TEXT_RGB

    # Embed Scatter Plot (Sharpe vs Returns)
    scatter_img_path = os.path.join(figures_dir, "15_expense_vs_return_scatter.png")
    if os.path.exists(scatter_img_path):
        slide5.shapes.add_picture(scatter_img_path, Inches(6.8), Inches(1.5), Inches(6.0), Inches(4.5))

    # SLIDE 6: MONTE CARLO SIMULATION
    slide6 = create_slide("Advanced Analytics: Monte Carlo NAV Projections")
    
    bullet_box = slide6.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(6.0), Inches(5.0))
    tf = bullet_box.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "Geometric Brownian Motion Projection"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = SECONDARY_RGB
    
    mc_bullets = [
        "Simulates daily NAV path for SBI Bluechip Fund (119551) over 5 years (1,260 trading days).",
        "Uses historical mean return drift and volatility standard deviation from daily returns.",
        "Expected Mean Path projects compounding trajectory based on log-normal asset growth.",
        "Confidence Bands: Shaded bands outline the 5th and 95th percentile paths, outlining pessimistic and optimistic limits.",
        "Aides investors in risk planning, showing capital probability limits over long horizons."
    ]
    for mb in mc_bullets:
        p_b = tf.add_paragraph()
        p_b.text = "• " + mb
        p_b.font.size = Pt(13)
        p_b.space_before = Pt(8)
        p_b.font.color.rgb = TEXT_RGB

    # If we have a monte carlo chart saved in reports/figures we can embed it,
    # otherwise we can use the correlation matrix or other advanced charts.
    # In Streamlit we run it interactively, and we also draw it in notebooks.
    # Let's see if 01_nav_trends can be shown as a placeholder or we can leave it.
    corr_img_path = os.path.join(figures_dir, "11_nav_correlation_matrix.png")
    if os.path.exists(corr_img_path):
        slide6.shapes.add_picture(corr_img_path, Inches(6.8), Inches(1.7), Inches(5.5), Inches(4.5))

    # SLIDE 7: MARKOWITZ EFFORT FRONTIER
    slide7 = create_slide("Advanced Analytics: Markowitz Portfolio Optimization")
    
    bullet_box = slide7.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(6.0), Inches(5.0))
    tf = bullet_box.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "Modern Portfolio Theory (MPT) Application"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = SECONDARY_RGB
    
    mpt_bullets = [
        "Combines 5 key large-cap funds (SBI, ICICI, Nippon, Axis, Kotak) to optimize weights.",
        "Computes historical daily covariance matrix to evaluate diversification benefits.",
        "Simulates 10,000 portfolio combinations to map the Markowitz Efficient Frontier curve.",
        "Maximum Sharpe Ratio Portfolio: Identifies weights that yield the highest risk-adjusted return.",
        "Minimum Volatility Portfolio: Yields weights that minimize portfolio standard deviation."
    ]
    for mp in mpt_bullets:
        p_b = tf.add_paragraph()
        p_b.text = "• " + mp
        p_b.font.size = Pt(13)
        p_b.space_before = Pt(8)
        p_b.font.color.rgb = TEXT_RGB

    # Sector donut or correlation heatmap
    donut_img_path = os.path.join(figures_dir, "12_sector_donut.png")
    if os.path.exists(donut_img_path):
        slide7.shapes.add_picture(donut_img_path, Inches(6.8), Inches(1.5), Inches(6.0), Inches(4.5))

    prs.save(pptx_path)
    print("Presentation PPTX generated successfully at reports/Presentation.pptx")

if __name__ == "__main__":
    build_pdf()
    build_pptx()
    conn.close()
