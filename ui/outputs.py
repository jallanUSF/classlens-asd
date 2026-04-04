"""
Generated Materials screen — Tabbed view of all material types.
Teacher-in-the-loop: approve/edit/regenerate for each output.
"""

import streamlit as st
import json


def render_outputs():
    """Render the Generated Materials tab."""
    st.header("Generated Materials")

    student_id = st.session_state.get("current_student")
    if not student_id:
        st.info("Select a student from the sidebar.")
        return

    profile = st.session_state.get("profiles", {}).get(student_id)
    if not profile:
        return

    # Check for pipeline results
    last_result = st.session_state.get("last_result")
    if not last_result or st.session_state.get("last_student") != student_id:
        st.info(
            f"No recent analysis for {profile['name']}. "
            "Go to Upload to analyze student work first, or generate materials below."
        )

    st.markdown(f"**Student:** {profile['name']} (Grade {profile['grade']})")

    # Material type tabs
    tabs = st.tabs([
        "Lesson Plans",
        "Tracking Sheets",
        "Social Stories",
        "Visual Schedules",
        "First-Then Boards",
        "Parent Letters",
        "Admin Reports",
    ])

    goals = profile.get("iep_goals", [])
    goal_options = {f"[{g['goal_id']}] {g['domain']}: {g['description'][:50]}...": g["goal_id"] for g in goals}

    with tabs[0]:
        _render_material_generator(
            student_id, profile, goal_options,
            "lesson_plan", "Lesson Plan",
            "Generate a goal-aligned lesson plan woven with student interests.",
        )

    with tabs[1]:
        _render_material_generator(
            student_id, profile, goal_options,
            "tracking_sheet", "Tracking Sheet",
            "Generate a printable data tracking sheet for classroom use.",
        )

    with tabs[2]:
        _render_social_story_generator(student_id, profile)

    with tabs[3]:
        _render_visual_schedule_generator(student_id, profile)

    with tabs[4]:
        _render_material_generator(
            student_id, profile, goal_options,
            "first_then", "First-Then Board",
            "Create a First-Then motivation board using student reinforcers.",
        )

    with tabs[5]:
        _render_material_generator(
            student_id, profile, goal_options,
            "parent_comm", "Parent Letter",
            "Write a warm, jargon-free progress update for parents.",
        )

    with tabs[6]:
        _render_admin_report_generator(student_id, profile)


def _get_forge():
    """Get or create MaterialForge instance."""
    if "forge" not in st.session_state:
        import os
        if os.getenv("GOOGLE_AI_STUDIO_KEY") and os.getenv("GOOGLE_AI_STUDIO_KEY") != "your_api_key_here":
            from core.gemma_client import GemmaClient
            client = GemmaClient()
        else:
            from tests.mock_api_responses import MockGemmaClient
            client = MockGemmaClient()
        from agents.material_forge import MaterialForge
        st.session_state["forge"] = MaterialForge(client)
    return st.session_state["forge"]


def _render_material_generator(student_id, profile, goal_options, material_type, label, description):
    """Generic material generator with goal selector."""
    st.markdown(f"_{description}_")

    if not goal_options:
        st.warning("No IEP goals found for this student.")
        return

    selected_label = st.selectbox(f"Select goal for {label}", list(goal_options.keys()), key=f"goal_{material_type}")
    goal_id = goal_options[selected_label]

    cache_key = f"{material_type}_{student_id}_{goal_id}"

    if st.button(f"Generate {label}", key=f"btn_{material_type}", type="primary"):
        with st.spinner(f"Generating {label.lower()}..."):
            forge = _get_forge()
            try:
                if material_type == "lesson_plan":
                    result = forge.generate_lesson_plan(student_id, goal_id)
                elif material_type == "tracking_sheet":
                    result = forge.generate_tracking_sheet(student_id, goal_id)
                elif material_type == "first_then":
                    result = forge.generate_first_then(student_id, goal_id)
                elif material_type == "parent_comm":
                    result = forge.generate_parent_comm(student_id, goal_id)
                else:
                    result = {"error": "Unknown material type"}
                st.session_state[cache_key] = result
            except Exception as e:
                st.error(f"Generation failed: {str(e)}")
                return

    # Display cached result
    if cache_key in st.session_state:
        result = st.session_state[cache_key]
        _display_material(result, label, cache_key)


def _render_social_story_generator(student_id, profile):
    """Social story with scenario input."""
    st.markdown("_Create a Carol Gray social story tailored to student interests._")

    scenario = st.text_input(
        "What situation or skill?",
        placeholder="e.g., Greeting peers at lunch, Waiting in line",
        key="social_story_scenario",
    )

    cache_key = f"social_story_{student_id}"

    if st.button("Generate Social Story", key="btn_social_story", type="primary") and scenario:
        with st.spinner("Creating social story..."):
            forge = _get_forge()
            try:
                result = forge.generate_social_story(student_id, scenario)
                st.session_state[cache_key] = result
            except Exception as e:
                st.error(f"Generation failed: {str(e)}")
                return

    if cache_key in st.session_state:
        _display_material(st.session_state[cache_key], "Social Story", cache_key)


def _render_visual_schedule_generator(student_id, profile):
    """Visual schedule with routine input."""
    st.markdown("_Create a step-by-step visual schedule for a routine._")

    routine = st.text_input(
        "What routine?",
        placeholder="e.g., Morning arrival, Lunch routine, Dismissal",
        key="schedule_routine",
    )

    cache_key = f"visual_schedule_{student_id}"

    if st.button("Generate Visual Schedule", key="btn_visual_schedule", type="primary") and routine:
        with st.spinner("Creating visual schedule..."):
            forge = _get_forge()
            try:
                result = forge.generate_visual_schedule(student_id, routine)
                st.session_state[cache_key] = result
            except Exception as e:
                st.error(f"Generation failed: {str(e)}")
                return

    if cache_key in st.session_state:
        result = st.session_state[cache_key]
        if isinstance(result, str):
            st.markdown(f'<div class="material-output">{result}</div>', unsafe_allow_html=True)
        else:
            _display_material(result, "Visual Schedule", cache_key)


def _render_admin_report_generator(student_id, profile):
    """Admin report for all goals."""
    st.markdown("_Generate a professional progress report for administrators._")

    cache_key = f"admin_report_{student_id}"

    if st.button("Generate Admin Report", key="btn_admin_report", type="primary"):
        with st.spinner("Generating admin report..."):
            forge = _get_forge()
            try:
                result = forge.generate_admin_report(student_id)
                st.session_state[cache_key] = result
            except Exception as e:
                st.error(f"Generation failed: {str(e)}")
                return

    if cache_key in st.session_state:
        _display_material(st.session_state[cache_key], "Admin Report", cache_key)


def _display_material(result, label, cache_key):
    """Display a generated material with approve/edit controls."""
    st.markdown("---")

    if isinstance(result, str):
        st.markdown(result)
    elif isinstance(result, dict):
        # Render key fields nicely
        for key, value in result.items():
            if key in ("student_id", "goal_id"):
                continue
            if isinstance(value, list):
                st.markdown(f"**{key.replace('_', ' ').title()}:**")
                for item in value:
                    if isinstance(item, dict):
                        st.json(item)
                    else:
                        st.markdown(f"- {item}")
            elif isinstance(value, str) and len(value) > 100:
                st.markdown(f"**{key.replace('_', ' ').title()}:**")
                st.markdown(value)
            elif value:
                st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")

    # Teacher-in-the-loop controls
    st.markdown("")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Approve", key=f"approve_{cache_key}"):
            st.success(f"{label} approved!")
    with col2:
        if st.button("Regenerate", key=f"regen_{cache_key}"):
            if cache_key in st.session_state:
                del st.session_state[cache_key]
            st.rerun()
    with col3:
        with st.expander("View JSON"):
            st.json(result if isinstance(result, (dict, list)) else {"text": result})
