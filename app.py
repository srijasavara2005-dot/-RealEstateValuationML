import streamlit as st
import pandas as pd
import joblib
import sqlite3
import hashlib
import os
import plotly.graph_objects as go
import warnings

# Suppress scikit-learn unpickling version warnings cleanly (1.6.1 vs 1.9.0)
try:
    from sklearn.exceptions import InconsistentVersionWarning
    warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
except ImportError:
    pass
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

# Global Construction Quality Multipliers (Defined safely before any code usage)
QUALITY_MULTIPLIERS = {
    "Basic": 0.90,
    "Standard": 1.00,
    "Premium": 1.25,
    "Luxury": 1.50
}
quality_multipliers = QUALITY_MULTIPLIERS

# Safe Streamlit DataFrame & Plotly rendering wrappers (Handles width='stretch' vs use_container_width seamlessly)
def render_dataframe(df, **kwargs):
    safe_df = df.astype(str) if isinstance(df, pd.DataFrame) else df
    try:
        st.dataframe(safe_df, width="stretch", **kwargs)
    except Exception:
        try:
            st.dataframe(safe_df, use_container_width=True, **kwargs)
        except Exception:
            st.dataframe(safe_df, **kwargs)

def render_plotly_chart(fig, **kwargs):
    try:
        st.plotly_chart(fig, width="stretch", **kwargs)
    except Exception:
        try:
            st.plotly_chart(fig, use_container_width=True, **kwargs)
        except Exception:
            st.plotly_chart(fig, **kwargs)

# Worldwide Country, Location & Currency Registry (196+ Countries Worldwide)
from worldwide_data import (
    ORDERED_COUNTRY_LIST,
    ALL_COUNTRY_NAMES,
    get_country_config,
    format_currency_value,
    number_to_words,
    map_location_to_internal_neighborhood
)

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Real Estate Valuation & 3D Architectural Studio",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# FILE PATHS & DIRECTORIES
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "users.db")
MODEL_FILE_GZ = os.path.join(BASE_DIR, "house_price_model.pkl.gz")
MODEL_FILE_PKL = os.path.join(BASE_DIR, "house_price_model.pkl")
MODEL_FILE = MODEL_FILE_GZ if os.path.exists(MODEL_FILE_GZ) else MODEL_FILE_PKL
FEATURE_FILE = os.path.join(BASE_DIR, "feature_columns.pkl")

# =========================================================
# MODERN REAL ESTATE STYLING (CSS)
# =========================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Background enhancement */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #eef2f6 50%, #f1f5f9 100%);
    }
    
    /* Hero Header Banner */
    .hero-banner {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 60%, #0284c7 100%);
        color: white;
        padding: 2.2rem 2.2rem;
        border-radius: 18px;
        margin-bottom: 2rem;
        box-shadow: 0 12px 28px -6px rgba(37, 99, 235, 0.25);
    }
    
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0 0 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .hero-subtitle {
        font-size: 1.05rem;
        opacity: 0.92;
        margin: 0;
        max-width: 850px;
        line-height: 1.5;
    }
    
    .hero-pills {
        display: flex;
        gap: 0.75rem;
        flex-wrap: wrap;
        margin-top: 1.25rem;
    }
    
    .hero-pill {
        background: rgba(255, 255, 255, 0.18);
        backdrop-filter: blur(8px);
        padding: 0.35rem 0.85rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.25);
    }
    
    /* Clean Glass Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
    }
    
    .card-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 0.6rem;
    }
    
    /* Valuation Highlight Card */
    .valuation-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white;
        border-radius: 20px;
        padding: 2.2rem;
        margin: 1.5rem 0 2rem 0;
        box-shadow: 0 20px 35px -8px rgba(15, 23, 42, 0.35);
        border: 1px solid #334155;
    }
    
    .val-header {
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #94a3b8;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .val-price {
        font-size: 3rem;
        font-weight: 800;
        color: #38bdf8;
        letter-spacing: -1px;
        margin-bottom: 0.35rem;
    }
    
    .val-words {
        font-size: 1.2rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 1.25rem;
        background: rgba(255, 255, 255, 0.07);
        padding: 0.6rem 1rem;
        border-radius: 10px;
        display: inline-block;
        border-left: 4px solid #38bdf8;
    }
    
    .val-location {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(56, 189, 248, 0.15);
        color: #bae6fd;
        padding: 0.45rem 1rem;
        border-radius: 9999px;
        font-size: 0.95rem;
        font-weight: 600;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
    
    /* Detail Badges & Metrics */
    .detail-metric-card {
        background: #ffffff;
        border-radius: 14px;
        padding: 1.2rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        text-align: center;
        height: 100%;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    
    .detail-metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
    }
    
    .metric-icon {
        font-size: 1.8rem;
        margin-bottom: 0.35rem;
    }
    
    .metric-val {
        font-size: 1.35rem;
        font-weight: 800;
        color: #0f172a;
    }
    
    .metric-lbl {
        font-size: 0.82rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Rating Box */
    .rating-banner {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 1px solid #fde68a;
        border-radius: 16px;
        padding: 1.4rem 1.8rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 1.5rem 0;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.08);
    }
    
    .rating-stars {
        font-size: 2.2rem;
        letter-spacing: 3px;
        line-height: 1;
    }
    
    .rating-tag {
        background: #f59e0b;
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 9999px;
        font-size: 0.9rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    
    /* Eco Box */
    .eco-banner {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 1px solid #bbf7d0;
        border-radius: 16px;
        padding: 1.4rem 1.8rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 1.5rem 0;
        box-shadow: 0 4px 15px rgba(22, 101, 52, 0.08);
    }
    
    .eco-tag {
        background: #16a34a;
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 9999px;
        font-size: 0.9rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    
    /* Feature Pills */
    .feature-pill {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        color: #166534;
        padding: 0.65rem 1rem;
        border-radius: 12px;
        font-size: 0.95rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        box-shadow: 0 2px 6px rgba(22, 101, 52, 0.05);
    }
    
    /* Streamlit Button Styling */
    div.stButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 0.65rem 1.5rem !important;
        transition: all 0.2s ease !important;
        border: none !important;
    }
    
    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12) !important;
    }

    /* Affordability Badges & Alert Cards */
    .afford-badge-fits {
        background: #f0fdf4;
        border: 1.5px solid #86efac;
        color: #166534;
        padding: 0.5rem 1.25rem;
        border-radius: 9999px;
        font-weight: 800;
        font-size: 1.05rem;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        box-shadow: 0 2px 8px rgba(22, 101, 52, 0.08);
    }
    .afford-badge-close {
        background: #fffbeb;
        border: 1.5px solid #fde68a;
        color: #92400e;
        padding: 0.5rem 1.25rem;
        border-radius: 9999px;
        font-weight: 800;
        font-size: 1.05rem;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        box-shadow: 0 2px 8px rgba(180, 83, 9, 0.08);
    }
    .afford-badge-exceeds {
        background: #fef2f2;
        border: 1.5px solid #fca5a5;
        color: #991b1b;
        padding: 0.5rem 1.25rem;
        border-radius: 9999px;
        font-weight: 800;
        font-size: 1.05rem;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        box-shadow: 0 2px 8px rgba(185, 28, 28, 0.08);
    }

    /* Financial Planning & EMI Card */
    .loan-metric-box {
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 14px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
    }
    .loan-metric-val {
        font-size: 1.6rem;
        font-weight: 800;
        color: #0284c7;
        margin: 0.25rem 0;
    }
    .loan-metric-lbl {
        font-size: 0.82rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# DATABASE OPERATIONS & SAFE MIGRATION
# =========================================================

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS valuations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            lot_area REAL,
            living_area REAL,
            bedrooms INTEGER,
            bathrooms INTEGER,
            quality INTEGER,
            year_built INTEGER,
            garage INTEGER,
            predicted_price REAL,
            bhk TEXT,
            floors TEXT,
            construction_cost REAL,
            neighborhood TEXT
        )
    """)

    cursor.execute("PRAGMA table_info(valuations)")
    existing_cols = [row[1] for row in cursor.fetchall()]

    new_cols = {
        "country": "TEXT",
        "state": "TEXT",
        "city": "TEXT",
        "local_area": "TEXT",
        "house_model": "TEXT",
        "budget": "REAL",
        "construction_quality": "TEXT",
        "rating": "TEXT",
        "eco_score": "TEXT",
        "additional_features": "TEXT"
    }

    for col, col_type in new_cols.items():
        if col not in existing_cols:
            cursor.execute(f"ALTER TABLE valuations ADD COLUMN {col} {col_type}")

    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def register_user(name, email, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (name, email, password)
            VALUES (?, ?, ?)
        """, (name.strip(), email.strip().lower(), hash_password(password)))
        conn.commit()
        result = True
    except sqlite3.IntegrityError:
        result = False
    conn.close()
    return result

def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, password
        FROM users
        WHERE LOWER(email) = ?
    """, (email.strip().lower(),))
    user = cursor.fetchone()
    conn.close()
    if user and user[1] == hash_password(password):
        return user[0]
    return None

def save_valuation(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO valuations (
            email, lot_area, living_area, bedrooms, bathrooms, quality,
            year_built, garage, predicted_price, bhk, floors,
            construction_cost, neighborhood, country, state, city,
            local_area, house_model, budget, construction_quality,
            rating, eco_score, additional_features
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()

def get_valuations(email):
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT
            neighborhood AS "Location",
            house_model AS "House Model",
            bhk AS "Configuration",
            floors AS "Floors",
            living_area AS "Living Area (sq ft)",
            bedrooms AS "Bedrooms",
            bathrooms AS "Bathrooms",
            predicted_price AS "Valuation",
            construction_cost AS "Est. Construction Cost",
            rating AS "Rating",
            eco_score AS "Eco Score"
        FROM valuations
        WHERE email = ?
        ORDER BY id DESC
    """, conn, params=(email,))
    conn.close()
    return df

create_database()

# =========================================================
# LOAD ML MODEL
# =========================================================

try:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        model = joblib.load(MODEL_FILE)
        features = joblib.load(FEATURE_FILE)
except Exception as e:
    st.error(f"❌ Unable to load ML model files: {e}")
    st.stop()

# =========================================================
# NUMBER FORMATTING & NUMBER TO WORDS ENGINE (WORLDWIDE)
# =========================================================
# Handled comprehensively by worldwide_data module supporting 196+ currencies worldwide

# =========================================================
# DYNAMIC PROPERTY RATING & ECO SCORE
# =========================================================

def calculate_dynamic_property_rating(
    overall_qual, living_area, bedrooms, bathrooms, garage,
    construction_quality, floors, balconies, parking_spaces,
    house_model, additional_features=None
):
    score = 1.0 + (overall_qual / 10.0) * 2.2
    
    if construction_quality == "Luxury":
        score += 0.70
    elif construction_quality == "Premium":
        score += 0.45
    elif construction_quality == "Standard":
        score += 0.20
        
    if bedrooms > 0:
        area_per_bed = living_area / bedrooms
        if area_per_bed >= 550:
            score += 0.35
        elif area_per_bed >= 400:
            score += 0.20
        elif area_per_bed < 250:
            score -= 0.15

        bath_ratio = bathrooms / bedrooms
        if bath_ratio >= 1.0:
            score += 0.30
        elif bath_ratio >= 0.7:
            score += 0.15
        elif bath_ratio < 0.5:
            score -= 0.20

    total_parking = garage + parking_spaces
    if total_parking >= 3:
        score += 0.20
    elif total_parking >= 1:
        score += 0.10

    if balconies >= 2:
        score += 0.15
    elif balconies == 1:
        score += 0.08

    model_boost = {
        "Premium House": 0.40,
        "Luxury Villa": 0.35,
        "Contemporary House": 0.25,
        "Modern House": 0.20,
        "Traditional House": 0.15,
        "Simple Family House": 0.05,
        "Compact House": 0.00
    }.get(house_model, 0.10)
    score += model_boost

    if additional_features:
        if "Swimming Pool" in additional_features:
            score += 0.30
        if "Lift / Elevator" in additional_features:
            score += 0.20
        if "Home Office" in additional_features:
            score += 0.10
        if "Terrace Garden" in additional_features:
            score += 0.10
        if "Solar Panels" in additional_features:
            score += 0.10
        if "Garden / Open Space" in additional_features:
            score += 0.10

    score = min(5.0, max(2.0, score))
    rounded_score = round(score, 1)

    full_stars = int(rounded_score)
    half_star = (rounded_score - full_stars) >= 0.4
    empty_stars = 5 - full_stars - (1 if half_star else 0)
    star_str = ("⭐" * full_stars) + ("½" if half_star else "") + ("☆" * empty_stars)

    if rounded_score >= 4.7:
        tag = "Exceptional Luxury"
    elif rounded_score >= 4.2:
        tag = "Superior Modern Spec"
    elif rounded_score >= 3.8:
        tag = "Highly Desirable"
    elif rounded_score >= 3.2:
        tag = "Good Quality Standard"
    else:
        tag = "Standard Living"

    return star_str, rounded_score, tag

def calculate_eco_score(additional_features, living_area, house_model):
    eco = 2.5
    features = additional_features or []
    
    if "Solar Panels" in features:
        eco += 1.0
    if "Terrace Garden" in features:
        eco += 0.5
    if "Garden / Open Space" in features:
        eco += 0.5
    if house_model == "Compact House":
        eco += 0.4
    if "Home Office" in features:
        eco += 0.2
    if "Swimming Pool" in features:
        eco -= 0.2
        
    eco = min(5.0, max(2.0, eco))
    rounded_eco = round(eco, 1)
    
    full_stars = int(rounded_eco)
    half_star = (rounded_eco - full_stars) >= 0.4
    empty_stars = 5 - full_stars - (1 if half_star else 0)
    eco_stars = ("★" * full_stars) + ("½" if half_star else "") + ("☆" * empty_stars)
    
    if rounded_eco >= 4.4:
        eco_tag = "Net-Zero Ready & Sustainable"
    elif rounded_eco >= 3.7:
        eco_tag = "High Energy Efficiency"
    elif rounded_eco >= 3.0:
        eco_tag = "Standard Green Features"
    else:
        eco_tag = "Basic Environmental Profile"
        
    return eco_stars, rounded_eco, eco_tag

# =========================================================
# 4-TIER HIERARCHICAL LOCATION SYSTEM (WORLDWIDE 196+ COUNTRIES)
# =========================================================

# Backwards-compatible lookup dynamically populated from worldwide registry
LOCATION_DATA = {c: get_country_config(c) for c in ORDERED_COUNTRY_LIST}

# =========================================================
# REAL DYNAMIC 3D ARCHITECTURAL HOUSE ENGINE
# =========================================================

HOUSE_THEMES = {
    "Modern House": {
        "footprint": (12.0, 8.5),
        "wall_color": "#F8FAFC",
        "accent_color": "#1E293B",
        "roof_type": "parapet_pergola",
        "roof_color": "#334155",
        "deck_color": "#CBD5E1",
        "door_color": "#0F172A",
        "window_frame": "#0F172A",
        "balcony_type": "glass",
        "carport_type": "modern_steel",
        "description": "Minimalist cubic geometry with floor-to-ceiling glass, black aluminum trims & rooftop terrace pergola."
    },
    "Luxury Villa": {
        "footprint": (14.5, 9.5),
        "wall_color": "#FDFBF7",
        "accent_color": "#C4A482",
        "roof_type": "hipped_tile",
        "roof_color": "#B85042",
        "deck_color": "#E2D4C0",
        "door_color": "#4A2E18",
        "window_frame": "#78350F",
        "balcony_type": "classic_baluster",
        "carport_type": "port_cochere",
        "description": "Grand Mediterranean villa featuring Spanish terracotta hipped roof, portico pillars & expansive verandas."
    },
    "Simple Family House": {
        "footprint": (11.0, 8.0),
        "wall_color": "#E8D5B5",
        "accent_color": "#C88264",
        "roof_type": "gabled_shingle",
        "roof_color": "#334155",
        "deck_color": "#D1D5DB",
        "door_color": "#8B5E3C",
        "window_frame": "#FFFFFF",
        "balcony_type": "picket_rail",
        "carport_type": "traditional_canopy",
        "description": "Warm suburban family home with classic A-frame pitched gabled roof, welcoming porch & multi-pane windows."
    },
    "Contemporary House": {
        "footprint": (12.5, 9.0),
        "wall_color": "#F1F5F9",
        "accent_color": "#A0522D",
        "roof_type": "shed_monopitch",
        "roof_color": "#475569",
        "deck_color": "#CBD5E1",
        "door_color": "#18181B",
        "window_frame": "#18181B",
        "balcony_type": "metal_slats",
        "carport_type": "modern_steel",
        "description": "Dynamic interlocking volumes with rich cedar timber panels, angular shed roof & corner ribbon glass."
    },
    "Traditional House": {
        "footprint": (12.5, 9.0),
        "wall_color": "#FDF6E2",
        "accent_color": "#A34828",
        "roof_type": "hipped_tile",
        "roof_color": "#A34828",
        "deck_color": "#E2D4C0",
        "door_color": "#5C2C16",
        "window_frame": "#78350F",
        "balcony_type": "timber_rail",
        "carport_type": "traditional_canopy",
        "description": "Regional heritage residence with Mangalore sloping tile roof, turned wooden pillars & shaded sit-out verandah."
    },
    "Compact House": {
        "footprint": (9.5, 7.5),
        "wall_color": "#E2E8F0",
        "accent_color": "#334155",
        "roof_type": "shed_monopitch",
        "roof_color": "#334155",
        "deck_color": "#94A3B8",
        "door_color": "#0F172A",
        "window_frame": "#0F172A",
        "balcony_type": "glass",
        "carport_type": "integrated_tuck",
        "description": "Space-efficient smart vertical micro-architecture with integrated carport & streamlined modern facade."
    },
    "Premium House": {
        "footprint": (14.0, 9.5),
        "wall_color": "#FFFFFF",
        "accent_color": "#0F172A",
        "roof_type": "parapet_pergola",
        "roof_color": "#0F172A",
        "deck_color": "#E2E8F0",
        "door_color": "#D97706",
        "window_frame": "#D97706",
        "balcony_type": "glass",
        "carport_type": "modern_steel",
        "description": "Ultra-luxury executive residence with double-height entrance glass, bronze metallic accents & sky lounge terrace."
    }
}

def add_box(fig, x0, x1, y0, y1, z0, z1, color, opacity=1.0, name=None, showlegend=False):
    vertices = [
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)
    ]
    faces = [
        (0, 1, 2), (0, 2, 3), (4, 6, 5), (4, 7, 6),
        (0, 4, 5), (0, 5, 1), (1, 5, 6), (1, 6, 2),
        (2, 6, 7), (2, 7, 3), (3, 7, 4), (3, 4, 0)
    ]
    xs, ys, zs = zip(*vertices)
    i, j, k = zip(*faces)
    
    fig.add_trace(
        go.Mesh3d(
            x=xs, y=ys, z=zs, i=i, j=j, k=k,
            color=color,
            opacity=opacity,
            flatshading=True,
            lighting=dict(ambient=0.75, diffuse=0.8, specular=0.25, roughness=0.5, fresnel=0.2),
            lightposition=dict(x=100, y=200, z=1000),
            hovertemplate=(name + "<extra></extra>" if name else None),
            name=name or "",
            showlegend=showlegend
        )
    )

def add_text(fig, x, y, z, text, size=13, color="#1e293b"):
    fig.add_trace(
        go.Scatter3d(
            x=[x], y=[y], z=[z],
            mode="text",
            text=[text],
            textfont=dict(size=size, color=color, family="Plus Jakarta Sans"),
            hovertemplate=f"{text}<extra></extra>",
            showlegend=False
        )
    )

def add_procedural_tree(fig, tx, ty, tz=0, trunk_h=1.6, foliage_r=1.2, tree_type="deciduous"):
    # Removed decorative tree to maintain clean appraisal focus
    pass

def add_pathway_light(fig, lx, ly, lz=0, h=0.85):
    # Removed decorative pathway light to maintain clean appraisal focus
    pass


# ---------------------------------------------------------
# ROOF MESHES
# ---------------------------------------------------------

def add_corner_quoins(fig, x, y, z0, z1, width=0.45, quoin_color="#D4C2AA"):
    h_step = 0.55
    curr_z = z0
    idx = 0
    while curr_z < z1 - 0.1:
        w = width if (idx % 2 == 0) else width * 0.65
        add_box(fig, x - w/2, x + w/2, y - w/2, y + w/2, curr_z, min(z1, curr_z + h_step - 0.08), quoin_color, 1.0, "Stone Quoin")
        curr_z += h_step
        idx += 1

def add_window_with_shutters(fig, x0, x1, y, z0, z1, frame_color="#FFFFFF", glass_color="#93C5FD", shutter_color="#1E3A8A"):
    add_box(fig, x0, x1, y - 0.08, y + 0.08, z0, z1, frame_color, 1.0, "Sash Window Frame")
    add_box(fig, x0 + 0.08, x1 - 0.08, y - 0.02, y + 0.02, z0 + 0.08, z1 - 0.08, glass_color, 0.5, "Window Glass")
    xm = (x0 + x1) / 2
    zm = (z0 + z1) / 2
    add_box(fig, xm - 0.03, xm + 0.03, y - 0.04, y + 0.04, z0 + 0.08, z1 - 0.08, frame_color, 1.0, "Window Grille")
    add_box(fig, x0 + 0.08, x1 - 0.08, y - 0.04, y + 0.04, zm - 0.03, zm + 0.03, frame_color, 1.0, "Window Grille")
    sw = 0.45
    add_box(fig, x0 - sw - 0.04, x0 - 0.04, y - 0.06, y + 0.06, z0 - 0.05, z1 + 0.05, shutter_color, 1.0, "Louvered Shutter")
    add_box(fig, x1 + 0.04, x1 + sw + 0.04, y - 0.06, y + 0.06, z0 - 0.05, z1 + 0.05, shutter_color, 1.0, "Louvered Shutter")

def add_gabled_roof(fig, x0, x1, y0, y1, z_base, roof_height=2.4, roof_color="#334155", gable_color="#F8FAFC", add_dormer=False):
    dx, dy = 0.5, 0.5
    rx0, rx1 = x0 - dx, x1 + dx
    ry0, ry1 = y0 - dy, y1 + dy
    xm = (rx0 + rx1) / 2
    zr = z_base + roof_height
    v = [
        (rx0, ry0, z_base), (xm, ry0, zr), (xm, ry1, zr), (rx0, ry1, z_base),
        (rx1, ry0, z_base), (rx1, ry1, z_base)
    ]
    i = [0, 0, 1, 1]
    j = [1, 2, 4, 5]
    k = [2, 3, 5, 2]
    xs, ys, zs = zip(*v)
    fig.add_trace(go.Mesh3d(x=xs, y=ys, z=zs, i=i, j=j, k=k, color=roof_color, opacity=1.0, flatshading=True, name="Pitched Gabled Roof", showlegend=False))
    
    gv = [
        (x0, y0, z_base), (xm, y0, zr - 0.08), (x1, y0, z_base),
        (x0, y1, z_base), (xm, y1, zr - 0.08), (x1, y1, z_base)
    ]
    gi, gj, gk = [0, 3], [1, 4], [2, 5]
    gxs, gys, gzs = zip(*gv)
    fig.add_trace(go.Mesh3d(x=gxs, y=gys, z=gzs, i=gi, j=gj, k=gk, color=gable_color, opacity=1.0, flatshading=True, name="Gable Wall", showlegend=False))

    if add_dormer:
        d_x0, d_x1 = xm - 1.2, xm + 1.2
        d_y0, d_y1 = ry0 + 0.3, ry0 + 2.5
        d_zb = z_base + 0.4
        d_zh = d_zb + 1.4
        add_box(fig, d_x0, d_x1, d_y0, d_y1, d_zb, d_zh, gable_color, 1.0, "Dormer Walls")
        add_box(fig, d_x0 + 0.3, d_x1 - 0.3, d_y0 - 0.05, d_y0 + 0.05, d_zb + 0.3, d_zh - 0.2, "#FFFFFF", 1.0, "Dormer Window Frame")
        add_box(fig, d_x0 + 0.38, d_x1 - 0.38, d_y0 - 0.02, d_y0 + 0.02, d_zb + 0.38, d_zh - 0.28, "#93C5FD", 0.6, "Dormer Window Glass")
        d_xm = (d_x0 + d_x1) / 2
        d_zr = d_zh + 0.65
        dv = [
            (d_x0 - 0.2, d_y0 - 0.2, d_zh), (d_xm, d_y0 - 0.2, d_zr), (d_xm, d_y1 + 0.2, d_zr), (d_x0 - 0.2, d_y1 + 0.2, d_zh),
            (d_x1 + 0.2, d_y0 - 0.2, d_zh), (d_x1 + 0.2, d_y1 + 0.2, d_zh)
        ]
        fig.add_trace(go.Mesh3d(x=[p[0] for p in dv], y=[p[1] for p in dv], z=[p[2] for p in dv], i=i, j=j, k=k, color=roof_color, opacity=1.0, flatshading=True, name="Dormer Gable Roof", showlegend=False))

def add_hipped_roof(fig, x0, x1, y0, y1, z_base, roof_height=2.3, roof_color="#B85042", is_luxury_villa=False):
    dx, dy = 0.6, 0.6
    rx0, rx1 = x0 - dx, x1 + dx
    ry0, ry1 = y0 - dy, y1 + dy
    offset = (ry1 - ry0) / 2.2
    ym = (ry0 + ry1) / 2
    zr = z_base + roof_height
    
    c0 = (rx0, ry0, z_base)
    c1 = (rx1, ry0, z_base)
    c2 = (rx1, ry1, z_base)
    c3 = (rx0, ry1, z_base)
    r0 = (rx0 + offset, ym, zr)
    r1 = (rx1 - offset, ym, zr)
    v = [c0, c1, c2, c3, r0, r1]
    i = [0, 0, 3, 3, 0, 1]
    j = [4, 5, 2, 5, 3, 5]
    k = [5, 1, 5, 4, 4, 2]
    xs, ys, zs = zip(*v)
    fig.add_trace(go.Mesh3d(x=xs, y=ys, z=zs, i=i, j=j, k=k, color=roof_color, opacity=1.0, flatshading=True, name="Spanish Terracotta Hipped Roof", showlegend=False))

    if is_luxury_villa:
        cx0, cx1 = 5.2, 9.8
        cy0, cy1 = -1.8, 4.2
        c_zb = z_base + 0.35
        c_zh = c_zb + 2.7
        c_ym = (cy0 + cy1) / 2
        c_off = (cy1 - cy0) / 2.2
        p0 = (cx0 - 0.3, cy0 - 0.3, c_zb)
        p1 = (cx1 + 0.3, cy0 - 0.3, c_zb)
        p2 = (cx1 + 0.3, cy1 + 0.3, c_zb)
        p3 = (cx0 - 0.3, cy1 + 0.3, c_zb)
        pr0 = (cx0 + c_off, c_ym, c_zh)
        pr1 = (cx1 - c_off, c_ym, c_zh)
        pv = [p0, p1, p2, p3, pr0, pr1]
        fig.add_trace(go.Mesh3d(x=[p[0] for p in pv], y=[p[1] for p in pv], z=[p[2] for p in pv], i=i, j=j, k=k, color="#991B1B", opacity=1.0, flatshading=True, name="Pavilion Hipped Crown", showlegend=False))
        add_box(fig, 7.35, 7.65, c_ym - 0.15, c_ym + 0.15, c_zh, c_zh + 0.8, "#D97706", 1.0, "Villa Golden Finial")

def add_parapet_flat_roof(fig, x0, x1, y0, y1, z_base, wall_color="#F8FAFC", deck_color="#94A3B8", accent_color="#1E293B", has_skylounge=False):
    add_box(fig, x0 - 0.2, x1 + 0.2, y0 - 0.2, y1 + 0.2, z_base, z_base + 0.15, deck_color, 1.0, "Rooftop Terrace Deck")
    h_parapet = 0.85
    t = 0.18
    add_box(fig, x0 - 0.2, x1 + 0.2, y0 - 0.2, y0 - 0.2 + t, z_base + 0.15, z_base + 0.15 + h_parapet, wall_color, 1.0, "Parapet Wall")
    add_box(fig, x0 - 0.2, x1 + 0.2, y1 + 0.2 - t, y1 + 0.2, z_base + 0.15, z_base + 0.15 + h_parapet, wall_color, 1.0, "Parapet Wall")
    add_box(fig, x0 - 0.2, x0 - 0.2 + t, y0 - 0.2, y1 + 0.2, z_base + 0.15, z_base + 0.15 + h_parapet, wall_color, 1.0, "Parapet Wall")
    add_box(fig, x1 + 0.2 - t, x1 + 0.2, y0 - 0.2, y1 + 0.2, z_base + 0.15, z_base + 0.15 + h_parapet, wall_color, 1.0, "Parapet Wall")
    
    if has_skylounge:
        lx0, lx1 = 3.5, 10.5
        ly0, ly1 = 1.5, 7.5
        lz0 = z_base + 0.15
        lz1 = lz0 + 2.5
        add_box(fig, lx0, lx1, ly0, ly1, lz0, lz0 + 0.1, "#D97706", 1.0, "Sky Lounge Flooring")
        add_box(fig, lx0, lx1, ly0, ly1, lz1, lz1 + 0.2, "#0F172A", 1.0, "Sky Lounge Overhang Fascia")
        add_box(fig, lx0, lx1, ly0 - 0.05, ly0 + 0.05, lz0 + 0.1, lz1, "#7DD3FC", 0.45, "Sky Lounge Panoramic Glass")
        add_box(fig, lx0, lx1, ly1 - 0.05, ly1 + 0.05, lz0 + 0.1, lz1, "#7DD3FC", 0.45, "Sky Lounge Panoramic Glass")
        add_box(fig, lx0 - 0.05, lx0 + 0.05, ly0, ly1, lz0 + 0.1, lz1, "#7DD3FC", 0.45, "Sky Lounge Panoramic Glass")
        add_box(fig, lx1 - 0.05, lx1 + 0.05, ly0, ly1, lz0 + 0.1, lz1, "#7DD3FC", 0.45, "Sky Lounge Panoramic Glass")
        for cx in [lx0, lx1]:
            for cy in [ly0, ly1]:
                add_box(fig, cx - 0.1, cx + 0.1, cy - 0.1, cy + 0.1, lz0, lz1, "#D97706", 1.0, "Bronze Column")
    else:
        add_box(fig, x1 - 3.5, x1 - 0.5, y1 - 3.2, y1 - 0.5, z_base + 0.15, z_base + 2.3, wall_color, 1.0, "Staircase Headhouse")
        px0, px1 = x0 + 1.0, x0 + 6.0
        py0, py1 = y0 + 1.5, y0 + 6.0
        pz = z_base + 0.15
        for cx in [px0, px1]:
            for cy in [py0, py1]:
                add_box(fig, cx - 0.08, cx + 0.08, cy - 0.08, cy + 0.08, pz, pz + 2.4, accent_color, 1.0, "Pergola Column")
        add_box(fig, px0 - 0.2, px1 + 0.2, py0 - 0.08, py0 + 0.08, pz + 2.4, pz + 2.55, accent_color, 1.0, "Pergola Beam")
        add_box(fig, px0 - 0.2, px1 + 0.2, py1 - 0.08, py1 + 0.08, pz + 2.4, pz + 2.55, accent_color, 1.0, "Pergola Beam")
        for lx in range(6):
            cx = px0 + lx * ((px1 - px0) / 5)
            add_box(fig, cx - 0.04, cx + 0.04, py0 - 0.25, py1 + 0.25, pz + 2.55, pz + 2.68, "#B45309", 1.0, "Timber Louver")

def add_shed_roof(fig, x0, x1, y0, y1, z_base, roof_height=2.0, roof_color="#475569", wall_color="#F1F5F9"):
    dx, dy = 0.6, 0.6
    rx0, rx1 = x0 - dx, x1 + dx
    ry0, ry1 = y0 - dy, y1 + dy
    z_low = z_base + 0.3
    z_high = z_base + roof_height
    v = [(rx0, ry0, z_low), (rx1, ry0, z_low), (rx1, ry1, z_high), (rx0, ry1, z_high)]
    i = [0, 0]
    j = [1, 2]
    k = [2, 3]
    xs, ys, zs = zip(*v)
    fig.add_trace(go.Mesh3d(x=xs, y=ys, z=zs, i=i, j=j, k=k, color=roof_color, opacity=1.0, flatshading=True, name="Angled Shed Roof", showlegend=False))

def add_modern_house_shell(fig, floor_index, floor_count, z, fp_w, fp_d, wall_color, accent_color, frame_color, door_color):
    h = 3.15
    z0, z1 = z, z + h
    add_box(fig, -0.15, fp_w + 0.15, -0.15, fp_d + 0.15, z0, z0 + 0.18, accent_color, 1.0, "Floor Slab Trim")
    add_box(fig, 0, fp_w, fp_d - 0.12, fp_d + 0.12, z0 + 0.18, z1, wall_color, 1.0, "Rear Wall")
    add_box(fig, -0.12, 0.12, 0, fp_d, z0 + 0.18, z1, wall_color, 1.0, "Side Wall Left")
    add_box(fig, fp_w - 0.12, fp_w + 0.12, 0, fp_d, z0 + 0.18, z1, wall_color, 1.0, "Side Wall Right")

    if floor_index == 0:
        add_box(fig, 0.4, 6.4, -0.06, 0.06, z0 + 0.18, z1 - 0.1, "#93C5FD", 0.45, "Curtain Wall Glass")
        for mx in [0.4, 2.4, 4.4, 6.4]:
            add_box(fig, mx - 0.04, mx + 0.04, -0.08, 0.08, z0 + 0.18, z1, "#0F172A", 1.0, "Mullion")
        add_box(fig, 0.4, 6.4, -0.08, 0.08, z0 + 1.6, z0 + 1.7, "#0F172A", 1.0, "Mullion Transom")
        add_box(fig, 6.8, 8.2, -0.06, 0.06, z0 + 0.18, z0 + 2.5, door_color, 1.0, "Modern Pivot Door")
        add_box(fig, 8.0, 8.08, -0.10, -0.04, z0 + 0.8, z0 + 1.8, "#E2E8F0", 1.0, "Stainless Door Handle")
        add_box(fig, 6.4, 8.5, -0.12, 0.12, z0 + 2.5, z1, wall_color, 1.0, "Wall Header")
        add_box(fig, 6.2, 8.8, -1.2, 0.1, z0 + 2.65, z0 + 2.8, accent_color, 1.0, "Entrance Canopy")
        add_box(fig, 8.5, fp_w, -0.12, 0.12, z0 + 0.18, z1, wall_color, 1.0, "Exterior Wall")
        for sx in [9.0, 9.6, 10.2, 10.8, 11.4]:
            add_box(fig, sx - 0.04, sx + 0.04, -0.18, -0.12, z0 + 0.18, z1, accent_color, 1.0, "Architectural Slat")
    else:
        add_box(fig, 0, 7.0, -1.2, 0, z0, z0 + 0.2, "#0F172A", 1.0, "Cantilever Soffit Panel")
        add_box(fig, 0, 7.0, -1.3, -1.1, z0 + 0.18, z1, wall_color, 1.0, "Cantilever Front Wall")
        add_box(fig, 1.0, 6.0, -1.28, -1.12, z0 + 0.8, z0 + 2.4, frame_color, 1.0, "Upper Ribbon Frame")
        add_box(fig, 1.08, 5.92, -1.22, -1.18, z0 + 0.88, z0 + 2.32, "#93C5FD", 0.45, "Upper Ribbon Glass")
        add_box(fig, -0.12, 0.12, -1.2, 0, z0 + 0.18, z1, wall_color, 1.0, "Cantilever Side Wall")
        add_box(fig, 6.88, 7.12, -1.2, 0, z0 + 0.18, z1, wall_color, 1.0, "Cantilever Side Wall")
        add_box(fig, 7.0, fp_w, -0.12, 0.12, z0 + 0.18, z1, wall_color, 1.0, "Upper Exterior Wall")
        add_box(fig, 8.5, 11.0, -0.08, 0.08, z0 + 1.0, z0 + 2.3, frame_color, 1.0, "Upper Window Frame")
        add_box(fig, 8.58, 10.92, -0.02, 0.02, z0 + 1.08, z0 + 2.22, "#93C5FD", 0.45, "Upper Window Glass")

def add_luxury_villa_shell(fig, floor_index, floor_count, z, fp_w, fp_d, wall_color, accent_color, frame_color, door_color):
    h = 3.15
    z0, z1 = z, z + h
    add_box(fig, -0.18, fp_w + 0.18, -0.18, fp_d + 0.18, z0, z0 + 0.22, accent_color, 1.0, "Molded Stone Base")
    for qx in [0.2, fp_w - 0.2]:
        for qy in [0.2, fp_d - 0.2]:
            add_corner_quoins(fig, qx, qy, z0, z1, width=0.5, quoin_color="#D4C2AA")
    add_box(fig, 5.5, 9.5, -1.5, 0.0, z0, z0 + 0.2, accent_color, 1.0, "Pavilion Plinth")
    add_box(fig, 5.4, 9.6, -1.6, -1.4, z0 + 0.2, z1, wall_color, 1.0, "Pavilion Front Wall")
    add_box(fig, 5.3, 5.5, -1.5, 0.0, z0 + 0.2, z1, wall_color, 1.0, "Pavilion Left Return")
    add_box(fig, 9.5, 9.7, -1.5, 0.0, z0 + 0.2, z1, wall_color, 1.0, "Pavilion Right Return")
    add_corner_quoins(fig, 5.5, -1.5, z0, z1, width=0.45, quoin_color="#D4C2AA")
    add_corner_quoins(fig, 9.5, -1.5, z0, z1, width=0.45, quoin_color="#D4C2AA")
    add_box(fig, 0, 5.5, -0.12, 0.12, z0 + 0.18, z1, wall_color, 1.0, "Villa Left Wing Wall")
    add_box(fig, 9.5, fp_w, -0.12, 0.12, z0 + 0.18, z1, wall_color, 1.0, "Villa Right Wing Wall")
    add_box(fig, 0, fp_w, fp_d - 0.12, fp_d + 0.12, z0 + 0.18, z1, wall_color, 1.0, "Villa Rear Wall")
    add_box(fig, -0.12, 0.12, 0, fp_d, z0 + 0.18, z1, wall_color, 1.0, "Villa Side Wall")
    add_box(fig, fp_w - 0.12, fp_w + 0.12, 0, fp_d, z0 + 0.18, z1, wall_color, 1.0, "Villa Side Wall")

    for wx0, wx1 in [(1.5, 3.8), (11.2, 13.5)]:
        add_box(fig, wx0, wx1, -0.16, 0.16, z0 + 0.7, z0 + 0.85, "#C4A482", 1.0, "Molded Stone Sill")
        add_box(fig, wx0 + 0.15, wx1 - 0.15, -0.10, 0.10, z0 + 0.85, z0 + 2.5, frame_color, 1.0, "Window Frame")
        add_box(fig, wx0 + 0.22, wx1 - 0.22, -0.02, 0.02, z0 + 0.92, z0 + 2.42, "#93C5FD", 0.45, "Window Glass")
        add_box(fig, wx0, wx1, -0.16, 0.16, z0 + 2.5, z0 + 2.7, "#C4A482", 1.0, "Classical Pediment Header")

    if floor_index == 0:
        add_box(fig, 5.8, 6.2, -2.4, -2.0, 0, 3.15, "#E6CCB2", 1.0, "Tuscan Portico Column")
        add_box(fig, 8.8, 9.2, -2.4, -2.0, 0, 3.15, "#E6CCB2", 1.0, "Tuscan Portico Column")
        add_box(fig, 5.5, 9.5, -2.6, -1.4, 3.15, 3.4, "#C4A482", 1.0, "Classical Portico Cornice")
        add_box(fig, 6.7, 8.3, -1.58, -1.44, z0 + 0.2, z0 + 2.6, door_color, 1.0, "Arched Double Doors")
        add_box(fig, 7.35, 7.42, -1.62, -1.56, z0 + 1.1, z0 + 1.4, "#D97706", 1.0, "Gold Door Handle")
        add_box(fig, 7.58, 7.65, -1.62, -1.56, z0 + 1.1, z0 + 1.4, "#D97706", 1.0, "Gold Door Handle")
    else:
        add_box(fig, 6.8, 8.2, -1.55, -1.45, z0 + 0.2, z0 + 2.5, frame_color, 1.0, "French Balcony Doors")
        add_box(fig, 6.88, 8.12, -1.52, -1.48, z0 + 0.28, z0 + 2.42, "#93C5FD", 0.45, "French Door Glass")
        add_box(fig, 6.0, 9.0, -2.4, -1.5, z0, z0 + 0.2, "#C4A482", 1.0, "Pavilion Balcony Stone Slab")
        add_box(fig, 6.0, 9.0, -2.4, -2.28, z0 + 0.2, z0 + 1.2, "#E2D4C0", 1.0, "Classical Stone Balustrade")
        add_box(fig, 6.0, 6.12, -2.4, -1.5, z0 + 0.2, z0 + 1.2, "#E2D4C0", 1.0, "Classical Stone Balustrade")
        add_box(fig, 8.88, 9.0, -2.4, -1.5, z0 + 0.2, z0 + 1.2, "#E2D4C0", 1.0, "Classical Stone Balustrade")

def add_family_house_shell(fig, floor_index, floor_count, z, fp_w, fp_d, wall_color, accent_color, frame_color, door_color):
    h = 3.15
    z0, z1 = z, z + h
    add_box(fig, -0.15, fp_w + 0.15, -0.15, fp_d + 0.15, z0, z0 + 0.18, "#D1D5DB", 1.0, "Foundation Plinth")
    add_box(fig, 0, fp_w, -0.12, 0.12, z0 + 0.18, z1, wall_color, 1.0, "Family House Front Wall")
    add_box(fig, 0, fp_w, fp_d - 0.12, fp_d + 0.12, z0 + 0.18, z1, wall_color, 1.0, "Family House Rear Wall")
    add_box(fig, -0.12, 0.12, 0, fp_d, z0 + 0.18, z1, wall_color, 1.0, "Family House Side Wall")
    add_box(fig, fp_w - 0.12, fp_w + 0.12, 0, fp_d, z0 + 0.18, z1, wall_color, 1.0, "Family House Side Wall")

    if floor_index == 0:
        add_box(fig, 0.5, fp_w - 0.5, -2.2, 0.0, 0.0, 0.22, "#C88264", 1.0, "Porch Wooden Deck")
        for cx in [0.8, 3.8, 7.2, fp_w - 0.8]:
            add_box(fig, cx - 0.12, cx + 0.12, -2.1, -1.86, 0.22, 2.7, "#FFFFFF", 1.0, "Porch Square Column")
        add_box(fig, 0.2, fp_w - 0.2, -2.4, 0.1, 2.7, 2.85, "#334155", 1.0, "Porch Roof Eave")
        add_box(fig, 0.8, 3.8, -2.1, -2.0, 0.22, 1.1, "#FFFFFF", 0.7, "White Picket Railing")
        add_box(fig, 7.2, fp_w - 0.8, -2.1, -2.0, 0.22, 1.1, "#FFFFFF", 0.7, "White Picket Railing")
        add_box(fig, 4.6, 5.8, -0.06, 0.06, z0 + 0.22, z0 + 2.4, door_color, 1.0, "Paneled Entry Door")
        add_box(fig, 5.85, 6.35, -0.04, 0.04, z0 + 0.6, z0 + 2.4, "#93C5FD", 0.5, "Door Sidelight Window")
        add_window_with_shutters(fig, 1.5, 3.0, 0.0, z0 + 0.9, z0 + 2.3, frame_color, "#93C5FD", "#1E3A8A")
        add_window_with_shutters(fig, 7.8, 9.3, 0.0, z0 + 0.9, z0 + 2.3, frame_color, "#93C5FD", "#1E3A8A")
    else:
        add_window_with_shutters(fig, 1.5, 3.2, 0.0, z0 + 0.9, z0 + 2.3, frame_color, "#93C5FD", "#1E3A8A")
        add_window_with_shutters(fig, 4.8, 6.2, 0.0, z0 + 0.9, z0 + 2.3, frame_color, "#93C5FD", "#1E3A8A")
        add_window_with_shutters(fig, 7.8, 9.5, 0.0, z0 + 0.9, z0 + 2.3, frame_color, "#93C5FD", "#1E3A8A")

def add_contemporary_house_shell(fig, floor_index, floor_count, z, fp_w, fp_d, wall_color, accent_color, frame_color, door_color):
    h = 3.15
    z0, z1 = z, z + h
    add_box(fig, -0.15, fp_w + 0.15, -0.15, fp_d + 0.15, z0, z0 + 0.18, "#334155", 1.0, "Architectural Slab Trim")
    add_box(fig, 0, 6.2, -0.12, 0.12, z0 + 0.18, z1, "#64748B", 1.0, "Concrete Facade Volume")
    add_box(fig, -0.12, 0.12, 0, fp_d, z0 + 0.18, z1, "#64748B", 1.0, "Concrete Side Wall")
    add_box(fig, 5.8, fp_w, -0.5, -0.35, z0 + 0.18, z1, "#B45309", 1.0, "Cedar Timber Wall")
    add_box(fig, 5.7, 5.9, -0.5, 0.0, z0 + 0.18, z1, "#B45309", 1.0, "Cedar Return Wall")
    add_box(fig, fp_w - 0.12, fp_w + 0.12, -0.5, fp_d, z0 + 0.18, z1, "#B45309", 1.0, "Cedar Side Wall")
    add_box(fig, 0, fp_w, fp_d - 0.12, fp_d + 0.12, z0 + 0.18, z1, wall_color, 1.0, "Rear Wall")

    add_box(fig, 0.1, 2.6, -0.06, 0.06, z0 + 0.8, z0 + 2.4, "#93C5FD", 0.45, "Corner Ribbon Glass Front")
    add_box(fig, -0.06, 0.06, 0.1, 2.6, z0 + 0.8, z0 + 2.4, "#93C5FD", 0.45, "Corner Ribbon Glass Side")
    add_box(fig, 0.08, 2.62, -0.08, 0.08, z0 + 0.75, z0 + 0.82, "#18181B", 1.0, "Black Window Sill")
    add_box(fig, -0.08, 0.08, 0.08, 2.62, z0 + 0.75, z0 + 0.82, "#18181B", 1.0, "Black Window Sill")

    if floor_index == 0:
        add_box(fig, 3.8, 5.2, -0.06, 0.06, z0 + 0.18, z0 + 2.5, door_color, 1.0, "Contemporary Entrance Door")
        add_box(fig, 3.4, 5.6, -1.4, 0.2, z0 + 2.65, z0 + 2.8, "#18181B", 1.0, "Steel Cantilever Canopy")
    else:
        add_box(fig, 7.0, 11.5, -0.42, -0.32, z0 + 1.1, z0 + 2.3, frame_color, 1.0, "Horizontal Ribbon Frame")
        add_box(fig, 7.08, 11.42, -0.38, -0.34, z0 + 1.18, z0 + 2.22, "#93C5FD", 0.45, "Horizontal Ribbon Glass")

def add_traditional_house_shell(fig, floor_index, floor_count, z, fp_w, fp_d, wall_color, accent_color, frame_color, door_color):
    h = 3.15
    z0, z1 = z, z + h
    add_box(fig, -0.15, fp_w + 0.15, -0.15, fp_d + 0.15, z0, z0 + 0.18, accent_color, 1.0, "Stone Plinth Trim")
    add_box(fig, 0, fp_w, -0.12, 0.12, z0 + 0.18, z1, wall_color, 1.0, "Heritage Front Wall")
    add_box(fig, 0, fp_w, fp_d - 0.12, fp_d + 0.12, z0 + 0.18, z1, wall_color, 1.0, "Heritage Rear Wall")
    add_box(fig, -0.12, 0.12, 0, fp_d, z0 + 0.18, z1, wall_color, 1.0, "Heritage Side Wall")
    add_box(fig, fp_w - 0.12, fp_w + 0.12, 0, fp_d, z0 + 0.18, z1, wall_color, 1.0, "Heritage Side Wall")

    if floor_index == 0:
        add_box(fig, 0, fp_w, -2.2, 0.0, 0.0, 0.35, "#C2410C", 1.0, "Terracotta Verandah Plinth")
        for px in [0.8, 3.5, 6.25, 9.0, fp_w - 0.8]:
            add_box(fig, px - 0.12, px + 0.12, -2.0, -1.76, 0.35, 2.75, "#78350F", 1.0, "Carved Teak Pillar")
            add_box(fig, px - 0.22, px + 0.22, -2.05, -1.71, 2.65, 2.75, "#78350F", 1.0, "Pillar Capital Bracket")
        add_box(fig, -0.3, fp_w + 0.3, -2.4, 0.1, 2.75, 2.95, "#A34828", 1.0, "Verandah Clay Tile Awning")
        add_box(fig, 5.2, 7.3, -0.08, 0.08, z0 + 0.35, z0 + 2.5, door_color, 1.0, "Carved Teak Double Door")
        add_box(fig, 5.0, 7.5, -0.12, 0.12, z0 + 2.5, z0 + 2.65, "#78350F", 1.0, "Ornamental Torana Lintel")
    else:
        for wx0, wx1 in [(1.8, 4.2), (8.3, 10.7)]:
            add_box(fig, wx0, wx1, -0.08, 0.08, z0 + 0.9, z0 + 2.4, frame_color, 1.0, "Wooden Window Frame")
            add_box(fig, wx0 + 0.1, wx1 - 0.1, -0.02, 0.02, z0 + 0.98, z0 + 2.32, "#93C5FD", 0.45, "Window Glass")
            add_box(fig, wx0 - 0.2, wx1 + 0.2, -0.6, 0.1, z0 + 2.45, z0 + 2.58, "#A34828", 1.0, "Terracotta Chajja Sunshade")

def add_compact_house_shell(fig, floor_index, floor_count, z, fp_w, fp_d, wall_color, accent_color, frame_color, door_color):
    h = 3.15
    z0, z1 = z, z + h
    add_box(fig, -0.15, fp_w + 0.15, -0.15, fp_d + 0.15, z0, z0 + 0.18, accent_color, 1.0, "Compact Base Trim")
    add_box(fig, 0, fp_w, fp_d - 0.12, fp_d + 0.12, z0 + 0.18, z1, wall_color, 1.0, "Rear Wall")
    add_box(fig, -0.12, 0.12, 0, fp_d, z0 + 0.18, z1, wall_color, 1.0, "Left Wall")

    if floor_index == 0:
        add_box(fig, 0, 4.5, -0.12, 0.12, z0 + 0.18, z1, wall_color, 1.0, "Compact Front Wall")
        add_box(fig, 1.8, 3.2, -0.06, 0.06, z0 + 0.18, z0 + 2.4, door_color, 1.0, "Recessed Entry Door")
        add_box(fig, 0.4, 1.2, -0.08, 0.08, z0 + 0.8, z0 + 2.4, frame_color, 1.0, "Slot Window Frame")
        add_box(fig, 0.45, 1.15, -0.02, 0.02, z0 + 0.85, z0 + 2.35, "#93C5FD", 0.45, "Slot Window Glass")
        add_box(fig, 4.5, fp_w, 4.8, 5.0, z0 + 0.18, z1, wall_color, 1.0, "Carport Back Wall")
        add_box(fig, 4.4, 4.6, 0, 5.0, z0 + 0.18, z1, wall_color, 1.0, "Carport Divider Wall")
        add_box(fig, fp_w - 0.25, fp_w + 0.05, -0.2, 0.1, 0, 3.15, "#0F172A", 1.0, "Carport Steel Column")
    else:
        add_box(fig, 0, fp_w, -0.12, 0.12, z0 + 0.18, z1, wall_color, 1.0, "Upper Full Front Wall")
        add_box(fig, fp_w - 0.12, fp_w + 0.12, 0, fp_d, z0 + 0.18, z1, wall_color, 1.0, "Right Side Wall")
        for wx in [1.2, 3.2, 5.6, 7.6]:
            add_box(fig, wx, wx + 0.65, -0.08, 0.08, z0 + 0.7, z0 + 2.6, frame_color, 1.0, "Vertical Slot Frame")
            add_box(fig, wx + 0.05, wx + 0.60, -0.02, 0.02, z0 + 0.75, z0 + 2.55, "#93C5FD", 0.45, "Vertical Slot Glass")

def add_premium_house_shell(fig, floor_index, floor_count, z, fp_w, fp_d, wall_color, accent_color, frame_color, door_color):
    h = 3.15
    z0, z1 = z, z + h
    add_box(fig, -0.2, fp_w + 0.2, -0.2, fp_d + 0.2, z0, z0 + 0.22, "#D97706", 1.0, "Polished Bronze Plinth")
    add_box(fig, 0, 4.8, -0.12, 0.12, z0 + 0.18, z1, wall_color, 1.0, "Left Marble Wing")
    add_box(fig, 9.2, fp_w, -0.12, 0.12, z0 + 0.18, z1, wall_color, 1.0, "Right Marble Wing")
    add_box(fig, 0, fp_w, fp_d - 0.12, fp_d + 0.12, z0 + 0.18, z1, wall_color, 1.0, "Marble Rear Wall")
    add_box(fig, -0.12, 0.12, 0, fp_d, z0 + 0.18, z1, wall_color, 1.0, "Marble Side Wall")
    add_box(fig, fp_w - 0.12, fp_w + 0.12, 0, fp_d, z0 + 0.18, z1, wall_color, 1.0, "Marble Side Wall")
    add_box(fig, 4.8, 9.2, -0.06, 0.06, z0 + 0.18, z1, "#93C5FD", 0.4, "Double-Height Atrium Glass")
    for mx in [4.8, 6.2, 7.8, 9.2]:
        add_box(fig, mx - 0.05, mx + 0.05, -0.08, 0.08, z0 + 0.18, z1, "#0F172A", 1.0, "Atrium Mullion")
    add_box(fig, 4.8, 9.2, -0.08, 0.08, z0 + 1.6, z0 + 1.7, "#0F172A", 1.0, "Atrium Horizontal Transom")
    add_box(fig, 4.4, 4.8, -0.6, -0.2, z0 + 0.18, z1, "#D97706", 1.0, "Bronze Fluted Column Left")
    add_box(fig, 9.2, 9.6, -0.6, -0.2, z0 + 0.18, z1, "#D97706", 1.0, "Bronze Fluted Column Right")

    if floor_index == 0:
        add_box(fig, 6.4, 7.6, -0.08, 0.08, z0 + 0.18, z0 + 2.5, door_color, 1.0, "Executive Entrance Door")
    for wx0, wx1 in [(1.2, 3.6), (10.4, 12.8)]:
        add_box(fig, wx0, wx1, -0.08, 0.08, z0 + 0.8, z0 + 2.4, frame_color, 1.0, "Executive Window Frame")
        add_box(fig, wx0 + 0.08, wx1 - 0.08, -0.02, 0.02, z0 + 0.88, z0 + 2.32, "#93C5FD", 0.45, "Window Glass")

# Master dispatcher
def add_exterior_building_shell(fig, floor_index, floor_count, z, fp_w, fp_d, wall_col, accent_col, frame_col, door_col, house_model):
    if house_model == "Modern House":
        add_modern_house_shell(fig, floor_index, floor_count, z, fp_w, fp_d, wall_col, accent_col, frame_col, door_col)
    elif house_model == "Luxury Villa":
        add_luxury_villa_shell(fig, floor_index, floor_count, z, fp_w, fp_d, wall_col, accent_col, frame_col, door_col)
    elif house_model == "Simple Family House":
        add_family_house_shell(fig, floor_index, floor_count, z, fp_w, fp_d, wall_col, accent_col, frame_col, door_col)
    elif house_model == "Contemporary House":
        add_contemporary_house_shell(fig, floor_index, floor_count, z, fp_w, fp_d, wall_col, accent_col, frame_col, door_col)
    elif house_model == "Traditional House":
        add_traditional_house_shell(fig, floor_index, floor_count, z, fp_w, fp_d, wall_col, accent_col, frame_col, door_col)
    elif house_model == "Compact House":
        add_compact_house_shell(fig, floor_index, floor_count, z, fp_w, fp_d, wall_col, accent_col, frame_col, door_col)
    elif house_model == "Premium House":
        add_premium_house_shell(fig, floor_index, floor_count, z, fp_w, fp_d, wall_col, accent_col, frame_col, door_col)
    else:
        add_modern_house_shell(fig, floor_index, floor_count, z, fp_w, fp_d, wall_col, accent_col, frame_col, door_col)

def add_swimming_pool(fig, px0, px1, py0, py1):
    # Pool Coping border
    add_box(fig, px0 - 0.35, px1 + 0.35, py0 - 0.35, py1 + 0.35, -0.05, 0.05, "#F8FAFC", 1.0, "Pool Coping")
    # Turquoise Water
    add_box(fig, px0, px1, py0, py1, -0.25, 0.01, "#38BDF8", 0.75, "Swimming Pool Water")
    # Sun Deck
    add_box(fig, px0 - 1.5, px0 - 0.4, py0, py1, -0.04, 0.06, "#A16207", 1.0, "Teak Sun Deck")
    # Loungers
    add_box(fig, px0 - 1.3, px0 - 0.6, (py0 + py1)/2 - 0.7, (py0 + py1)/2 + 0.7, 0.06, 0.28, "#1E293B", 1.0, "Pool Lounger")

def add_solar_panels(fig, sx0, sx1, sy0, sy1, sz):
    rows, cols = 2, 4
    dx = (sx1 - sx0) / cols
    dy = (sy1 - sy0) / rows
    for r in range(rows):
        for c in range(cols):
            x = sx0 + c * dx + 0.08
            y = sy0 + r * dy + 0.08
            # Aluminum frame
            add_box(fig, x, x + dx - 0.16, y, y + dy - 0.16, sz, sz + 0.06, "#94A3B8", 1.0, "Solar Mount")
            # Photovoltaic dark blue cells
            add_box(fig, x + 0.04, x + dx - 0.20, y + 0.04, y + dy - 0.20, sz + 0.06, sz + 0.10, "#1E3A8A", 1.0, "PV Solar Cell")

def add_lift_elevator(fig, lx0, lx1, ly0, ly1, total_h):
    # Glass elevator shaft
    add_box(fig, lx0, lx1, ly0, ly1, 0, total_h, "#7DD3FC", 0.35, "Glass Lift Elevator Shaft")
    for cx in [lx0, lx1]:
        for cy in [ly0, ly1]:
            add_box(fig, cx - 0.05, cx + 0.05, cy - 0.05, cy + 0.05, 0, total_h, "#0F172A", 1.0, "Lift Elevator Frame")
    # Elevator car
    add_box(fig, lx0 + 0.1, lx1 - 0.1, ly0 + 0.1, ly1 - 0.1, 0.2, 2.2, "#CBD5E1", 0.9, "Lift Elevator Cabin")

# ---------------------------------------------------------
# INTERIOR ROOMS & FURNITURE (EXACT REQUIREMENT-BASED)
# ---------------------------------------------------------

def add_home_office(fig, x0, x1, y0, y1, z):
    # Executive Desk
    add_box(fig, (x0 + x1)/2 - 0.7, (x0 + x1)/2 + 0.7, y0 + 0.4, y0 + 1.1, z + 0.12, z + 0.75, "#8B5E3C", 1.0, "Office Desk")
    # Ergonomic Chair
    add_box(fig, (x0 + x1)/2 - 0.25, (x0 + x1)/2 + 0.25, y0 + 1.2, y0 + 1.6, z + 0.12, z + 0.95, "#1E293B", 1.0, "Office Chair")
    # Bookshelf
    add_box(fig, x1 - 0.4, x1 - 0.1, y0 + 0.2, y1 - 0.2, z + 0.12, z + 1.9, "#334155", 1.0, "Bookshelf")

def add_room_floor(fig, x0, x1, y0, y1, z, color, label):
    add_box(fig, x0, x1, y0, y1, z, z + 0.10, color, 1.0, label)
    add_text(fig, (x0 + x1) / 2, (y0 + y1) / 2, z + 0.28, label, 11)

def add_interior_partitions(fig, x0, x1, y0, y1, z, h=1.25):
    t = 0.10
    wall_color = "#E8D8C4"
    add_box(fig, x0, x1, y1 - t, y1, z + 0.10, z + h, wall_color, 0.35)
    add_box(fig, x0, x0 + t, y0, y1, z + 0.10, z + h, wall_color, 0.35)
    add_box(fig, x1 - t, x1, y0, y1, z + 0.10, z + h, wall_color, 0.35)

def add_bed(fig, x, y, z, w=1.45, d=1.9):
    add_box(fig, x, x + w, y, y + d, z + 0.12, z + 0.40, "#1E293B", 1.0, "Bed Frame")
    add_box(fig, x + 0.05, x + w - 0.05, y + 0.05, y + d - 0.05, z + 0.40, z + 0.52, "#F8FAFC", 1.0, "Mattress")
    add_box(fig, x + 0.1, x + w - 0.1, y + d - 0.45, y + d - 0.05, z + 0.52, z + 0.65, "#E2E8F0", 1.0, "Pillow")
    add_box(fig, x - 0.4, x - 0.05, y + d - 0.5, y + d, z + 0.12, z + 0.45, "#475569", 1.0, "Nightstand")
    add_box(fig, x + w + 0.05, x + w + 0.4, y + d - 0.5, y + d, z + 0.12, z + 0.45, "#475569", 1.0, "Nightstand")

def add_living_lounge(fig, x0, x1, y0, y1, z):
    add_box(fig, x0 + 0.4, x1 - 0.4, y1 - 1.4, y1 - 0.6, z + 0.12, z + 0.52, "#1E293B", 1.0, "Modern Sectional")
    add_box(fig, x0 + 0.4, x0 + 1.2, y1 - 2.5, y1 - 1.4, z + 0.12, z + 0.52, "#1E293B", 1.0, "Sofa Chaise")
    add_box(fig, (x0 + x1) / 2 - 0.6, (x0 + x1) / 2 + 0.6, (y0 + y1) / 2 - 0.35, (y0 + y1) / 2 + 0.35, z + 0.12, z + 0.38, "#A16207", 1.0, "Coffee Table")
    add_box(fig, (x0 + x1) / 2 - 1.1, (x0 + x1) / 2 + 1.1, y0 + 0.25, y0 + 0.35, z + 0.60, z + 1.45, "#0F172A", 1.0, "Smart TV")

def add_modular_kitchen(fig, x0, x1, y0, y1, z):
    add_box(fig, x0 + 0.2, x1 - 0.2, y0 + 0.2, y0 + 0.75, z + 0.12, z + 0.90, "#1E293B", 1.0, "Quartz Kitchen Counter")
    add_box(fig, x0 + 0.2, x0 + 0.75, y0 + 0.75, y1 - 0.2, z + 0.12, z + 0.90, "#1E293B", 1.0, "Kitchen Counter")
    add_box(fig, x0 + 0.35, x0 + 0.95, y0 + 0.25, y0 + 0.70, z + 0.90, z + 0.96, "#CBD5E1", 1.0, "Stainless Sink")
    add_box(fig, x1 - 1.2, x1 - 0.45, y0 + 0.25, y0 + 0.70, z + 0.90, z + 0.98, "#0F172A", 1.0, "Induction Cooktop")
    add_box(fig, x1 - 0.85, x1 - 0.15, y1 - 0.95, y1 - 0.15, z + 0.12, z + 1.85, "#E2E8F0", 1.0, "Double-Door Fridge")

def add_dining_room(fig, x0, x1, y0, y1, z):
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    add_box(fig, cx - 0.8, cx + 0.8, cy - 0.45, cy + 0.45, z + 0.12, z + 0.75, "#8B5E3C", 1.0, "Dining Table")
    for dx in [-0.5, 0.0, 0.5]:
        add_box(fig, cx + dx - 0.18, cx + dx + 0.18, cy - 0.8, cy - 0.5, z + 0.12, z + 0.85, "#1E293B", 1.0, "Dining Chair")
        add_box(fig, cx + dx - 0.18, cx + dx + 0.18, cy + 0.5, cy + 0.8, z + 0.12, z + 0.85, "#1E293B", 1.0, "Dining Chair")

def add_luxury_bathroom(fig, x0, x1, y0, y1, z):
    add_box(fig, x0 + 0.25, x0 + 0.90, y0 + 0.25, y0 + 0.85, z + 0.12, z + 0.48, "#FFFFFF", 1.0, "Ceramic Commode")
    add_box(fig, x1 - 1.1, x1 - 0.25, y1 - 0.85, y1 - 0.25, z + 0.12, z + 0.65, "#F1F5F9", 1.0, "Vanity Basin")
    add_box(fig, x1 - 1.35, x1 - 0.15, y0 + 0.15, y0 + 1.35, z + 0.10, z + 0.18, "#BAE6FD", 0.6, "Shower Tray")
    add_box(fig, x1 - 1.35, x1 - 0.15, y0 + 0.15, y0 + 0.22, z + 0.18, z + 1.75, "#7DD3FC", 0.35, "Tempered Shower Glass")

def add_balcony_with_railings(fig, x0, x1, y0, y1, z, balcony_type="glass", number=1):
    add_box(fig, x0, x1, y0, y1, z, z + 0.14, "#CBD5E1", 1.0, f"Balcony Deck {number}")
    h_rail = 1.05
    if balcony_type == "glass":
        add_box(fig, x0, x1, y0, y0 + 0.06, z + 0.14, z + 0.14 + h_rail, "#7DD3FC", 0.4, f"Glass Balustrade {number}")
        add_box(fig, x0, x1, y1 - 0.06, y1, z + 0.14, z + 0.14 + h_rail, "#7DD3FC", 0.4, f"Glass Balustrade {number}")
        add_box(fig, x1 - 0.06, x1, y0, y1, z + 0.14, z + 0.14 + h_rail, "#7DD3FC", 0.4, f"Glass Balustrade {number}")
    elif balcony_type == "classic_baluster":
        add_box(fig, x0, x1, y0, y0 + 0.12, z + 0.14, z + 0.14 + h_rail, "#E2D4C0", 1.0, "Classical Balustrade")
        add_box(fig, x0, x1, y1 - 0.12, y1, z + 0.14, z + 0.14 + h_rail, "#E2D4C0", 1.0, "Classical Balustrade")
        add_box(fig, x1 - 0.12, x1, y0, y1, z + 0.14, z + 0.14 + h_rail, "#E2D4C0", 1.0, "Classical Balustrade")
    else:
        for rx in [x0, (x0 + x1)/2, x1]:
            add_box(fig, rx - 0.04, rx + 0.04, y0, y0 + 0.08, z + 0.14, z + 0.14 + h_rail, "#334155", 1.0, "Railing Post")
        add_box(fig, x0, x1, y0, y0 + 0.06, z + 0.14 + h_rail, z + 0.22 + h_rail, "#334155", 1.0, "Top Rail")
        add_box(fig, x0, x1, y0 + 0.01, y0 + 0.05, z + 0.14, z + 0.14 + h_rail, "#64748B", 0.6, "Metal Balustrade")

def distribute_labels(labels, floor_count):
    result = [[] for _ in range(floor_count)]
    if floor_count <= 0:
        return result
    for i, label in enumerate(labels):
        result[i % floor_count].append(label)
    return result

def add_floor_cutaway_rooms(fig, floor_index, floor_count, fp_w, fp_d, bedroom_count=3, bathroom_count=2, kitchen_count=1, dining_count=1, balcony_count=1, balcony_type="glass", has_home_office=False):
    z = floor_index * 3.15
    
    bedrooms = [f"BEDROOM {i + 1}" for i in range(max(0, int(bedroom_count)))]
    bathrooms = [f"BATHROOM {i + 1}" for i in range(max(0, int(bathroom_count)))]
    kitchens = [f"KITCHEN {i + 1}" for i in range(max(0, int(kitchen_count)))]
    dining = [f"DINING {i + 1}" for i in range(max(0, int(dining_count)))]

    bed_by_floor = distribute_labels(bedrooms, floor_count)
    bath_by_floor = distribute_labels(bathrooms, floor_count)
    kitchen_by_floor = distribute_labels(kitchens, floor_count)
    dining_by_floor = distribute_labels(dining, floor_count)

    all_items = []
    if floor_index == 0:
        all_items += [("LIVING LOUNGE", "#E2E8F0")]
        all_items += [("KITCHEN", "#FEF3C7")] * len(kitchen_by_floor[floor_index])
        all_items += [("DINING AREA", "#FFEDD5")] * len(dining_by_floor[floor_index])
        if has_home_office:
            all_items.append(("HOME OFFICE", "#FEF08A"))
    for lab in bed_by_floor[floor_index]:
        all_items.append((lab, "#FCE7F3"))
    for lab in bath_by_floor[floor_index]:
        all_items.append((lab, "#E0F2FE"))
    if not all_items:
        all_items.append(("OPEN SUITE LOUNGE", "#EDE9FE"))

    cols = 3
    rows = (len(all_items) + cols - 1) // cols
    cell_w = fp_w / cols
    cell_h = fp_d / max(1, rows)

    for idx, (label, color) in enumerate(all_items):
        r, c = divmod(idx, cols)
        x0 = c * cell_w + 0.10
        x1 = (c + 1) * cell_w - 0.10
        y0 = r * cell_h + 0.10
        y1 = (r + 1) * cell_h - 0.10
        
        add_room_floor(fig, x0, x1, y0, y1, z, color, label)
        add_interior_partitions(fig, x0, x1, y0, y1, z)
        
        u = label.upper()
        if "BEDROOM" in u:
            add_bed(fig, x0 + 0.3, y0 + 0.35, z)
        elif "BATHROOM" in u:
            add_luxury_bathroom(fig, x0, x1, y0, y1, z)
        elif "KITCHEN" in u:
            add_modular_kitchen(fig, x0, x1, y0, y1, z)
        elif "DINING" in u:
            add_dining_room(fig, x0, x1, y0, y1, z)
        elif "LIVING" in u or "LOUNGE" in u:
            add_living_lounge(fig, x0, x1, y0, y1, z)
        elif "OFFICE" in u:
            add_home_office(fig, x0, x1, y0, y1, z)

    # Stairs
    add_box(fig, fp_w - 1.8, fp_w - 0.4, fp_d - 1.8, fp_d - 0.4, z, z + 1.2, "#8B5E3C", 1.0, "Stairs")

    # Balconies (only if balcony_count > 0 and on upper floors)
    if balcony_count > 0 and floor_index > 0:
        per_floor = distribute_labels([f"BALCONY {i + 1}" for i in range(int(balcony_count))], floor_count)
        for n, _ in enumerate(per_floor[floor_index], start=1):
            add_balcony_with_railings(fig, fp_w + 0.08, fp_w + 2.2, 2.5 + (n - 1) * 2.2, 4.5 + (n - 1) * 2.2, z, balcony_type=balcony_type, number=n)

def add_carport_and_parking(fig, parking_spaces, base_x, carport_type="modern_steel"):
    if parking_spaces <= 0:
        return
    
    add_box(fig, base_x - 1.5, base_x + 4.5, -4.8, -0.2, -0.05, 0.02, "#475569", 1.0, "Driveway Pavement")
    
    for n in range(min(4, int(parking_spaces))):
        cx = base_x - 0.5 + (n % 2) * 2.4
        cy = -1.6 - (n // 2) * 2.2
        # Clean architectural parking bay demarcations (no decorative toy cars)
        add_box(fig, cx - 1.0, cx + 1.0, cy - 1.8, cy + 1.8, 0.02, 0.05, "#334155", 1.0, f"Parking Bay {n+1}")
        add_box(fig, cx - 1.05, cx - 0.95, cy - 1.8, cy + 1.8, 0.05, 0.07, "#F8FAFC", 1.0, f"Bay Marking L {n+1}")
        add_box(fig, cx + 0.95, cx + 1.05, cy - 1.8, cy + 1.8, 0.05, 0.07, "#F8FAFC", 1.0, f"Bay Marking R {n+1}")

    if carport_type != "integrated_tuck":
        add_box(fig, base_x - 1.6, base_x - 1.4, -4.4, -0.4, 0, 2.8, "#334155", 1.0, "Carport Column")
        add_box(fig, base_x + 4.2, base_x + 4.4, -4.4, -0.4, 0, 2.8, "#334155", 1.0, "Carport Column")
        add_box(fig, base_x - 1.8, base_x + 4.6, -4.6, -0.2, 2.8, 2.95, "#1E293B", 1.0, "Carport Canopy Roof")

# ---------------------------------------------------------
# MASTER 3D HOUSE GENERATOR
# ---------------------------------------------------------

def generate_architectural_house_3d(
    house_model="Modern House",
    bhk="3 BHK",
    floors="2 Floors",
    view_mode="🏡 Exterior View (Full House + Roof)",
    parking_spaces=1,
    kitchen_count=1,
    dining_count=1,
    balcony_count=1,
    bedroom_count=3,
    bathroom_count=2,
    camera_angle="📐 Isometric 3D View",
    additional_features=None
):
    try:
        floor_count = int(str(floors).split()[0])
    except Exception:
        floor_count = 1
    floor_count = max(1, min(4, floor_count))

    theme = HOUSE_THEMES.get(house_model, HOUSE_THEMES["Modern House"])
    fp_w, fp_d = theme["footprint"]
    wall_col = theme["wall_color"]
    accent_col = theme["accent_color"]
    roof_col = theme["roof_color"]
    roof_type = theme["roof_type"]
    door_col = theme["door_color"]
    frame_col = theme["window_frame"]
    balcony_type = theme["balcony_type"]
    carport_type = theme["carport_type"]

    fig = go.Figure()

    # Clean architectural building foundation & site pad
    add_box(fig, -1.2, fp_w + 1.2, -1.8, fp_d + 1.2, -0.15, 0.0, "#E2E8F0", 1.0, "Site Foundation Pad")

    # Swimming Pool (if selected)
    has_pool = additional_features and "Swimming Pool" in additional_features
    if has_pool:
        add_swimming_pool(fig, -3.0, -0.8, 1.5, fp_d - 1.5)

    # Parking & Carport
    add_carport_and_parking(fig, parking_spaces, base_x=fp_w - 3.5, carport_type=carport_type)

    total_h = floor_count * 3.15

    # Residential Lift / Elevator (if selected)
    has_lift = additional_features and "Lift / Elevator" in additional_features
    if has_lift:
        add_lift_elevator(fig, fp_w - 2.2, fp_w - 0.4, fp_d - 3.8, fp_d - 2.0, total_h)

    # Home Office check
    has_office = additional_features and "Home Office" in additional_features

    # VIEW MODE LOGIC
    if "Exterior" in view_mode:
        for fl_idx in range(floor_count):
            z_curr = fl_idx * 3.15
            add_exterior_building_shell(fig, fl_idx, floor_count, z_curr, fp_w, fp_d, wall_col, accent_col, frame_col, door_col, house_model)
            if balcony_count > 0 and fl_idx > 0:
                add_balcony_with_railings(fig, fp_w + 0.08, fp_w + 2.2, 2.5, 4.8, z_curr, balcony_type=balcony_type, number=fl_idx)

        # Roof
        z_roof = total_h
        if house_model == "Luxury Villa":
            add_hipped_roof(fig, 0, fp_w, 0, fp_d, z_roof, roof_height=2.3, roof_color=roof_col, is_luxury_villa=True)
        elif house_model == "Simple Family House":
            add_gabled_roof(fig, 0, fp_w, 0, fp_d, z_roof, roof_height=2.4, roof_color=roof_col, gable_color=wall_col, add_dormer=True)
        elif house_model == "Contemporary House":
            add_shed_roof(fig, 0, fp_w, 0, fp_d, z_roof, roof_height=2.0, roof_color=roof_col, wall_color=wall_col)
        elif house_model == "Compact House":
            add_shed_roof(fig, 0, fp_w, 0, fp_d, z_roof, roof_height=1.5, roof_color=roof_col, wall_color=wall_col)
        elif house_model == "Premium House":
            add_parapet_flat_roof(fig, 0, fp_w, 0, fp_d, z_roof, wall_color=wall_col, deck_color=theme["deck_color"], accent_color=accent_col, has_skylounge=True)
        elif house_model == "Traditional House":
            add_hipped_roof(fig, 0, fp_w, 0, fp_d, z_roof, roof_height=2.3, roof_color=roof_col, is_luxury_villa=False)
        else: # Modern House
            add_parapet_flat_roof(fig, 0, fp_w, 0, fp_d, z_roof, wall_color=wall_col, deck_color=theme["deck_color"], accent_color=accent_col, has_skylounge=False)

        # Solar Panels (if selected)
        if additional_features and "Solar Panels" in additional_features:
            add_solar_panels(fig, 1.0, fp_w - 4.5, 1.0, fp_d - 1.0, z_roof + 0.2)

        # Terrace Garden (if selected and flat roof)
        if additional_features and "Terrace Garden" in additional_features and "parapet" in roof_type:
            add_box(fig, 1.5, 4.5, fp_d - 2.5, fp_d - 0.8, z_roof + 0.15, z_roof + 0.55, "#166534", 1.0, "Rooftop Planter Garden")

    elif "All Floors" in view_mode:
        for fl_idx in range(floor_count):
            add_floor_cutaway_rooms(
                fig, fl_idx, floor_count, fp_w, fp_d,
                bedroom_count=bedroom_count, bathroom_count=bathroom_count,
                kitchen_count=kitchen_count, dining_count=dining_count,
                balcony_count=balcony_count, balcony_type=balcony_type,
                has_home_office=has_office
            )
        for x, y in [(0, 0), (fp_w, 0), (0, fp_d), (fp_w, fp_d)]:
            add_box(fig, x - 0.06, x + 0.06, y - 0.06, y + 0.06, 0, total_h, accent_col, 0.45, "Structural Column")
    else:
        floor_names = {"Ground Floor": 0, "First Floor": 1, "Second Floor": 2, "Third Floor": 3}
        sel_idx = 0
        for name, idx in floor_names.items():
            if name in view_mode:
                sel_idx = idx
                break
        sel_idx = min(sel_idx, floor_count - 1)
        add_floor_cutaway_rooms(
            fig, sel_idx, floor_count, fp_w, fp_d,
            bedroom_count=bedroom_count, bathroom_count=bathroom_count,
            kitchen_count=kitchen_count, dining_count=dining_count,
            balcony_count=balcony_count, balcony_type=balcony_type,
            has_home_office=has_office
        )

    # Floor Labels
    floor_colours = ["#16A34A", "#2563EB", "#7C3AED", "#D97706"]
    floor_labels = ["GROUND", "FIRST", "SECOND", "THIRD"]
    for i in range(floor_count):
        add_text(fig, -1.8, fp_d + 0.8, i * 3.15 + 0.4, f"{floor_labels[i]} LEVEL", 12, floor_colours[i])

    # Camera Preset Angle
    if "Front" in camera_angle:
        cam_eye = dict(x=0.01, y=2.5, z=0.45)
    elif "Side" in camera_angle:
        cam_eye = dict(x=2.5, y=0.01, z=0.45)
    elif "Top-Down" in camera_angle:
        cam_eye = dict(x=0.001, y=0.001, z=2.8)
    else: # Isometric
        cam_eye = dict(x=1.65, y=1.75, z=1.2)

    fig.update_layout(
        height=720,
        margin=dict(l=0, r=0, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            xaxis=dict(visible=False, showgrid=False, showbackground=False),
            yaxis=dict(visible=False, showgrid=False, showbackground=False),
            zaxis=dict(visible=False, showgrid=False, showbackground=False),
            aspectmode="manual",
            aspectratio=dict(x=1.45, y=1.08, z=0.85),
            camera=dict(eye=cam_eye),
            dragmode="orbit"
        ),
        showlegend=False
    )
    return fig

# =========================================================
# SESSION STATE MANAGEMENT
# =========================================================

defaults = {
    "logged_in": False,
    "user_name": "",
    "user_email": "",
    "page": "dashboard",
    "prediction": None,
    "formatted_price": "",
    "price_words": "",
    "formatted_cost": "",
    "cost_words": "",
    "bhk": "",
    "floors": "",
    "construction_cost": 0,
    "cost_breakdown": {},
    "property_data": None,
    "rating_stars": "⭐⭐⭐⭐☆",
    "rating_score": 4.2,
    "rating_tag": "Highly Desirable",
    "eco_stars": "★★★★☆",
    "eco_score": 4.1,
    "eco_tag": "High Energy Efficiency",
    "location_display": "India → Telangana → Hyderabad → Banjara Hills",
    "user_country": "India",
    "user_state": "Telangana",
    "user_city": "Hyderabad",
    "user_area": "Banjara Hills",
    "custom_locality": "",
    "selected_house_model": "Modern House",
    "additional_features": ["Landscaped Garden / Open Space", "Rooftop Solar Panels"],
    "additional_cost": 0,
    "formatted_additional": "",
    "total_estimated_cost": 0,
    "formatted_total": "",
    "total_words": "",
    "user_budget": 0,
    "formatted_budget": "",
    "budget_words": "",
    "net_budget": 0,
    "remaining_budget": 0,
    "budget_shortfall": 0,
    "is_within_budget": True,
    "affordability_status": "FITS BUDGET",
    "affordability_icon": "🟢",
    "affordability_color": "#16a34a"
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# LOGIN / REGISTER VIEW
# =========================================================

if not st.session_state.logged_in:
    st.markdown("""
        <div class="hero-banner">
            <div class="hero-title">🏠 AI Real Estate Valuation & 3D Architectural Studio</div>
            <div class="hero-subtitle">Intelligent residential property valuation, AI house design planner, dynamic budget optimization, and interactive 3D architectural house generation.</div>
            <div class="hero-pills">
                <span class="hero-pill">📍 Location Hierarchy</span>
                <span class="hero-pill">💰 Multi-Currency Engine</span>
                <span class="hero-pill">⭐ Dynamic Property Rating</span>
                <span class="hero-pill">🌱 Eco / Smart House Score</span>
                <span class="hero-pill">🏗️ Real Requirement-Based 3D</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    auth_col1, auth_col2, auth_col3 = st.columns([1, 2, 1])
    with auth_col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        login_tab, register_tab = st.tabs(["🔐 Sign In", "📝 Create Account"])

        with login_tab:
            st.subheader("Welcome Back")
            st.caption("Sign in to access your valuations and appraisal tools.")
            login_email = st.text_input("Email Address", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")

            if st.button("Sign In to Account", use_container_width=True, type="primary"):
                if not login_email or not login_password:
                    st.warning("Please enter your email and password.")
                else:
                    user_name = login_user(login_email, login_password)
                    if user_name:
                        st.session_state.logged_in = True
                        st.session_state.user_name = user_name
                        st.session_state.user_email = login_email.strip().lower()
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password.")

        with register_tab:
            st.subheader("New User Registration")
            st.caption("Create an account to start valuing properties.")
            reg_name = st.text_input("Full Name", key="reg_name")
            reg_email = st.text_input("Email Address", key="reg_email")
            reg_pass = st.text_input("Create Password", type="password", key="reg_pass")
            reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")

            if st.button("Create Account", use_container_width=True, type="primary"):
                if not reg_name:
                    st.warning("Please enter your full name.")
                elif "@" not in reg_email:
                    st.warning("Please enter a valid email address.")
                elif len(reg_pass) < 6:
                    st.warning("Password must contain at least 6 characters.")
                elif reg_pass != reg_confirm:
                    st.error("❌ Passwords do not match.")
                elif register_user(reg_name, reg_email, reg_pass):
                    st.success("✅ Account created successfully! Please sign in using the Login tab.")
                else:
                    st.error("❌ An account with this email already exists.")

        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# =========================================================
# SIDEBAR NAVIGATION & PROFILE
# =========================================================

with st.sidebar:
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e293b, #0f172a); color: white; padding: 1.25rem; border-radius: 14px; margin-bottom: 1rem; border: 1px solid #334155;">
            <div style="font-size: 1.1rem; font-weight: 700; display: flex; align-items: center; gap: 0.5rem;">
                <span>👤</span> {st.session_state.user_name}
            </div>
            <div style="font-size: 0.82rem; color: #94a3b8; margin-top: 0.25rem;">
                {st.session_state.user_email}
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🏠 Valuation Dashboard", use_container_width=True, type="primary" if st.session_state.page == "dashboard" else "secondary"):
        st.session_state.page = "dashboard"
        st.rerun()

    if st.button("📋 Saved Valuations", use_container_width=True, type="primary" if st.session_state.page == "saved" else "secondary"):
        st.session_state.page = "saved"
        st.rerun()

    st.divider()
    
    st.markdown("""
        <div style="font-size: 0.85rem; color: #64748b; line-height: 1.5;">
            <b>🏛️ 3D Architectural Models:</b><br>
            • Modern House<br>
            • Luxury Villa<br>
            • Simple Family House<br>
            • Contemporary House<br>
            • Traditional House<br>
            • Compact House<br>
            • Premium House
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()

    if st.button("🚪 Logout", use_container_width=True):
        for key, value in defaults.items():
            st.session_state[key] = value
        st.rerun()

# =========================================================
# SAVED VALUATIONS PAGE
# =========================================================

if st.session_state.page == "saved":
    st.markdown("""
        <div class="hero-banner" style="padding: 1.5rem 2rem; margin-bottom: 1.5rem;">
            <div class="hero-title" style="font-size: 1.8rem;">📋 My Saved Valuations & House Plans</div>
            <div class="hero-subtitle">Review previously evaluated properties, architectural specifications, ratings and eco scores.</div>
        </div>
    """, unsafe_allow_html=True)

    saved_data = get_valuations(st.session_state.user_email)

    if saved_data.empty:
        st.info("ℹ️ You have not saved any property valuations yet. Go to the Valuation Dashboard to evaluate and save a property.")
    else:
        st.success(f"✅ Found **{len(saved_data)}** saved valuation(s) for your account.")
        display_df = saved_data.copy()
        if "Valuation" in display_df.columns:
            display_df["Valuation"] = display_df["Valuation"].apply(lambda v: f"{v:,.0f}" if pd.notnull(v) else "-")
        if "Est. Construction Cost" in display_df.columns:
            display_df["Est. Construction Cost"] = display_df["Est. Construction Cost"].apply(lambda v: f"{v:,.0f}" if pd.notnull(v) else "-")
            
        render_dataframe(display_df, hide_index=True)
    st.stop()

# =========================================================
# DASHBOARD: PROPERTY INPUT & VALUATION
# =========================================================

st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🏠 AI Real Estate Valuation & Architectural Studio</div>
        <div class="hero-subtitle">Comprehensive AI-powered valuation, architectural design synthesis, dynamic budget optimization, and interactive 3D house planning.</div>
        <div class="hero-pills">
            <span class="hero-pill">📍 Location Hierarchy</span>
            <span class="hero-pill">💰 Country-Based Currency</span>
            <span class="hero-pill">⭐ Dynamic Rating</span>
            <span class="hero-pill">🌱 Eco Score</span>
            <span class="hero-pill">🏛️ Requirement-Based 3D</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SECTION 1: HIERARCHICAL LOCATION & CURRENCY
# ---------------------------------------------------------
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">📍 Step 1: Select Property Location</div>', unsafe_allow_html=True)

loc_col1, loc_col2, loc_col3, loc_col4 = st.columns(4)

with loc_col1:
    countries = ORDERED_COUNTRY_LIST
    curr_c = st.session_state.user_country if st.session_state.user_country in countries else "India"
    selected_country = st.selectbox(
        "Country",
        countries,
        index=countries.index(curr_c),
        key="sel_country"
    )
    if selected_country != st.session_state.user_country:
        st.session_state.user_country = selected_country
        new_c_cfg = get_country_config(selected_country)
        new_states = [s for s in new_c_cfg["states"].keys() if s != "Other"] + ["Other"]
        st.session_state.user_state = new_states[0]
        new_cities = [c for c in new_c_cfg["states"].get(new_states[0], {}).keys() if c != "Other"] + ["Other"]
        st.session_state.user_city = new_cities[0]
        new_areas = [a for a in new_c_cfg["states"].get(new_states[0], {}).get(new_cities[0], []) if a != "Other"] + ["Other"]
        st.session_state.user_area = new_areas[0]
        st.session_state.prediction = None
        st.rerun()

country_cfg = get_country_config(selected_country)
curr_symbol = country_cfg["currency"]
admin_label = country_cfg.get("admin_unit_name", "State / Region / Province")

# States list: Real locations first, 'Other' strictly last
raw_states = [s for s in country_cfg["states"].keys() if s != "Other"]
available_states = raw_states + ["Other"]

with loc_col2:
    if st.session_state.user_state not in available_states:
        st.session_state.user_state = available_states[0]
    selected_state = st.selectbox(
        admin_label,
        available_states,
        index=available_states.index(st.session_state.user_state),
        key="sel_state"
    )
    if selected_state != st.session_state.user_state:
        st.session_state.user_state = selected_state
        if selected_state != "Other":
            new_cities = [c for c in country_cfg["states"].get(selected_state, {}).keys() if c != "Other"] + ["Other"]
            st.session_state.user_city = new_cities[0]
            new_areas = [a for a in country_cfg["states"].get(selected_state, {}).get(new_cities[0], []) if a != "Other"] + ["Other"]
            st.session_state.user_area = new_areas[0]
        else:
            st.session_state.user_city = "Other"
            st.session_state.user_area = "Other"
        st.rerun()

# Cities list: Real locations first, 'Other' strictly last
if selected_state != "Other":
    raw_cities = [c for c in country_cfg["states"].get(selected_state, {}).keys() if c != "Other"]
    available_cities = raw_cities + ["Other"]
else:
    available_cities = ["Other"]

with loc_col3:
    if st.session_state.user_city not in available_cities:
        st.session_state.user_city = available_cities[0]
    selected_city = st.selectbox(
        "City / District",
        available_cities,
        index=available_cities.index(st.session_state.user_city),
        key="sel_city"
    )
    if selected_city != st.session_state.user_city:
        st.session_state.user_city = selected_city
        if selected_city != "Other" and selected_state != "Other":
            new_areas = [a for a in country_cfg["states"].get(selected_state, {}).get(selected_city, []) if a != "Other"] + ["Other"]
            st.session_state.user_area = new_areas[0]
        else:
            st.session_state.user_area = "Other"
        st.rerun()

# Local Areas list: Real locations first, 'Other' strictly last
if selected_state != "Other" and selected_city != "Other":
    raw_areas = [a for a in country_cfg["states"].get(selected_state, {}).get(selected_city, []) if a != "Other"]
    available_areas = raw_areas + ["Other"]
else:
    available_areas = ["Other"]

with loc_col4:
    if st.session_state.user_area not in available_areas:
        st.session_state.user_area = available_areas[0]
    selected_area = st.selectbox(
        "Local Area / Locality",
        available_areas,
        index=available_areas.index(st.session_state.user_area),
        key="sel_area"
    )
    st.session_state.user_area = selected_area

# Handle custom text entries if 'Other' is chosen at ANY level
custom_needed = sum([selected_state == "Other", selected_city == "Other", selected_area == "Other"])
final_state = selected_state
final_city = selected_city
final_locality = selected_area

if custom_needed > 0:
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    c_inputs = st.columns(custom_needed)
    c_idx = 0
    
    if selected_state == "Other":
        with c_inputs[c_idx]:
            custom_st = st.text_input(
                f"Enter Custom {admin_label}",
                value=st.session_state.get("custom_state", ""),
                placeholder=f"Type your {admin_label.lower()} name...",
                key="input_custom_state"
            )
            final_state = custom_st.strip() if custom_st.strip() else "Other"
            st.session_state.custom_state = final_state
        c_idx += 1
    
    if selected_city == "Other":
        with c_inputs[c_idx]:
            custom_ct = st.text_input(
                "Enter Custom City / District",
                value=st.session_state.get("custom_city", ""),
                placeholder="Type your city name...",
                key="input_custom_city"
            )
            final_city = custom_ct.strip() if custom_ct.strip() else "Other City"
            st.session_state.custom_city = final_city
        c_idx += 1
        
    if selected_area == "Other":
        with c_inputs[c_idx]:
            custom_loc = st.text_input(
                "Enter Custom Locality / Neighborhood",
                value=st.session_state.get("custom_locality", ""),
                placeholder="Type neighborhood or sector name...",
                key="input_custom_locality"
            )
            final_locality = custom_loc.strip() if custom_loc.strip() else "Central Area"
            st.session_state.custom_locality = final_locality

location_hierarchy_string = f"{selected_country} → {final_state} → {final_city} → {final_locality}"
st.caption(f"📍 **Selected Location:** {location_hierarchy_string}  |  **Active Currency:** {curr_symbol} ({country_cfg['currency_code']} - {country_cfg['currency_name']})")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# SECTION 2: ARCHITECTURAL MODEL & SPECIFICATIONS
# ---------------------------------------------------------
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">🏛️ Step 2: Choose Architectural House Model</div>', unsafe_allow_html=True)

house_models = list(HOUSE_THEMES.keys())
selected_house_model = st.selectbox(
    "Select House Model",
    house_models,
    index=house_models.index(st.session_state.selected_house_model) if st.session_state.selected_house_model in house_models else 0,
    help="Select the design aesthetic for realistic 3D building generation"
)
st.session_state.selected_house_model = selected_house_model
st.info(f"✨ **Design Aesthetic:** {HOUSE_THEMES[selected_house_model]['description']}")

st.markdown('<br>', unsafe_allow_html=True)
st.markdown('<div class="card-title">🏡 Step 3: Property Specifications</div>', unsafe_allow_html=True)

spec_col1, spec_col2 = st.columns(2)

with spec_col1:
    lot_area = st.number_input("Lot Area (sq ft)", min_value=500, max_value=50000, value=8000, step=500)
    gr_liv_area = st.number_input("Living Area (sq ft)", min_value=400, max_value=20000, value=1800, step=100)
    bedroom_abvgr = st.number_input("Number of Bedrooms", min_value=1, max_value=10, value=3)
    full_bath = st.number_input("Number of Bathrooms", min_value=1, max_value=10, value=2)

with spec_col2:
    overall_qual = st.slider("Overall Finish Quality (1 = Basic, 10 = Luxury)", min_value=1, max_value=10, value=7)
    year_built = st.number_input("Year Built / Construction Year", min_value=1900, max_value=2026, value=2020)
    garage_cars = st.number_input("Garage Capacity (Cars)", min_value=0, max_value=6, value=2)

# Derive BHK representation from bedroom count
if bedroom_abvgr <= 2:
    recommended_bhk = f"{bedroom_abvgr} BHK"
elif bedroom_abvgr == 3:
    recommended_bhk = "3 BHK"
elif bedroom_abvgr == 4:
    recommended_bhk = "4 BHK"
else:
    recommended_bhk = f"{bedroom_abvgr}+ BHK"

st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------------
# SECTION 3: HOUSE PLANNING, BUDGET & OPTIONAL FEATURES
# ---------------------------------------------------------
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">🏗️ Step 4: House Planning & Budget Preferences</div>', unsafe_allow_html=True)

plan_col1, plan_col2 = st.columns(2)

with plan_col1:
    user_budget = st.number_input(
        f"💰 User Budget ({curr_symbol})",
        min_value=0,
        value=country_cfg["budget_default"],
        step=country_cfg["budget_step"],
        help="Enter your planned or available budget in your active currency"
    )
    available_budget = user_budget
    parking_spaces = st.number_input("Parking Spaces", min_value=0, max_value=5, value=2)
    kitchen_count = st.number_input("Number of Kitchens", min_value=1, max_value=4, value=1)

with plan_col2:
    dining_count = st.number_input("Dining Areas", min_value=0, max_value=4, value=1)
    balcony_count = st.number_input("Balconies", min_value=0, max_value=6, value=2)
    construction_quality = st.selectbox("Construction Quality Tier", ["Basic", "Standard", "Premium", "Luxury"], index=1)

floor_preference = st.selectbox(
    "🏢 Floor Preference",
    ["Let system recommend", "1 Floor", "2 Floors", "3 Floors", "4 Floors"]
)

# Expandable Additional Features
with st.expander("🌿 Optional Additional Features (Swimming Pool, Solar, Lift, Home Office, etc.)", expanded=False):
    st.caption("Select luxury or sustainable amenities to incorporate into your house design, rating, and 3D visualization.")
    opt_col1, opt_col2 = st.columns(2)
    
    with opt_col1:
        feat_garden = st.checkbox("🌿 Landscaped Garden / Open Space", value=True)
        feat_office = st.checkbox("💼 Dedicated Home Office / Study", value=False)
        feat_pool = st.checkbox("🏊 Private Swimming Pool & Sun Deck", value=(selected_house_model == "Luxury Villa"))
        
    with opt_col2:
        feat_lift = st.checkbox("🛗 Residential Lift / Elevator", value=False)
        feat_solar = st.checkbox("☀️ Rooftop Solar Panels (Green Energy)", value=True)
        feat_terrace_garden = st.checkbox("🌺 Terrace Garden & Pergola", value=False)

selected_additional_features = []
if feat_garden: selected_additional_features.append("Garden / Open Space")
if feat_office: selected_additional_features.append("Home Office")
if feat_pool: selected_additional_features.append("Swimming Pool")
if feat_lift: selected_additional_features.append("Lift / Elevator")
if feat_solar: selected_additional_features.append("Solar Panels")
if feat_terrace_garden: selected_additional_features.append("Terrace Garden")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# PREDICT & SYNTHESIS PIPELINE
# ---------------------------------------------------------
if st.button("🔮 Calculate Property Valuation & Synthesize AI House Plan", use_container_width=True, type="primary"):
    internal_neighborhood = map_location_to_internal_neighborhood(
        selected_country, final_state, final_city, final_locality
    )
    
    input_data = pd.DataFrame(0, index=[0], columns=features)
    feature_mappings = {
        "LotArea": lot_area,
        "OverallQual": overall_qual,
        "YearBuilt": year_built,
        "GrLivArea": gr_liv_area,
        "FullBath": full_bath,
        "BedroomAbvGr": bedroom_abvgr,
        "GarageCars": garage_cars
    }
    
    for col, val in feature_mappings.items():
        if col in input_data.columns:
            input_data[col] = val

    for col in input_data.columns:
        if str(col).startswith("Neighborhood_"):
            input_data[col] = 0

    target_neighborhood_col = f"Neighborhood_{internal_neighborhood}"
    if target_neighborhood_col in input_data.columns:
        input_data[target_neighborhood_col] = 1
    elif "Neighborhood_NAmes" in input_data.columns:
        input_data["Neighborhood_NAmes"] = 1

    base_prediction_usd = float(model.predict(input_data)[0])
    converted_prediction = base_prediction_usd * country_cfg["rate_multiplier"]
    
    # Automatic BHK recommendation
    if bedroom_abvgr <= 2:
        recommended_bhk = f"{bedroom_abvgr} BHK"
    elif bedroom_abvgr == 3:
        recommended_bhk = "3 BHK"
    elif bedroom_abvgr == 4:
        recommended_bhk = "4 BHK"
    else:
        recommended_bhk = f"{bedroom_abvgr}+ BHK"

    # Floor Recommendation
    if floor_preference != "Let system recommend":
        recommended_floors = floor_preference
    else:
        b_ratio = available_budget / max(1, country_cfg["budget_default"])
        if b_ratio < 0.9:
            recommended_floors = "1 Floor"
        elif b_ratio < 1.8:
            recommended_floors = "2 Floors"
        elif b_ratio < 2.8:
            recommended_floors = "3 Floors"
        else:
            recommended_floors = "4 Floors"

    floor_count = int(recommended_floors.split()[0])

    # Construction Cost Breakdown Calculation
    base_rate = country_cfg["construction_rate_sqft"] * quality_multipliers.get(construction_quality, 1.0)
    
    cost_structure = gr_liv_area * base_rate
    cost_beds = bedroom_abvgr * country_cfg["cost_bedroom"]
    cost_baths = full_bath * country_cfg["cost_bathroom"]
    cost_parks = parking_spaces * country_cfg["cost_parking"]
    cost_kitch = kitchen_count * country_cfg["cost_kitchen"]
    cost_din = dining_count * country_cfg["cost_dining"]
    cost_balc = balcony_count * country_cfg["cost_balcony"]
    cost_extra_flr = max(0, floor_count - 1) * gr_liv_area * country_cfg["cost_floor_extra"]
    
    # 1. Base Construction Cost (Core structure, essential rooms, multi-floor elevation & parking)
    base_construction_cost = (
        cost_structure + cost_beds + cost_baths + cost_parks +
        cost_kitch + cost_din + cost_balc + cost_extra_flr
    )

    # 2. Additional Features Cost (Selected luxury & green amenities)
    additional_features_cost = sum(country_cfg["opt_costs"].get(f, 0) for f in selected_additional_features)
    
    # 3. Total Estimated Project Cost
    total_estimated_cost = base_construction_cost + additional_features_cost
    total_construction_cost = total_estimated_cost # Preserved for backwards compatibility

    # 4. User Budget, Remaining Surplus / Budget Shortfall & Affordability Status
    net_budget = user_budget - total_estimated_cost
    if net_budget >= 0:
        remaining_budget = net_budget
        budget_shortfall = 0.0
        is_within_budget = True
        affordability_status = "FITS BUDGET"
        affordability_icon = "🟢"
        affordability_color = "#16a34a"
        affordability_class = "afford-badge-fits"
    else:
        remaining_budget = 0.0
        budget_shortfall = abs(net_budget)
        is_within_budget = False
        shortfall_ratio = budget_shortfall / max(1.0, float(user_budget))
        if shortfall_ratio <= 0.15:
            affordability_status = "CLOSE TO BUDGET"
            affordability_icon = "🟡"
            affordability_color = "#d97706"
            affordability_class = "afford-badge-close"
        else:
            affordability_status = "EXCEEDS BUDGET"
            affordability_icon = "🔴"
            affordability_color = "#dc2626"
            affordability_class = "afford-badge-exceeds"

    cost_breakdown_dict = {
        "Structure & Living Area": cost_structure,
        "Bedrooms Framing & Interiors": cost_beds,
        "Bathrooms & Plumbing": cost_baths,
        "Kitchen & Cabinetry": cost_kitch,
        "Dining Areas": cost_din,
        "Parking Bays & Carport": cost_parks,
        "Balconies & Railings": cost_balc,
        "Multi-Floor Elevation Structure": cost_extra_flr,
        "Optional Selected Amenities": additional_features_cost
    }

    # Dynamic Ratings
    rating_stars, rating_score, rating_tag = calculate_dynamic_property_rating(
        overall_qual, gr_liv_area, bedroom_abvgr, full_bath, garage_cars,
        construction_quality, floor_count, balcony_count, parking_spaces,
        selected_house_model, selected_additional_features
    )

    eco_stars, eco_score, eco_tag = calculate_eco_score(
        selected_additional_features, gr_liv_area, selected_house_model
    )

    formatted_val = format_currency_value(converted_prediction, selected_country)
    val_in_words = number_to_words(converted_prediction, selected_country)

    formatted_base_cost = format_currency_value(base_construction_cost, selected_country)
    base_cost_words = number_to_words(base_construction_cost, selected_country)

    formatted_additional = format_currency_value(additional_features_cost, selected_country)
    additional_words = number_to_words(additional_features_cost, selected_country)

    formatted_total = format_currency_value(total_estimated_cost, selected_country)
    total_words = number_to_words(total_estimated_cost, selected_country)

    formatted_budget = format_currency_value(user_budget, selected_country)
    budget_words = number_to_words(user_budget, selected_country)

    formatted_remaining = format_currency_value(remaining_budget, selected_country)
    remaining_words = number_to_words(remaining_budget, selected_country)

    formatted_shortfall = format_currency_value(budget_shortfall, selected_country)
    shortfall_words = number_to_words(budget_shortfall, selected_country)

    # Save to session state
    st.session_state.prediction = converted_prediction
    st.session_state.formatted_price = formatted_val
    st.session_state.price_words = val_in_words

    st.session_state.base_construction_cost = base_construction_cost
    st.session_state.formatted_base_cost = formatted_base_cost
    st.session_state.base_cost_words = base_cost_words

    st.session_state.additional_cost = additional_features_cost
    st.session_state.formatted_additional = formatted_additional
    st.session_state.additional_words = additional_words

    st.session_state.total_estimated_cost = total_estimated_cost
    st.session_state.formatted_total = formatted_total
    st.session_state.total_words = total_words

    # Legacy compatibility keys
    st.session_state.construction_cost = total_estimated_cost
    st.session_state.formatted_cost = formatted_total
    st.session_state.cost_words = total_words

    st.session_state.user_budget = user_budget
    st.session_state.formatted_budget = formatted_budget
    st.session_state.budget_words = budget_words

    st.session_state.net_budget = net_budget
    st.session_state.remaining_budget = remaining_budget
    st.session_state.formatted_remaining = formatted_remaining
    st.session_state.remaining_words = remaining_words

    st.session_state.budget_shortfall = budget_shortfall
    st.session_state.formatted_shortfall = formatted_shortfall
    st.session_state.shortfall_words = shortfall_words

    st.session_state.is_within_budget = is_within_budget
    st.session_state.affordability_status = affordability_status
    st.session_state.affordability_icon = affordability_icon
    st.session_state.affordability_color = affordability_color
    st.session_state.affordability_class = affordability_class

    st.session_state.bhk = f"{selected_house_model} - {recommended_bhk}"
    st.session_state.floors = recommended_floors
    st.session_state.cost_breakdown = cost_breakdown_dict
    st.session_state.rating_stars = rating_stars
    st.session_state.rating_score = rating_score
    st.session_state.rating_tag = rating_tag
    st.session_state.eco_stars = eco_stars
    st.session_state.eco_score = eco_score
    st.session_state.eco_tag = eco_tag
    st.session_state.location_display = location_hierarchy_string
    st.session_state.additional_features = selected_additional_features
    
    st.session_state.property_data = (
        st.session_state.user_email,
        lot_area,
        gr_liv_area,
        bedroom_abvgr,
        full_bath,
        overall_qual,
        year_built,
        garage_cars,
        converted_prediction,
        st.session_state.bhk,
        recommended_floors,
        total_estimated_cost,
        location_hierarchy_string,
        selected_country,
        final_state,
        final_city,
        final_locality,
        selected_house_model,
        user_budget,
        construction_quality,
        f"{rating_stars} {rating_score}/5.0",
        f"{eco_stars} {eco_score}/5.0",
        ", ".join(selected_additional_features)
    )

# =========================================================
# FINAL RESULTS, COST BREAKDOWN & 3D STUDIO
# =========================================================

if st.session_state.prediction is not None:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 1. PROPERTY VALUATION HERO CARD
    st.markdown(f"""
        <div class="valuation-card">
            <div class="val-header">🏠 AI PROPERTY VALUATION & AUTOMATED APPRAISAL ENGINE</div>
            <div style="font-size: 1rem; color: #94a3b8; margin-top: 0.2rem;">💰 Estimated Market Property Value (ML)</div>
            <div class="val-price">{st.session_state.formatted_price}</div>
            <div style="margin-top: 0.6rem;">
                <span style="font-size: 0.85rem; color: #cbd5e1; text-transform: uppercase; font-weight: 700;">📝 Price in Words:</span><br>
                <div class="val-words">{st.session_state.price_words}</div>
            </div>
            <div style="margin-top: 0.75rem; display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center;">
                <div class="val-location">
                    <span>📍</span> {st.session_state.location_display}
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1.5rem; padding-top: 1.25rem; border-top: 1px solid rgba(255,255,255,0.15);">
                <div style="background: rgba(255,255,255,0.08); padding: 0.85rem 1.1rem; border-radius: 12px; border-left: 3px solid #38bdf8;">
                    <div style="font-size: 0.78rem; text-transform: uppercase; color: #94a3b8; font-weight: 700;">🏗️ Base Construction Cost</div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: #f8fafc; margin-top: 0.2rem;">{st.session_state.formatted_base_cost}</div>
                </div>
                <div style="background: rgba(255,255,255,0.08); padding: 0.85rem 1.1rem; border-radius: 12px; border-left: 3px solid #10b981;">
                    <div style="font-size: 0.78rem; text-transform: uppercase; color: #94a3b8; font-weight: 700;">🌿 Additional Features Cost</div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: #f8fafc; margin-top: 0.2rem;">{st.session_state.formatted_additional}</div>
                </div>
                <div style="background: rgba(255,255,255,0.12); padding: 0.85rem 1.1rem; border-radius: 12px; border-left: 3px solid #f59e0b;">
                    <div style="font-size: 0.78rem; text-transform: uppercase; color: #cbd5e1; font-weight: 700;">💼 Total Estimated Project Cost</div>
                    <div style="font-size: 1.35rem; font-weight: 800; color: #38bdf8; margin-top: 0.2rem;">{st.session_state.formatted_total}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. HOUSE DETAILS GRID
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🏡 HOUSE DETAILS</div>', unsafe_allow_html=True)
    
    h_col1, h_col2, h_col3, h_col4, h_col5, h_col6 = st.columns(6)
    with h_col1:
        st.markdown(f"""
            <div class="detail-metric-card">
                <div class="metric-icon">🏛️</div>
                <div class="metric-val">{st.session_state.bhk}</div>
                <div class="metric-lbl">House Model & Type</div>
            </div>
        """, unsafe_allow_html=True)
    with h_col2:
        st.markdown(f"""
            <div class="detail-metric-card">
                <div class="metric-icon">🏢</div>
                <div class="metric-val">{st.session_state.floors}</div>
                <div class="metric-lbl">Building Levels</div>
            </div>
        """, unsafe_allow_html=True)
    with h_col3:
        st.markdown(f"""
            <div class="detail-metric-card">
                <div class="metric-icon">🛏️</div>
                <div class="metric-val">{bedroom_abvgr}</div>
                <div class="metric-lbl">Bedrooms</div>
            </div>
        """, unsafe_allow_html=True)
    with h_col4:
        st.markdown(f"""
            <div class="detail-metric-card">
                <div class="metric-icon">🚿</div>
                <div class="metric-val">{full_bath}</div>
                <div class="metric-lbl">Bathrooms</div>
            </div>
        """, unsafe_allow_html=True)
    with h_col5:
        st.markdown(f"""
            <div class="detail-metric-card">
                <div class="metric-icon">📐</div>
                <div class="metric-val">{gr_liv_area:,}</div>
                <div class="metric-lbl">Living Sq Ft</div>
            </div>
        """, unsafe_allow_html=True)
    with h_col6:
        st.markdown(f"""
            <div class="detail-metric-card">
                <div class="metric-icon">🚗</div>
                <div class="metric-val">{parking_spaces}</div>
                <div class="metric-lbl">Parking Bays</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # 3. AFFORDABILITY & BUDGET HEALTH ANALYSIS
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">💰 AFFORDABILITY & TOTAL PROJECT BUDGET HEALTH</div>', unsafe_allow_html=True)

    b_col1, b_col2, b_col3 = st.columns([1.2, 1.2, 1.2])
    with b_col1:
        st.markdown(f"""
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 1.25rem; height: 100%;">
                <div style="font-size: 0.82rem; color: #64748b; font-weight: 700; text-transform: uppercase;">💼 Total Estimated Project Cost</div>
                <div style="font-size: 1.85rem; font-weight: 800; color: #0284c7; margin: 0.25rem 0;">{st.session_state.formatted_total}</div>
                <div style="font-size: 0.88rem; font-weight: 600; color: #475569; margin-top: 0.35rem;">
                    <b>In Words:</b> {st.session_state.total_words}
                </div>
            </div>
        """, unsafe_allow_html=True)
    with b_col2:
        st.markdown(f"""
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 1.25rem; height: 100%;">
                <div style="font-size: 0.82rem; color: #64748b; font-weight: 700; text-transform: uppercase;">💰 User Planned Budget</div>
                <div style="font-size: 1.85rem; font-weight: 800; color: #0f172a; margin: 0.25rem 0;">{st.session_state.formatted_budget}</div>
                <div style="font-size: 0.88rem; font-weight: 600; color: #475569; margin-top: 0.35rem;">
                    <b>In Words:</b> {st.session_state.budget_words}
                </div>
            </div>
        """, unsafe_allow_html=True)
    with b_col3:
        st.markdown(f"""
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 1.25rem; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
                <div style="font-size: 0.82rem; color: #64748b; font-weight: 700; text-transform: uppercase; margin-bottom: 0.6rem;">📊 Affordability Status</div>
                <div class="{st.session_state.affordability_class}">
                    <span>{st.session_state.affordability_icon}</span> {st.session_state.affordability_status}
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Dynamic Advisory Status Banner
    if st.session_state.is_within_budget:
        st.markdown(f"""
            <div style="background: #f0fdf4; border: 1.5px solid #86efac; border-radius: 14px; padding: 1.25rem;">
                <div style="font-size: 1.05rem; font-weight: 700; color: #166534;">🟢 Within Budget • Surplus Available</div>
                <div style="font-size: 1rem; color: #15803d; margin-top: 0.4rem; line-height: 1.5;">
                    Your planned budget of <b>{st.session_state.formatted_budget}</b> comfortably covers the total estimated project cost of <b>{st.session_state.formatted_total}</b> with a remaining budget surplus of <b>{st.session_state.formatted_remaining}</b> (<b>{st.session_state.remaining_words}</b>).
                </div>
            </div>
        """, unsafe_allow_html=True)
    elif st.session_state.affordability_status == "CLOSE TO BUDGET":
        st.markdown(f"""
            <div style="background: #fffbeb; border: 1.5px solid #fde68a; border-radius: 14px; padding: 1.25rem;">
                <div style="font-size: 1.05rem; font-weight: 700; color: #b45309;">🟡 Close to Budget (Within 15%) • Shortfall: {st.session_state.formatted_shortfall}</div>
                <div style="font-size: 0.98rem; color: #92400e; margin-top: 0.4rem; line-height: 1.5;">
                    Total project cost of <b>{st.session_state.formatted_total}</b> slightly exceeds your planned budget of <b>{st.session_state.formatted_budget}</b> by <b>{st.session_state.formatted_shortfall}</b> (<b>{st.session_state.shortfall_words}</b>). Minor adjustments in the Requirement Optimizer below can bring your project comfortably within budget.
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style="background: #fef2f2; border: 1.5px solid #fca5a5; border-radius: 14px; padding: 1.25rem;">
                <div style="font-size: 1.05rem; font-weight: 700; color: #991b1b;">🔴 Exceeds Budget • Shortfall: {st.session_state.formatted_shortfall}</div>
                <div style="font-size: 0.98rem; color: #b91c1c; margin-top: 0.4rem; line-height: 1.5;">
                    Total project cost of <b>{st.session_state.formatted_total}</b> exceeds your planned budget of <b>{st.session_state.formatted_budget}</b> by <b>{st.session_state.formatted_shortfall}</b> (<b>{st.session_state.shortfall_words}</b>). Review the value-engineering recommendations in the Requirement Optimizer below to balance your design and budget.
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Itemized Cost Breakdown Table
    with st.expander("📊 View Itemized Cost Breakdown (Base Construction vs Luxury Amenities)", expanded=False):
        breakdown_rows = []
        for item_name, item_cost in st.session_state.cost_breakdown.items():
            if item_cost > 0:
                cat = "Luxury & Green Amenities" if item_name == "Optional Selected Amenities" else "Base Construction Core"
                breakdown_rows.append({
                    "Component": item_name,
                    "Category": cat,
                    "Estimated Amount": format_currency_value(item_cost, selected_country)
                })
        breakdown_rows.append({
            "Component": "— BASE CONSTRUCTION SUBTOTAL —",
            "Category": "Subtotal",
            "Estimated Amount": st.session_state.formatted_base_cost
        })
        if st.session_state.additional_cost > 0:
            breakdown_rows.append({
                "Component": "— ADDITIONAL AMENITIES SUBTOTAL —",
                "Category": "Subtotal",
                "Estimated Amount": st.session_state.formatted_additional
            })
        breakdown_rows.append({
            "Component": "★ TOTAL ESTIMATED PROJECT COST ★",
            "Category": "Total",
            "Estimated Amount": st.session_state.formatted_total
        })
        breakdown_rows.append({
            "Component": "💰 USER PLANNED BUDGET",
            "Category": "Budget",
            "Estimated Amount": st.session_state.formatted_budget
        })
        if st.session_state.is_within_budget:
            breakdown_rows.append({
                "Component": "🟢 REMAINING BUDGET SURPLUS",
                "Category": "Surplus",
                "Estimated Amount": st.session_state.formatted_remaining
            })
        else:
            breakdown_rows.append({
                "Component": "🔴 BUDGET SHORTFALL",
                "Category": "Deficit",
                "Estimated Amount": f"-{st.session_state.formatted_shortfall}"
            })

        breakdown_df = pd.DataFrame(breakdown_rows)
        render_dataframe(breakdown_df, hide_index=True)
        st.caption(f"**Total Project Estimate:** {st.session_state.formatted_total} ({st.session_state.total_words})")

    st.markdown('</div>', unsafe_allow_html=True)

    # 4. RATINGS & ECO SCORES
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        st.markdown(f"""
            <div class="rating-banner">
                <div>
                    <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; color: #b45309; letter-spacing: 1px;">⭐ PROPERTY RATING</div>
                    <div class="rating-stars" style="margin-top: 0.35rem;">{st.session_state.rating_stars}</div>
                    <div style="font-size: 0.95rem; color: #78350f; font-weight: 600; margin-top: 0.35rem;">Score: <b>{st.session_state.rating_score} / 5.0</b></div>
                </div>
                <div>
                    <span class="rating-tag">{st.session_state.rating_tag}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with r_col2:
        st.markdown(f"""
            <div class="eco-banner">
                <div>
                    <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; color: #166534; letter-spacing: 1px;">🌱 ECO & SMART HOUSE SCORE</div>
                    <div class="rating-stars" style="color: #16a34a; margin-top: 0.35rem;">{st.session_state.eco_stars}</div>
                    <div style="font-size: 0.95rem; color: #14532d; font-weight: 600; margin-top: 0.35rem;">Score: <b>{st.session_state.eco_score} / 5.0</b></div>
                </div>
                <div>
                    <span class="eco-tag">{st.session_state.eco_tag}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # 5. LOCATION-AWARE CLIMATE & PLANNING SUGGESTIONS
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">📍 Location-Aware Planning Suggestions for {final_locality}, {selected_city} ({selected_country})</div>', unsafe_allow_html=True)
    
    mid_east_countries = ["UAE", "Saudi Arabia", "Qatar", "Kuwait", "Oman", "Egypt", "Bahrain", "Jordan", "Iraq"]
    tropical_countries = ["Singapore", "Malaysia", "Thailand", "Indonesia", "Philippines", "Vietnam", "India", "Sri Lanka", "Bangladesh", "Brazil"]
    cold_countries = ["UK", "Germany", "France", "Canada", "Norway", "Sweden", "Denmark", "Finland", "Poland", "Russia", "Austria", "Switzerland", "Iceland"]
    
    if selected_country in mid_east_countries:
        sug_text = (
            "☀️ **Arid Climate & Solar Protection:** Specify high-performance Low-E insulated glazing (U-value < 1.4 W/m²K) with thermal-break aluminum profiles. "
            "Incorporate exterior solar shading louvers / modern mashrabiya screens on South and West elevations. "
            "High-efficiency VRF central HVAC cooling and insulated roof deck construction are strongly recommended."
        )
    elif selected_country in tropical_countries:
        sug_text = (
            "🌧️ **Tropical Monsoon & Cross-Ventilation:** Design deep balcony overhangs and extended roof eaves to shield against torrential monsoon downpours and intense solar radiation. "
            "Maximize dual-aspect cross-ventilation corridors. Anti-fungal moisture-resistant exterior paint and elevated plinths recommended for storm drainage."
        )
    elif selected_country in cold_countries:
        sug_text = (
            "❄️ **High-Efficiency Thermal Envelope:** Specify triple-glazed argon-filled windows, continuous external wall insulation (EWI), and an airtight vapor barrier. "
            "Mechanical Ventilation with Heat Recovery (MVHR) is recommended to maintain superior indoor air quality while minimizing heating energy loss during winter."
        )
    elif selected_country in ["USA", "Australia", "New Zealand", "South Africa", "Mexico"]:
        sug_text = (
            "🌿 **Indoor-Outdoor Architecture & Solar Yield:** Seamless sliding glass patio doors connecting living zones to outdoor alfresco decks. "
            "Position roof pitches for maximum solar PV collection efficiency. Drought-tolerant native landscaping and rainwater harvesting storage tanks recommended."
        )
    else:
        sug_text = (
            "🏡 **Sustainable Climate-Calibrated Architecture:** Prioritize natural passive solar orientation, high-durability regional masonry materials, "
            "energy-efficient LED illumination zones, and low-VOC interior finishes tailored to local environmental standards."
        )
    st.info(sug_text)
    st.caption("ℹ️ *Informational planning suggestions based on regional climate factors. Professional structural and architectural drawings must be certified by registered local architects.*")
    st.markdown('</div>', unsafe_allow_html=True)

    # 6. GENERATED REAL DYNAMIC 3D HOUSE MODEL
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🏗️ GENERATED 3D ARCHITECTURAL HOUSE PLANNER</div>', unsafe_allow_html=True)
    st.write(f"Dynamic architectural model synthesized for **{selected_house_model}** based on your exact requirements ({st.session_state.floors}, {bedroom_abvgr} Beds, {full_bath} Baths, {parking_spaces} Parking, {balcony_count} Balconies).")

    floor_cnt = int(st.session_state.floors.split()[0])
    floor_count = floor_cnt
    
    view_options = [
        "🏡 Exterior View (Full House + Roof)",
        "🏗️ All Floors (Cutaway Interior)",
        "🏢 Ground Floor (Interior)"
    ]
    if floor_cnt >= 2:
        view_options.append("🏢 First Floor (Interior)")
    if floor_cnt >= 3:
        view_options.append("🏢 Second Floor (Interior)")
    if floor_cnt >= 4:
        view_options.append("🏢 Third Floor (Interior)")

    v_col1, v_col2 = st.columns([1, 1])
    with v_col1:
        sel_view_mode = st.selectbox("👁️ Model View Mode", view_options, index=0, key="viewer_perspective")
    with v_col2:
        sel_camera_angle = st.selectbox(
            "📐 Camera Angle Preset",
            ["📐 Isometric 3D View", "🏛️ Front Elevation", "🏢 Side Elevation", "🗺️ Top-Down Plan View"],
            index=0,
            key="viewer_cam_angle"
        )

    fig3d = generate_architectural_house_3d(
        house_model=selected_house_model,
        bhk=st.session_state.bhk,
        floors=st.session_state.floors,
        view_mode=sel_view_mode,
        parking_spaces=parking_spaces,
        kitchen_count=kitchen_count,
        dining_count=dining_count,
        balcony_count=balcony_count,
        bedroom_count=bedroom_abvgr,
        bathroom_count=full_bath,
        camera_angle=sel_camera_angle,
        additional_features=st.session_state.additional_features
    )

    render_plotly_chart(fig3d, config={"scrollZoom": True, "displaylogo": False, "responsive": True})
    st.caption("💡 **3D Interaction:** Left-click drag to rotate/orbit in 3D space, right-click drag to pan, and scroll wheel to zoom in and out.")
    st.markdown('</div>', unsafe_allow_html=True)

    # 7. WHAT-IF DESIGN SENSITIVITY ANALYSIS
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🔄 What-If Design & Budget Sensitivity Analysis</div>', unsafe_allow_html=True)
    st.write("Interactively test how changing key requirements (living area, bedrooms, bathrooms, floors, parking, quality tier, or amenities) dynamically impacts your project cost and budget feasibility.")
    
    wi_c1, wi_c2, wi_c3, wi_c4 = st.columns(4)
    with wi_c1:
        wi_area = st.number_input("What-If Living Area (sq ft)", min_value=400, max_value=20000, value=gr_liv_area, step=100)
        wi_beds = st.number_input("What-If Bedrooms", min_value=1, max_value=10, value=bedroom_abvgr)
    with wi_c2:
        wi_baths = st.number_input("What-If Bathrooms", min_value=1, max_value=10, value=full_bath)
        wi_parks = st.number_input("What-If Parking Bays", min_value=0, max_value=6, value=parking_spaces)
    with wi_c3:
        wi_floors = st.selectbox("What-If Building Levels", ["1 Floor", "2 Floors", "3 Floors", "4 Floors"], index=floor_cnt - 1)
        wi_quality = st.selectbox("What-If Quality Tier", ["Basic", "Standard", "Premium", "Luxury"], index=["Basic", "Standard", "Premium", "Luxury"].index(construction_quality))
    with wi_c4:
        wi_budget_override = st.number_input(f"What-If Budget ({curr_symbol})", min_value=0, value=int(user_budget), step=country_cfg["budget_step"])
        wi_include_amenities = st.checkbox("Include Selected Amenities in What-If", value=True)

    wi_fl_cnt = int(wi_floors.split()[0])
    wi_base_rate = country_cfg["construction_rate_sqft"] * quality_multipliers.get(wi_quality, 1.0)
    wi_base_cost = (
        wi_area * wi_base_rate +
        wi_beds * country_cfg["cost_bedroom"] +
        wi_baths * country_cfg["cost_bathroom"] +
        wi_parks * country_cfg["cost_parking"] +
        kitchen_count * country_cfg["cost_kitchen"] +
        dining_count * country_cfg["cost_dining"] +
        balcony_count * country_cfg["cost_balcony"] +
        max(0, wi_fl_cnt - 1) * wi_area * country_cfg["cost_floor_extra"]
    )
    wi_amenities_cost = sum(country_cfg["opt_costs"].get(f, 0) for f in selected_additional_features) if wi_include_amenities else 0.0
    wi_total_cost = wi_base_cost + wi_amenities_cost
    wi_delta = wi_total_cost - st.session_state.total_estimated_cost
    wi_net = wi_budget_override - wi_total_cost

    if wi_net >= 0:
        wi_status = "🟢 Within Budget"
    elif abs(wi_net) <= 0.15 * max(1.0, float(wi_budget_override)):
        wi_status = "🟡 Close to Budget"
    else:
        wi_status = "🔴 Exceeds Budget"

    wi_res_c1, wi_res_c2, wi_res_c3, wi_res_c4 = st.columns(4)
    wi_res_c1.metric("What-If Total Cost", format_currency_value(wi_total_cost, selected_country))
    wi_res_c2.metric("Difference vs Current", format_currency_value(abs(wi_delta), selected_country), delta=f"{'+' if wi_delta >= 0 else '-'}{format_currency_value(abs(wi_delta), selected_country)}", delta_color="inverse")
    wi_res_c3.metric("Net Surplus / Deficit", format_currency_value(abs(wi_net), selected_country), delta="Surplus" if wi_net >= 0 else "Deficit")
    wi_res_c4.metric("What-If Feasibility", wi_status)
    st.markdown('</div>', unsafe_allow_html=True)

    # 8. REQUIREMENT OPTIMIZER (VALUE-ENGINEERING RECOMMENDATIONS)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">💡 REQUIREMENT OPTIMIZER & VALUE-ENGINEERING ADVISOR</div>', unsafe_allow_html=True)

    if not st.session_state.is_within_budget:
        st.write(f"The project currently has an estimated budget shortfall of **{st.session_state.formatted_shortfall}**. Below are calculated, actionable value-engineering options to bring your design within budget without compromising structural integrity:")
        
        opt_cols = st.columns(3)
        savings_options = []
        
        # Option 1: Quality Tier
        if construction_quality in ["Luxury", "Premium"]:
            target_tier = "Premium" if construction_quality == "Luxury" else "Standard"
            tier_rate = country_cfg["construction_rate_sqft"] * quality_multipliers[target_tier]
            tier_savings = gr_liv_area * (base_rate - tier_rate)
            if tier_savings > 0:
                savings_options.append((f"Switch Quality: {construction_quality} → {target_tier}", tier_savings))

        # Option 2: Area Optimization
        if gr_liv_area > 1000:
            area_delta = min(300, max(100, int(gr_liv_area * 0.12)))
            area_savings = area_delta * base_rate
            savings_options.append((f"Optimize Living Area by -{area_delta:,} sq ft", area_savings))

        # Option 3: Floors
        if floor_cnt > 1:
            floor_savings = gr_liv_area * country_cfg["cost_floor_extra"]
            savings_options.append((f"Reduce Building Height by 1 Level ({floor_cnt} → {floor_cnt - 1} Fl)", floor_savings))

        # Option 4: Parking
        if parking_spaces > 1:
            park_savings = country_cfg["cost_parking"]
            savings_options.append((f"Reduce Parking Bays by 1 ({parking_spaces} → {parking_spaces - 1})", park_savings))

        # Option 5: Luxury Amenities
        for feat in ["Swimming Pool", "Lift / Elevator", "Terrace Garden"]:
            if feat in st.session_state.additional_features:
                f_cost = country_cfg["opt_costs"].get(feat, 0)
                if f_cost > 0:
                    savings_options.append((f"Phase {feat} to Future Stage", f_cost))

        for idx, (label, amt) in enumerate(savings_options[:3]):
            with opt_cols[idx % 3]:
                st.markdown(f"""
                    <div style="background: #f8fafc; border: 1.5px solid #cbd5e1; border-radius: 12px; padding: 1.1rem; text-align: center; height: 100%;">
                        <div style="font-size: 0.88rem; font-weight: 700; color: #1e293b;">{label}</div>
                        <div style="font-size: 1.35rem; font-weight: 800; color: #16a34a; margin: 0.35rem 0;">
                            Saves {format_currency_value(amt, selected_country)}
                        </div>
                        <div style="font-size: 0.78rem; color: #64748b;">Direct project cost reduction</div>
                    </div>
                """, unsafe_allow_html=True)

        total_possible = sum(amt for _, amt in savings_options)
        new_surplus = total_possible - st.session_state.budget_shortfall
        if new_surplus >= 0:
            st.success(f"🎯 **Combined Savings Potential:** Applying the recommended options yields up to **{format_currency_value(total_possible, selected_country)}** in savings, successfully transforming the budget shortfall into a net surplus of **{format_currency_value(new_surplus, selected_country)}**!")
    else:
        st.write(f"🎉 **Your Project is Fully Within Budget!** You have a healthy budget surplus of **{st.session_state.formatted_remaining}**.")
        st.markdown(f"""
            <div style="background: #f0fdf4; border: 1.5px solid #86efac; border-radius: 12px; padding: 1.25rem;">
                <div style="font-weight: 700; color: #166534; font-size: 1rem;">🌟 High-Value Sustainable Recommendations:</div>
                <div style="color: #15803d; font-size: 0.95rem; margin-top: 0.5rem; line-height: 1.5;">
                    • <b>Rooftop Solar PV Installation:</b> Estimated cost {format_currency_value(country_cfg['opt_costs'].get('Solar Panels', 200000), selected_country)} provides 25+ years of green electricity yield and boosts Eco Score to 5.0.<br>
                    • <b>Interior Finish Upgrades:</b> Premium low-VOC Italian flooring or smart home automation can be accommodated within your remaining surplus.<br>
                    • <b>Contingency Reserve:</b> Retain 5–10% of the surplus for unforeseen site groundworks or municipal approval contingencies.
                </div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 9. SIMPLE HOME LOAN / EMI FINANCIAL PLANNING CALCULATOR
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🏦 Simple Home Loan & EMI Planning Calculator</div>', unsafe_allow_html=True)
    st.write("Estimate monthly mortgage payments and financing feasibility for your project. Designed for initial budgeting and feasibility planning.")
    
    emi_c1, emi_c2, emi_c3, emi_c4 = st.columns(4)
    with emi_c1:
        loan_project_cost = st.number_input(
            f"Project Cost ({curr_symbol})",
            min_value=0,
            value=int(st.session_state.total_estimated_cost),
            step=country_cfg["budget_step"],
            key="loan_cost_input"
        )
    with emi_c2:
        down_payment_pct = st.slider(
            "Down Payment (%)",
            min_value=5,
            max_value=60,
            value=20,
            step=5,
            key="loan_down_pct"
        )
    with emi_c3:
        annual_rate = st.slider(
            "Annual Interest Rate (%)",
            min_value=2.5,
            max_value=16.0,
            value=8.5,
            step=0.1,
            key="loan_interest_pct"
        )
    with emi_c4:
        tenure_years = st.selectbox(
            "Loan Tenure (Years)",
            [5, 10, 15, 20, 25, 30],
            index=3,
            key="loan_tenure_sel"
        )

    # Loan Computations
    down_payment_val = loan_project_cost * (down_payment_pct / 100.0)
    principal_loan = max(0.0, loan_project_cost - down_payment_val)
    
    monthly_r = (annual_rate / 100.0) / 12.0
    tenure_months = tenure_years * 12
    
    if principal_loan > 0 and monthly_r > 0 and tenure_months > 0:
        monthly_emi = (principal_loan * monthly_r * ((1.0 + monthly_r) ** tenure_months)) / (((1.0 + monthly_r) ** tenure_months) - 1.0)
        total_loan_repayment = monthly_emi * tenure_months
        total_loan_interest = max(0.0, total_loan_repayment - principal_loan)
    else:
        monthly_emi = 0.0
        total_loan_repayment = principal_loan
        total_loan_interest = 0.0

    emi_res_c1, emi_res_c2, emi_res_c3, emi_res_c4 = st.columns(4)
    with emi_res_c1:
        st.markdown(f"""
            <div class="loan-metric-box">
                <div class="loan-metric-lbl">📅 Monthly EMI</div>
                <div class="loan-metric-val">{format_currency_value(monthly_emi, selected_country)}</div>
                <div style="font-size: 0.78rem; color: #475569; font-weight: 600;">{number_to_words(monthly_emi, selected_country)}/month</div>
            </div>
        """, unsafe_allow_html=True)
    with emi_res_c2:
        st.markdown(f"""
            <div class="loan-metric-box">
                <div class="loan-metric-lbl">💳 Principal Borrowed</div>
                <div class="loan-metric-val" style="color: #0f172a;">{format_currency_value(principal_loan, selected_country)}</div>
                <div style="font-size: 0.78rem; color: #64748b;">Down payment: {format_currency_value(down_payment_val, selected_country)} ({down_payment_pct}%)</div>
            </div>
        """, unsafe_allow_html=True)
    with emi_res_c3:
        st.markdown(f"""
            <div class="loan-metric-box">
                <div class="loan-metric-lbl">📈 Total Interest</div>
                <div class="loan-metric-val" style="color: #d97706;">{format_currency_value(total_loan_interest, selected_country)}</div>
                <div style="font-size: 0.78rem; color: #64748b;">Over {tenure_years} years @ {annual_rate}%</div>
            </div>
        """, unsafe_allow_html=True)
    with emi_res_c4:
        st.markdown(f"""
            <div class="loan-metric-box">
                <div class="loan-metric-lbl">🧾 Total Repayment</div>
                <div class="loan-metric-val" style="color: #7c3aed;">{format_currency_value(total_loan_repayment, selected_country)}</div>
                <div style="font-size: 0.78rem; color: #64748b;">Principal + Interest combined</div>
            </div>
        """, unsafe_allow_html=True)

    st.caption("ℹ️ **Financial Planning Estimate:** For budgeting and preliminary feasibility only. Excludes loan origination fees, property taxes, homeowner's insurance, and private mortgage insurance (PMI). No bank accounts, KYC, or credit bureau checks required.")
    st.markdown('</div>', unsafe_allow_html=True)

    # 10. DESIGN COMPARISON TOOL (COMPARE 2 DESIGNS)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">⚖️ Compare Designs Side-by-Side</div>', unsafe_allow_html=True)
    st.write("Compare your current generated design with an alternative architectural style.")
    
    other_models = [m for m in house_models if m != selected_house_model]
    cmp_model = st.selectbox("Select Alternative House Model to Compare", other_models, index=0)
    
    cmp_t1, cmp_t2 = st.tabs(["📊 Metric Comparison Table", "🏗️ Alternative 3D Preview"])
    with cmp_t1:
        cmp_rating_stars, cmp_rating_score, cmp_rating_tag = calculate_dynamic_property_rating(
            overall_qual, gr_liv_area, bedroom_abvgr, full_bath, garage_cars,
            construction_quality, floor_count, balcony_count, parking_spaces,
            cmp_model, selected_additional_features
        )
        
        cmp_table_data = {
            "Specification": ["House Model", "Levels", "Bedrooms", "Bathrooms", "Parking", "Balconies", "Rating", "Eco Score", "Architectural Style"],
            f"Current Design ({selected_house_model})": [
                str(selected_house_model), str(st.session_state.floors), str(bedroom_abvgr), str(full_bath),
                str(parking_spaces), str(balcony_count), f"{st.session_state.rating_stars} ({st.session_state.rating_score}/5.0)",
                f"{st.session_state.eco_stars} ({st.session_state.eco_score}/5.0)", str(HOUSE_THEMES[selected_house_model]["roof_type"].replace("_", " ").title())
            ],
            f"Alternative Design ({cmp_model})": [
                str(cmp_model), str(st.session_state.floors), str(bedroom_abvgr), str(full_bath),
                str(parking_spaces), str(balcony_count), f"{cmp_rating_stars} ({cmp_rating_score}/5.0)",
                f"{st.session_state.eco_stars} ({st.session_state.eco_score}/5.0)", str(HOUSE_THEMES[cmp_model]["roof_type"].replace("_", " ").title())
            ]
        }
        cmp_df = pd.DataFrame(cmp_table_data).astype(str)
        render_dataframe(cmp_df, hide_index=True)
        
    with cmp_t2:
        fig_cmp = generate_architectural_house_3d(
            house_model=cmp_model,
            bhk=f"{cmp_model} - {recommended_bhk}",
            floors=st.session_state.floors,
            view_mode="🏡 Exterior View (Full House + Roof)",
            parking_spaces=parking_spaces,
            kitchen_count=kitchen_count,
            dining_count=dining_count,
            balcony_count=balcony_count,
            bedroom_count=bedroom_abvgr,
            bathroom_count=full_bath,
            additional_features=st.session_state.additional_features
        )
        render_plotly_chart(fig_cmp)
    st.markdown('</div>', unsafe_allow_html=True)

    # 11. PROPERTY REPORT & SAVE VALUATION
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📄 Generate Executive Property Report & Save</div>', unsafe_allow_html=True)
    
    rep_col1, rep_col2 = st.columns(2)
    with rep_col1:
        if st.button("💾 Save Property Valuation & Design", use_container_width=True, type="primary"):
            if st.session_state.property_data is None:
                st.error("Please calculate a property valuation first.")
            else:
                try:
                    save_valuation(st.session_state.property_data)
                    st.success("✅ Valuation and architectural design successfully saved! View it anytime under 'Saved Valuations' in the sidebar.")
                except Exception as ex:
                    st.error(f"❌ Unable to save valuation: {ex}")

    with rep_col2:
        report_text = f"""==================================================
AI REAL ESTATE VALUATION & ARCHITECTURAL APPRAISAL REPORT
==================================================
1. Property Location: {st.session_state.location_display}
2. Country / Currency: {selected_country} ({curr_symbol})
3. House Architectural Model: {selected_house_model}
4. Layout Configuration: {recommended_bhk}
5. Building Levels (Floors): {st.session_state.floors}
6. Living Area: {gr_liv_area:,} sq ft
7. Lot Area: {lot_area:,} sq ft
8. Bedrooms: {bedroom_abvgr}
9. Bathrooms: {full_bath}
10. Parking Bays: {parking_spaces}
11. Balconies: {balcony_count}
12. Construction Finish Quality: {construction_quality}

FINANCIAL APPRAISAL & BUDGET BREAKDOWN:
13. Estimated Market Property Value (ML): {st.session_state.formatted_price}
    Price in Words: {st.session_state.price_words}
14. Base Construction Cost: {st.session_state.formatted_base_cost}
    Base Cost in Words: {st.session_state.base_cost_words}
15. Selected Additional Features Cost: {st.session_state.formatted_additional}
    Total Estimated Project Cost: {st.session_state.formatted_total}
    Total Cost in Words: {st.session_state.total_words}
    User Planned Budget: {st.session_state.formatted_budget}
    Budget Affordability Status: {st.session_state.affordability_icon} {st.session_state.affordability_status}
    Net Remaining Surplus / Shortfall: {st.session_state.formatted_remaining if st.session_state.is_within_budget else f"-{st.session_state.formatted_shortfall}"}

RATINGS & SCORES:
- Property Rating: {st.session_state.rating_stars} ({st.session_state.rating_score}/5.0 - {st.session_state.rating_tag})
- Eco / Smart House Score: {st.session_state.eco_stars} ({st.session_state.eco_score}/5.0 - {st.session_state.eco_tag})
- Selected Amenities: {', '.join(st.session_state.additional_features) if st.session_state.additional_features else 'None'}

==================================================
Report Generated by AI Real Estate Valuation Studio
=================================================="""

        st.download_button(
            label="📄 Download Executive Property Report (.txt)",
            data=report_text,
            file_name=f"Property_Valuation_Report_{selected_city}_{selected_house_model.replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    with st.expander("👁️ Preview Formatted Property Report", expanded=False):
        st.text(report_text)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# FOOTER
# =========================================================

st.markdown("""
    <div style="text-align: center; color: #94a3b8; font-size: 0.85rem; padding: 2rem 0; margin-top: 2rem; border-top: 1px solid #e2e8f0;">
        🏠 AI-Based Real Estate Valuation & Architectural Appraisal Studio • Built with Precision
    </div>
""", unsafe_allow_html=True)