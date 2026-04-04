"""
Admin Reports screen — Generate polished progress reports.
"Admin eat up fancy reports and data." — Sarah
"""

import streamlit as st
import plotly.graph_objects as go


def render_reports():
    """Render the Admin Reports tab."""
    st.header("Admin Reports")
    st.markdown("_Professional progress reports for IEP meetings and compliance._")

    student_id = st.session_state.get("current_student")
    if not student_id:
        st.info("Select a student from the sidebar.")
        return

    profile = st.session_state.get("profiles", {}).get(student_id)
    if not profile:
        return

    st.markdown(f"**Student:** {profile['name']} (Grade {profile['grade']})")

    # Summary metrics across all goals
    goals = profile.get("iep_goals", [])
    _render_summary_metrics(goals)

    st.markdown("---")

    # Progress overview chart (all goals)
    if any(g.get("trial_history") for g in goals):
        st.subheader("Progress Overview")
        _render_multi_goal_chart(goals)

    st.markdown("---")

    # Generate full admin report
    cache_key = f"admin_report_{student_id}"

    if st.button("Generate Full Report", type="primary", use_container_width=True):
        with st.spinner("Generating comprehensive admin report..."):
            from ui.outputs import _get_forge
            forge = _get_forge()
            try:
                result = forge.generate_admin_report(student_id)
                st.session_state[cache_key] = result
            except Exception as e:
                st.error(f"Report generation failed: {str(e)}")

    if cache_key in st.session_state:
        _render_admin_report(st.session_state[cache_key])

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Approve Report", key="approve_report"):
                st.success("Report approved and ready for IEP meeting.")
        with col2:
            if st.button("Regenerate Report", key="regen_report"):
                del st.session_state[cache_key]
                st.rerun()


def _render_summary_metrics(goals):
    """Show summary metric cards for all goals."""
    cols = st.columns(len(goals) if goals else 1)
    for i, goal in enumerate(goals):
        with cols[i % len(cols)]:
            history = goal.get("trial_history", [])
            if history:
                latest = history[-1].get("pct", 0)
                baseline = goal.get("baseline", {})
                base_val = baseline.get("value", 0) if isinstance(baseline, dict) else baseline
                delta = latest - base_val
                st.metric(
                    f"[{goal['goal_id']}] {goal['domain'].title()}",
                    f"{latest:.0f}%",
                    delta=f"{delta:+.0f}% from baseline",
                )
            else:
                st.metric(f"[{goal['goal_id']}]", "No data")


def _render_multi_goal_chart(goals):
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

        fig.add_trace(go.Scatter(
            x=dates, y=pcts,
            mode="lines+markers",
            name=f"[{goal['goal_id']}] {goal['domain'].title()}",
            line=dict(color=color, width=2),
            marker=dict(size=6),
        ))

        # Target line
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


def _render_admin_report(report: dict):
    """Render the admin report in a professional format."""
    st.markdown("---")
    st.subheader("Progress Report")

    if report.get("executive_summary"):
        st.markdown("**Executive Summary**")
        st.markdown(report["executive_summary"])

    if report.get("goal_summaries"):
        st.markdown("**Goal-by-Goal Analysis**")
        for gs in report["goal_summaries"]:
            st.markdown(
                f'<div class="goal-card">'
                f'<strong>[{gs.get("goal_id", "?")}]</strong> '
                f'{gs.get("goal_description", "")[:100]}'
                f'</div>',
                unsafe_allow_html=True,
            )
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Baseline", f"{gs.get('baseline', 'N/A')}%")
            with col2:
                st.metric("Current", f"{gs.get('current', 'N/A')}%")
            with col3:
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
