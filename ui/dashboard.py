"""
Progress Dashboard — Per-student goal cards with Plotly trend charts.
"""

import streamlit as st
import plotly.graph_objects as go


def render_dashboard():
    """Render the Progress Dashboard tab."""
    st.header("Progress Dashboard")

    student_id = st.session_state.get("current_student")
    if not student_id:
        st.info("Select a student from the sidebar to view their progress.")
        return

    profile = st.session_state.get("profiles", {}).get(student_id)
    if not profile:
        return

    # Student summary metrics
    goals = profile.get("iep_goals", [])
    total_trials = sum(len(g.get("trial_history", [])) for g in goals)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Active Goals", len(goals))
    with col2:
        st.metric("Total Data Points", total_trials)
    with col3:
        if total_trials > 0:
            all_pcts = []
            for g in goals:
                for t in g.get("trial_history", []):
                    all_pcts.append(t.get("pct", 0))
            avg = sum(all_pcts) / len(all_pcts) if all_pcts else 0
            st.metric("Overall Average", f"{avg:.0f}%")
        else:
            st.metric("Overall Average", "No data")

    st.markdown("---")

    # Goal cards with trend charts
    for goal in goals:
        _render_goal_card(goal, profile["name"])


def _render_goal_card(goal: dict, student_name: str):
    """Render a single goal card with trend chart."""
    history = goal.get("trial_history", [])
    baseline = goal.get("baseline", {})
    baseline_val = baseline.get("value", 0) if isinstance(baseline, dict) else baseline
    target = goal.get("target", 100)

    # Calculate trend
    trend_text, trend_color = _calculate_trend(history)

    # Goal header
    st.markdown(
        f'<div class="goal-card">'
        f'<strong>[{goal["goal_id"]}] {goal["domain"].title()}</strong> '
        f'<span class="badge-{trend_color}">{trend_text}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown(f"_{goal['description'][:120]}..._" if len(goal.get("description", "")) > 120 else f"_{goal.get('description', '')}_")

    col1, col2 = st.columns([2, 1])

    with col1:
        if history:
            fig = _make_trend_chart(history, baseline_val, target, goal["goal_id"])
            st.plotly_chart(fig, use_container_width=True, key=f"chart_{goal['goal_id']}")
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


def _make_trend_chart(history: list, baseline: float, target: float, goal_id: str):
    """Create a Plotly trend chart for a goal."""
    dates = [h.get("date", "") for h in history]
    pcts = [h.get("pct", 0) for h in history]

    fig = go.Figure()

    # Trial data line
    fig.add_trace(go.Scatter(
        x=dates, y=pcts,
        mode="lines+markers",
        name="Performance",
        line=dict(color="#5B8FB9", width=2),
        marker=dict(size=8),
    ))

    # Baseline line
    fig.add_hline(
        y=baseline, line_dash="dot", line_color="#95A5A6",
        annotation_text=f"Baseline ({baseline}%)",
        annotation_position="bottom left",
    )

    # Target line
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
