"""
add_native_visuals.py
Adds data-bound native Power BI visuals (KPI cards, slicers, scatter, table)
to the existing 5 pages in the Bluestock_MF_Dashboard PBIP project.
Uses the PBIP v2.10.0 per-visual-file format.
"""
import json
import os
import hashlib

REPORT_DIR = r"C:\Datatatatta\dashboard\Bluestock_MF_Dashboard.Report"
DEF_DIR = os.path.join(REPORT_DIR, "definition")
PAGES_DIR = os.path.join(DEF_DIR, "pages")

# Bluestock colours
NAVY   = "#002A54"
CYAN   = "#00D2FF"
CARD_BG= "#0A3A6B"
WHITE  = "#FFFFFF"
ORANGE = "#FF6B35"

# Page IDs (confirmed from PBI Desktop output)
P1 = "6f0c41c85a7c03310d46"  # Industry Overview
P2 = "7f0c41c85a7c03310d47"  # Fund Performance
P3 = "8f0c41c85a7c03310d48"  # Investor Analytics
P4 = "9f0c41c85a7c03310d49"  # SIP & Market Trends
P5 = "0f0c41c85a7c03310d50"  # NAV Detail

SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.10.0/schema.json"

# ─── Visual builder functions ─────────────────────────────────────────────────

def vid(page_id, suffix):
    """Generate a unique visual ID."""
    h = hashlib.md5(f"{page_id}_{suffix}".encode()).hexdigest()[:12]
    return f"visual_native_{h}"

def write_visual(page_id, name, pos, visual_obj):
    """Write a visual.json file to the page's visuals folder."""
    page_visuals_dir = os.path.join(PAGES_DIR, page_id, "visuals", name)
    os.makedirs(page_visuals_dir, exist_ok=True)
    data = {
        "$schema": SCHEMA,
        "name": name,
        "position": pos,
        "visual": visual_obj
    }
    path = os.path.join(page_visuals_dir, "visual.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path

def mk_pos(x, y, w, h, z=10, tab=10):
    return {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": tab}

def mk_field(entity, prop):
    return {"Column": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}

def mk_proj(entity, prop, active=False):
    p = {"field": mk_field(entity, prop), "queryRef": f"{entity}.{prop}"}
    if active:
        p["active"] = True
    return p

def kpi_card(page_id, name, x, y, w, h, entity, measure, title, z=10, tab=10):
    """Create a KPI card visual."""
    visual_obj = {
        "visualType": "card",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [mk_proj(entity, measure)]
                }
            }
        },
        "objects": {
            "title": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                    "fontColor": {"solid": {"color": CYAN}},
                    "fontSize": {"expr": {"Literal": {"Value": "12D"}}},
                    "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI Semibold'"}}}
                }
            }],
            "labels": [{
                "properties": {
                    "fontSize": {"expr": {"Literal": {"Value": "24D"}}},
                    "color": {"solid": {"color": WHITE}},
                    "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI Semibold'"}}}
                }
            }],
            "background": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "color": {"solid": {"color": CARD_BG}},
                    "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                }
            }]
        },
        "drillFilterOtherVisuals": True
    }
    vname = vid(page_id, name)
    write_visual(page_id, vname, mk_pos(x, y, w, h, z, tab), visual_obj)
    return vname

def slicer_v(page_id, name, x, y, w, h, entity, col, title, z=10, tab=10):
    """Create a slicer visual."""
    visual_obj = {
        "visualType": "slicer",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [mk_proj(entity, col)]
                }
            }
        },
        "objects": {
            "header": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "fontColor": {"solid": {"color": CYAN}},
                    "fontSize": {"expr": {"Literal": {"Value": "11D"}}},
                    "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}
                }
            }],
            "items": [{
                "properties": {
                    "fontColor": {"solid": {"color": WHITE}},
                    "background": {"solid": {"color": CARD_BG}},
                    "fontSize": {"expr": {"Literal": {"Value": "10D"}}}
                }
            }],
            "background": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "color": {"solid": {"color": CARD_BG}},
                    "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                }
            }]
        },
        "drillFilterOtherVisuals": True
    }
    vname = vid(page_id, name)
    write_visual(page_id, vname, mk_pos(x, y, w, h, z, tab), visual_obj)
    return vname

def table_v(page_id, name, x, y, w, h, columns, title, z=10, tab=10):
    """Create a table visual. columns: list of (entity, col)."""
    projs = [mk_proj(t, c) for t, c in columns]
    visual_obj = {
        "visualType": "tableEx",
        "query": {
            "queryState": {
                "Values": {"projections": projs}
            }
        },
        "objects": {
            "title": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                    "fontColor": {"solid": {"color": CYAN}},
                    "fontSize": {"expr": {"Literal": {"Value": "12D"}}}
                }
            }],
            "columnHeaders": [{
                "properties": {
                    "fontColor": {"solid": {"color": CYAN}},
                    "backColor": {"solid": {"color": NAVY}},
                    "fontSize": {"expr": {"Literal": {"Value": "10D"}}}
                }
            }],
            "values": [{
                "properties": {
                    "fontColor": {"solid": {"color": WHITE}},
                    "backColor": {"solid": {"color": CARD_BG}},
                    "fontSize": {"expr": {"Literal": {"Value": "10D"}}}
                }
            }],
            "background": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "color": {"solid": {"color": CARD_BG}},
                    "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                }
            }]
        },
        "drillFilterOtherVisuals": True
    }
    vname = vid(page_id, name)
    write_visual(page_id, vname, mk_pos(x, y, w, h, z, tab), visual_obj)
    return vname

def scatter_v(page_id, name, x, y, w, h, detail_e, detail_c, x_e, x_c, y_e, y_c, size_e=None, size_c=None, title="", z=10, tab=10):
    """Create a scatter chart visual."""
    qs = {
        "Details": {"projections": [mk_proj(detail_e, detail_c)]},
        "X": {"projections": [mk_proj(x_e, x_c, active=True)]},
        "Y": {"projections": [mk_proj(y_e, y_c, active=True)]}
    }
    if size_e and size_c:
        qs["Size"] = {"projections": [mk_proj(size_e, size_c, active=True)]}
    visual_obj = {
        "visualType": "scatterChart",
        "query": {"queryState": qs},
        "objects": {
            "title": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                    "fontColor": {"solid": {"color": CYAN}},
                    "fontSize": {"expr": {"Literal": {"Value": "12D"}}}
                }
            }],
            "background": [{
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "color": {"solid": {"color": CARD_BG}},
                    "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                }
            }],
            "dataPoint": [{
                "properties": {
                    "defaultColor": {"solid": {"color": CYAN}}
                }
            }]
        },
        "drillFilterOtherVisuals": True
    }
    vname = vid(page_id, name)
    write_visual(page_id, vname, mk_pos(x, y, w, h, z, tab), visual_obj)
    return vname

def line_v(page_id, name, x, y, w, h, cat_e, cat_c, values, title="", z=10, tab=10):
    """values: list of (entity, col)."""
    y_projs = [mk_proj(t, c, active=True) for t, c in values]
    qs = {
        "Category": {"projections": [mk_proj(cat_e, cat_c)]},
        "Y": {"projections": y_projs}
    }
    visual_obj = {
        "visualType": "lineChart",
        "query": {"queryState": qs},
        "objects": {
            "title": [{"properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                "fontColor": {"solid": {"color": CYAN}},
                "fontSize": {"expr": {"Literal": {"Value": "12D"}}}
            }}],
            "background": [{"properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "color": {"solid": {"color": CARD_BG}},
                "transparency": {"expr": {"Literal": {"Value": "0D"}}}
            }}]
        },
        "drillFilterOtherVisuals": True
    }
    vname = vid(page_id, name)
    write_visual(page_id, vname, mk_pos(x, y, w, h, z, tab), visual_obj)
    return vname

def bar_v(page_id, name, x, y, w, h, cat_e, cat_c, val_e, val_c, title="", horizontal=False, z=10, tab=10):
    qs = {
        "Category": {"projections": [mk_proj(cat_e, cat_c)]},
        "Y": {"projections": [mk_proj(val_e, val_c, active=True)]}
    }
    vtype = "barChart" if horizontal else "columnChart"
    visual_obj = {
        "visualType": vtype,
        "query": {"queryState": qs},
        "objects": {
            "title": [{"properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                "fontColor": {"solid": {"color": CYAN}},
                "fontSize": {"expr": {"Literal": {"Value": "12D"}}}
            }}],
            "background": [{"properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "color": {"solid": {"color": CARD_BG}},
                "transparency": {"expr": {"Literal": {"Value": "0D"}}}
            }}],
            "dataPoint": [{"properties": {
                "defaultColor": {"solid": {"color": CYAN}}
            }}]
        },
        "drillFilterOtherVisuals": True
    }
    vname = vid(page_id, name)
    write_visual(page_id, vname, mk_pos(x, y, w, h, z, tab), visual_obj)
    return vname

def donut_v(page_id, name, x, y, w, h, cat_e, cat_c, val_e, val_c, title="", z=10, tab=10):
    qs = {
        "Category": {"projections": [mk_proj(cat_e, cat_c)]},
        "Y": {"projections": [mk_proj(val_e, val_c, active=True)]}
    }
    visual_obj = {
        "visualType": "donutChart",
        "query": {"queryState": qs},
        "objects": {
            "title": [{"properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                "fontColor": {"solid": {"color": CYAN}},
                "fontSize": {"expr": {"Literal": {"Value": "12D"}}}
            }}],
            "background": [{"properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "color": {"solid": {"color": CARD_BG}},
                "transparency": {"expr": {"Literal": {"Value": "0D"}}}
            }}]
        },
        "drillFilterOtherVisuals": True
    }
    vname = vid(page_id, name)
    write_visual(page_id, vname, mk_pos(x, y, w, h, z, tab), visual_obj)
    return vname

def combo_v(page_id, name, x, y, w, h, cat_e, cat_c, bar_e, bar_c, line_e, line_c, title="", z=10, tab=10):
    qs = {
        "Category": {"projections": [mk_proj(cat_e, cat_c)]},
        "Y": {"projections": [mk_proj(bar_e, bar_c, active=True)]},
        "Y2": {"projections": [mk_proj(line_e, line_c, active=True)]}
    }
    visual_obj = {
        "visualType": "lineClusteredColumnComboChart",
        "query": {"queryState": qs},
        "objects": {
            "title": [{"properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                "fontColor": {"solid": {"color": CYAN}},
                "fontSize": {"expr": {"Literal": {"Value": "12D"}}}
            }}],
            "background": [{"properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "color": {"solid": {"color": CARD_BG}},
                "transparency": {"expr": {"Literal": {"Value": "0D"}}}
            }}]
        },
        "drillFilterOtherVisuals": True
    }
    vname = vid(page_id, name)
    write_visual(page_id, vname, mk_pos(x, y, w, h, z, tab), visual_obj)
    return vname

# =============================================================================
# PAGE 1 — INDUSTRY OVERVIEW
# Note: Existing image visuals are at y=20-670 in 560x270 positions.
# We add KPI cards along the TOP (y=700+) — actually let's overlay a new row
# We'll place KPIs below the existing charts at y=20 (adding z=20 to be above)
# Layout: existing images take ~y=20..670, so we add row at y=700 which is out
# Better: add KPI cards as OVERLAY at top left (small, high z-order)
# =============================================================================

print("Adding native visuals to Page 1 — Industry Overview...")
kpi_card(P1, "kpi_aum", 20, 20, 155, 65, "03_aum_by_fund_house", "aum_lakh_crore",
         "Industry AUM (Lakh Cr)", z=20, tab=20)
kpi_card(P1, "kpi_sip", 185, 20, 155, 65, "04_monthly_sip_inflows", "sip_inflow_crore",
         "SIP Inflow (Cr)", z=20, tab=21)
kpi_card(P1, "kpi_folios", 350, 20, 155, 65, "06_industry_folio_count", "total_folios_crore",
         "Folios (Cr)", z=20, tab=22)
kpi_card(P1, "kpi_schemes", 515, 20, 155, 65, "01_fund_master", "Industry Schemes (AMFI)",
         "Total Schemes", z=20, tab=23)
print("  Added 4 KPI cards")

# =============================================================================
# PAGE 2 — FUND PERFORMANCE
# Add scatter chart, fund scorecard table, slicers
# Place below existing image at y=700 (scrollable) or overlay at y=20, high z
# =============================================================================

print("Adding native visuals to Page 2 — Fund Performance...")
# Slicers (small, top strip)
slicer_v(P2, "slicer_fundhouse",  20, 20, 190, 60, "01_fund_master", "fund_house", "Fund House", z=20, tab=20)
slicer_v(P2, "slicer_category",  220, 20, 190, 60, "01_fund_master", "category",   "Category",   z=20, tab=21)
slicer_v(P2, "slicer_plan",      420, 20, 190, 60, "07_scheme_performance", "plan", "Plan",       z=20, tab=22)

# Scatter chart — return vs risk
scatter_v(P2, "scatter_risk_return",
          640, 20, 600, 290,
          "07_scheme_performance", "scheme_name",
          "07_scheme_performance", "return_3yr_pct",
          "07_scheme_performance", "std_dev_ann_pct",
          size_e="07_scheme_performance", size_c="aum_crore",
          title="Return (3Yr %) vs Risk (Std Dev) — Bubble = AUM",
          z=20, tab=23)

# Fund scorecard table
table_v(P2, "table_scorecard",
        20, 90, 600, 280,
        [
            ("07_scheme_performance", "scheme_name"),
            ("07_scheme_performance", "category"),
            ("07_scheme_performance", "return_1yr_pct"),
            ("07_scheme_performance", "return_3yr_pct"),
            ("07_scheme_performance", "sharpe_ratio"),
            ("07_scheme_performance", "risk_grade"),
            ("07_scheme_performance", "aum_crore"),
        ],
        title="Fund Scorecard (click to drill through)", z=20, tab=24)
print("  Added scatter + table + 3 slicers")

# =============================================================================
# PAGE 3 — INVESTOR ANALYTICS
# Add slicers, donut, bar
# =============================================================================

print("Adding native visuals to Page 3 — Investor Analytics...")
slicer_v(P3, "slicer_state",     20, 20, 185, 60, "08_investor_transactions", "state",     "State",     z=20, tab=20)
slicer_v(P3, "slicer_agegroup", 215, 20, 185, 60, "08_investor_transactions", "age_group", "Age Group", z=20, tab=21)
slicer_v(P3, "slicer_citytier", 410, 20, 185, 60, "08_investor_transactions", "city_tier", "City Tier", z=20, tab=22)

# Donut: transaction type split
donut_v(P3, "donut_txn_type",
        640, 20, 280, 260,
        "08_investor_transactions", "transaction_type",
        "08_investor_transactions", "amount_inr",
        title="SIP / Lumpsum / Redemption Split", z=20, tab=23)

# Bar: top states
bar_v(P3, "bar_state_txn",
      940, 20, 300, 260,
      "08_investor_transactions", "state",
      "08_investor_transactions", "amount_inr",
      title="Txn Amount by State (Top)", horizontal=True, z=20, tab=24)
print("  Added 3 slicers + donut + bar")

# =============================================================================
# PAGE 4 — SIP & MARKET TRENDS
# Add combo chart and bar for top categories
# =============================================================================

print("Adding native visuals to Page 4 — SIP & Market Trends...")

# Combo chart: SIP inflow + Nifty 50
combo_v(P4, "combo_sip_nifty",
        640, 20, 600, 280,
        "04_monthly_sip_inflows", "month",
        "04_monthly_sip_inflows", "sip_inflow_crore",
        "10_benchmark_indices", "close_value",
        title="SIP Inflow (Bar) vs Nifty 50 (Line) 2022-2025", z=20, tab=20)

# Bar: top categories inflow
bar_v(P4, "bar_cat_inflow",
      20, 20, 600, 280,
      "05_category_inflows", "category",
      "05_category_inflows", "net_inflow_crore",
      title="Top Categories by Net Inflow FY25 (Cr)", horizontal=True, z=20, tab=21)
print("  Added combo chart + bar chart")

# =============================================================================
# PAGE 5 — NAV DETAIL (Drill-through)
# Add NAV line chart, metric cards
# =============================================================================

print("Adding native visuals to Page 5 — NAV Detail...")

# KPI cards for selected fund metrics
kpi_card(P5, "kpi_1yr",    20,  20, 190, 65, "07_scheme_performance", "Avg 1Yr Return (%)", "1-Yr Return (%)", z=20, tab=20)
kpi_card(P5, "kpi_3yr",   220,  20, 190, 65, "07_scheme_performance", "Avg 3Yr Return (%)", "3-Yr Return (%)", z=20, tab=21)
kpi_card(P5, "kpi_sharpe",420,  20, 190, 65, "07_scheme_performance", "Avg Sharpe Ratio",   "Sharpe Ratio",    z=20, tab=22)
kpi_card(P5, "kpi_stddev",620,  20, 190, 65, "07_scheme_performance", "Avg Std Dev (%)",    "Risk Std Dev (%)",z=20, tab=23)
kpi_card(P5, "kpi_alpha", 820,  20, 190, 65, "07_scheme_performance", "Avg Alpha (%)",      "Alpha (%)",       z=20, tab=24)

# NAV line chart
line_v(P5, "line_nav",
       20, 95, 1220, 300,
       "02_nav_history", "date",
       [("02_nav_history", "nav")],
       title="Daily NAV History (Selected Fund)", z=20, tab=25)

# Fund info table
table_v(P5, "table_fund_info",
        20, 405, 600, 250,
        [
            ("01_fund_master", "scheme_name"),
            ("01_fund_master", "fund_house"),
            ("01_fund_master", "category"),
            ("01_fund_master", "fund_manager"),
            ("01_fund_master", "benchmark"),
        ],
        title="Fund Information", z=20, tab=26)

# Risk metrics table
table_v(P5, "table_risk_metrics",
        640, 405, 600, 250,
        [
            ("07_scheme_performance", "scheme_name"),
            ("07_scheme_performance", "alpha"),
            ("07_scheme_performance", "beta"),
            ("07_scheme_performance", "sortino_ratio"),
            ("07_scheme_performance", "max_drawdown_pct"),
        ],
        title="Risk Metrics Detail", z=20, tab=27)
print("  Added 5 KPI cards + NAV line + 2 tables")

# =============================================================================
# Update page 2 to set drillthrough target on fund scorecard
# =============================================================================

p5_page_path = os.path.join(PAGES_DIR, P5, "page.json")
with open(p5_page_path, "r", encoding="utf-8") as f:
    p5_data = json.load(f)

# Add drillthrough configuration
p5_data["drillthrough"] = {
    "targets": [
        {
            "field": mk_field("07_scheme_performance", "scheme_name"),
            "queryRef": "07_scheme_performance.scheme_name"
        }
    ]
}
with open(p5_page_path, "w", encoding="utf-8") as f:
    json.dump(p5_data, f, indent=2, ensure_ascii=False)
print("\nDrill-through configured on NAV Detail page")

# =============================================================================
# Final count
# =============================================================================

print("\n=== FINAL VISUAL COUNT PER PAGE ===")
for pid, pname in [(P1,"Industry Overview"),(P2,"Fund Performance"),(P3,"Investor Analytics"),(P4,"SIP & Market Trends"),(P5,"NAV Detail")]:
    vdir = os.path.join(PAGES_DIR, pid, "visuals")
    count = len([d for d in os.listdir(vdir) if os.path.isdir(os.path.join(vdir, d))]) if os.path.exists(vdir) else 0
    print(f"  [{pid[:8]}...] {pname:25s}: {count} visuals")

print("\nDone! All native visuals added.")
