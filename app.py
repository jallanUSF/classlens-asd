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

# ── Inject design system CSS ─────────────────────────────
inject_styles()

# ── Emoji map for students ────────────────────────────────
STUDENT_EMOJI = {
    "maya_2026": "🦕",
    "jaylen_2026": "🚂",
    "sofia_2026": "🌍",
}

# ── Load student profiles into session state ──────────────
if "profiles" not in st.session_state:
    profiles = {}
    students_dir = Path("data/students")
    for json_file in sorted(students_dir.glob("*.json")):
        with open(json_file, "r") as f:
            data = json.load(f)
        profiles[data["student_id"]] = data
    st.session_state["profiles"] = profiles

# ── Initialize navigation state ──────────────────────────
if "active_view" not in st.session_state:
    st.session_state["active_view"] = "students"


# ── App header ─────────────────────────────────────────────
st.title("ClassLens ASD")
st.markdown("**Multimodal IEP Intelligence for Autistic Learners**")


# ── Demo mode banner ──────────────────────────────────────
api_key = os.getenv("GOOGLE_AI_STUDIO_KEY", "")
if not api_key or api_key == "your_api_key_here":
    st.info(
        "Demo Mode Active — Using sample data for quick preview. "
        "Set GOOGLE_AI_STUDIO_KEY in .env for live Gemma 4 inference."
    )


# ── 3-view navigation ────────────────────────────────────
def _switch_view(view: str):
    st.session_state["active_view"] = view


nav_cols = st.columns(3)
views = [
    ("students", "My Students"),
    ("capture", "Capture & Create"),
    ("progress", "Progress & Reports"),
]
for i, (key, label) in enumerate(views):
    with nav_cols[i]:
        btn_type = "primary" if st.session_state["active_view"] == key else "secondary"
        if st.button(label, key=f"nav_{key}", use_container_width=True, type=btn_type):
            _switch_view(key)
            st.rerun()

st.markdown("---")


# ── Sidebar: compact student list + profile ───────────────
with st.sidebar:
    st.markdown("### ClassLens ASD")
    st.caption("Select a student to begin")

    profiles = st.session_state["profiles"]
    current = st.session_state.get("current_student")

    for sid, prof in profiles.items():
        emoji = STUDENT_EMOJI.get(sid, "👤")
        is_active = sid == current
        badge_class = "sidebar-student-active" if is_active else ""

        if st.button(
            f"{emoji} {prof['name']} — Grade {prof['grade']}",
            key=f"sidebar_{sid}",
            use_container_width=True,
        ):
            st.session_state["current_student"] = sid
            if st.session_state["active_view"] == "students":
                st.session_state["active_view"] = "capture"
            st.rerun()

    st.markdown("---")

    # Show selected student profile summary
    if current and current in profiles:
        p = profiles[current]
        emoji = STUDENT_EMOJI.get(current, "👤")
        st.markdown(f"**{emoji} {p['name']}**")
        st.caption(f"Grade {p['grade']} | ASD Level {p['asd_level']}")
        st.caption(f"Comm: {p.get('communication_level', 'verbal')[:50]}")

        interests = p.get("interests", [])
        if interests:
            st.caption(f"Interests: {interests[0].split('(')[0].strip()}")

        goals = p.get("iep_goals", [])
        total_trials = sum(len(g.get("trial_history", [])) for g in goals)
        st.caption(f"{len(goals)} goals · {total_trials} sessions")

        sensory = p.get("sensory_profile", {})
        calming = sensory.get("calming_strategies", [])
        if calming:
            st.caption(f"Calming: {', '.join(calming[:2])}")

    st.markdown("---")
    st.caption("ClassLens ASD v0.2")
    st.caption("Gemma 4 Good Hackathon 2026")


# ── Route to active view ──────────────────────────────────
active = st.session_state["active_view"]

if active == "students":
    from ui.students_view import render_students
    render_students()
elif active == "capture":
    from ui.capture_view import render_capture
    render_capture()
elif active == "progress":
    from ui.progress_view import render_progress
    render_progress()
