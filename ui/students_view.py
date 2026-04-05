"""
My Students view — Card grid of all students.
Click a card to select student and switch to Capture & Create.
"""

import streamlit as st

STUDENT_EMOJI = {
    "maya_2026": "🦕",
    "jaylen_2026": "🚂",
    "sofia_2026": "🌍",
}


def render_students():
    """Render the My Students card grid."""
    st.header("My Students")
    st.markdown("_Select a student to capture work and generate materials._")

    profiles = st.session_state.get("profiles", {})
    if not profiles:
        st.warning("No student profiles found.")
        return

    cols = st.columns(3)
    for i, (sid, prof) in enumerate(profiles.items()):
        with cols[i % 3]:
            _render_student_card(sid, prof)


def _render_student_card(sid: str, prof: dict):
    """Render a single student card with stats."""
    emoji = STUDENT_EMOJI.get(sid, "👤")
    name = prof["name"]
    grade = prof["grade"]
    level = prof["asd_level"]
    goals = prof.get("iep_goals", [])
    total_sessions = sum(len(g.get("trial_history", [])) for g in goals)

    # Calculate overall trend
    trend_text, trend_arrow = _get_overall_trend(goals)

    # Level badge color
    level_class = f"badge-level-{level}"

    is_current = st.session_state.get("current_student") == sid
    card_border = "border-left: 4px solid #4ECDC4;" if is_current else "border-left: 4px solid transparent;"

    st.markdown(
        f"""<div style="background: #FFFFFF; border-radius: 12px; padding: 1.2rem 1.5rem;
            margin-bottom: 0.8rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); {card_border}">
            <div style="font-size: 1.3rem; margin-bottom: 2px;">
                {emoji} <strong style="color: #2C3E50;">{name}</strong>
            </div>
            <div style="font-size: 0.85rem; color: #7F8C8D; margin-bottom: 6px;">
                Grade {grade} · <span class="{level_class}">Level {level}</span>
            </div>
            <div style="font-size: 0.85rem; color: #7F8C8D; margin-bottom: 4px;">
                {trend_text} {trend_arrow}
            </div>
            <div style="font-size: 0.85rem; color: #7F8C8D;">
                {len(goals)} goals · {total_sessions} sessions
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    if st.button(f"Select {name}", key=f"select_{sid}", use_container_width=True):
        st.session_state["current_student"] = sid
        st.session_state["active_view"] = "capture"
        st.rerun()


def _get_overall_trend(goals: list) -> tuple:
    """Calculate overall trend across all goals. Returns (text, arrow)."""
    all_recent = []
    all_older = []

    for g in goals:
        history = g.get("trial_history", [])
        if len(history) < 2:
            continue
        recent = [h.get("pct", 0) for h in history[-3:]]
        older = [h.get("pct", 0) for h in history[-6:-3]] if len(history) >= 6 else [h.get("pct", 0) for h in history[:3]]
        all_recent.extend(recent)
        all_older.extend(older)

    if not all_recent or not all_older:
        return "New", ""

    recent_avg = sum(all_recent) / len(all_recent)
    older_avg = sum(all_older) / len(all_older)
    diff = recent_avg - older_avg

    if diff > 5:
        return f"{recent_avg:.0f}%", "↑"
    elif diff < -5:
        return f"{recent_avg:.0f}%", "↓"
    else:
        return f"{recent_avg:.0f}%", "→"
