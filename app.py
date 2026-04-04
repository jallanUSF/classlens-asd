"""
ClassLens ASD — Streamlit Demo App
Multimodal IEP Intelligence for Autistic Learners

Entry point: streamlit run app.py
"""

import json
import os
from pathlib import Path

import streamlit as st

from ui.styles import inject_styles

# ── Bridge st.secrets → os.environ for Streamlit Cloud ──
# The app reads API keys via os.getenv(), but Streamlit Cloud
# serves them through st.secrets. Copy them over early.
try:
    for key in ("GOOGLE_AI_STUDIO_KEY", "OPENROUTER_API_KEY"):
        if key not in os.environ and key in st.secrets:
            os.environ[key] = st.secrets[key]
except Exception:
    pass


# ── Page config (must be first Streamlit call) ─────────────
st.set_page_config(
    page_title="ClassLens ASD",
    page_icon="🔍",
    layout="wide",
)

# ── Inject ASD-friendly CSS ───────────────────────────────
inject_styles()

# ── Load student profiles into session state ──────────────
if "profiles" not in st.session_state:
    profiles = {}
    students_dir = Path("data/students")
    for json_file in sorted(students_dir.glob("*.json")):
        with open(json_file, "r") as f:
            data = json.load(f)
        profiles[data["student_id"]] = data
    st.session_state["profiles"] = profiles


# ── App header ─────────────────────────────────────────────
st.title("ClassLens ASD")
st.markdown("**Multimodal IEP Intelligence for Autistic Learners**")


# ── Sidebar: student selector ─────────────────────────────
with st.sidebar:
    st.markdown("### Select a Student")
    st.caption("Your student roster. Click to view their profile and recent work.")

    profiles = st.session_state["profiles"]
    for sid, prof in profiles.items():
        interests_short = prof.get("interests", [""])[0].split("(")[0].strip()
        label = f"{prof['name']} (Grade {prof['grade']}) — {interests_short}"
        if st.button(label, key=f"student_{sid}", use_container_width=True):
            st.session_state["current_student"] = sid

    st.markdown("---")

    # Show current student info
    current = st.session_state.get("current_student")
    if current and current in profiles:
        p = profiles[current]
        st.markdown(f"**{p['name']}**")
        st.caption(f"Grade {p['grade']} | ASD Level {p['asd_level']}")
        st.caption(f"Comm: {p.get('communication_level', 'verbal')}")
        st.caption(f"Goals: {len(p.get('iep_goals', []))}")

    st.markdown("---")
    st.caption("ClassLens ASD v0.1")
    st.caption("Gemma 4 Good Hackathon 2026")


# ── Demo mode banner ──────────────────────────────────────
api_key = os.getenv("GOOGLE_AI_STUDIO_KEY", "")
if not api_key or api_key == "your_api_key_here":
    st.info(
        "Demo Mode Active — Using sample data for quick preview. "
        "Set GOOGLE_AI_STUDIO_KEY in .env for live Gemma 4 inference."
    )


# ── Main navigation tabs ──────────────────────────────────
tab_upload, tab_dashboard, tab_materials, tab_lessons, tab_reports = st.tabs([
    "📸 Upload Work",
    "📊 Progress Dashboard",
    "📝 Generated Materials",
    "🎯 Lesson Planner",
    "📋 Admin Reports",
])

with tab_upload:
    from ui.upload import render_upload
    render_upload()

with tab_dashboard:
    from ui.dashboard import render_dashboard
    render_dashboard()

with tab_materials:
    from ui.outputs import render_outputs
    render_outputs()

with tab_lessons:
    from ui.lesson_planner import render_lesson_planner
    render_lesson_planner()

with tab_reports:
    from ui.reports import render_reports
    render_reports()
