"""
build_pbi_report.py
Generates all Power BI report page JSON files for the Bluestock MF Dashboard.
Produces: 5 pages (Industry Overview, Fund Performance, Investor Analytics,
          SIP & Market Trends, NAV Detail drill-through)
Also creates: Bluestock theme JSON, updates pages.json, copies logo resource.
"""
import json
import os
import shutil
import uuid

# ─── Paths ────────────────────────────────────────────────────────────────────
REPORT_DIR = r"C:\Datatatatta\dashboard\Bluestock_MF_Dashboard.Report"
DEF_DIR = os.path.join(REPORT_DIR, "definition")
PAGES_DIR = os.path.join(DEF_DIR, "pages")
STATIC_RES = os.path.join(REPORT_DIR, "StaticResources", "RegisteredResources")
LOGO_SRC = r"C:\Datatatatta\logo.png"

os.makedirs(PAGES_DIR, exist_ok=True)
os.makedirs(STATIC_RES, exist_ok=True)

# ─── Bluestock Colour Palette ─────────────────────────────────────────────────
NAVY      = "#002A54"
CYAN      = "#00D2FF"
ORANGE    = "#FF6B35"
TEAL      = "#00B4A0"
LIME      = "#A8E063"
WHITE     = "#FFFFFF"
LIGHT_BG  = "#F0F4FA"
DARK_TEXT = "#1A1A2E"
MUTED     = "#8899AA"
CARD_BG   = "#0A3A6B"
GRID      = "#1A4070"

DATA_COLORS = [CYAN, ORANGE, TEAL, LIME, "#FFD166", "#EF476F", "#118AB2", "#06D6A0"]

# ─── Bluestock Theme JSON ─────────────────────────────────────────────────────
theme = {
    "name": "BluestockTheme",
    "dataColors": DATA_COLORS,
    "background": NAVY,
    "foreground": WHITE,
    "tableAccent": CYAN,
    "visualStyles": {
        "*": {
            "*": {
                "background": [{"color": {"solid": {"color": CARD_BG}}}],
                "fontColor": [{"color": {"solid": {"color": WHITE}}}],
                "titleFontColor": [{"color": {"solid": {"color": WHITE}}}]
            }
        },
        "card": {
            "*": {
                "calloutValue": [{"fontSize": 28, "fontFamily": "Segoe UI Semibold", "color": {"solid": {"color": CYAN}}}],
                "label": [{"fontSize": 11, "color": {"solid": {"color": WHITE}}, "fontFamily": "Segoe UI"}],
                "background": [{"color": {"solid": {"color": CARD_BG}}}]
            }
        },
        "lineChart": {
            "*": {
                "lineColor": [{"color": {"solid": {"color": CYAN}}}],
                "background": [{"color": {"solid": {"color": CARD_BG}}}]
            }
        },
        "barChart": {
            "*": {
                "dataColor": [{"color": {"solid": {"color": CYAN}}}],
                "background": [{"color": {"solid": {"color": CARD_BG}}}]
            }
        },
        "scatterChart": {
            "*": {
                "background": [{"color": {"solid": {"color": CARD_BG}}}]
            }
        },
        "donutChart": {
            "*": {
                "background": [{"color": {"solid": {"color": CARD_BG}}}]
            }
        },
        "tableEx": {
            "*": {
                "background": [{"color": {"solid": {"color": CARD_BG}}}],
                "fontColor": [{"color": {"solid": {"color": WHITE}}}]
            }
        },
        "slicer": {
            "*": {
                "background": [{"color": {"solid": {"color": CARD_BG}}}],
                "fontColor": [{"color": {"solid": {"color": WHITE}}}]
            }
        }
    },
    "textClasses": {
        "label": {"fontFace": "Segoe UI", "color": WHITE, "fontSize": 10},
        "callout": {"fontFace": "Segoe UI Semibold", "color": CYAN, "fontSize": 28},
        "title": {"fontFace": "Segoe UI Semibold", "color": WHITE, "fontSize": 13},
        "header": {"fontFace": "Segoe UI", "color": WHITE, "fontSize": 12}
    }
}

theme_path = os.path.join(STATIC_RES, "BluestockTheme.json")
with open(theme_path, "w", encoding="utf-8") as f:
    json.dump(theme, f, indent=2)
print(f"✓ Theme written: {theme_path}")

# Copy logo
logo_dst = os.path.join(STATIC_RES, "logo.png")
if os.path.exists(LOGO_SRC):
    shutil.copy2(LOGO_SRC, logo_dst)
    print(f"✓ Logo copied: {logo_dst}")
else:
    print(f"⚠ Logo not found at {LOGO_SRC}")

# ─── Update report.json to register custom theme ──────────────────────────────
report_json_path = os.path.join(DEF_DIR, "report.json")
with open(report_json_path, "r", encoding="utf-8") as f:
    rjson = json.load(f)

rjson["themeCollection"] = {
    "baseTheme": {
        "name": "CY26SU05",
        "reportVersionAtImport": {"visual": "2.9.0", "report": "3.3.0", "page": "2.3.1"},
        "type": "SharedResources"
    },
    "customTheme": {
        "name": "BluestockTheme",
        "type": "RegisteredResources"
    }
}

if "resourcePackages" not in rjson:
    rjson["resourcePackages"] = []

# add registered resources package if not present
has_registered = any(p.get("type") == "RegisteredResources" for p in rjson.get("resourcePackages", []))
if not has_registered:
    rjson["resourcePackages"].append({
        "name": "RegisteredResources",
        "type": "RegisteredResources",
        "items": [
            {"name": "BluestockTheme", "path": "BluestockTheme.json", "type": "CustomTheme"},
            {"name": "logo", "path": "logo.png", "type": "Image"}
        ]
    })

with open(report_json_path, "w", encoding="utf-8") as f:
    json.dump(rjson, f, indent=2)
print(f"✓ report.json updated with Bluestock theme")

# ─── Visual JSON helpers ──────────────────────────────────────────────────────

def uid():
    return str(uuid.uuid4())[:8].upper()

def make_config(visual_type: str, extra: dict = None) -> dict:
    cfg = {
        "version": "6.0.0",
        "themeCollection": {"baseTheme": {"name": "CY26SU05", "type": "SharedResources", "reportVersionAtImport": {"visual": "2.9.0", "report": "3.3.0", "page": "2.3.1"}}},
        "visualType": visual_type,
    }
    if extra:
        cfg.update(extra)
    return cfg

def visual_container(x, y, w, h, visual_type, config_extra=None, name=None):
    """Return a visualContainer dict for use in page visuals array."""
    vname = name or uid()
    return {
        "name": vname,
        "position": {"x": x, "y": y, "width": w, "height": h, "z": 0, "tabOrder": 0},
        "visualContainerObjects": {
            "visualContainer": [{
                "properties": {
                    "border": {"expr": {"Literal": {"Value": "false"}}},
                    "shadow": {"expr": {"Literal": {"Value": "false"}}},
                    "background": {"solid": {"color": CARD_BG}},
                    "visualContainerHeaderText": {"fontColor": {"solid": {"color": CYAN}}}
                }
            }]
        },
        "visual": {
            "visualType": visual_type,
            "query": {},
            "config": json.dumps(make_config(visual_type, config_extra))
        }
    }

# Full visual definitions use the newer v3 format that Power BI Desktop can parse
def v(x, y, w, h, visual_type, query_fields=None, title=None, tooltip=True, name=None):
    """Create a complete visual object."""
    vname = name or ("V_" + uid())
    
    config = {
        "version": "6.0.0",
        "themeCollection": {
            "baseTheme": {
                "name": "CY26SU05",
                "type": "SharedResources",
                "reportVersionAtImport": {"visual": "2.9.0", "report": "3.3.0", "page": "2.3.1"}
            }
        },
        "visualType": visual_type,
        "objects": {}
    }
    
    if title:
        config["objects"]["title"] = [{
            "properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                "fontColor": {"solid": {"color": CYAN}},
                "fontSize": {"expr": {"Literal": {"Value": "13D"}}},
                "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI Semibold'"}}},
                "background": {"solid": {"color": CARD_BG}},
                "alignment": {"expr": {"Literal": {"Value": "'left'"}}}
            }
        }]

    config["objects"]["background"] = [{
        "properties": {
            "show": {"expr": {"Literal": {"Value": "true"}}},
            "color": {"solid": {"color": CARD_BG}},
            "transparency": {"expr": {"Literal": {"Value": "0D"}}}
        }
    }]
    
    if tooltip:
        config["objects"]["tooltip"] = [{
            "properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}}
            }
        }]

    obj = {
        "name": vname,
        "position": {"x": x, "y": y, "width": w, "height": h, "z": 0, "tabOrder": 0},
        "visual": {
            "visualType": visual_type,
            "query": {"queryState": query_fields or {}},
            "config": json.dumps(config)
        }
    }
    return obj

def card(x, y, w, h, table, measure, title="", name=None):
    qf = {
        "Values": {
            "projections": [{
                "field": {"Column": {"Expression": {"SourceRef": {"Entity": table}}, "Property": measure}},
                "queryRef": f"{table}.{measure}"
            }]
        }
    }
    return v(x, y, w, h, "card", qf, title, name=name)

def line_chart(x, y, w, h, axis_table, axis_col, values, title="", name=None):
    """values: list of (table, column/measure)"""
    projs_y = [
        {
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": t}}, "Property": c}},
            "queryRef": f"{t}.{c}", "active": True
        }
        for t, c in values
    ]
    projs_x = [{
        "field": {"Column": {"Expression": {"SourceRef": {"Entity": axis_table}}, "Property": axis_col}},
        "queryRef": f"{axis_table}.{axis_col}"
    }]
    qf = {
        "Category": {"projections": projs_x},
        "Y": {"projections": projs_y}
    }
    return v(x, y, w, h, "lineChart", qf, title, name=name)

def bar_chart(x, y, w, h, cat_table, cat_col, val_table, val_col, title="", name=None, horizontal=False):
    qf = {
        "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": cat_table}}, "Property": cat_col}}, "queryRef": f"{cat_table}.{cat_col}"}]},
        "Y": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": val_table}}, "Property": val_col}}, "queryRef": f"{val_table}.{val_col}", "active": True}]}
    }
    vtype = "columnChart" if not horizontal else "barChart"
    return v(x, y, w, h, vtype, qf, title, name=name)

def scatter_chart(x, y, w, h, detail_table, detail_col, x_table, x_col, y_table, y_col, size_table=None, size_col=None, title="", name=None):
    qf = {
        "Details": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": detail_table}}, "Property": detail_col}}, "queryRef": f"{detail_table}.{detail_col}"}]},
        "X": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": x_table}}, "Property": x_col}}, "queryRef": f"{x_table}.{x_col}", "active": True}]},
        "Y": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": y_table}}, "Property": y_col}}, "queryRef": f"{y_table}.{y_col}", "active": True}]}
    }
    if size_table and size_col:
        qf["Size"] = {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": size_table}}, "Property": size_col}}, "queryRef": f"{size_table}.{size_col}", "active": True}]}
    return v(x, y, w, h, "scatterChart", qf, title, name=name)

def table_visual(x, y, w, h, columns, title="", name=None):
    """columns: list of (table, col)"""
    projs = [
        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": t}}, "Property": c}}, "queryRef": f"{t}.{c}"}
        for t, c in columns
    ]
    qf = {"Values": {"projections": projs}}
    return v(x, y, w, h, "tableEx", qf, title, name=name)

def slicer(x, y, w, h, table, col, title="", name=None):
    qf = {
        "Values": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": table}}, "Property": col}}, "queryRef": f"{table}.{col}"}]}
    }
    return v(x, y, w, h, "slicer", qf, title, name=name)

def donut_chart(x, y, w, h, cat_table, cat_col, val_table, val_col, title="", name=None):
    qf = {
        "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": cat_table}}, "Property": cat_col}}, "queryRef": f"{cat_table}.{cat_col}"}]},
        "Y": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": val_table}}, "Property": val_col}}, "queryRef": f"{val_table}.{val_col}", "active": True}]}
    }
    return v(x, y, w, h, "donutChart", qf, title, name=name)

def matrix_visual(x, y, w, h, rows_list, cols_list, values_list, title="", name=None):
    """rows_list/cols_list/values_list: each is list of (table, col)"""
    def proj(t, c):
        return {"field": {"Column": {"Expression": {"SourceRef": {"Entity": t}}, "Property": c}}, "queryRef": f"{t}.{c}"}
    qf = {
        "Rows": {"projections": [proj(t, c) for t, c in rows_list]},
        "Columns": {"projections": [proj(t, c) for t, c in cols_list]},
        "Values": {"projections": [proj(t, c) for t, c in values_list]}
    }
    return v(x, y, w, h, "matrix", qf, title, name=name)

def header_shape(page_title: str, page_subtitle: str = ""):
    """Full-width dark navy header bar with page title."""
    config = {
        "version": "6.0.0",
        "themeCollection": {"baseTheme": {"name": "CY26SU05", "type": "SharedResources", "reportVersionAtImport": {"visual": "2.9.0", "report": "3.3.0", "page": "2.3.1"}}},
        "visualType": "shape",
        "objects": {
            "line": [{"properties": {"roundEdge": {"expr": {"Literal": {"Value": "0D"}}}}}],
            "fill": [{"properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "fillColor": {"solid": {"color": NAVY}},
                "transparency": {"expr": {"Literal": {"Value": "0D"}}}
            }}]
        }
    }
    shape = {
        "name": "V_HEADER_SHAPE",
        "position": {"x": 0, "y": 0, "width": 1280, "height": 72, "z": -1, "tabOrder": 0},
        "visual": {
            "visualType": "shape",
            "query": {"queryState": {}},
            "config": json.dumps(config)
        }
    }
    
    # Title textbox
    title_cfg = {
        "version": "6.0.0",
        "themeCollection": {"baseTheme": {"name": "CY26SU05", "type": "SharedResources", "reportVersionAtImport": {"visual": "2.9.0", "report": "3.3.0", "page": "2.3.1"}}},
        "visualType": "textbox",
        "objects": {
            "general": [{"properties": {
                "paragraphs": [
                    {"textRuns": [{"value": page_title, "textRunStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "22px", "fontColor": {"solid": {"color": CYAN}}, "bold": True}}], "horizontalTextAlignment": "left"},
                    *([{"textRuns": [{"value": page_subtitle, "textRunStyle": {"fontFamily": "Segoe UI", "fontSize": "11px", "fontColor": {"solid": {"color": WHITE}}}}], "horizontalTextAlignment": "left"}] if page_subtitle else [])
                ]
            }}]
        }
    }
    title_box = {
        "name": "V_HEADER_TITLE",
        "position": {"x": 160, "y": 8, "width": 900, "height": 60, "z": 1, "tabOrder": 1},
        "visual": {
            "visualType": "textbox",
            "query": {"queryState": {}},
            "config": json.dumps(title_cfg)
        }
    }
    return [shape, title_box]


def write_page(page_id, display_name, visuals, order, page_bg=NAVY, drillthrough_fields=None, height=720, width=1280):
    """Write page.json into pages/<page_id>/page.json."""
    page_dir = os.path.join(PAGES_DIR, page_id)
    os.makedirs(page_dir, exist_ok=True)
    
    page_obj = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": page_id,
        "displayName": display_name,
        "displayOption": "FitToPage",
        "height": height,
        "width": width,
        "objects": {
            "section": [{
                "properties": {
                    "background": {"solid": {"color": NAVY}},
                    "backgroundTransparency": {"expr": {"Literal": {"Value": "0D"}}},
                    "verticalAlignment": {"expr": {"Literal": {"Value": "'Top'"}}}
                }
            }]
        },
        "ordinal": order,
        "visualContainers": visuals
    }
    
    if drillthrough_fields:
        page_obj["drillthrough"] = {
            "fields": drillthrough_fields
        }
    
    page_json_path = os.path.join(page_dir, "page.json")
    with open(page_json_path, "w", encoding="utf-8") as f:
        json.dump(page_obj, f, indent=2, ensure_ascii=False)
    print(f"✓ Page written: {display_name} → {page_json_path}")
    return page_id


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — INDUSTRY OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════

p1_id = "page_industry_overview"
p1_visuals = header_shape(
    "🏦 Industry Overview",
    "Indian Mutual Fund Industry — AUM, SIP & Folio Snapshot"
)

# Row 1: 4 KPI cards (y=90, h=120)
p1_visuals += [
    card( 20, 90, 290, 120, "03_aum_by_fund_house", "aum_lakh_crore",   "Total Industry AUM (₹ Lakh Cr)"),
    card(330, 90, 290, 120, "04_monthly_sip_inflows", "sip_inflow_crore", "Monthly SIP Inflows (₹ Cr)"),
    card(640, 90, 290, 120, "06_industry_folio_count", "total_folios_crore","Total Folios (Crore)"),
    card(950, 90, 310, 120, "01_fund_master", "Industry Schemes (AMFI)",   "Total Schemes"),
]

# Row 2: Line chart AUM trend (left 2/3) + Bar chart AUM by AMC (right 1/3)
p1_visuals += [
    line_chart( 20, 230, 820, 280,
        "03_aum_by_fund_house", "date",
        [("03_aum_by_fund_house", "aum_lakh_crore")],
        "Industry AUM Trend 2022–2025 (₹ Lakh Cr)"),
    bar_chart(860, 230, 400, 280,
        "03_aum_by_fund_house", "fund_house",
        "03_aum_by_fund_house", "aum_crore",
        "AUM by AMC (₹ Crore)", horizontal=True),
]

# Row 3: SIP inflow trend + Folio trend
p1_visuals += [
    line_chart( 20, 530, 400, 170,
        "04_monthly_sip_inflows", "month",
        [("04_monthly_sip_inflows", "sip_inflow_crore")],
        "Monthly SIP Inflow Trend"),
    line_chart(440, 530, 400, 170,
        "06_industry_folio_count", "month",
        [("06_industry_folio_count", "total_folios_crore")],
        "Total Folios Trend"),
    slicer(860, 530, 400, 170,
        "dim_date", "Year",
        "Filter by Year"),
]

write_page(p1_id, "Industry Overview", p1_visuals, 0)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — FUND PERFORMANCE
# ═══════════════════════════════════════════════════════════════════════════════

p2_id = "page_fund_performance"
p2_visuals = header_shape(
    "📈 Fund Performance",
    "Return vs Risk Analysis, Scorecard & NAV Benchmarking"
)

# Slicers — top right area
p2_visuals += [
    slicer(860, 82, 130, 120, "01_fund_master", "fund_house", "Fund House"),
    slicer(1000, 82, 130, 120, "01_fund_master", "category",  "Category"),
    slicer(1140, 82, 130, 120, "07_scheme_performance", "plan", "Plan"),
]

# Scatter chart — Return vs Risk
p2_visuals.append(
    scatter_chart(20, 82, 820, 280,
        "07_scheme_performance", "scheme_name",
        "07_scheme_performance", "return_3yr_pct",
        "07_scheme_performance", "std_dev_ann_pct",
        size_table="07_scheme_performance", size_col="aum_crore",
        title="Return (3Yr %) vs Risk (Std Dev) — Bubble Size = AUM")
)

# Fund scorecard table
p2_visuals.append(
    table_visual(20, 380, 820, 320,
        [
            ("07_scheme_performance", "scheme_name"),
            ("07_scheme_performance", "category"),
            ("07_scheme_performance", "return_1yr_pct"),
            ("07_scheme_performance", "return_3yr_pct"),
            ("07_scheme_performance", "return_5yr_pct"),
            ("07_scheme_performance", "sharpe_ratio"),
            ("07_scheme_performance", "std_dev_ann_pct"),
            ("07_scheme_performance", "risk_grade"),
            ("07_scheme_performance", "aum_crore"),
            ("07_scheme_performance", "morningstar_rating"),
        ],
        title="Fund Scorecard (Drill-through → NAV Detail)")
)

# NAV line chart vs benchmark
p2_visuals.append(
    line_chart(860, 220, 400, 480,
        "02_nav_history", "date",
        [
            ("02_nav_history", "nav"),
            ("07_scheme_performance", "benchmark_3yr_pct"),
        ],
        title="NAV vs Benchmark (3Yr %)")
)

write_page(p2_id, "Fund Performance", p2_visuals, 1)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — INVESTOR ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════

p3_id = "page_investor_analytics"
p3_visuals = header_shape(
    "👥 Investor Analytics",
    "Transaction Patterns by State, Type, Age Group & Channel"
)

# Slicers
p3_visuals += [
    slicer( 20, 82, 200, 80, "08_investor_transactions", "state",     "State"),
    slicer(240, 82, 200, 80, "08_investor_transactions", "age_group", "Age Group"),
    slicer(460, 82, 200, 80, "08_investor_transactions", "city_tier", "City Tier"),
]

# Bar chart: Txn amount by state
p3_visuals.append(
    bar_chart(20, 180, 620, 260,
        "08_investor_transactions", "state",
        "08_investor_transactions", "amount_inr",
        "Transaction Amount by State (₹)", horizontal=True)
)

# Donut: SIP/Lumpsum/Redemption split
p3_visuals.append(
    donut_chart(660, 180, 600, 260,
        "08_investor_transactions", "transaction_type",
        "08_investor_transactions", "amount_inr",
        "Transaction Split: SIP / Lumpsum / Redemption")
)

# Bar: Age group vs avg amount
p3_visuals.append(
    bar_chart(20, 460, 590, 240,
        "08_investor_transactions", "age_group",
        "08_investor_transactions", "amount_inr",
        "Age Group vs Avg Transaction Amount (₹)")
)

# Line: Monthly transaction volume
p3_visuals.append(
    line_chart(630, 460, 630, 240,
        "08_investor_transactions", "transaction_date",
        [("08_investor_transactions", "amount_inr")],
        "Monthly Transaction Volume (₹)")
)

write_page(p3_id, "Investor Analytics", p3_visuals, 2)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — SIP & MARKET TRENDS
# ═══════════════════════════════════════════════════════════════════════════════

p4_id = "page_sip_market_trends"
p4_visuals = header_shape(
    "📊 SIP & Market Trends",
    "SIP Inflows vs Nifty 50 · Category Heatmap · FY25 Leaders"
)

# Dual-axis combo: SIP bar + Nifty 50 line (use lineClusteredColumnComboChart)
p4_visuals.append({
    "name": "V_SIP_NIFTY_COMBO",
    "position": {"x": 20, "y": 82, "width": 820, "height": 290, "z": 0, "tabOrder": 0},
    "visual": {
        "visualType": "lineClusteredColumnComboChart",
        "query": {
            "queryState": {
                "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "04_monthly_sip_inflows"}}, "Property": "month"}}, "queryRef": "04_monthly_sip_inflows.month"}]},
                "Y": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "04_monthly_sip_inflows"}}, "Property": "sip_inflow_crore"}}, "queryRef": "04_monthly_sip_inflows.sip_inflow_crore", "active": True}]},
                "Y2": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "10_benchmark_indices"}}, "Property": "index_value"}}, "queryRef": "10_benchmark_indices.index_value", "active": True}]}
            }
        },
        "config": json.dumps({
            "version": "6.0.0",
            "themeCollection": {"baseTheme": {"name": "CY26SU05", "type": "SharedResources", "reportVersionAtImport": {"visual": "2.9.0", "report": "3.3.0", "page": "2.3.1"}}},
            "visualType": "lineClusteredColumnComboChart",
            "objects": {
                "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": {"expr": {"Literal": {"Value": "'SIP Inflow (₹ Cr, Bar) vs Nifty 50 (Line) 2022–2025'"}}}, "fontColor": {"solid": {"color": CYAN}}}}],
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": CARD_BG}}, "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
                "tooltip": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]
            }
        })
    }
})

# Category inflow heatmap (matrix)
p4_visuals.append(
    matrix_visual(20, 392, 820, 308,
        [("05_category_inflows", "category")],
        [("05_category_inflows", "month")],
        [("05_category_inflows", "net_inflow_crore")],
        "Category Net Inflow Heatmap (₹ Crore)")
)

# Top 5 categories FY25 (bar chart on right)
p4_visuals.append(
    bar_chart(860, 82, 400, 280,
        "05_category_inflows", "category",
        "05_category_inflows", "net_inflow_crore",
        "Top Categories by Net Inflow FY25 (₹ Cr)", horizontal=True)
)

# SIP accounts trend
p4_visuals.append(
    line_chart(860, 382, 400, 180,
        "04_monthly_sip_inflows", "month",
        [("04_monthly_sip_inflows", "active_sip_accounts_crore")],
        "Active SIP Accounts (Crore)")
)

# YoY growth card
p4_visuals.append(
    card(860, 582, 400, 118,
        "04_monthly_sip_inflows", "SIP YoY Growth (%)",
        "SIP YoY Growth (Latest Month)")
)

write_page(p4_id, "SIP & Market Trends", p4_visuals, 3)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — NAV DETAIL (Drill-through)
# ═══════════════════════════════════════════════════════════════════════════════

p5_id = "page_nav_detail"
p5_visuals = header_shape(
    "🔍 NAV Detail",
    "Drill-through Fund View — Daily NAV History & Key Metrics"
)

# KPI cards for selected fund
p5_visuals += [
    card( 20, 90, 240, 100, "07_scheme_performance", "Avg 1Yr Return (%)",  "1-Year Return (%)"),
    card(280, 90, 240, 100, "07_scheme_performance", "Avg 3Yr Return (%)",  "3-Year Return (%)"),
    card(540, 90, 240, 100, "07_scheme_performance", "Avg Sharpe Ratio",    "Sharpe Ratio"),
    card(800, 90, 240, 100, "07_scheme_performance", "Avg Std Dev (%)",     "Risk / Std Dev (%)"),
    card(1060, 90, 200, 100, "07_scheme_performance", "Avg Alpha (%)",      "Alpha (%)"),
]

# NAV history line chart — large
p5_visuals.append(
    line_chart(20, 210, 1240, 340,
        "02_nav_history", "date",
        [("02_nav_history", "nav")],
        "Daily NAV History (₹)")
)

# Fund info table
p5_visuals.append(
    table_visual(20, 570, 600, 130,
        [
            ("01_fund_master", "scheme_name"),
            ("01_fund_master", "fund_house"),
            ("01_fund_master", "category"),
            ("01_fund_master", "benchmark"),
            ("01_fund_master", "fund_manager"),
        ],
        title="Fund Information")
)

# Alpha/Beta/Sortino scorecard
p5_visuals.append(
    table_visual(640, 570, 620, 130,
        [
            ("07_scheme_performance", "scheme_name"),
            ("07_scheme_performance", "alpha"),
            ("07_scheme_performance", "beta"),
            ("07_scheme_performance", "sortino_ratio"),
            ("07_scheme_performance", "max_drawdown_pct"),
            ("07_scheme_performance", "expense_ratio_pct"),
        ],
        title="Risk Metrics Detail")
)

# Drill-through field definition
drillthrough = [
    {
        "field": {
            "Column": {
                "Expression": {"SourceRef": {"Entity": "07_scheme_performance"}},
                "Property": "scheme_name"
            }
        },
        "queryRef": "07_scheme_performance.scheme_name"
    }
]

write_page(p5_id, "NAV Detail", p5_visuals, 4, drillthrough_fields=drillthrough)


# ─── Update pages.json ────────────────────────────────────────────────────────

pages_json_path = os.path.join(DEF_DIR, "pages", "pages.json")
pages_index = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pages/1.0.0/schema.json",
    "pageOrder": [
        p1_id,
        p2_id,
        p3_id,
        p4_id,
        p5_id
    ]
}
with open(pages_json_path, "w", encoding="utf-8") as f:
    json.dump(pages_index, f, indent=2)
print(f"✓ pages.json updated with 5 pages")


# ─── Validate JSON syntax ─────────────────────────────────────────────────────

errors = []
for root, dirs, files in os.walk(PAGES_DIR):
    for fname in files:
        if fname.endswith(".json"):
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, encoding="utf-8") as f:
                    data = json.load(f)
                # validate nested config strings too
                for vc in data.get("visualContainers", []):
                    cfg_str = vc.get("visual", {}).get("config", "")
                    if cfg_str:
                        json.loads(cfg_str)
            except Exception as e:
                errors.append(f"  ❌ {fpath}: {e}")

if errors:
    print("\n⚠ JSON validation errors:")
    for e in errors:
        print(e)
else:
    print(f"\n✅ All JSON files validated successfully")

# ─── Copy .pbix to target path ────────────────────────────────────────────────
src_pbix = r"C:\Datatatatta\dashboard\Bluestock_MF_Dashboard.pbix"
dst_pbix = r"C:\Users\fredd\Downloads\mfcap.pbix"
if os.path.exists(src_pbix):
    shutil.copy2(src_pbix, dst_pbix)
    print(f"✓ PBIX copied: {dst_pbix}")

print("\n🚀 Build complete! Open Bluestock_MF_Dashboard.pbip in Power BI Desktop to view all 5 pages.")
