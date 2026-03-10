"""
WaveIQ — Car Wash Customer Intelligence Platform
Architected by Gopi Chand

Run:
    pip install streamlit pandas plotly
    streamlit run waveiq_app.py
"""

import re
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WaveIQ — Car Wash Intelligence",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'Outfit', sans-serif; background: #0C0D0F; color: #E0E0D8; }
.stApp { background: #0C0D0F; }

section[data-testid="stSidebar"] { background: #0F1114 !important; border-right: 1px solid rgba(255,200,60,0.1); }
section[data-testid="stSidebar"] label { color: #ccc !important; font-family: 'JetBrains Mono', monospace !important; font-size: 10px !important; letter-spacing: 2px !important; text-transform: uppercase; }
section[data-testid="stSidebar"] p { color: #ccc !important; }

.stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid rgba(255,255,255,0.07) !important; gap: 4px; }
.stTabs [data-baseweb="tab"] { font-family: 'Outfit', sans-serif !important; font-weight: 600 !important; font-size: 11px !important; letter-spacing: 2px !important; text-transform: uppercase !important; color: #999 !important; background: transparent !important; border: none !important; padding: 10px 18px !important; }
.stTabs [aria-selected="true"] { color: #FFC83C !important; border-bottom: 2px solid #FFC83C !important; }

[data-testid="metric-container"] { background: rgba(255,255,255,0.025) !important; border: 1px solid rgba(255,255,255,0.06) !important; border-top: 2px solid #FFC83C !important; border-radius: 12px !important; padding: 18px 20px !important; }
[data-testid="stMetricLabel"] p { font-family: 'JetBrains Mono', monospace !important; font-size: 9px !important; letter-spacing: 3px !important; text-transform: uppercase !important; color: #ccc !important; }
[data-testid="stMetricValue"] { font-family: 'Bebas Neue', sans-serif !important; font-size: 34px !important; letter-spacing: 2px !important; color: #FFC83C !important; }
[data-testid="stMetricDelta"] { font-family: 'JetBrains Mono', monospace !important; font-size: 10px !important; }

.stDataFrame { border: 1px solid rgba(255,255,255,0.06) !important; border-radius: 10px !important; }
[data-testid="stFileUploader"] { background: rgba(255,200,60,0.02) !important; border: 2px dashed rgba(255,200,60,0.25) !important; border-radius: 14px !important; }

.stButton > button { background: rgba(255,200,60,0.08) !important; border: 1px solid rgba(255,200,60,0.3) !important; color: #FFC83C !important; font-family: 'JetBrains Mono', monospace !important; font-size: 10px !important; letter-spacing: 2px !important; text-transform: uppercase !important; border-radius: 8px !important; }
.stButton > button:hover { background: rgba(255,200,60,0.18) !important; }

.stSelectbox > div > div { background: rgba(255,255,255,0.03) !important; border-color: rgba(255,255,255,0.1) !important; color: #ccc !important; }
.stSlider [data-baseweb="slider"] div[role="slider"] { background: #FFC83C !important; }
.stTextInput input { background: rgba(255,255,255,0.03) !important; border-color: rgba(255,255,255,0.1) !important; color: #ccc !important; font-family: 'JetBrains Mono', monospace !important; font-size: 12px !important; }

div[data-testid="stExpander"] { background: rgba(255,255,255,0.02) !important; border: 1px solid rgba(255,255,255,0.06) !important; border-radius: 10px !important; }

#MainMenu, footer, header { visibility: hidden; }
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-thumb { background: rgba(255,200,60,0.25); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
AMBER = "#FFC83C"
BG    = "#0C0D0F"
GRID  = "rgba(255,255,255,0.04)"
MONO  = "JetBrains Mono"

SEG_COLORS = {
    "High Frequency Members": "#FFC83C",
    "Churn Risk Members":     "#FF5A5A",
    "Premium Buyers":         "#A78BFA",
    "Weekend Washers":        "#34D399",
    "Price Sensitive":        "#60A5FA",
    "First Time Visitors":    "#FB923C",
}
SEG_ICONS = {
    "High Frequency Members": "⚡",
    "Churn Risk Members":     "⚠️",
    "Premium Buyers":         "💎",
    "Weekend Washers":        "☀️",
    "Price Sensitive":        "🏷️",
    "First Time Visitors":    "👋",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor=BG, plot_bgcolor=BG,
    font=dict(family=MONO, color="#ccc", size=11),
)

# ── Helper: card HTML ─────────────────────────────────────────────────────────
def card(content: str, border_color: str = AMBER, padding: str = "20px 24px") -> str:
    return f"""
    <div style="background:rgba(255,255,255,0.025); border:1px solid rgba(255,255,255,0.06);
         border-top:2px solid {border_color}; border-radius:12px; padding:{padding}; margin-bottom:8px">
        {content}
    </div>"""

def insight_box(text: str, icon: str = "💡") -> str:
    return f"""
    <div style="background:rgba(255,200,60,0.06); border:1px solid rgba(255,200,60,0.15);
         border-left:3px solid {AMBER}; border-radius:8px; padding:14px 18px; margin:10px 0">
        <span style="font-size:14px">{icon}</span>
        <span style="font-family:'Outfit',sans-serif; font-size:13px; color:#ddd;
              line-height:1.7; margin-left:8px">{text}</span>
    </div>"""

def action_box(text: str) -> str:
    return f"""
    <div style="background:rgba(167,139,250,0.06); border-left:3px solid #A78BFA;
         border-radius:6px; padding:10px 16px; margin:6px 0; font-family:'Outfit',sans-serif;
         font-size:13px; color:#ccc">→ {text}</div>"""

def section_header(label: str, title: str) -> None:
    st.markdown(f"""
    <div style="margin:36px 0 20px">
        <div style="font-family:'{MONO}',monospace; font-size:9px; color:#ccc;
             letter-spacing:4px; text-transform:uppercase; margin-bottom:6px">{label}</div>
        <div style="font-family:'Bebas Neue',sans-serif; font-size:26px;
             letter-spacing:2px; color:#E0E0D8">{title}</div>
    </div>""", unsafe_allow_html=True)

# ── Data Processing ───────────────────────────────────────────────────────────

def clean_plate(p: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(p).upper().strip())

def load_and_process(file, premium_kw, basic_kw, churn_days, hf_vpw, wknd_thresh) -> dict:
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip().str.replace('"', '').str.lower()

    # Column mapping flexibility
    col_map = {
        "time": ["time", "date", "transaction_date", "datetime", "date_time"],
        "licensePlate": ["licenseplate", "plate", "license_plate", "lp"],
        "package": ["package", "wash_package", "package_name", "service"],
        "total": ["total", "price", "price_paid", "amount", "total_val"],
        "type": ["type", "wash_type", "transaction_type", "membership_flag"],
        "location": ["location", "site", "store"],
    }
    rename = {}
    for canonical, aliases in col_map.items():
        for alias in aliases:
            if alias in df.columns and canonical not in df.columns:
                rename[alias] = canonical
                break
    df = df.rename(columns=rename)

    # Parse
    df["time"] = pd.to_datetime(df["time"], infer_datetime_format=True, errors="coerce")
    df["total_val"] = (
        df.get("total", pd.Series(dtype=str)).astype(str)
        .str.replace(r"[$,]", "", regex=True).str.strip()
        .pipe(pd.to_numeric, errors="coerce").fillna(0)
    )
    df["plate_clean"] = df["licensePlate"].apply(clean_plate)
    df = df[df["plate_clean"].str.len() > 0]
    df = df[df["time"].notna()]

    # Wash types
    member_types = ["member wash", "member"]
    retail_types = ["single wash", "retail", "single", "cash"]
    df["is_member_tx"] = df["type"].str.lower().str.strip().isin(member_types)
    df["is_retail_tx"] = df["type"].str.lower().str.strip().isin(retail_types)
    df["is_billing"]   = df["type"].str.lower().str.strip().str.contains("billing", na=False)

    wash_df = df[df["is_member_tx"] | df["is_retail_tx"]].copy()

    # Package tier by price rank
    pkg_avg = wash_df[wash_df["total_val"] > 0].groupby("package")["total_val"].mean().sort_values()
    n = len(pkg_avg)
    tier_map = {}
    for i, pkg in enumerate(pkg_avg.index):
        if   i < n * 0.34: tier_map[pkg] = "Tier 1 (Basic)"
        elif i < n * 0.67: tier_map[pkg] = "Tier 2 (Mid)"
        else:               tier_map[pkg] = "Tier 3 (Premium)"
    # Override with keywords if provided
    for pkg in wash_df["package"].dropna().unique():
        if any(k.lower() in str(pkg).lower() for k in premium_kw):
            tier_map[pkg] = "Tier 3 (Premium)"
        elif any(k.lower() in str(pkg).lower() for k in basic_kw):
            tier_map[pkg] = "Tier 1 (Basic)"
    wash_df["tier"] = wash_df["package"].map(tier_map).fillna("Tier 2 (Mid)")

    # Dates
    now   = wash_df["time"].max()
    start = wash_df["time"].min()
    period_days = max((now - start).days, 1)
    period_months = max(period_days / 30, 1)

    # Customer profiles
    grp = wash_df.groupby("plate_clean")
    profiles = pd.DataFrame({
        "total_visits":    grp.size(),
        "member_visits":   grp["is_member_tx"].sum(),
        "retail_visits":   grp["is_retail_tx"].sum(),
        "last_visit":      grp["time"].max(),
        "first_visit":     grp["time"].min(),
        "avg_spend":       grp["total_val"].mean().round(2),
        "total_spend":     grp["total_val"].sum().round(2),
        "packages":        grp["package"].apply(lambda x: " | ".join(sorted(set(x.dropna())))),
        "weekend_visits":  grp["time"].apply(lambda x: x.dt.dayofweek.isin([5, 6]).sum()),
        "premium_visits":  grp.apply(lambda g: (g["tier"] == "Tier 3 (Premium)").sum()),
        "basic_visits":    grp.apply(lambda g: (g["tier"] == "Tier 1 (Basic)").sum()),
    }).reset_index()

    profiles["days_since"]       = (now - profiles["last_visit"]).dt.days.astype(int)
    profiles["is_member"]        = profiles["member_visits"] > 0
    profiles["weekend_ratio"]    = (profiles["weekend_visits"] / profiles["total_visits"]).round(4)
    profiles["premium_ratio"]    = (profiles["premium_visits"] / profiles["total_visits"]).round(4)
    profiles["basic_ratio"]      = (profiles["basic_visits"] / profiles["total_visits"]).round(4)
    profiles["visits_per_month"] = (profiles["total_visits"] / period_months).round(2)
    profiles["visits_per_week"]  = (profiles["total_visits"] / (period_days / 7)).round(4)
    profiles["is_first_time"]    = profiles["total_visits"] == 1

    # Segmentation
    def classify(r):
        if r["is_member"] and r["visits_per_month"] >= hf_vpw:
            return "High Frequency Members"
        elif r["is_member"] and r["days_since"] >= churn_days:
            return "Churn Risk Members"
        elif r["premium_ratio"] >= 0.70:
            return "Premium Buyers"
        elif r["is_first_time"]:
            return "First Time Visitors"
        elif r["basic_ratio"] >= 0.80:
            return "Price Sensitive"
        elif r["weekend_ratio"] >= wknd_thresh:
            return "Weekend Washers"
        else:
            return "Price Sensitive"

    profiles["segment"] = profiles.apply(classify, axis=1)

    # Churn risk tiers
    def churn_level(r):
        if not r["is_member"]: return None
        if r["days_since"] >= churn_days:          return "High Risk"
        elif r["days_since"] >= churn_days * 0.7:  return "Medium Risk"
        else:                                       return "Low Risk"
    profiles["churn_level"] = profiles.apply(churn_level, axis=1)

    # Time patterns
    wash_df["day_name"]  = wash_df["time"].dt.day_name()
    wash_df["hour"]      = wash_df["time"].dt.hour

    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    day_dist  = wash_df["day_name"].value_counts().reindex(day_order, fill_value=0).reset_index()
    day_dist.columns = ["Day", "Visits"]
    day_dist["Pct"] = (day_dist["Visits"] / day_dist["Visits"].sum() * 100).round(1)

    # Package performance
    pkg_perf = wash_df.groupby("package").agg(
        transactions=("plate_clean", "count"),
        revenue=("total_val", "sum"),
        tier=("tier", "first"),
    ).reset_index().sort_values("transactions", ascending=False)
    pkg_perf["share_pct"] = (pkg_perf["transactions"] / pkg_perf["transactions"].sum() * 100).round(1)

    # Revenue by segment
    rev_seg = profiles.groupby("is_member")["total_spend"].sum().reset_index()
    rev_seg["label"] = rev_seg["is_member"].map({True: "Members", False: "Retail"})

    # Member visit freq distribution
    mem_profiles = profiles[profiles["is_member"]].copy()
    mem_profiles["freq_bucket"] = pd.cut(
        mem_profiles["visits_per_month"],
        bins=[0, 1, 2, 3, 999],
        labels=["1 visit/mo", "2 visits/mo", "3 visits/mo", "4+ visits/mo"],
    )
    mem_freq = mem_profiles["freq_bucket"].value_counts().sort_index().reset_index()
    mem_freq.columns = ["Frequency", "Members"]

    return {
        "wash_df":    wash_df,
        "profiles":   profiles,
        "tier_map":   tier_map,
        "pkg_perf":   pkg_perf,
        "day_dist":   day_dist,
        "rev_seg":    rev_seg,
        "mem_freq":   mem_freq,
        "now":        now,
        "period_days": period_days,
        "period_months": period_months,
    }

# ── Chart helpers ─────────────────────────────────────────────────────────────

def fig_base(fig):
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

def donut(labels, values, colors, center_text=""):
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.62,
        marker=dict(colors=colors, line=dict(color=BG, width=3)),
        textinfo="percent", textfont=dict(size=11, color="#0C0D0F"),
        hovertemplate="<b>%{label}</b><br>%{value:,}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=300, showlegend=True,
        legend=dict(font=dict(size=10, color="#ccc"), bgcolor="rgba(0,0,0,0)", x=1.02, y=0.5),
        margin=dict(l=0, r=130, t=10, b=10),
        annotations=[dict(text=center_text, x=0.5, y=0.5, showarrow=False,
            font=dict(size=13, color=AMBER, family="Bebas Neue"))],
    )
    return fig

def hbar(df, x_col, y_col, color_col=None, colors=None, title="", height=260):
    if colors and color_col:
        color_vals = df[color_col].map(colors) if isinstance(colors, dict) else colors
    else:
        color_vals = AMBER
    fig = go.Figure(go.Bar(
        x=df[x_col], y=df[y_col], orientation="h",
        marker=dict(color=color_vals, opacity=0.85, line=dict(width=0)),
        text=df[x_col].round(1) if df[x_col].dtype in ["float64", "float32"] else df[x_col],
        textposition="outside", textfont=dict(size=10, color="#ccc"),
        hovertemplate=f"<b>%{{y}}</b><br>{x_col}: %{{x}}<extra></extra>",
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=height, showlegend=False,
        xaxis=dict(gridcolor=GRID, zeroline=False, tickfont=dict(color="#bbb")),
        yaxis=dict(showgrid=False, tickfont=dict(color="#bbb", size=10)),
        margin=dict(l=0, r=50, t=28, b=10), title=dict(text=title, font=dict(color="#aaa", size=11), x=0),
    )
    return fig

def vbar(df, x_col, y_col, color=AMBER, title="", height=260):
    fig = go.Figure(go.Bar(
        x=df[x_col], y=df[y_col],
        marker=dict(color=color, opacity=0.8, line=dict(width=0)),
        text=df[y_col], textposition="outside",
        textfont=dict(size=10, color="#ccc"),
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=height, showlegend=False,
        xaxis=dict(showgrid=False, tickfont=dict(color="#bbb", size=10)),
        yaxis=dict(gridcolor=GRID, zeroline=False, tickfont=dict(color="#bbb")),
        margin=dict(l=10, r=10, t=28, b=10), title=dict(text=title, font=dict(color="#aaa", size=11)),
    )
    return fig

# ── SIDEBAR ───────────────────────────────────────────────────────────────────

def sidebar():
    st.sidebar.markdown(f"""
    <div style="font-family:'Bebas Neue',sans-serif; font-size:28px; letter-spacing:5px; color:{AMBER}; margin-bottom:2px">WAVEIQ</div>
    <div style="font-family:'{MONO}',monospace; font-size:8px; color:#ddd; letter-spacing:3px; margin-bottom:24px">CAR WASH INTELLIGENCE</div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("**Segment Thresholds**")
    hf_vpw     = st.sidebar.slider("High Freq — min visits/month", 1, 6, 3)
    churn_days = st.sidebar.slider("Churn — inactive days",        14, 60, 30)
    wknd       = st.sidebar.slider("Weekend ratio threshold %",    40, 85, 60) / 100

    st.sidebar.markdown("**Package Keywords**")
    prem_raw = st.sidebar.text_input("Premium keywords", "VIP, Graphene, Rockstar, Ceramic, Ultimate")
    basic_raw= st.sidebar.text_input("Basic keywords",   "Bassline, Basic, Bronze, Economy")
    prem_kw  = [k.strip() for k in prem_raw.split(",") if k.strip()]
    basic_kw = [k.strip() for k in basic_raw.split(",") if k.strip()]

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    <div style="font-family:'{MONO}',monospace; font-size:8px; color:#ccc; line-height:2">
        Architected by<br>
        <span style="color:#ddd; font-size:10px">Gopi Chand</span>
    </div>""", unsafe_allow_html=True)

    return hf_vpw, churn_days, wknd, prem_kw, basic_kw

# ── UPLOAD SCREEN ─────────────────────────────────────────────────────────────

def upload_screen():
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:flex-start;
         border-bottom:1px solid rgba(255,200,60,0.1); padding-bottom:24px; margin-bottom:40px">
        <div>
            <div style="font-family:'Bebas Neue',sans-serif; font-size:52px; letter-spacing:6px; color:{AMBER}; line-height:1">WAVEIQ</div>
            <div style="font-family:'{MONO}',monospace; font-size:9px; color:#ccc; letter-spacing:5px; margin-top:4px">CAR WASH CUSTOMER INTELLIGENCE PLATFORM</div>
        </div>
        <div style="text-align:right; padding-top:10px">
            <div style="font-family:'{MONO}',monospace; font-size:8px; color:#ddd; letter-spacing:2px">Architected by</div>
            <div style="font-family:'Outfit',sans-serif; font-size:15px; font-weight:600; color:#bbb">Gopi Chand</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_r = st.columns([1.15, 1], gap="large")

    with col_l:
        st.markdown(f"""
        <div style="font-family:'{MONO}',monospace; font-size:9px; color:{AMBER}; letter-spacing:4px; margin-bottom:14px">● CUSTOMER SEGMENTATION PLATFORM</div>
        <div style="font-family:'Bebas Neue',sans-serif; font-size:58px; letter-spacing:2px; line-height:0.92; color:#F0F0E8; margin-bottom:22px">
            KNOW YOUR<br><span style="color:{AMBER}">CUSTOMERS.</span><br>GROW YOUR<br>REVENUE.
        </div>
        <p style="font-size:14px; color:#ddd; line-height:1.85; font-weight:300; max-width:420px; margin-bottom:30px">
            WaveIQ turns your raw POS export into a complete behavioral intelligence report —
            membership health, churn risk, segment breakdowns, revenue patterns, and operator insights —
            all in one screen. No spreadsheets. No data science team.
        </p>
        """, unsafe_allow_html=True)

        s1, s2, s3, s4 = st.columns(4)
        for col, val, lbl in [(s1,"13","Analytics Modules"),(s2,"6","Segments"),(s3,"100%","POS-Agnostic"),(s4,"0","Code Needed")]:
            col.markdown(f"""
            <div>
                <div style="font-family:'Bebas Neue',sans-serif; font-size:28px; color:{AMBER}; letter-spacing:2px; line-height:1">{val}</div>
                <div style="font-family:'{MONO}',monospace; font-size:7px; color:#ccc; letter-spacing:2px; text-transform:uppercase; margin-top:3px; line-height:1.5">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    with col_r:
        st.markdown(f"""
        <div style="background:rgba(255,200,60,0.02); border:2px dashed rgba(255,200,60,0.2);
             border-radius:16px; padding:28px 24px 12px; margin-top:6px">
            <div style="font-family:'Bebas Neue',sans-serif; font-size:20px; letter-spacing:3px; color:#D0D0C8; margin-bottom:6px">UPLOAD YOUR CSV REPORT</div>
            <div style="font-family:'{MONO}',monospace; font-size:9px; color:#ccc; line-height:2; margin-bottom:14px">
                Drag & drop or click below · Any POS export works<br>
                DRB · PDQ · Washify · Sonny's · WashConnect · Custom
            </div>
        </div>
        """, unsafe_allow_html=True)

        uploaded = st.file_uploader("", type=["csv"], label_visibility="collapsed")

        st.markdown(f"""
        <div style="font-family:'{MONO}',monospace; font-size:8px; color:#ddd; line-height:2; margin-top:10px; text-align:center">
            Required: license plate · package · wash type · date · price<br>
            Data is processed entirely in your browser session.
        </div>
        """, unsafe_allow_html=True)

    # Features
    st.markdown(f"""
    <div style="font-family:'{MONO}',monospace; font-size:9px; color:#ddd; letter-spacing:5px; text-align:center; margin:52px 0 24px">
        WHAT YOU GET AFTER UPLOADING
    </div>""", unsafe_allow_html=True)

    feats = [
        ("📊","Site Overview","Total transactions, unique customers, avg ticket, premium rate — your operation at a glance."),
        ("👥","Membership Analytics","Penetration rate, visit frequency distribution, member vs retail revenue split."),
        ("🎯","6 Customer Segments","High Frequency, Churn Risk, Premium, Weekend, Price Sensitive, First Timers — each with counts and actions."),
        ("📦","Package Performance","Transaction share, revenue by tier, premium adoption rate vs industry benchmark."),
        ("📅","Time Patterns","Day-of-week and hour distributions to understand when your customers show up."),
        ("🤖","AI Operator Insights","Written plain-English observations and recommended actions tailored to your data."),
    ]
    cols = st.columns(3)
    for i, (icon, title, body) in enumerate(feats):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,200,60,0.07);
                 border-top:2px solid {AMBER}; border-radius:12px; padding:20px 18px; margin-bottom:12px; height:155px">
                <div style="font-size:22px; margin-bottom:8px">{icon}</div>
                <div style="font-family:'Outfit',sans-serif; font-weight:700; font-size:13px; color:#D0D0C8; margin-bottom:6px">{title}</div>
                <div style="font-family:'Outfit',sans-serif; font-size:11px; color:#ddd; line-height:1.7; font-weight:300">{body}</div>
            </div>""", unsafe_allow_html=True)

    return uploaded

# ── DASHBOARD ─────────────────────────────────────────────────────────────────

def dashboard(d, hf_vpw, churn_days):
    profiles   = d["profiles"]
    wash_df    = d["wash_df"]
    pkg_perf   = d["pkg_perf"]
    day_dist   = d["day_dist"]
    rev_seg    = d["rev_seg"]
    mem_freq   = d["mem_freq"]
    now        = d["now"]
    period_days= d["period_days"]

    total      = len(profiles)
    members    = profiles["is_member"].sum()
    retail     = total - members
    avg_ticket = wash_df[wash_df["total_val"] > 0]["total_val"].mean()
    prem_rate  = (wash_df["tier"] == "Tier 3 (Premium)").mean() * 100
    mem_pct    = members / total * 100 if total else 0
    seg_counts = profiles["segment"].value_counts()

    # ── Top brand bar
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center;
         border-bottom:1px solid rgba(255,200,60,0.1); padding-bottom:16px; margin-bottom:28px">
        <div style="display:flex; align-items:center; gap:18px">
            <div style="font-family:'Bebas Neue',sans-serif; font-size:30px; letter-spacing:5px; color:{AMBER}">WAVEIQ</div>
            <div style="width:1px; height:28px; background:rgba(255,255,255,0.06)"></div>
            <div>
                <div style="font-family:'Outfit',sans-serif; font-size:13px; font-weight:600; color:#bbb">Intelligence Report</div>
                <div style="font-family:'{MONO}',monospace; font-size:9px; color:#ccc; letter-spacing:1px">
                    {int(period_days)} days of data · through {now.strftime("%b %d, %Y")}
                </div>
            </div>
        </div>
        <div style="text-align:right">
            <div style="font-family:'{MONO}',monospace; font-size:8px; color:#ddd; letter-spacing:2px">Architected by</div>
            <div style="font-family:'Outfit',sans-serif; font-size:13px; font-weight:600; color:#bbb">Gopi Chand</div>
        </div>
    </div>""", unsafe_allow_html=True)

    tabs = st.tabs(["📊  Overview", "👥  Membership", "🎯  Segments", "📦  Packages", "📅  Time Patterns", "⚠️  Churn Risk", "🤖  Insights"])

    # ─────────────────────────────── TAB 1: OVERVIEW ─────────────────────────
    with tabs[0]:
        section_header("Site Performance", "Dashboard Overview")

        k1,k2,k3,k4,k5,k6 = st.columns(6)
        k1.metric("Total Transactions", f"{len(wash_df):,}")
        k2.metric("Unique Customers",   f"{total:,}")
        k3.metric("Members",            f"{members:,}")
        k4.metric("Retail Customers",   f"{retail:,}")
        k5.metric("Avg Ticket",         f"${avg_ticket:.2f}" if avg_ticket else "—")
        k6.metric("Premium Rate",       f"{prem_rate:.0f}%")

        st.markdown("<div style='margin:28px 0'></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)

        with c1:
            st.markdown(f"<div style='font-family:{MONO},monospace; font-size:9px; color:#999; letter-spacing:3px; text-transform:uppercase; margin-bottom:8px'>Customer Mix</div>", unsafe_allow_html=True)
            st.plotly_chart(
                donut(["Members","Retail"], [members, retail], [AMBER,"#444"],
                      f"{mem_pct:.0f}%\nMember"),
                use_container_width=True, config={"displayModeBar": False}
            )

        with c2:
            st.markdown(f"<div style='font-family:{MONO},monospace; font-size:9px; color:#999; letter-spacing:3px; text-transform:uppercase; margin-bottom:8px'>Segment Distribution</div>", unsafe_allow_html=True)
            seg_df = seg_counts.reset_index()
            seg_df.columns = ["Segment","Count"]
            st.plotly_chart(
                donut(seg_df["Segment"].tolist(), seg_df["Count"].tolist(),
                      [SEG_COLORS.get(s,"#888") for s in seg_df["Segment"]], f"{total:,}\ntotal"),
                use_container_width=True, config={"displayModeBar": False}
            )

        # Stacked proportion bar
        st.markdown(f"<div style='font-family:{MONO},monospace; font-size:9px; color:#999; letter-spacing:3px; text-transform:uppercase; margin:20px 0 10px'>All Segments — Proportional View</div>", unsafe_allow_html=True)
        fig_stack = go.Figure()
        for seg, cnt in seg_counts.items():
            pct = cnt / total * 100
            fig_stack.add_trace(go.Bar(
                x=[cnt], y=["Segments"], orientation="h", name=seg,
                marker=dict(color=SEG_COLORS.get(seg,"#888"), line=dict(width=2,color=BG)),
                text=f"{pct:.0f}%" if pct > 7 else "",
                textposition="inside", textfont=dict(size=12,color="rgba(0,0,0,0.6)"),
                hovertemplate=f"<b>{seg}</b><br>{cnt:,} customers ({pct:.1f}%)<extra></extra>",
            ))
        fig_stack.update_layout(**PLOTLY_LAYOUT, barmode="stack", height=72,
            xaxis=dict(showgrid=False,showticklabels=False,zeroline=False),
            yaxis=dict(showgrid=False,showticklabels=False),
            showlegend=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_stack, use_container_width=True, config={"displayModeBar": False})

        leg_cols = st.columns(len(seg_counts))
        for col, (seg, cnt) in zip(leg_cols, seg_counts.items()):
            col.markdown(f"""
            <div style="border-left:3px solid {SEG_COLORS.get(seg,'#888')}; padding-left:8px; margin-top:4px">
                <div style="font-family:'{MONO}',monospace; font-size:7px; color:#ccc; text-transform:uppercase; letter-spacing:1px; white-space:nowrap; overflow:hidden">{seg.split()[-1]}</div>
                <div style="font-family:'Bebas Neue',sans-serif; font-size:18px; color:{SEG_COLORS.get(seg,'#888')}; letter-spacing:1px">{cnt:,}</div>
            </div>""", unsafe_allow_html=True)

    # ─────────────────────────────── TAB 2: MEMBERSHIP ───────────────────────
    with tabs[1]:
        section_header("Membership Analytics", "Member Health")

        mem_profiles = profiles[profiles["is_member"]].copy()
        avg_vpmo     = mem_profiles["visits_per_month"].mean() if len(mem_profiles) else 0
        mem_rev_pct  = rev_seg[rev_seg["label"]=="Members"]["total_spend"].sum() / rev_seg["total_spend"].sum() * 100 if len(rev_seg) else 0

        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Membership Penetration", f"{mem_pct:.0f}%")
        m2.metric("Active Members",         f"{members:,}")
        m3.metric("Avg Visits / Member / Mo", f"{avg_vpmo:.1f}")
        m4.metric("Member Revenue Share",    f"{mem_rev_pct:.0f}%")

        st.markdown("<div style='margin:20px 0'></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)

        with c1:
            st.markdown(f"<div style='font-family:{MONO},monospace; font-size:9px; color:#999; letter-spacing:3px; text-transform:uppercase; margin-bottom:8px'>Member Visit Frequency Distribution</div>", unsafe_allow_html=True)
            st.plotly_chart(
                vbar(mem_freq, "Frequency", "Members", color=AMBER, height=280),
                use_container_width=True, config={"displayModeBar":False}
            )
            if len(mem_freq):
                top_bucket = mem_freq.loc[mem_freq["Members"].idxmax(), "Frequency"]
                st.markdown(insight_box(f"Most members visit <b>{top_bucket}</b> on average."), unsafe_allow_html=True)

        with c2:
            st.markdown(f"<div style='font-family:{MONO},monospace; font-size:9px; color:#999; letter-spacing:3px; text-transform:uppercase; margin-bottom:8px'>Revenue: Members vs Retail</div>", unsafe_allow_html=True)
            rev_labels = rev_seg["label"].tolist()
            rev_vals   = rev_seg["total_spend"].tolist()
            st.plotly_chart(
                donut(rev_labels, rev_vals, [AMBER,"#444"], "Revenue\nSplit"),
                use_container_width=True, config={"displayModeBar":False}
            )
            st.markdown(insight_box("Membership program drives majority of revenue when penetration exceeds 30%."), unsafe_allow_html=True)

        # Benchmark callout
        benchmark = 36.0
        delta = mem_pct - benchmark
        delta_txt = f"+{delta:.1f}pp above" if delta >= 0 else f"{delta:.1f}pp below"
        color_delta = "#34D399" if delta >= 0 else "#FF5A5A"
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06);
             border-radius:12px; padding:20px 24px; margin-top:12px; display:flex; align-items:center; gap:28px">
            <div>
                <div style="font-family:'{MONO}',monospace; font-size:9px; color:#999; letter-spacing:2px; text-transform:uppercase; margin-bottom:4px">Your Penetration</div>
                <div style="font-family:'Bebas Neue',sans-serif; font-size:36px; color:{AMBER}; letter-spacing:2px">{mem_pct:.0f}%</div>
            </div>
            <div style="width:1px; height:48px; background:rgba(255,255,255,0.06)"></div>
            <div>
                <div style="font-family:'{MONO}',monospace; font-size:9px; color:#999; letter-spacing:2px; text-transform:uppercase; margin-bottom:4px">Industry Avg</div>
                <div style="font-family:'Bebas Neue',sans-serif; font-size:36px; color:#ddd; letter-spacing:2px">{benchmark:.0f}%</div>
            </div>
            <div style="width:1px; height:48px; background:rgba(255,255,255,0.06)"></div>
            <div>
                <div style="font-family:'{MONO}',monospace; font-size:9px; color:#999; letter-spacing:2px; text-transform:uppercase; margin-bottom:4px">vs Benchmark</div>
                <div style="font-family:'Bebas Neue',sans-serif; font-size:28px; color:{color_delta}; letter-spacing:1px">{delta_txt}</div>
            </div>
            <div style="font-family:'Outfit',sans-serif; font-size:12px; color:#ddd; line-height:1.7; font-weight:300; max-width:300px">
                Industry benchmark for express tunnel operations is <b style="color:#ccc">35–45%</b>.
                {"You're tracking well." if delta >= 0 else "Focus on converting retail customers at POS."}
            </div>
        </div>""", unsafe_allow_html=True)

    # ─────────────────────────────── TAB 3: SEGMENTS ─────────────────────────
    with tabs[2]:
        section_header("Behavioral Segmentation", "Customer Segments")

        all_segs = ["High Frequency Members","Churn Risk Members","Premium Buyers",
                    "Weekend Washers","Price Sensitive","First Time Visitors"]

        for seg in all_segs:
            if seg not in seg_counts.index:
                continue
            cnt   = seg_counts[seg]
            color = SEG_COLORS.get(seg, "#888")
            icon  = SEG_ICONS.get(seg, "●")
            seg_df = profiles[profiles["segment"] == seg]
            pct    = cnt / total * 100

            with st.expander(f"{icon}  **{seg}**  —  {cnt:,} customers  ({pct:.1f}%)", expanded=False):
                e1,e2,e3,e4 = st.columns(4)
                e1.metric("Count",        f"{cnt:,}")
                e2.metric("Avg Visits",   f"{seg_df['total_visits'].mean():.1f}")
                e3.metric("Avg Spend",    f"${seg_df['avg_spend'].mean():.2f}")
                e4.metric("Avg Days Ago", f"{seg_df['days_since'].mean():.0f}d")

                descs = {
                    "High Frequency Members":
                        "These customers represent your most loyal base. They've built a habit around your wash. Protect them with recognition, early access to new services, and loyalty perks.",
                    "Churn Risk Members":
                        "Members with no recent visit. Without intervention, a significant portion will cancel at next billing. A targeted free upgrade or personal outreach can recover most of them.",
                    "Premium Buyers":
                        "Customers who consistently choose your top-tier package. They're already invested in quality — upsell add-ons and membership to deepen that relationship.",
                    "Weekend Washers":
                        "Their visit pattern is predictable — Saturday and Sunday. Design weekend-specific bundles, flash deals, and social content timed to their rhythm.",
                    "Price Sensitive":
                        "Entry-level package regulars. A limited-time upgrade trial at a discounted rate often converts 20-30% of this group into mid-tier members.",
                    "First Time Visitors":
                        "Large opportunity — these plates appeared once. A follow-up offer within 48 hours drives the highest repeat conversion rate of any segment.",
                }
                desc_text = descs.get(seg, "")
                st.markdown(f"""
                <div style="border-left:3px solid {color}; padding-left:14px; margin:12px 0 8px">
                    <div style="font-family:'Outfit',sans-serif; font-size:13px; color:#ddd; line-height:1.8; font-weight:300">{desc_text}</div>
                </div>
                <div style="height:5px; background:rgba(255,255,255,0.06); border-radius:3px; margin:10px 0 4px">
                    <div style="height:5px; width:{pct:.1f}%; background:{color}; border-radius:3px"></div>
                </div>
                <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#ccc; margin-top:4px">{pct:.1f}% of all customers</div>
                """, unsafe_allow_html=True)

        # Segment comparison bar chart
        st.markdown("<div style='margin:28px 0 8px'></div>", unsafe_allow_html=True)
        section_header("", "Segment Size Comparison")
        seg_comp = seg_counts.reset_index()
        seg_comp.columns = ["Segment","Count"]
        seg_comp = seg_comp.sort_values("Count")
        fig_seg = go.Figure(go.Bar(
            x=seg_comp["Count"], y=seg_comp["Segment"], orientation="h",
            marker=dict(color=[SEG_COLORS.get(s,"#888") for s in seg_comp["Segment"]], opacity=0.85, line=dict(width=0)),
            text=seg_comp["Count"], textposition="outside", textfont=dict(size=11,color="#ccc"),
            hovertemplate="<b>%{y}</b><br>%{x:,} customers<extra></extra>",
        ))
        fig_seg.update_layout(**PLOTLY_LAYOUT, height=300, showlegend=False,
            xaxis=dict(gridcolor=GRID,zeroline=False,tickfont=dict(color="#bbb")),
            yaxis=dict(showgrid=False,tickfont=dict(color="#ddd",size=10)),
            margin=dict(l=0,r=60,t=10,b=10))
        st.plotly_chart(fig_seg, use_container_width=True, config={"displayModeBar":False})

    # ─────────────────────────────── TAB 4: PACKAGES ─────────────────────────
    with tabs[3]:
        section_header("Package Performance", "What's Selling")

        p1,p2,p3 = st.columns(3)
        prem_txns  = (wash_df["tier"]=="Tier 3 (Premium)").sum()
        prem_adopt = prem_txns / len(wash_df) * 100 if len(wash_df) else 0
        top_pkg    = pkg_perf.iloc[0]["package"] if len(pkg_perf) else "—"
        p1.metric("Premium Adoption",  f"{prem_adopt:.0f}%")
        p2.metric("Top Package",       top_pkg)
        p3.metric("Packages Available",f"{len(pkg_perf)}")

        c1, c2 = st.columns(2)

        with c1:
            st.markdown(f"<div style='font-family:{MONO},monospace; font-size:9px; color:#999; letter-spacing:3px; text-transform:uppercase; margin-bottom:8px'>Transactions by Package</div>", unsafe_allow_html=True)
            pkg_sorted = pkg_perf.sort_values("transactions")
            tier_colors = {"Tier 1 (Basic)":"#60A5FA","Tier 2 (Mid)":AMBER,"Tier 3 (Premium)":"#A78BFA"}
            fig_pkg = go.Figure(go.Bar(
                x=pkg_sorted["transactions"], y=pkg_sorted["package"], orientation="h",
                marker=dict(color=[tier_colors.get(t,"#888") for t in pkg_sorted["tier"]], opacity=0.85, line=dict(width=0)),
                text=pkg_sorted["transactions"], textposition="outside",
                textfont=dict(size=10,color="#ccc"),
                hovertemplate="<b>%{y}</b><br>%{x:,} transactions<extra></extra>",
            ))
            fig_pkg.update_layout(**PLOTLY_LAYOUT, height=max(260, len(pkg_perf)*40+40),
                showlegend=False,
                xaxis=dict(gridcolor=GRID,zeroline=False,tickfont=dict(color="#bbb")),
                yaxis=dict(showgrid=False,tickfont=dict(color="#ddd",size=10)),
                margin=dict(l=0,r=60,t=10,b=10))
            st.plotly_chart(fig_pkg, use_container_width=True, config={"displayModeBar":False})

        with c2:
            st.markdown(f"<div style='font-family:{MONO},monospace; font-size:9px; color:#999; letter-spacing:3px; text-transform:uppercase; margin-bottom:8px'>Transactions by Tier</div>", unsafe_allow_html=True)
            tier_agg = wash_df.groupby("tier").size().reset_index()
            tier_agg.columns = ["Tier","Transactions"]
            st.plotly_chart(
                donut(tier_agg["Tier"].tolist(), tier_agg["Transactions"].tolist(),
                      [tier_colors.get(t,"#888") for t in tier_agg["Tier"]], "Tiers"),
                use_container_width=True, config={"displayModeBar":False}
            )

        # Package table
        st.markdown(f"<div style='font-family:{MONO},monospace; font-size:9px; color:#999; letter-spacing:3px; text-transform:uppercase; margin:20px 0 10px'>Package Summary Table</div>", unsafe_allow_html=True)
        tbl = pkg_perf[["package","tier","transactions","share_pct","revenue"]].copy()
        tbl.columns = ["Package","Tier","Transactions","Share %","Revenue ($)"]
        tbl["Revenue ($)"] = tbl["Revenue ($)"].round(0).astype(int)
        st.dataframe(tbl, use_container_width=True, hide_index=True, height=280)

        if prem_adopt >= 20:
            st.markdown(insight_box(f"Premium adoption is <b>{prem_adopt:.0f}%</b> — above the 20% threshold considered strong for express tunnel operations. ✅"), unsafe_allow_html=True)
        else:
            st.markdown(insight_box(f"Premium adoption is <b>{prem_adopt:.0f}%</b>. Industry strong performers exceed 20%. Consider POS upsell prompts.", "📉"), unsafe_allow_html=True)

    # ─────────────────────────────── TAB 5: TIME PATTERNS ────────────────────
    with tabs[4]:
        section_header("Time Pattern Analysis", "When Customers Show Up")

        c1, c2 = st.columns(2)

        with c1:
            st.markdown(f"<div style='font-family:{MONO},monospace; font-size:9px; color:#999; letter-spacing:3px; text-transform:uppercase; margin-bottom:8px'>Day of Week Distribution</div>", unsafe_allow_html=True)
            day_colors = [AMBER if d in ["Saturday","Sunday"] else "#444" for d in day_dist["Day"]]
            fig_day = go.Figure(go.Bar(
                x=day_dist["Day"], y=day_dist["Pct"],
                marker=dict(color=day_colors, opacity=0.85, line=dict(width=0)),
                text=day_dist["Pct"].astype(str)+"%",
                textposition="outside", textfont=dict(size=10,color="#ccc"),
                hovertemplate="<b>%{x}</b><br>%{y}% of visits<extra></extra>",
            ))
            fig_day.update_layout(**PLOTLY_LAYOUT, height=300, showlegend=False,
                xaxis=dict(showgrid=False,tickfont=dict(color="#ddd",size=10)),
                yaxis=dict(gridcolor=GRID,zeroline=False,tickfont=dict(color="#bbb")),
                margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig_day, use_container_width=True, config={"displayModeBar":False})

            wknd_pct = day_dist[day_dist["Day"].isin(["Saturday","Sunday"])]["Pct"].sum()
            st.markdown(insight_box(f"Weekend traffic (Sat + Sun) accounts for <b>{wknd_pct:.0f}%</b> of all visits. Staff and supply accordingly."), unsafe_allow_html=True)

        with c2:
            st.markdown(f"<div style='font-family:{MONO},monospace; font-size:9px; color:#999; letter-spacing:3px; text-transform:uppercase; margin-bottom:8px'>Hour of Day Distribution</div>", unsafe_allow_html=True)
            hour_dist = wash_df.groupby("hour").size().reset_index()
            hour_dist.columns = ["Hour","Visits"]
            peak_hour = hour_dist.loc[hour_dist["Visits"].idxmax(), "Hour"] if len(hour_dist) else 0
            hour_colors = [AMBER if h == peak_hour else "#444" for h in hour_dist["Hour"]]
            fig_hr = go.Figure(go.Bar(
                x=hour_dist["Hour"], y=hour_dist["Visits"],
                marker=dict(color=hour_colors, opacity=0.85, line=dict(width=0)),
                hovertemplate="<b>%{x}:00</b><br>%{y:,} visits<extra></extra>",
            ))
            fig_hr.update_layout(**PLOTLY_LAYOUT, height=300, showlegend=False,
                xaxis=dict(showgrid=False,tickfont=dict(color="#ddd",size=10),
                           tickvals=list(range(0,24,2)),ticktext=[f"{h}:00" for h in range(0,24,2)]),
                yaxis=dict(gridcolor=GRID,zeroline=False,tickfont=dict(color="#bbb")),
                margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig_hr, use_container_width=True, config={"displayModeBar":False})
            st.markdown(insight_box(f"Peak hour is <b>{peak_hour}:00</b>. Ensure full lane staffing and chemical levels during this window."), unsafe_allow_html=True)

        # Retail visit frequency
        st.markdown("<div style='margin:28px 0 8px'></div>", unsafe_allow_html=True)
        section_header("", "Retail Customer Visit Frequency")
        retail_profiles = profiles[~profiles["is_member"]].copy()
        if len(retail_profiles):
            retail_rep = retail_profiles[retail_profiles["total_visits"] > 1]
            repeat_rate = len(retail_rep) / len(retail_profiles) * 100
            retail_dist = retail_profiles["total_visits"].clip(upper=5).value_counts().sort_index().reset_index()
            retail_dist.columns = ["Visits","Customers"]
            retail_dist["Visits"] = retail_dist["Visits"].astype(str)
            retail_dist.loc[retail_dist["Visits"]=="5","Visits"] = "5+"

            r1, r2 = st.columns(2)
            with r1:
                st.plotly_chart(vbar(retail_dist,"Visits","Customers",color="#60A5FA",height=260),
                    use_container_width=True, config={"displayModeBar":False})
            with r2:
                st.metric("Retail Repeat Rate", f"{repeat_rate:.0f}%")
                st.markdown(insight_box(f"<b>{repeat_rate:.0f}%</b> of retail customers return more than once. Industry average is ~29%. {'Above average ✅' if repeat_rate>=29 else 'Below average — consider a post-visit follow-up offer.'}"), unsafe_allow_html=True)

    # ─────────────────────────────── TAB 6: CHURN RISK ───────────────────────
    with tabs[5]:
        section_header("Churn Risk Detection", "Member Retention Alert")

        churn_df = profiles[profiles["is_member"]].copy()
        high  = churn_df[churn_df["churn_level"]=="High Risk"]
        med   = churn_df[churn_df["churn_level"]=="Medium Risk"]
        low   = churn_df[churn_df["churn_level"]=="Low Risk"]

        cr1,cr2,cr3 = st.columns(3)
        cr1.metric("🟢 Low Risk",    f"{len(low):,}",  help="Active members with recent visits")
        cr2.metric("🟡 Medium Risk", f"{len(med):,}",  help="Members approaching inactivity threshold")
        cr3.metric("🔴 High Risk",   f"{len(high):,}", help=f"Members with no visit in {churn_days}+ days")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div style='font-family:{MONO},monospace; font-size:9px; color:#999; letter-spacing:3px; text-transform:uppercase; margin:16px 0 8px'>Churn Risk Breakdown</div>", unsafe_allow_html=True)
            risk_labels = ["Low Risk","Medium Risk","High Risk"]
            risk_vals   = [len(low), len(med), len(high)]
            risk_colors = ["#34D399","#FFC83C","#FF5A5A"]
            st.plotly_chart(
                donut(risk_labels, risk_vals, risk_colors, "Risk\nLevels"),
                use_container_width=True, config={"displayModeBar":False}
            )

        with c2:
            st.markdown(f"<div style='font-family:{MONO},monospace; font-size:9px; color:#999; letter-spacing:3px; text-transform:uppercase; margin:16px 0 8px'>Days Since Last Visit — Members</div>", unsafe_allow_html=True)
            days_hist = churn_df["days_since"].clip(upper=60)
            fig_hist = go.Figure(go.Histogram(
                x=days_hist, nbinsx=20,
                marker=dict(color=AMBER, opacity=0.7, line=dict(width=0)),
                hovertemplate="<b>%{x} days</b><br>%{y} members<extra></extra>",
            ))
            fig_hist.add_vline(x=churn_days, line_color="#FF5A5A", line_dash="dash",
                annotation_text=f"Churn threshold ({churn_days}d)",
                annotation_font=dict(color="#FF5A5A", size=10))
            fig_hist.update_layout(**PLOTLY_LAYOUT, height=280,
                xaxis=dict(gridcolor=GRID,zeroline=False,tickfont=dict(color="#bbb"),title=dict(text="Days Inactive",font=dict(color="#ddd",size=10))),
                yaxis=dict(gridcolor=GRID,zeroline=False,tickfont=dict(color="#bbb")),
                margin=dict(l=10,r=10,t=10,b=32))
            st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar":False})

        if len(high):
            st.markdown(insight_box(f"<b>{len(high):,} members</b> have not visited in over {churn_days} days and are at high risk of cancellation. A free upgrade or personal outreach now has the highest recovery rate.", "🚨"), unsafe_allow_html=True)

        # High risk table
        if len(high):
            st.markdown(f"<div style='font-family:{MONO},monospace; font-size:9px; color:#999; letter-spacing:3px; text-transform:uppercase; margin:20px 0 8px'>High Risk Members</div>", unsafe_allow_html=True)
            show = high[["plate_clean","days_since","total_visits","avg_spend","packages"]].copy()
            show.columns = ["Plate","Days Inactive","Total Visits","Avg Spend ($)","Packages"]
            show = show.sort_values("Days Inactive", ascending=False)
            st.dataframe(show, use_container_width=True, hide_index=True, height=320)

    # ─────────────────────────────── TAB 7: INSIGHTS ─────────────────────────
    with tabs[6]:
        section_header("AI Operator Insights", "What Your Data Is Telling You")

        retail_rep_rate = 0
        retail_p = profiles[~profiles["is_member"]]
        if len(retail_p):
            retail_rep_rate = len(retail_p[retail_p["total_visits"]>1]) / len(retail_p) * 100

        first_time = profiles[profiles["is_first_time"]]
        churn_high = profiles[(profiles["is_member"]) & (profiles["churn_level"]=="High Risk")]

        insights = [
            (
                f"Your membership penetration is <b>{mem_pct:.0f}%</b>, "
                + ("which is within the typical 35–45% range for express tunnel operations. ✅" if 35 <= mem_pct <= 45
                   else "slightly below the typical 35–45% range observed in express tunnel operations. Focus on POS conversion prompts." if mem_pct < 35
                   else "above the typical range — strong membership health. ✅"),
                "👥"
            ),
            (
                f"Premium package adoption is <b>{prem_adopt:.0f}%</b>. "
                + ("This is above the 20% benchmark — strong upsell performance. ✅" if prem_adopt >= 20
                   else "This is below the 20% benchmark. Consider menu redesign or digital menu board upsell prompts."),
                "📦"
            ),
            (
                f"<b>{len(churn_high):,} members</b> have not visited in over {churn_days} days and may be at risk of cancellation. "
                "Consider sending a promotional reminder or complimentary upgrade offer immediately.",
                "⚠️"
            ),
            (
                f"<b>{len(first_time):,} first-time visitors</b> represent your largest conversion opportunity. "
                "A post-visit SMS or email offer within 48 hours typically yields a 15–25% return rate.",
                "👋"
            ),
            (
                f"Retail repeat rate is <b>{retail_rep_rate:.0f}%</b>. "
                + ("Above industry average of 29%. ✅" if retail_rep_rate >= 29
                   else "Below the 29% industry average. A loyalty punch card or digital follow-up can close this gap."),
                "🔄"
            ),
            (
                f"Weekend visits account for <b>{day_dist[day_dist['Day'].isin(['Saturday','Sunday'])]['Pct'].sum():.0f}%</b> of all traffic. "
                "Ensure peak staffing, chemical inventory, and equipment checks are completed by Friday close.",
                "📅"
            ),
        ]

        for text, icon in insights:
            st.markdown(insight_box(text, icon), unsafe_allow_html=True)

        # Recommended Actions
        st.markdown("<div style='margin:28px 0 12px'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-family:'Bebas Neue',sans-serif; font-size:22px; letter-spacing:2px; color:#E0E0D8; margin-bottom:16px">
            Recommended Actions
        </div>""", unsafe_allow_html=True)

        actions = [
            f"Target {len(churn_high):,} churn-risk members with a free premium upgrade this week.",
            "Promote premium packages to price-sensitive segment via POS screen or staff prompt.",
            f"Launch a follow-up offer to {len(first_time):,} first-time visitors within 48 hours of their visit.",
            "Run a weekend membership sign-up special — your Saturday/Sunday traffic is your best conversion window.",
            "Review digital menu board to ensure premium packages are visually prominent and first-positioned.",
        ]
        for a in actions:
            st.markdown(action_box(a), unsafe_allow_html=True)

        # CLV summary
        st.markdown("<div style='margin:28px 0 12px'></div>", unsafe_allow_html=True)
        st.markdown("""<div style="font-family:'Bebas Neue',sans-serif; font-size:22px; letter-spacing:2px; color:#E0E0D8; margin-bottom:16px">Customer Lifetime Value Estimate</div>""", unsafe_allow_html=True)

        retail_avg_ticket = profiles[~profiles["is_member"]]["avg_spend"].mean() if retail > 0 else 0.0
        retail_avg_visits = profiles[~profiles["is_member"]]["total_visits"].mean() if retail > 0 else 0.0
        mem_annual = avg_ticket * avg_vpmo * 12 if (avg_ticket and avg_vpmo) else 0.0
        retail_clv = retail_avg_ticket * retail_avg_visits

        cl1, cl2 = st.columns(2)
        with cl1:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.025); border:1px solid rgba(255,255,255,0.06);
                 border-top:2px solid {AMBER}; border-radius:12px; padding:20px 24px; margin-bottom:8px">
                <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#ddd;
                     letter-spacing:2px; text-transform:uppercase; margin-bottom:10px">Retail Customer</div>
                <div style="font-family:'Bebas Neue',sans-serif; font-size:42px; color:{AMBER};
                     letter-spacing:2px; line-height:1">${retail_clv:.0f}</div>
                <div style="font-family:'JetBrains Mono',monospace; font-size:10px; color:#bbb;
                     margin-top:8px">avg ticket x avg visits</div>
            </div>
            """, unsafe_allow_html=True)
        with cl2:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.025); border:1px solid rgba(255,255,255,0.06);
                 border-top:2px solid {AMBER}; border-radius:12px; padding:20px 24px; margin-bottom:8px">
                <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#ddd;
                     letter-spacing:2px; text-transform:uppercase; margin-bottom:10px">Member (Annual)</div>
                <div style="font-family:'Bebas Neue',sans-serif; font-size:42px; color:{AMBER};
                     letter-spacing:2px; line-height:1">${mem_annual:.0f}</div>
                <div style="font-family:'JetBrains Mono',monospace; font-size:10px; color:#bbb;
                     margin-top:8px">avg ticket x visits/mo x 12</div>
            </div>
            """, unsafe_allow_html=True)

        # ── PDF DOWNLOAD ──────────────────────────────────────────────────────
        st.markdown("<div style='margin:36px 0 12px'></div>", unsafe_allow_html=True)
        st.markdown("""<div style="font-family:'Bebas Neue',sans-serif; font-size:22px; letter-spacing:2px; color:#E0E0D8; margin-bottom:12px">Download Report</div>""", unsafe_allow_html=True)

        report_lines = [
            "WAVEIQ — CAR WASH CUSTOMER INTELLIGENCE REPORT",
            "Architected by Gopi Chand",
            "=" * 60,
            f"Generated: {datetime.now().strftime('%B %d, %Y %H:%M')}",
            f"Data through: {now.strftime('%B %d, %Y')}",
            f"Analysis period: {int(period_days)} days",
            "",
            "SITE OVERVIEW",
            "-" * 40,
            f"Total Transactions  : {len(wash_df):,}",
            f"Unique Customers    : {total:,}",
            f"Members             : {members:,}",
            f"Retail Customers    : {retail:,}",
            f"Avg Ticket Price    : ${avg_ticket:.2f}" if avg_ticket else "Avg Ticket Price    : —",
            f"Premium Package Rate: {prem_adopt:.0f}%",
            f"Membership Penetr.  : {mem_pct:.0f}%",
            "",
            "CUSTOMER SEGMENTS",
            "-" * 40,
        ]
        for seg_name, cnt in seg_counts.items():
            report_lines.append(f"  {seg_name:<30} {cnt:>6,} customers  ({cnt/total*100:.1f}%)")

        report_lines += [
            "",
            "PACKAGE PERFORMANCE",
            "-" * 40,
        ]
        for _, row in pkg_perf.iterrows():
            report_lines.append(f"  {row['package']:<28} {row['transactions']:>6,} txns  {row['share_pct']:.1f}%  {row['tier']}")

        report_lines += [
            "",
            "CHURN RISK",
            "-" * 40,
            f"  High Risk  (no visit {churn_days}+ days) : {len(profiles[(profiles['is_member']) & (profiles['churn_level']=='High Risk')]):,}",
            f"  Medium Risk                        : {len(profiles[(profiles['is_member']) & (profiles['churn_level']=='Medium Risk')]):,}",
            f"  Low Risk                           : {len(profiles[(profiles['is_member']) & (profiles['churn_level']=='Low Risk')]):,}",
            "",
            "CUSTOMER LIFETIME VALUE",
            "-" * 40,
            f"  Retail Customer CLV  : ${retail_clv:.2f}",
            f"  Member Annual Value  : ${mem_annual:.2f}",
            "",
            "DAY OF WEEK",
            "-" * 40,
        ]
        for _, row in day_dist.iterrows():
            report_lines.append(f"  {row['Day']:<12} {row['Pct']:.1f}%")

        report_lines += [
            "",
            "=" * 60,
            "DISCLAIMER",
            "-" * 40,
            "This report is generated by WaveIQ for informational and",
            "educational purposes only. The data, insights, and metrics",
            "presented are based solely on the CSV file uploaded by the",
            "user and are not independently verified.",
            "",
            "WaveIQ, its developers, and Gopi Chand are not responsible",
            "for any business decisions, financial outcomes, or operational",
            "changes made based on this report. Operators should consult",
            "qualified professionals before making significant business",
            "decisions. Use of this tool constitutes acceptance of these terms.",
            "=" * 60,
            "WAVEIQ · Architected by Gopi Chand · Car Wash Intelligence",
        ]

        report_text = "\n".join(report_lines)
        st.download_button(
            label="⬇  Download Full Report (TXT)",
            data=report_text.encode("utf-8"),
            file_name=f"waveiq_report_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=False,
        )
        st.markdown("""
        <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#888;
             margin-top:8px; line-height:1.8">
            Downloads as a formatted text report. Open in any text editor or word processor.
        </div>""", unsafe_allow_html=True)

        # ── DISCLAIMER ────────────────────────────────────────────────────────
        st.markdown("<div style='margin:36px 0 12px'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,200,60,0.12);
             border-left:3px solid {AMBER}; border-radius:8px; padding:18px 22px; margin-top:8px">
            <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:{AMBER};
                 letter-spacing:3px; text-transform:uppercase; margin-bottom:10px">Disclaimer</div>
            <div style="font-family:'Outfit',sans-serif; font-size:12px; color:#bbb; line-height:1.9; font-weight:300">
                This report is generated by <strong style="color:#ddd">WaveIQ</strong> for
                <strong style="color:#ddd">informational and educational purposes only.</strong>
                The data, insights, and metrics presented are derived solely from the CSV file
                uploaded by the user and have not been independently verified.<br><br>
                WaveIQ, its developers, and Gopi Chand are
                <strong style="color:#ddd">not responsible for any business decisions,
                financial outcomes, or operational changes</strong> made based on this report.
                Operators should consult qualified business or financial professionals before
                making significant operational decisions. Past customer behavior does not
                guarantee future results. Use of this tool constitutes acceptance of these terms.
            </div>
        </div>""", unsafe_allow_html=True)

        # Footer
        st.markdown(f"""
        <div style="border-top:1px solid rgba(255,255,255,0.04); margin-top:48px; padding-top:20px;
             display:flex; justify-content:space-between; align-items:center">
            <div style="font-family:'Bebas Neue',sans-serif; font-size:20px; letter-spacing:4px; color:#bbb">WAVEIQ</div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:8px; color:#ddd; letter-spacing:2px">Architected by Gopi Chand · Car Wash Customer Intelligence</div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:8px; color:#bbb">v2.0</div>
        </div>""", unsafe_allow_html=True)


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    hf_vpw, churn_days, wknd, prem_kw, basic_kw = sidebar()

    if "data" not in st.session_state:
        st.session_state.data = None

    uploaded = upload_screen()

    if uploaded is not None:
        with st.spinner("🌊  Analyzing your data..."):
            try:
                d = load_and_process(uploaded, prem_kw, basic_kw, churn_days, hf_vpw, wknd)
                st.session_state.data = d
            except Exception as e:
                st.error(f"Error processing file: {e}")
                return

    if st.session_state.data is not None:
        st.markdown("<hr style='border-color:rgba(255,200,60,0.08); margin:36px 0'>", unsafe_allow_html=True)
        dashboard(st.session_state.data, hf_vpw, churn_days)


if __name__ == "__main__":
    main()
