"""
Progress & Reports view — Merged dashboard + admin reports.
Summary metrics, per-goal trend cards, multi-goal chart, report generator.
"""

import os
import streamlit as st
import plotly.graph_objects as go

STUDENT_EMOJI = {
    "maya_2026": "🦕",
    "jaylen_2026": "🚂",
    "sofia_2026": "🌍",
}


def render_progress():
    """Render the Progress & Reports view."""
    student_id = st.session_state.get("current_student")
    if not student_id:
        st.header("Progress & Reports")
        st.info("Select a student from My Students or the sidebar to view progress.")
        return

    profile = st.session_state.get("profiles", {}).get(student_id)
    if not profile:
        return

    emoji = STUDENT_EMOJI.get(student_id, "👤")
    st.header(f"{emoji} {profile['name']} — Progress & Reports")

    goals = profile.get("iep_goals", [])

    # ── Summary metrics row ───────────────────────────────
    _render_summary_metrics(goals)

    st.markdown("---")

    # ── Multi-goal overview chart ─────────────────────────
    if any(g.get("trial_history") for g in goals):
        st.subheader("Progress Overview")
        _render_multi_goal_chart(goals)
        st.markdown("---")

    # ── Per-goal detail cards ─────────────────────────────
    st.subheader("Goal Details")
    for goal in goals:
        _render_goal_card(goal, profile["name"])

    # ── Admin report section ──────────────────────────────
    st.markdown("---")
    st.subheader("Admin Report")
    st.markdown("_Professional progress report for IEP meetings and compliance._")

    cache_key = f"progress_admin_report_{student_id}"

    if st.button("Generate Full Report", type="primary", use_container_width=True):
        with st.spinner("Generating comprehensive report..."):
            forge = _get_forge()
            try:
                result = forge.generate_admin_report(student_id)
                st.session_state[cache_key] = result
            except Exception as e:
                st.error(f"Report generation failed: {str(e)}")

    if cache_key in st.session_state:
        _render_admin_report(st.session_state[cache_key])

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Approve Report", key="approve_full_report"):
                st.success("Report approved and ready for IEP meeting.")
        with c2:
            if st.button("Regenerate Report", key="regen_full_report"):
                del st.session_state[cache_key]
                st.rerun()


# ── Summary metrics ───────────────────────────────────────

def _render_summary_metrics(goals: list):
    """Show summary metric cards."""
    total_trials = sum(len(g.get("trial_history", [])) for g in goals)

    # Calculate overall average
    all_pcts = []
    for g in goals:
        for t in g.get("trial_history", []):
            all_pcts.append(t.get("pct", 0))
    avg = sum(all_pcts) / len(all_pcts) if all_pcts else 0

    # Overall trend
    trend_text = _get_overall_trend_text(goals)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Active Goals", len(goals))
    with c2:
        st.metric("Total Data Points", total_trials)
    with c3:
        st.metric("Overall Average", f"{avg:.0f}%" if all_pcts else "No data")
    with c4:
        st.metric("Trend", trend_text)


def _get_overall_trend_text(goals: list) -> str:
    """Calculate overall trend across all goals."""
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
        return "New"

    diff = (sum(all_recent) / len(all_recent)) - (sum(all_older) / len(all_older))
    if diff > 5:
        return "↑ Up"
    elif diff < -5:
        return "↓ Down"
    return "→ Steady"


# ── Per-goal cards ────────────────────────────────────────

def _render_goal_card(goal: dict, student_name: str):
    """Render a single goal card with trend chart."""
    history = goal.get("trial_history", [])
    baseline = goal.get("baseline", {})
    baseline_val = baseline.get("value", 0) if isinstance(baseline, dict) else baseline
    target = goal.get("target", 100)

    trend_text, trend_class = _calculate_trend(history)

    # Fix underscore labels: Following_Directions → Following Directions
    domain_display = goal["domain"].replace("_", " ").title()

    st.markdown(
        f'<div class="goal-card">'
        f'<strong>[{goal["goal_id"]}] {domain_display}</strong> '
        f'<span class="badge-{trend_class}">{trend_text}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    desc = goal.get("description", "")
    st.markdown(f"_{desc[:120]}..._" if len(desc) > 120 else f"_{desc}_")

    col1, col2 = st.columns([2, 1])

    with col1:
        if history:
            fig = _make_trend_chart(history, baseline_val, target, goal["goal_id"])
            st.plotly_chart(fig, use_container_width=True, key=f"pchart_{goal['goal_id']}")
        else:
            st.info("No trial data yet for this goal.")

    with col2:
        if history:
            recent = history[-1]
            st.metric(
                "Latest",
                f"{recent.get('pct', 0):.0f}%",
                delta=f"{recent.get('pct', 0) - baseline_val:.0f}% from baseline",
            )
            st.caption(f"Baseline: {baseline_val}% | Target: {target}%")
            st.caption(f"Sessions: {len(history)}")
            if recent.get("notes"):
                st.caption(f"Note: {recent['notes'][:80]}")

    st.markdown("")


def _calculate_trend(history: list):
    """Return (trend_text, css_class_suffix) for badge styling."""
    if len(history) < 2:
        return "New", "stable"

    recent = [h.get("pct", 0) for h in history[-3:]]
    older = [h.get("pct", 0) for h in history[-6:-3]] if len(history) >= 6 else [h.get("pct", 0) for h in history[:3]]

    recent_avg = sum(recent) / len(recent)
    older_avg = sum(older) / len(older) if older else recent_avg

    diff = recent_avg - older_avg
    if diff > 5:
        return "Improving", "improving"
    elif diff < -5:
        return "Declining", "declining"
    elif abs(diff) <= 5 and recent_avg > 0:
        return "Stable", "stable"
    return "New", "stable"


# ── Charts ────────────────────────────────────────────────

def _make_trend_chart(history: list, baseline: float, target: float, goal_id: str):
    """Create a Plotly trend chart for a goal."""
    dates = [h.get("date", "") for h in history]
    pcts = [h.get("pct", 0) for h in history]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates, y=pcts,
        mode="lines+markers",
        name="Performance",
        line=dict(color="#5B8FB9", width=2),
        marker=dict(size=8),
    ))

    fig.add_hline(
        y=baseline, line_dash="dot", line_color="#95A5A6",
        annotation_text=f"Baseline ({baseline}%)",
        annotation_position="bottom left",
    )

    fig.add_hline(
        y=target, line_dash="dash", line_color="#28A745",
        annotation_text=f"Target ({target}%)",
        annotation_position="top left",
    )

    fig.update_layout(
        height=250,
        margin=dict(l=0, r=0, t=20, b=0),
        yaxis=dict(range=[0, 105], title="% Correct"),
        xaxis=dict(title=""),
        showlegend=False,
        plot_bgcolor="white",
    )

    return fig


def _render_multi_goal_chart(goals: list):
    """Render a multi-line chart showing all goals on one plot."""
    fig = go.Figure()
    colors = ["#5B8FB9", "#28A745", "#FFC107", "#DC3545", "#6F42C1"]

    for i, goal in enumerate(goals):
        history = goal.get("trial_history", [])
        if not history:
            continue

        dates = [h.get("date", "") for h in history]
        pcts = [h.get("pct", 0) for h in history]
        color = colors[i % len(colors)]

        # Fix underscore labels
        domain_display = goal["domain"].replace("_", " ").title()

        fig.add_trace(go.Scatter(
            x=dates, y=pcts,
            mode="lines+markers",
            name=f"[{goal['goal_id']}] {domain_display}",
            line=dict(color=color, width=2),
            marker=dict(size=6),
        ))

        fig.add_hline(
            y=goal.get("target", 100),
            line_dash="dot", line_color=color, opacity=0.4,
        )

    fig.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=30, b=0),
        yaxis=dict(range=[0, 105], title="% Correct"),
        xaxis=dict(title="Date"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3),
        plot_bgcolor="white",
    )

    st.plotly_chart(fig, use_container_width=True)


# ── Admin report rendering ────────────────────────────────

def _get_forge():
    """Get or create MaterialForge instance."""
    if "forge" not in st.session_state:
        if os.getenv("GOOGLE_AI_STUDIO_KEY") and os.getenv("GOOGLE_AI_STUDIO_KEY") != "your_api_key_here":
            from core.gemma_client import GemmaClient
            client = GemmaClient()
        else:
            from tests.mock_api_responses import MockGemmaClient
            client = MockGemmaClient()
        from agents.material_forge import MaterialForge
        st.session_state["forge"] = MaterialForge(client)
    return st.session_state["forge"]


def _render_admin_report(report: dict):
    """Render the admin report in a professional format."""
    st.markdown("---")

    if report.get("executive_summary"):
        st.markdown("**Executive Summary**")
        st.markdown(report["executive_summary"])

    if report.get("goal_summaries"):
        st.markdown("**Goal-by-Goal Analysis**")
        for gs in report["goal_summaries"]:
            # Fix underscore labels in goal descriptions
            goal_desc = gs.get("goal_description", "")
            st.markdown(
                f'<div class="goal-card">'
                f'<strong>[{gs.get("goal_id", "?")}]</strong> '
                f'{goal_desc[:100]}'
                f'</div>',
                unsafe_allow_html=True,
            )
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Baseline", f"{gs.get('baseline', 'N/A')}%")
            with c2:
                st.metric("Current", f"{gs.get('current', 'N/A')}%")
            with c3:
                st.metric("Target", f"{gs.get('target', 'N/A')}%")
            if gs.get("narrative"):
                st.markdown(gs["narrative"])
            if gs.get("recommendation"):
                st.markdown(f"**Recommendation:** {gs['recommendation']}")
            st.markdown("")

    if report.get("overall_assessment"):
        st.markdown("**Overall Assessment**")
        st.markdown(report["overall_assessment"])

    if report.get("next_steps"):
        st.markdown("**Next Steps**")
        st.markdown(report["next_steps"])
