"""
Capture & Create view — Two-column layout.
Left: image upload + analyze + results.
Right: material tile grid + inline generation.
Merges logic from upload.py, outputs.py, and lesson_planner.py.
"""

import os
import streamlit as st
from pathlib import Path
from datetime import date


MATERIAL_TILES = [
    ("📝", "Lesson Plan", "lesson_plan"),
    ("📊", "Tracking Sheet", "tracking_sheet"),
    ("📖", "Social Story", "social_story"),
    ("📅", "Visual Schedule", "visual_schedule"),
    ("🏠", "Parent Letter", "parent_comm"),
    ("📋", "Admin Report", "admin_report"),
]

STUDENT_EMOJI = {
    "maya_2026": "🦕",
    "jaylen_2026": "🚂",
    "sofia_2026": "🌍",
}


def render_capture():
    """Render the Capture & Create two-column view."""
    student_id = st.session_state.get("current_student")
    if not student_id:
        st.header("Capture & Create")
        st.info("Select a student from My Students or the sidebar to get started.")
        return

    profile = st.session_state.get("profiles", {}).get(student_id)
    if not profile:
        return

    # Student context bar
    emoji = STUDENT_EMOJI.get(student_id, "👤")
    st.markdown(
        f"### {emoji} {profile['name']} — Grade {profile['grade']} · "
        f"{date.today().strftime('%B %d, %Y')}"
    )

    # Two-column layout
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        _render_capture_column(student_id, profile)

    with col_right:
        _render_create_column(student_id, profile)


# ── Left column: Capture ──────────────────────────────────

def _render_capture_column(student_id: str, profile: dict):
    """Left column: upload/select image, analyze, show results."""
    st.markdown("#### Capture Student Work")

    # Work type selector
    work_types = {
        "Worksheet": "worksheet",
        "Behavior Tally Sheet": "tally_sheet",
        "Task Checklist": "checklist",
        "Visual Schedule": "visual_schedule",
        "Free Response / Writing": "free_response",
    }
    work_label = st.selectbox("Work type", list(work_types.keys()))
    work_type = work_types[work_label]

    # Subject
    subject = st.text_input("Subject area", value="math", placeholder="e.g., math, reading")

    # Image source
    upload_mode = st.radio(
        "Image source",
        ["Sample image", "Upload photo"],
        horizontal=True,
    )

    image_path = None

    if upload_mode == "Sample image":
        image_path = _handle_sample_image(profile)
    else:
        image_path = _handle_upload()

    # Analyze button
    if image_path:
        if st.button("Analyze Student Work", type="primary", use_container_width=True):
            _run_pipeline(student_id, image_path, work_type, subject, str(date.today()))
    else:
        st.markdown(
            '<div class="locked-placeholder">Select or upload an image to analyze</div>',
            unsafe_allow_html=True,
        )

    # Show results if available
    last_result = st.session_state.get("last_result")
    if last_result and st.session_state.get("last_student") == student_id:
        _render_analysis_results(last_result)


def _handle_sample_image(profile: dict) -> str | None:
    """Handle sample image selection. Returns path or None."""
    sample_dir = Path("data/sample_work")
    samples = sorted(sample_dir.glob("*.png")) + sorted(sample_dir.glob("*.jpg"))
    student_samples = [s for s in samples if profile["name"].lower() in s.stem.lower()]
    other_samples = [s for s in samples if profile["name"].lower() not in s.stem.lower()]

    available = student_samples or other_samples
    if not available:
        st.caption("No sample images available.")
        return None

    if student_samples:
        sample_names = [s.stem.replace("_", " ").title() for s in student_samples]
        choice = st.selectbox("Select sample", sample_names)
        idx = sample_names.index(choice)
        path = str(student_samples[idx])
    else:
        sample_names = [s.stem.replace("_", " ").title() for s in other_samples]
        choice = st.selectbox("Select sample", sample_names)
        idx = sample_names.index(choice)
        path = str(other_samples[idx])

    st.image(path, caption=choice, width=500)
    return path


def _handle_upload() -> str | None:
    """Handle file upload. Returns path or None."""
    uploaded = st.file_uploader(
        "Upload a photo of student work",
        type=["jpg", "jpeg", "png"],
        help="Take a clear photo of the student's work. Good lighting helps!",
    )
    if uploaded:
        upload_dir = Path("data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        save_path = upload_dir / uploaded.name
        with open(save_path, "wb") as f:
            f.write(uploaded.getbuffer())
        st.image(str(save_path), caption="Uploaded photo", width=500)
        return str(save_path)
    return None


def _run_pipeline(student_id: str, image_path: str, work_type: str, subject: str, date_str: str):
    """Run the full pipeline and store results in session state."""
    with st.spinner("Reading student work..."):
        from core.pipeline import ClassLensPipeline
        from tests.mock_api_responses import MockGemmaClient

        if os.getenv("GOOGLE_AI_STUDIO_KEY") and os.getenv("GOOGLE_AI_STUDIO_KEY") != "your_api_key_here":
            pipeline = ClassLensPipeline()
        else:
            pipeline = ClassLensPipeline(client=MockGemmaClient())

        result = pipeline.process_work_artifact(
            student_id=student_id,
            image_path=image_path,
            work_type=work_type,
            subject=subject,
            date=date_str,
        )

    st.session_state["last_result"] = result
    st.session_state["last_student"] = student_id


def _render_analysis_results(result: dict):
    """Show analysis results as summary cards + expandable details."""
    st.success("Analysis complete!")

    transcription = result.get("transcription", {})
    mapping = result.get("goal_mapping", {})
    alerts = result.get("alerts", [])

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Items Found", transcription.get("total_items", "?"))
    with c2:
        st.metric("Goals Matched", len(mapping.get("matched_goals", [])))
    with c3:
        st.metric("Alerts", len(alerts))

    with st.expander("Transcription Details", expanded=False):
        st.json(transcription)

    with st.expander("Goal Mapping"):
        for gm in mapping.get("matched_goals", []):
            st.markdown(
                f"**{gm.get('goal_id', '?')}** — "
                f"{gm.get('relevance', 'N/A')} match, "
                f"{gm.get('percentage', 0):.0f}% accuracy"
            )
            if gm.get("reasoning"):
                st.caption(gm["reasoning"])

    if alerts:
        st.warning("Alerts detected")
        for a in alerts:
            st.markdown(f"- **{a.get('goal_id', '?')}**: {a.get('alert_message', 'Alert')}")


# ── Right column: Create Materials ────────────────────────

def _render_create_column(student_id: str, profile: dict):
    """Right column: material tile grid + inline generation."""
    st.markdown("#### Create Materials")

    has_result = (
        st.session_state.get("last_result") is not None
        and st.session_state.get("last_student") == student_id
    )

    if not has_result:
        st.markdown(
            '<div class="locked-placeholder">'
            '🔒 Analyze student work first, or generate materials directly below'
            '</div>',
            unsafe_allow_html=True,
        )

    # Material tile grid: 3x2
    for row in range(2):
        tile_cols = st.columns(3)
        for col_idx in range(3):
            tile_idx = row * 3 + col_idx
            if tile_idx < len(MATERIAL_TILES):
                icon, label, mat_type = MATERIAL_TILES[tile_idx]
                with tile_cols[col_idx]:
                    if st.button(
                        f"{icon}\n{label}",
                        key=f"tile_{mat_type}",
                        use_container_width=True,
                    ):
                        st.session_state["active_material"] = mat_type

    # Show generation UI for selected material
    active_mat = st.session_state.get("active_material")
    if active_mat:
        st.markdown("---")
        _render_material_generator(student_id, profile, active_mat)


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


def _render_material_generator(student_id: str, profile: dict, material_type: str):
    """Render generation UI for a specific material type."""
    goals = profile.get("iep_goals", [])
    goal_options = {
        f"[{g['goal_id']}] {g['domain'].replace('_', ' ').title()}: {g['description'][:50]}...": g["goal_id"]
        for g in goals
    }

    # Social story and visual schedule need extra inputs
    if material_type == "social_story":
        _render_social_story(student_id)
        return

    if material_type == "visual_schedule":
        _render_visual_schedule(student_id)
        return

    if material_type == "admin_report":
        _render_admin_report_gen(student_id)
        return

    # Standard goal-based materials
    if not goal_options:
        st.warning("No IEP goals found for this student.")
        return

    mat_labels = {
        "lesson_plan": "Lesson Plan",
        "tracking_sheet": "Tracking Sheet",
        "parent_comm": "Parent Letter",
    }
    label = mat_labels.get(material_type, material_type.replace("_", " ").title())

    selected_label = st.selectbox(f"Goal for {label}", list(goal_options.keys()), key=f"goal_sel_{material_type}")
    goal_id = goal_options[selected_label]

    cache_key = f"gen_{material_type}_{student_id}_{goal_id}"

    if st.button(f"Generate {label}", key=f"gen_btn_{material_type}", type="primary"):
        with st.spinner(f"Generating {label.lower()}..."):
            forge = _get_forge()
            try:
                if material_type == "lesson_plan":
                    result = forge.generate_lesson_plan(student_id, goal_id)
                elif material_type == "tracking_sheet":
                    result = forge.generate_tracking_sheet(student_id, goal_id)
                elif material_type == "parent_comm":
                    result = forge.generate_parent_comm(student_id, goal_id)
                else:
                    result = {"error": "Unknown material type"}
                st.session_state[cache_key] = result
            except Exception as e:
                st.error(f"Generation failed: {str(e)}")
                return

    if cache_key in st.session_state:
        _display_material(st.session_state[cache_key], label, cache_key)


def _render_social_story(student_id: str):
    """Social story generator with scenario input."""
    st.markdown("**Social Story** — _Carol Gray format, tailored to student interests_")
    scenario = st.text_input(
        "Situation or skill",
        placeholder="e.g., Greeting peers at lunch, Waiting in line",
        key="ss_scenario",
    )
    cache_key = f"gen_social_story_{student_id}"

    if st.button("Generate Social Story", key="gen_btn_ss", type="primary") and scenario:
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


def _render_visual_schedule(student_id: str):
    """Visual schedule generator with routine input."""
    st.markdown("**Visual Schedule** — _Step-by-step routine guide_")
    routine = st.text_input(
        "Routine",
        placeholder="e.g., Morning arrival, Lunch routine, Dismissal",
        key="vs_routine",
    )
    cache_key = f"gen_visual_schedule_{student_id}"

    if st.button("Generate Visual Schedule", key="gen_btn_vs", type="primary") and routine:
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


def _render_admin_report_gen(student_id: str):
    """Admin report generator (all goals)."""
    st.markdown("**Admin Report** — _Professional progress report for IEP meetings_")
    cache_key = f"gen_admin_report_{student_id}"

    if st.button("Generate Admin Report", key="gen_btn_admin", type="primary"):
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


def _display_material(result, label: str, cache_key: str):
    """Display generated material with approve/regenerate controls."""
    st.markdown(
        f'<div class="material-output">',
        unsafe_allow_html=True,
    )

    if isinstance(result, str):
        st.markdown(result)
    elif isinstance(result, dict):
        for key, value in result.items():
            if key in ("student_id", "goal_id"):
                continue
            display_key = key.replace("_", " ").title()
            if isinstance(value, list):
                st.markdown(f"**{display_key}:**")
                for item in value:
                    if isinstance(item, dict):
                        st.json(item)
                    else:
                        st.markdown(f"- {item}")
            elif isinstance(value, str) and len(value) > 100:
                st.markdown(f"**{display_key}:**")
                st.markdown(value)
            elif value:
                st.markdown(f"**{display_key}:** {value}")

    st.markdown('</div>', unsafe_allow_html=True)

    # Teacher-in-the-loop controls
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Approve", key=f"approve_{cache_key}"):
            st.success(f"{label} approved!")
    with c2:
        if st.button("Regenerate", key=f"regen_{cache_key}"):
            if cache_key in st.session_state:
                del st.session_state[cache_key]
            st.rerun()
    with c3:
        with st.expander("View JSON"):
            st.json(result if isinstance(result, (dict, list)) else {"text": result})
