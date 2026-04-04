"""
ASD-friendly CSS styles for ClassLens Streamlit app.
Calm colors, predictable layouts, high contrast, minimal visual noise.
"""

ASD_FRIENDLY_CSS = """
<style>
/* ── Base: reduce visual noise ─────────────────────────── */
.stApp {
    max-width: 1100px;
    margin: 0 auto;
}

/* Calm, predictable spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* ── Typography: readable, consistent ──────────────────── */
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

/* ── Cards: consistent containers ──────────────────────── */
.goal-card {
    background: #F0F4F8;
    border-radius: 8px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    border-left: 4px solid #5B8FB9;
}

.alert-card {
    background: #FFF3CD;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    border-left: 4px solid #FFC107;
}

.success-card {
    background: #D4EDDA;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    border-left: 4px solid #28A745;
}

/* ── Status badges ─────────────────────────────────────── */
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

/* ── Buttons: clear, predictable ───────────────────────── */
.stButton > button {
    border-radius: 6px;
    font-weight: 500;
    transition: background-color 0.2s;
}

/* ── Reduce Streamlit visual noise ─────────────────────── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Tabs: calmer styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    padding: 8px 16px;
    font-weight: 500;
}

/* ── Material output containers ────────────────────────── */
.material-output {
    background: white;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    padding: 1.5rem;
    margin: 1rem 0;
    line-height: 1.6;
}

/* ── Metric cards ──────────────────────────────────────── */
div[data-testid="stMetric"] {
    background: #F0F4F8;
    border-radius: 8px;
    padding: 0.8rem;
}
</style>
"""


def inject_styles():
    """Inject ASD-friendly CSS into the Streamlit app."""
    import streamlit as st
    st.markdown(ASD_FRIENDLY_CSS, unsafe_allow_html=True)
