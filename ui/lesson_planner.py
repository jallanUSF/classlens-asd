"""
Lesson Planner screen — Select student + goal -> generate lesson plan + tracking sheet.
This is the "hero" output Sarah requested most.
"""

import streamlit as st


def render_lesson_planner():
    """Render the Lesson Planner tab."""
    st.header("Lesson Planner")
    st.markdown("_Create IEP-aligned lesson plans woven with student interests._")

    student_id = st.session_state.get("current_student")
    if not student_id:
        st.info("Select a student from the sidebar.")
        return

    profile = st.session_state.get("profiles", {}).get(student_id)
    if not profile:
        return

    goals = profile.get("iep_goals", [])
    if not goals:
        st.warning("No IEP goals found for this student.")
        return

    st.markdown(f"**Student:** {profile['name']} (Grade {profile['grade']})")
    st.markdown(f"**Interests:** {', '.join(profile.get('interests', []))}")

    # Goal selector
    goal_labels = {
        f"[{g['goal_id']}] {g['domain'].title()}: {g['description'][:60]}...": g["goal_id"]
        for g in goals
    }
    selected = st.selectbox("Select IEP goal", list(goal_labels.keys()))
    goal_id = goal_labels[selected]

    # Find the goal
    goal = next(g for g in goals if g["goal_id"] == goal_id)
    baseline = goal.get("baseline", {})
    baseline_val = baseline.get("value", "N/A") if isinstance(baseline, dict) else baseline

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Baseline", f"{baseline_val}%")
    with col2:
        st.metric("Target", f"{goal['target']}%")
    with col3:
        history = goal.get("trial_history", [])
        if history:
            st.metric("Latest", f"{history[-1].get('pct', 0)}%")
        else:
            st.metric("Latest", "No data")

    st.markdown("---")

    # Generate both lesson plan and tracking sheet
    col_plan, col_sheet = st.columns(2)

    with col_plan:
        if st.button("Generate Lesson Plan", type="primary", use_container_width=True):
            _generate_lesson_plan(student_id, goal_id)

    with col_sheet:
        if st.button("Generate Tracking Sheet", type="secondary", use_container_width=True):
            _generate_tracking_sheet(student_id, goal_id)

    # Display results
    lp_key = f"lp_{student_id}_{goal_id}"
    ts_key = f"ts_{student_id}_{goal_id}"

    if lp_key in st.session_state:
        st.markdown("### Lesson Plan")
        result = st.session_state[lp_key]
        if isinstance(result, dict):
            if result.get("lesson_title"):
                st.markdown(f"**{result['lesson_title']}**")
            if result.get("objective"):
                st.markdown(f"**Objective:** {result['objective']}")
            if result.get("materials_needed"):
                st.markdown("**Materials:**")
                for m in result["materials_needed"]:
                    st.markdown(f"- {m}")
            for section in ["warm_up", "main_activity", "guided_practice", "independent_practice", "assessment_check"]:
                if result.get(section):
                    st.markdown(f"**{section.replace('_', ' ').title()}:**")
                    st.markdown(result[section])
            if result.get("interest_integration"):
                st.markdown(f"**Interest Integration:** {result['interest_integration']}")
            if result.get("scaffolding_notes"):
                st.markdown(f"**Scaffolding Notes:** {result['scaffolding_notes']}")
            if result.get("estimated_duration_minutes"):
                st.markdown(f"**Duration:** {result['estimated_duration_minutes']} minutes")
        else:
            st.markdown(str(result))

        # Approve/regenerate
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Approve Lesson Plan", key="approve_lp"):
                st.success("Lesson plan approved!")
        with c2:
            if st.button("Regenerate", key="regen_lp"):
                del st.session_state[lp_key]
                st.rerun()

    if ts_key in st.session_state:
        st.markdown("### Tracking Sheet")
        result = st.session_state[ts_key]
        if isinstance(result, dict):
            if result.get("sheet_title"):
                st.markdown(f"**{result['sheet_title']}**")
            if result.get("instructions"):
                st.markdown(f"_{result['instructions']}_")
            if result.get("columns"):
                st.markdown("**Columns:**")
                for col in result["columns"]:
                    st.markdown(f"- {col.get('header', '?')} ({col.get('width', 'auto')})")
            if result.get("goal_text"):
                st.markdown(f"**Goal:** {result['goal_text']}")
            if result.get("target_criterion"):
                st.markdown(f"**Target:** {result['target_criterion']}")
        else:
            st.markdown(str(result))


def _generate_lesson_plan(student_id, goal_id):
    """Generate and cache a lesson plan."""
    with st.spinner("Generating lesson plan..."):
        from ui.outputs import _get_forge
        forge = _get_forge()
        try:
            result = forge.generate_lesson_plan(student_id, goal_id)
            st.session_state[f"lp_{student_id}_{goal_id}"] = result
        except Exception as e:
            st.error(f"Failed: {str(e)}")


def _generate_tracking_sheet(student_id, goal_id):
    """Generate and cache a tracking sheet."""
    with st.spinner("Generating tracking sheet..."):
        from ui.outputs import _get_forge
        forge = _get_forge()
        try:
            result = forge.generate_tracking_sheet(student_id, goal_id)
            st.session_state[f"ts_{student_id}_{goal_id}"] = result
        except Exception as e:
            st.error(f"Failed: {str(e)}")
