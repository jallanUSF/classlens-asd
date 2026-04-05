"""
ClassLens ASD — Design System CSS
Calm colors, predictable layouts, high contrast, minimal visual noise.
3-view navigation: My Students → Capture & Create → Progress & Reports
"""

ASD_FRIENDLY_CSS = """
<style>
/* ── Base ─────────────────────────────────────────────────── */
.stApp {
    max-width: 1200px;
    margin: 0 auto;
    background: #FAFAFA;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

/* ── Typography ───────────────────────────────────────────── */
h1 {
    color: #2C3E50;
    font-size: 1.8rem !important;
    font-weight: 600 !important;
    border-bottom: 3px solid #5B8FB9;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem !important;
}

h2 {
    color: #2C3E50;
    font-size: 1.3rem !important;
    font-weight: 600 !important;
    margin-top: 1.5rem !important;
}

h3 {
    color: #5B8FB9;
    font-size: 1.1rem !important;
    font-weight: 500 !important;
}

/* ── Navigation bar ───────────────────────────────────────── */
.nav-container {
    display: flex;
    gap: 8px;
    margin-bottom: 1.5rem;
    border-bottom: 2px solid #E8ECF0;
    padding-bottom: 8px;
}

.nav-btn {
    padding: 10px 24px;
    border-radius: 8px 8px 0 0;
    border: none;
    font-size: 0.95rem;
    font-weight: 500;
    cursor: pointer;
    color: #7F8C8D;
    background: transparent;
    border-bottom: 3px solid transparent;
    transition: color 0.15s, border-color 0.15s;
}

.nav-btn:hover {
    color: #5B8FB9;
}

.nav-btn.active {
    color: #5B8FB9;
    border-bottom: 3px solid #5B8FB9;
    font-weight: 600;
}

/* ── Cards ────────────────────────────────────────────────── */
.cl-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border-left: 4px solid transparent;
}

.cl-card-selected {
    border-left: 4px solid #4ECDC4;
}

.goal-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    border-left: 4px solid #5B8FB9;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.alert-card {
    background: #FFF3CD;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
    border-left: 4px solid #FFC107;
}

.success-card {
    background: #D4EDDA;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
    border-left: 4px solid #28A745;
}

/* ── Student cards ────────────────────────────────────────── */
.student-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    cursor: pointer;
    border-left: 4px solid transparent;
    transition: box-shadow 0.15s, border-color 0.15s;
}

.student-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.student-card-active {
    border-left: 4px solid #4ECDC4;
}

.student-name {
    font-size: 1.15rem;
    font-weight: 600;
    color: #2C3E50;
    margin-bottom: 4px;
}

.student-meta {
    font-size: 0.85rem;
    color: #7F8C8D;
    margin-bottom: 4px;
}

.student-stats {
    font-size: 0.85rem;
    color: #7F8C8D;
}

/* ── ASD Level badges ─────────────────────────────────────── */
.badge-level-1 {
    background: #4ECDC4;
    color: white;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 500;
}

.badge-level-2 {
    background: #5B8FB9;
    color: white;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 500;
}

.badge-level-3 {
    background: #9B59B6;
    color: white;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 500;
}

/* ── Trend badges ─────────────────────────────────────────── */
.badge-improving {
    background: #28A745;
    color: white;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: 500;
}

.badge-stable {
    background: #5B8FB9;
    color: white;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: 500;
}

.badge-plateau {
    background: #FFC107;
    color: #2C3E50;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: 500;
}

.badge-declining {
    background: #DC3545;
    color: white;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: 500;
}

/* ── Metric cards ─────────────────────────────────────────── */
div[data-testid="stMetric"] {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 0.8rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border-left: 4px solid;
    border-image: linear-gradient(to bottom, #5B8FB9, #4ECDC4) 1;
}

/* ── Material tiles (3x2 grid) ────────────────────────────── */
.material-tile {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    cursor: pointer;
    transition: box-shadow 0.15s, transform 0.15s;
    border: 1px solid #E8ECF0;
}

.material-tile:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    transform: translateY(-2px);
}

.material-tile-icon {
    font-size: 1.8rem;
    margin-bottom: 4px;
}

.material-tile-label {
    font-size: 0.8rem;
    font-weight: 500;
    color: #2C3E50;
}

/* ── Material output containers ───────────────────────────── */
.material-output {
    background: white;
    border: 1px solid #E0E0E0;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    line-height: 1.6;
}

/* ── Buttons ──────────────────────────────────────────────── */
.stButton > button {
    border-radius: 8px;
    font-weight: 500;
}

/* ── Sidebar ──────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #F0F4F8;
}

.sidebar-student {
    background: #FFFFFF;
    border-radius: 10px;
    padding: 0.7rem 0.9rem;
    margin-bottom: 0.5rem;
    cursor: pointer;
    border-left: 3px solid transparent;
    font-size: 0.9rem;
    transition: border-color 0.15s;
}

.sidebar-student:hover {
    border-left: 3px solid #5B8FB9;
}

.sidebar-student-active {
    border-left: 3px solid #4ECDC4;
    background: #E8F8F5;
}

/* ── Locked placeholder ───────────────────────────────────── */
.locked-placeholder {
    background: #F5F5F5;
    border: 2px dashed #D0D0D0;
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    color: #ABABAB;
}

/* ── Hide Streamlit chrome ────────────────────────────────── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""


def inject_styles():
    """Inject ASD-friendly CSS into the Streamlit app."""
    import streamlit as st
    st.markdown(ASD_FRIENDLY_CSS, unsafe_allow_html=True)
