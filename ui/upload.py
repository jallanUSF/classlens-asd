"""
Upload Work screen — Student selector + image upload + process button.
"""

import streamlit as st
from pathlib import Path


def render_upload():
    """Render the Upload Student Work tab."""
    st.header("Upload Student Work")

    # Get current student from session
    student_id = st.session_state.get("current_student")
    if not student_id:
        st.info("Select a student from the sidebar to get started.")
        return

    profile = st.session_state.get("profiles", {}).get(student_id)
    if not profile:
        return

    st.markdown(f"**Student:** {profile['name']} (Grade {profile['grade']})")

    # Work type selector
    work_types = {
        "Worksheet": "worksheet",
        "Behavior Tally Sheet": "tally_sheet",
        "Task Checklist": "checklist",
        "Visual Schedule": "visual_schedule",
        "Free Response / Writing": "free_response",
    }
    work_label = st.selectbox("What type of student work is this?", list(work_types.keys()))
    work_type = work_types[work_label]

    # Subject area
    subject = st.text_input("Subject area", value="math", placeholder="e.g., math, reading, social skills")

    # Date
    from datetime import date
    work_date = st.date_input("Date of this work", value=date.today())

    # File upload OR sample image
    st.markdown("---")
    upload_mode = st.radio(
        "Choose image source",
        ["Use a sample image", "Upload a photo"],
        horizontal=True,
    )

    image_path = None

    if upload_mode == "Use a sample image":
        sample_dir = Path("data/sample_work")
        samples = sorted(sample_dir.glob("*.png")) + sorted(sample_dir.glob("*.jpg"))
        # Filter to current student's samples
        student_samples = [s for s in samples if profile["name"].lower() in s.stem.lower()]
        other_samples = [s for s in samples if profile["name"].lower() not in s.stem.lower()]

        if student_samples:
            st.markdown(f"**{profile['name']}'s sample work:**")
            sample_names = [s.stem.replace("_", " ").title() for s in student_samples]
            choice = st.selectbox("Select sample", sample_names)
            idx = sample_names.index(choice)
            image_path = str(student_samples[idx])
            st.image(image_path, caption=choice, width=400)
        elif other_samples:
            st.warning(f"No sample images found for {profile['name']}. Showing all samples.")
            sample_names = [s.stem.replace("_", " ").title() for s in other_samples]
            choice = st.selectbox("Select sample", sample_names)
            idx = sample_names.index(choice)
            image_path = str(other_samples[idx])
            st.image(image_path, caption=choice, width=400)
    else:
        uploaded = st.file_uploader(
            "Upload a photo of student work",
            type=["jpg", "jpeg", "png"],
            help="Take a clear photo of the student's work. Good lighting helps!",
        )
        if uploaded:
            # Save to temp
            upload_dir = Path("data/uploads")
            upload_dir.mkdir(parents=True, exist_ok=True)
            save_path = upload_dir / uploaded.name
            with open(save_path, "wb") as f:
                f.write(uploaded.getbuffer())
            image_path = str(save_path)
            st.image(image_path, caption="Uploaded photo", width=400)

    # Process button
    st.markdown("---")
    if image_path:
        if st.button("Analyze Student Work", type="primary", use_container_width=True):
            _run_pipeline(student_id, image_path, work_type, subject, str(work_date))
    else:
        st.info("Select or upload an image to analyze.")


def _run_pipeline(student_id, image_path, work_type, subject, date_str):
    """Run the full pipeline and store results in session state."""
    with st.spinner("Reading student work..."):
        from core.pipeline import ClassLensPipeline
        from tests.mock_api_responses import MockGemmaClient

        # Use mock client for demo; swap to real GemmaClient when API key is set
        import os
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

    # Show success summary
    st.success("Analysis complete!")

    transcription = result.get("transcription", {})
    mapping = result.get("goal_mapping", {})
    alerts = result.get("alerts", [])

    col1, col2, col3 = st.columns(3)
    with col1:
        items = transcription.get("total_items", "?")
        correct = transcription.get("correct_items", "?")
        st.metric("Items Found", items)
    with col2:
        matched = len(mapping.get("matched_goals", []))
        st.metric("Goals Matched", matched)
    with col3:
        st.metric("Alerts", len(alerts))

    # Show transcription details
    with st.expander("View Transcription Details", expanded=True):
        st.json(transcription)

    # Show goal mapping
    with st.expander("View Goal Mapping"):
        for gm in mapping.get("matched_goals", []):
            st.markdown(
                f"**{gm.get('goal_id', '?')}** — "
                f"{gm.get('relevance', 'N/A')} match, "
                f"{gm.get('percentage', 0):.0f}% accuracy"
            )
            if gm.get("reasoning"):
                st.caption(gm["reasoning"])

    # Show alerts
    if alerts:
        st.warning("Alerts detected — check the Dashboard for details.")
        for a in alerts:
            st.markdown(f"- **{a.get('goal_id', '?')}**: {a.get('alert_message', 'Alert')}")
