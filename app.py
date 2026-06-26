import streamlit as st
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
from datetime import datetime
import base64
from io import StringIO

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="EO Portfolio Triage",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════════
# PROFESSIONAL DESIGN SYSTEM — Dark Mode First, Insurance-Grade
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* ── ROOT TOKENS ── */
    :root {
        --bg-page: #0B0C10;
        --bg-surface: #111318;
        --bg-elevated: #181A20;
        --bg-hover: #1E2028;
        --border-subtle: #2A2D35;
        --border-medium: #3A3D47;
        --text-primary: #E8E9EC;
        --text-secondary: #8B8F99;
        --text-muted: #5C6069;
        --accent-primary: #4ADE80;
        --accent-secondary: #60A5FA;
        --accent-warning: #FBBF24;
        --accent-danger: #F87171;
        --accent-info: #38BDF8;
        --font-mono: 'SF Mono', 'Menlo', 'Monaco', monospace;
        --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', sans-serif;
    }

    /* ── GLOBAL RESET ── */
    .main { background-color: var(--bg-page); color: var(--text-primary); font-family: var(--font-sans); }
    .stApp { background-color: var(--bg-page); }
    .block-container { padding: 2rem 3rem; max-width: 1600px; }

    /* ── TYPOGRAPHY ── */
    h1 { color: var(--text-primary); font-weight: 700; font-size: 1.75rem; letter-spacing: -0.02em; margin-bottom: 0.25rem; }
    h2 { color: var(--text-primary); font-weight: 600; font-size: 1.25rem; margin-top: 0; }
    h3 { color: var(--text-secondary); font-weight: 500; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; }

    /* ── KPI CARDS (Glassmorphism-lite) ── */
    .kpi-card {
        background: linear-gradient(145deg, var(--bg-surface), var(--bg-elevated));
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        position: relative;
        overflow: hidden;
        transition: all 0.2s ease;
    }
    .kpi-card:hover { border-color: var(--border-medium); transform: translateY(-1px); }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        border-radius: 12px 12px 0 0;
    }
    .kpi-card.green::before { background: var(--accent-primary); }
    .kpi-card.blue::before { background: var(--accent-secondary); }
    .kpi-card.amber::before { background: var(--accent-warning); }
    .kpi-card.red::before { background: var(--accent-danger); }
    .kpi-card.neutral::before { background: var(--text-muted); }

    .kpi-value { font-size: 1.75rem; font-weight: 700; color: var(--text-primary); font-family: var(--font-mono); }
    .kpi-label { font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.08em; margin-top: 0.25rem; }
    .kpi-delta { font-size: 0.8125rem; margin-top: 0.5rem; font-weight: 500; }
    .kpi-delta.up { color: var(--accent-primary); }
    .kpi-delta.down { color: var(--accent-danger); }
    .kpi-delta.neutral { color: var(--text-muted); }

    /* ── SECTION CARDS ── */
    .section-card {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.25rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--border-subtle);
    }
    .section-title { font-size: 0.875rem; font-weight: 600; color: var(--text-primary); text-transform: uppercase; letter-spacing: 0.05em; }

    /* ── FILTER BAR ── */
    .filter-bar {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 1rem 1.25rem;
        display: flex;
        gap: 1rem;
        align-items: center;
        flex-wrap: wrap;
        margin-bottom: 1.5rem;
    }

    /* ── TABLE STYLING ── */
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    .stDataFrame thead tr th {
        background-color: var(--bg-elevated) !important;
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        border-bottom: 1px solid var(--border-subtle) !important;
        padding: 12px 16px !important;
    }
    .stDataFrame tbody tr td {
        background-color: var(--bg-surface) !important;
        color: var(--text-primary) !important;
        border-bottom: 1px solid var(--border-subtle) !important;
        padding: 10px 16px !important;
        font-size: 0.8125rem !important;
    }
    .stDataFrame tbody tr:hover td { background-color: var(--bg-hover) !important; }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 4px; 
        background: var(--bg-surface); 
        border-radius: 10px; 
        padding: 6px; 
        border: 1px solid var(--border-subtle);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 500;
        font-size: 0.8125rem;
        color: var(--text-secondary);
        border: none;
    }
    .stTabs [data-baseweb="tab"]:hover { color: var(--text-primary); background: var(--bg-hover); }
    .stTabs [aria-selected="true"] { 
        background: var(--bg-elevated) !important; 
        color: var(--text-primary) !important; 
        font-weight: 600 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }

    /* ── BUTTONS ── */
    .stButton>button {
        background: var(--bg-elevated);
        color: var(--text-primary);
        border: 1px solid var(--border-medium);
        border-radius: 8px;
        padding: 0.5rem 1.25rem;
        font-weight: 500;
        font-size: 0.8125rem;
        transition: all 0.15s ease;
    }
    .stButton>button:hover { 
        background: var(--bg-hover); 
        border-color: var(--text-secondary); 
    }
    .stButton>button[kind="primary"] {
        background: var(--accent-primary);
        color: #0B0C10;
        border: none;
        font-weight: 600;
    }
    .stButton>button[kind="primary"]:hover { background: #3ECF6E; }

    /* ── BADGES ── */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.6875rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }
    .badge-green { background: rgba(74, 222, 128, 0.15); color: var(--accent-primary); }
    .badge-amber { background: rgba(251, 191, 36, 0.15); color: var(--accent-warning); }
    .badge-red { background: rgba(248, 113, 113, 0.15); color: var(--accent-danger); }
    .badge-blue { background: rgba(96, 165, 250, 0.15); color: var(--accent-secondary); }
    .badge-gray { background: rgba(139, 143, 153, 0.15); color: var(--text-secondary); }

    /* ── SIDEBAR ── */
    .css-1d391kg { background-color: var(--bg-surface) !important; border-right: 1px solid var(--border-subtle) !important; }
    .css-1d391kg .stMarkdown { color: var(--text-secondary); }

    /* ── SLIDER / INPUTS ── */
    .stSlider > div > div { background: var(--bg-elevated) !important; }
    .stNumberInput input { background: var(--bg-elevated) !important; color: var(--text-primary) !important; border: 1px solid var(--border-subtle) !important; border-radius: 8px !important; }
    .stSelectbox > div > div { background: var(--bg-elevated) !important; color: var(--text-primary) !important; border: 1px solid var(--border-subtle) !important; border-radius: 8px !important; }

    /* ── FILE UPLOADER ── */
    .stFileUploader > div > div { background: var(--bg-elevated) !important; border: 2px dashed var(--border-medium) !important; border-radius: 10px !important; color: var(--text-secondary) !important; }

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-page); }
    ::-webkit-scrollbar-thumb { background: var(--border-medium); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

    /* ── TOOLTIP / INFO ── */
    .stAlert { background: var(--bg-elevated) !important; border: 1px solid var(--border-subtle) !important; border-radius: 10px !important; }
    .stAlert [data-testid="stAlertContent"] { color: var(--text-secondary) !important; }

    /* ── DIVIDER ── */
    hr { border-color: var(--border-subtle) !important; margin: 1.5rem 0 !important; }

    /* ── FOOTER ── */
    .footer { text-align: center; color: var(--text-muted); font-size: 0.6875rem; padding: 2rem 0; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# DATA LOADING & PROCESSING
# ═══════════════════════════════════════════════════════════════
@st.cache_data
def load_geojson():
    with open('portfolio.geojson', 'r') as f:
        data = json.load(f)
    return data

@st.cache_data
def build_summary_df(data):
    rows = []
    for feat in data['features']:
        props = feat['properties']
        geom = feat['geometry']
        farm_id = props['farm_id']

        if geom['type'] == 'Polygon':
            coords = geom['coordinates'][0]
            lons = [c[0] for c in coords]
            lats = [c[1] for c in coords]
            centroid_lon = np.mean(lons)
            centroid_lat = np.mean(lats)
        else:
            centroid_lon = centroid_lat = None

        vi = props['VI_timeseries']
        if vi:
            latest = vi[-1]
            prev = vi[-2] if len(vi) > 1 else latest

            ndvi_now = latest.get('NDVI', np.nan)
            ndvi_prev = prev.get('NDVI', np.nan)
            ndvi_change = ndvi_now - ndvi_prev if not (np.isnan(ndvi_now) or np.isnan(ndvi_prev)) else np.nan

            evi_now = latest.get('EVI', np.nan)
            ndmi_now = latest.get('NDMI', np.nan)
            bsi_now = latest.get('BSI', np.nan)
            latest_date = latest.get('date', 'N/A')

            # Calculate seasonal stats
            ndvi_values = [e.get('NDVI', np.nan) for e in vi if 'NDVI' in e]
            ndvi_mean = np.nanmean(ndvi_values) if ndvi_values else np.nan
            ndvi_min = np.nanmin(ndvi_values) if ndvi_values else np.nan
            ndvi_max = np.nanmax(ndvi_values) if ndvi_values else np.nan
            ndvi_vol = np.nanstd(ndvi_values) if ndvi_values else np.nan
        else:
            ndvi_now = evi_now = ndmi_now = bsi_now = ndvi_change = ndvi_mean = ndvi_min = ndvi_max = ndvi_vol = np.nan
            latest_date = 'N/A'

        missing_count = sum(1 for entry in vi if any(k not in entry for k in ['NDVI','EVI','NDMI','BSI']))

        # Risk classification
        risk = 'Unknown'
        if not np.isnan(ndvi_now):
            if ndvi_now < 0.15:
                risk = 'High'
            elif ndvi_now < 0.3:
                risk = 'Elevated'
            elif ndvi_now < 0.5:
                risk = 'Moderate'
            else:
                risk = 'Low'

        rows.append({
            'Farm ID': farm_id,
            'Latest Date': latest_date,
            'NDVI': round(ndvi_now, 3) if not np.isnan(ndvi_now) else None,
            'NDVI Δ': round(ndvi_change, 3) if not np.isnan(ndvi_change) else None,
            'EVI': round(evi_now, 3) if not np.isnan(evi_now) else None,
            'NDMI': round(ndmi_now, 3) if not np.isnan(ndmi_now) else None,
            'BSI': round(bsi_now, 3) if not np.isnan(bsi_now) else None,
            'NDVI Mean': round(ndvi_mean, 3) if not np.isnan(ndvi_mean) else None,
            'NDVI Min': round(ndvi_min, 3) if not np.isnan(ndvi_min) else None,
            'NDVI Max': round(ndvi_max, 3) if not np.isnan(ndvi_max) else None,
            'NDVI Vol': round(ndvi_vol, 3) if not np.isnan(ndvi_vol) else None,
            'Missing': missing_count,
            'Risk': risk,
            'Centroid Lon': centroid_lon,
            'Centroid Lat': centroid_lat,
            'VI Timeseries': vi,
            'Top K Similar': props.get('top_k', []),
            'Geometry': geom,
            'Feature ID': feat['id']
        })

    return pd.DataFrame(rows)

@st.cache_data
def build_geojson_for_map(df):
    features = []
    for _, row in df.iterrows():
        features.append({
            "type": "Feature",
            "geometry": row['Geometry'],
            "properties": {
                "farm_id": row['Farm ID'],
                "ndvi": row['NDVI'] if row['NDVI'] is not None else 0,
                "ndvi_change": row['NDVI Δ'] if row['NDVI Δ'] is not None else 0,
                "risk": row['Risk']
            }
        })
    return {"type": "FeatureCollection", "features": features}

# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════
def init_session_state():
    defaults = {
        'selected_farm': None,
        'flagged_farms': set(),
        'compare_farms': [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session_state()

# ═══════════════════════════════════════════════════════════════
# EXPORT HELPERS
# ═══════════════════════════════════════════════════════════════
def get_csv_download_link(df, filename="portfolio_export.csv"):
    export_cols = ['Farm ID', 'Latest Date', 'NDVI', 'NDVI Δ', 'EVI', 'NDMI', 'BSI', 'Missing', 'Risk']
    csv = df[export_cols].to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}" style="text-decoration:none;"><button style="background:#181A20;color:#E8E9EC;padding:8px 16px;border:1px solid #3A3D47;border-radius:8px;cursor:pointer;font-weight:500;font-size:0.8125rem;">📥 Export CSV</button></a>'

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🌾 EO Triage")
    st.markdown("<p style='color:#5C6069;font-size:0.75rem;'>Portfolio exploration for underwriters</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#2A2D35;margin:1rem 0;'>", unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload GeoJSON", type=['geojson', 'json'])

    if uploaded is not None:
        data = json.load(uploaded)
        st.success(f"✓ {len(data['features'])} parcels")
    else:
        try:
            data = load_geojson()
            st.info(f"📊 {len(data['features'])} parcels loaded")
        except Exception as e:
            st.error(f"⚠️ Upload required")
            st.stop()

    st.markdown("<hr style='border-color:#2A2D35;margin:1rem 0;'>", unsafe_allow_html=True)

    df = build_summary_df(data)

    st.markdown("### Filters")

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        ndvi_min = st.number_input("NDVI min", 0.0, 1.0, 0.0, 0.05)
    with col_f2:
        ndvi_max = st.number_input("NDVI max", 0.0, 1.0, 1.0, 0.05)

    missing_max = st.slider("Max missing", 0, 12, 5)
    risk_filter = st.multiselect("Risk level", ['Low', 'Moderate', 'Elevated', 'High', 'Unknown'], 
                                  default=['Low', 'Moderate', 'Elevated', 'High', 'Unknown'])

    filtered_df = df[
        (df['NDVI'].fillna(-1) >= ndvi_min) &
        (df['NDVI'].fillna(-1) <= ndvi_max) &
        (df['Missing'] <= missing_max) &
        (df['Risk'].isin(risk_filter))
    ].copy()

    st.markdown(f"<p style='color:#5C6069;font-size:0.75rem;'>Showing {len(filtered_df)} of {len(df)} parcels</p>", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#2A2D35;margin:1rem 0;'>", unsafe_allow_html=True)

    st.markdown("### Sort")
    sort_options = ['NDVI', 'NDVI Δ', 'EVI', 'NDMI', 'BSI', 'Missing', 'NDVI Vol']
    sort_by = st.selectbox("Sort by", sort_options, index=1)
    sort_asc = st.toggle("Ascending", value=True)

    filtered_df = filtered_df.sort_values(by=sort_by, ascending=sort_asc, na_position='last')

    st.markdown("<hr style='border-color:#2A2D35;margin:1rem 0;'>", unsafe_allow_html=True)

    st.markdown(get_csv_download_link(filtered_df), unsafe_allow_html=True)

    if st.session_state['flagged_farms']:
        st.markdown("<hr style='border-color:#2A2D35;margin:1rem 0;'>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#FBBF24;font-size:0.75rem;'>🚩 {len(st.session_state['flagged_farms'])} flagged</p>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# MAIN HEADER
# ═══════════════════════════════════════════════════════════════
header_col1, header_col2 = st.columns([4, 1])
with header_col1:
    st.markdown("# EO Portfolio Triage")
    st.markdown("<p style='color:#5C6069;font-size:0.875rem;'>Raw satellite indices. No synthesized scores. You decide what needs attention.</p>", unsafe_allow_html=True)
with header_col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ═══════════════════════════════════════════════════════════════
# KPI ROW — Inverted Pyramid, Top-Left Priority
# ═══════════════════════════════════════════════════════════════
# Calculate KPIs
kpi_data = {
    'total': len(df),
    'filtered': len(filtered_df),
    'low_ndvi': len(filtered_df[filtered_df['NDVI'].fillna(1) < 0.2]),
    'neg_change': len(filtered_df[filtered_df['NDVI Δ'].fillna(0) < -0.05]),
    'flagged': len(st.session_state['flagged_farms']),
    'high_risk': len(filtered_df[filtered_df['Risk'] == 'High']),
    'avg_ndvi': filtered_df['NDVI'].mean() if len(filtered_df) > 0 else 0,
    'missing_total': filtered_df['Missing'].sum() if len(filtered_df) > 0 else 0,
}

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.markdown(f"""
    <div class="kpi-card green">
        <div class="kpi-value">{kpi_data['filtered']}</div>
        <div class="kpi-label">Active Parcels</div>
        <div class="kpi-delta up">of {kpi_data['total']} total</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    pct_low = f"{kpi_data['low_ndvi']/kpi_data['filtered']*100:.0f}%" if kpi_data['filtered'] > 0 else "0%"
    st.markdown(f"""
    <div class="kpi-card amber">
        <div class="kpi-value">{kpi_data['low_ndvi']}</div>
        <div class="kpi-label">NDVI &lt; 0.2</div>
        <div class="kpi-delta down">{pct_low} of filtered</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="kpi-card red">
        <div class="kpi-value">{kpi_data['neg_change']}</div>
        <div class="kpi-label">NDVI Drop &gt;5%</div>
        <div class="kpi-delta down">month-over-month</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="kpi-card blue">
        <div class="kpi-value">{kpi_data['high_risk']}</div>
        <div class="kpi-label">High Risk</div>
        <div class="kpi-delta neutral">NDVI &lt; 0.15</div>
    </div>
    """, unsafe_allow_html=True)

with kpi5:
    st.markdown(f"""
    <div class="kpi-card neutral">
        <div class="kpi-value">{kpi_data['flagged']}</div>
        <div class="kpi-label">Flagged</div>
        <div class="kpi-delta neutral">for review</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(["🗺️  Map", "📋  Triage", "📈  Detail"])

# ═══════════════════════════════════════════════════════════════
# TAB 1: MAP
# ═══════════════════════════════════════════════════════════════
with tab1:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)

    map_col1, map_col2 = st.columns([3, 1])

    with map_col1:
        st.markdown("<h2 style='margin-bottom:0.5rem;'>Portfolio Overview</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#5C6069;font-size:0.8125rem;'>Color = current NDVI. Click a parcel to inspect.</p>", unsafe_allow_html=True)

        def ndvi_color(ndvi):
            if ndvi is None or np.isnan(ndvi):
                return [128, 128, 128, 100]
            if ndvi > 0.5:
                return [34, 139, 34, 200]
            elif ndvi > 0.3:
                return [154, 205, 50, 200]
            elif ndvi > 0.15:
                return [210, 180, 140, 200]
            else:
                return [220, 53, 69, 200]

        geojson_data = build_geojson_for_map(filtered_df)
        for feat in geojson_data['features']:
            ndvi = feat['properties']['ndvi']
            feat['properties']['fill_color'] = ndvi_color(ndvi)

        layer = pdk.Layer(
            "GeoJsonLayer",
            geojson_data,
            pickable=True,
            stroked=True,
            filled=True,
            extruded=False,
            line_width_min_pixels=1,
            get_fill_color="properties.fill_color",
            get_line_color=[255, 255, 255, 60],
            get_line_width=1,
            opacity=0.85,
        )

        if len(filtered_df) > 0 and filtered_df['Centroid Lon'].notna().any():
            view_state = pdk.ViewState(
                longitude=filtered_df['Centroid Lon'].mean(),
                latitude=filtered_df['Centroid Lat'].mean(),
                zoom=10,
                pitch=0,
                bearing=0
            )
        else:
            view_state = pdk.ViewState(longitude=37.86, latitude=-2.04, zoom=10, pitch=0)

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={
                "html": "<div style='background:#111318;color:#E8E9EC;padding:10px 14px;border-radius:8px;border:1px solid #2A2D35;font-family:sans-serif;'><b style='font-size:0.875rem;'>{farm_id}</b><br/><span style='color:#8B8F99;font-size:0.75rem;'>NDVI: {ndvi:.3f} | Δ: {ndvi_change:.3f}</span><br/><span style='color:#8B8F99;font-size:0.75rem;'>Risk: {risk}</span></div>",
                "style": {"backgroundColor": "transparent"}
            },
            map_style='mapbox://styles/mapbox/dark-v10'
        )

        st.pydeck_chart(deck, use_container_width=True)

    with map_col2:
        st.markdown("<h3 style='margin-bottom:1rem;'>Legend</h3>", unsafe_allow_html=True)
        legend_items = [
            ("🟢", "> 0.5", "Healthy", "badge-green"),
            ("🟡", "0.3 – 0.5", "Moderate", "badge-amber"),
            ("🟤", "0.15 – 0.3", "Stressed", "badge-red"),
            ("🔴", "< 0.15", "Bare / High Risk", "badge-red"),
            ("⚪", "Missing", "No data", "badge-gray"),
        ]
        for emoji, range_str, desc, badge_class in legend_items:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;padding:8px 10px;background:#181A20;border-radius:8px;border:1px solid #2A2D35;">
                <span style="font-size:1rem;">{emoji}</span>
                <div>
                    <div style="font-size:0.8125rem;font-weight:600;color:#E8E9EC;">{range_str}</div>
                    <div style="font-size:0.6875rem;color:#5C6069;">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom:0.75rem;'>Quick Stats</h3>", unsafe_allow_html=True)

        # Mini stats
        risk_counts = filtered_df['Risk'].value_counts().to_dict()
        for risk in ['High', 'Elevated', 'Moderate', 'Low']:
            count = risk_counts.get(risk, 0)
            pct = f"{count/len(filtered_df)*100:.0f}%" if len(filtered_df) > 0 else "0%"
            color = {'High':'#F87171','Elevated':'#FBBF24','Moderate':'#60A5FA','Low':'#4ADE80'}.get(risk, '#8B8F99')
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #2A2D35;">
                <span style="font-size:0.8125rem;color:#8B8F99;">{risk}</span>
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="font-size:0.8125rem;font-weight:600;color:{color};">{count}</span>
                    <span style="font-size:0.6875rem;color:#5C6069;">{pct}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TAB 2: TRIAGE TABLE
# ═══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)

    st.markdown("""
    <div class="section-header">
        <span class="section-title">Triage Surface</span>
        <span style="font-size:0.75rem;color:#5C6069;">Click a row to inspect. Use sidebar to filter and sort.</span>
    </div>
    """, unsafe_allow_html=True)

    # Prepare display data with badges
    display_df = filtered_df[['Farm ID', 'Latest Date', 'NDVI', 'NDVI Δ', 'EVI', 'NDMI', 'BSI', 'Missing', 'Risk']].copy()

    # Add flag indicator
    display_df['Status'] = display_df['Farm ID'].apply(
        lambda x: '⚑' if x in st.session_state['flagged_farms'] else ''
    )

    # Reorder columns
    display_df = display_df[['Farm ID', 'Status', 'Latest Date', 'NDVI', 'NDVI Δ', 'EVI', 'NDMI', 'BSI', 'Missing', 'Risk']]

    st.dataframe(
        display_df,
        use_container_width=True,
        height=550,
        column_config={
            "Farm ID": st.column_config.TextColumn(width="medium"),
            "Status": st.column_config.TextColumn(width="small"),
            "NDVI": st.column_config.NumberColumn(format="%.3f", width="small"),
            "NDVI Δ": st.column_config.NumberColumn(format="%.3f", width="small"),
            "EVI": st.column_config.NumberColumn(format="%.3f", width="small"),
            "NDMI": st.column_config.NumberColumn(format="%.3f", width="small"),
            "BSI": st.column_config.NumberColumn(format="%.3f", width="small"),
            "Missing": st.column_config.NumberColumn(width="small"),
            "Risk": st.column_config.TextColumn(width="small"),
        },
        hide_index=True
    )

    # Inspector
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    inspect_col1, inspect_col2, inspect_col3 = st.columns([3, 1, 1])
    with inspect_col1:
        selected = st.selectbox("Select parcel to inspect", 
                                options=[''] + list(filtered_df['Farm ID'].values),
                                index=0, key="table_select")
    with inspect_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if selected:
            is_flagged = selected in st.session_state['flagged_farms']
            label = "⚑ Unflag" if is_flagged else "⚑ Flag"
            if st.button(label, use_container_width=True, key="table_flag_btn"):
                if is_flagged:
                    st.session_state['flagged_farms'].discard(selected)
                    st.toast(f"Unflagged {selected}")
                else:
                    st.session_state['flagged_farms'].add(selected)
                    st.toast(f"Flagged {selected}")
                st.rerun()
    with inspect_col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if selected and st.button("📈 View Detail", use_container_width=True, key="table_view_btn"):
            st.session_state['selected_farm'] = selected
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TAB 3: DETAIL
# ═══════════════════════════════════════════════════════════════
with tab3:
    if st.session_state.get('selected_farm'):
        detail_farm = st.session_state['selected_farm']
    else:
        detail_farm = st.selectbox("Select parcel", 
                                   options=list(df['Farm ID'].values),
                                   index=0, key="detail_select")

    if detail_farm:
        farm_row = df[df['Farm ID'] == detail_farm].iloc[0]
        vi_data = farm_row['VI Timeseries']
        top_k = farm_row['Top K Similar']

        # ── Header with actions ──
        st.markdown(f"""
        <div class="section-card">
            <div class="section-header" style="border-bottom:none;margin-bottom:0;">
                <div>
                    <h2 style="margin-bottom:0.25rem;">📍 {detail_farm}</h2>
                    <p style="color:#5C6069;font-size:0.8125rem;">Latest observation: {farm_row['Latest Date']} | Risk: <span style="color:{'#F87171' if farm_row['Risk']=='High' else '#FBBF24' if farm_row['Risk']=='Elevated' else '#4ADE80'}">{farm_row['Risk']}</span></p>
                </div>
        </div>
        """, unsafe_allow_html=True)

        # Quick stats
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        metrics = [
            ("NDVI", farm_row['NDVI'], "#4ADE80"),
            ("NDVI Δ", farm_row['NDVI Δ'], "#FBBF24" if farm_row['NDVI Δ'] and farm_row['NDVI Δ'] < 0 else "#4ADE80"),
            ("EVI", farm_row['EVI'], "#60A5FA"),
            ("NDMI", farm_row['NDMI'], "#38BDF8"),
            ("BSI", farm_row['BSI'], "#8B5CF6"),
            ("Volatility", farm_row['NDVI Vol'], "#F87171"),
        ]
        for col, (label, val, color) in zip([c1, c2, c3, c4, c5, c6], metrics):
            with col:
                val_str = f"{val:.3f}" if val is not None else "N/A"
                st.markdown(f"""
                <div style="text-align:center;padding:0.75rem;background:#181A20;border-radius:8px;border:1px solid #2A2D35;">
                    <div style="font-size:0.6875rem;color:#5C6069;text-transform:uppercase;letter-spacing:0.05em;">{label}</div>
                    <div style="font-size:1.25rem;font-weight:700;color:{color};font-family:var(--font-mono);">{val_str}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ── Timeseries ──
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Vegetation Indices Over Time</div>", unsafe_allow_html=True)

        plot_data = []
        for entry in vi_data:
            date = entry.get('date')
            for idx in ['NDVI', 'EVI', 'NDMI', 'BSI']:
                if idx in entry:
                    plot_data.append({'Date': date, 'Index': idx, 'Value': entry[idx]})

        plot_df = pd.DataFrame(plot_data)
        plot_df['Date'] = pd.to_datetime(plot_df['Date'])

        fig = px.line(plot_df, x='Date', y='Value', color='Index',
                      template='plotly_dark',
                      color_discrete_map={
                          'NDVI': '#4ADE80',
                          'EVI': '#60A5FA', 
                          'NDMI': '#38BDF8',
                          'BSI': '#A78BFA'
                      })
        fig.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E8E9EC', family='Inter, sans-serif'),
            xaxis=dict(gridcolor='#2A2D35', showgrid=True),
            yaxis=dict(gridcolor='#2A2D35', showgrid=True),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            margin=dict(l=40, r=20, t=60, b=40),
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Per-index + Similar + Map ──
        col_left, col_right = st.columns([2, 1])

        with col_left:
            # Per-index breakdown
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>Per-Index Breakdown</div>", unsafe_allow_html=True)

            idx_cols = st.columns(2)
            indices = ['NDVI', 'EVI', 'NDMI', 'BSI']
            colors = ['#4ADE80', '#60A5FA', '#38BDF8', '#A78BFA']

            for i, (idx_name, color) in enumerate(zip(indices, colors)):
                with idx_cols[i % 2]:
                    idx_data = plot_df[plot_df['Index'] == idx_name]
                    if not idx_data.empty:
                        fig_idx = px.area(idx_data, x='Date', y='Value',
                                          template='plotly_dark',
                                          color_discrete_sequence=[color])
                        fig_idx.update_layout(
                            height=220,
                            showlegend=False,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='#E8E9EC', size=10),
                            xaxis=dict(gridcolor='#2A2D35', showgrid=True, title=''),
                            yaxis=dict(gridcolor='#2A2D35', showgrid=True, title=''),
                            margin=dict(l=30, r=10, t=30, b=20),
                            title=dict(text=idx_name, font=dict(size=12, color='#E8E9EC'), x=0.5)
                        )
                        st.plotly_chart(fig_idx, use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)

            # Compare similar
            if top_k:
                st.markdown("<div class='section-card'>", unsafe_allow_html=True)
                st.markdown("<div class='section-title'>Compare to Similar Parcels</div>", unsafe_allow_html=True)
                st.markdown("<p style='color:#5C6069;font-size:0.75rem;margin-bottom:1rem;'>Pre-computed similarity scores. No additional clustering.</p>", unsafe_allow_html=True)

                similar = top_k[:5]
                compare_data = []
                for entry in vi_data:
                    if 'NDVI' in entry:
                        compare_data.append({'Date': entry['date'], 'Farm': f"{detail_farm} (selected)", 'NDVI': entry['NDVI']})

                for sim_entry in similar:
                    sim_id = sim_entry['target']
                    sim_score = sim_entry['similarity']
                    sim_row = df[df['Farm ID'] == sim_id]
                    if not sim_row.empty:
                        sim_vi = sim_row.iloc[0]['VI Timeseries']
                        for entry in sim_vi:
                            if 'NDVI' in entry:
                                compare_data.append({'Date': entry['date'], 'Farm': f"{sim_id} (sim: {sim_score:.3f})", 'NDVI': entry['NDVI']})

                compare_df = pd.DataFrame(compare_data)
                compare_df['Date'] = pd.to_datetime(compare_df['Date'])

                fig_comp = px.line(compare_df, x='Date', y='NDVI', color='Farm', template='plotly_dark')
                fig_comp.update_layout(
                    height=350,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#E8E9EC'),
                    xaxis=dict(gridcolor='#2A2D35'),
                    yaxis=dict(gridcolor='#2A2D35'),
                    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(size=10)),
                    margin=dict(l=40, r=20, t=60, b=40),
                    hovermode='x unified'
                )
                st.plotly_chart(fig_comp, use_container_width=True)

                sim_df = pd.DataFrame([
                    {'Rank': i+1, 'Farm': s['target'], 'Score': f"{s['similarity']:.4f}"}
                    for i, s in enumerate(similar)
                ])
                st.dataframe(sim_df, hide_index=True, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

        with col_right:
            # Mini map
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>Parcel Location</div>", unsafe_allow_html=True)

            farm_geom = farm_row['Geometry']
            if farm_geom['type'] == 'Polygon':
                coords = farm_geom['coordinates'][0]
                lons = [c[0] for c in coords]
                lats = [c[1] for c in coords]
                center_lon = np.mean(lons)
                center_lat = np.mean(lats)

                mini_geojson = {
                    "type": "FeatureCollection",
                    "features": [{
                        "type": "Feature",
                        "geometry": farm_geom,
                        "properties": {"farm_id": detail_farm}
                    }]
                }

                mini_layer = pdk.Layer(
                    "GeoJsonLayer",
                    mini_geojson,
                    pickable=True,
                    filled=True,
                    stroked=True,
                    get_fill_color=[74, 222, 128, 180],
                    get_line_color=[255, 255, 255, 150],
                    get_line_width=2,
                )

                mini_deck = pdk.Deck(
                    layers=[mini_layer],
                    initial_view_state=pdk.ViewState(
                        longitude=center_lon, latitude=center_lat, zoom=14, pitch=0
                    ),
                    map_style='mapbox://styles/mapbox/satellite-v9',
                    tooltip={"text": "{farm_id}"}
                )
                st.pydeck_chart(mini_deck, use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)

            # Summary stats card
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>Historical Summary</div>", unsafe_allow_html=True)

            stats = [
                ("Mean NDVI", farm_row['NDVI Mean'], "#4ADE80"),
                ("Min NDVI", farm_row['NDVI Min'], "#F87171"),
                ("Max NDVI", farm_row['NDVI Max'], "#60A5FA"),
                ("Volatility (σ)", farm_row['NDVI Vol'], "#FBBF24"),
                ("Missing Months", farm_row['Missing'], "#8B8F99"),
            ]
            for label, val, color in stats:
                val_str = f"{val:.3f}" if val is not None else "N/A"
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #2A2D35;">
                    <span style="font-size:0.8125rem;color:#8B8F99;">{label}</span>
                    <span style="font-size:0.875rem;font-weight:600;color:{color};font-family:var(--font-mono);">{val_str}</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════
st.markdown("<div class='footer'>EO Portfolio Triage Tool — Raw index values, no synthesized scores. Built for underwriters.</div>", unsafe_allow_html=True)