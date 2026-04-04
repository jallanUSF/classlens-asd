# ClassLens ASD 🔍

**Multimodal IEP Intelligence for Autistic Learners**

A multi-agent system built on Google Gemma 4 that helps teachers of autistic students transform daily classroom work artifacts into IEP-aligned progress intelligence and personalized intervention materials.

> *"This would give me back my Tuesdays. That time goes back to being WITH my students."*
> — Practicing K-12 Special Education Teacher

## What It Does

📸 **Upload** a photo of student work (handwritten worksheets, tally sheets, visual schedules)

📊 **Track** IEP goal progress automatically — no more manual tally counting

🎯 **Generate** personalized lesson plans themed to each student's interests

📝 **Create** social stories, visual schedules, parent communications, and admin reports

👩‍🏫 **Teacher stays in control** — every output is reviewed and approved before use

## Architecture

Four specialized Gemma 4 agents working in sequence:

1. **Vision Reader** — Multimodal OCR reads handwritten student work
2. **IEP Mapper** — Maps transcribed work to specific IEP goals via function calling
3. **Progress Analyst** — Detects trends and flags regressions using thinking mode
4. **Material Forge** — Generates 7 output types for teachers, parents, and administrators

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
# Add your Google AI Studio API key to .env
streamlit run app.py
```

## Built With

- [Google Gemma 4](https://ai.google.dev/gemma) — Multimodal vision, native function calling, thinking mode
- [Streamlit](https://streamlit.io) — Demo application
- [Plotly](https://plotly.com/python/) — Progress charts and dashboards

## Team

Built for the [Gemma 4 Good Hackathon](https://kaggle.com/competitions/gemma-4-good-hackathon) — Future of Education Track

**Jeff Allan** — AI Architecture & Engineering
**Sarah Allan** — K-12 Special Education Teacher & Domain Expert

## Why This Matters

- 1 in 36 children has ASD
- Teachers spend 15+ hours/week on IEP data collection
- Only 10 empirical studies exist on GenAI for ASD education
- Every student's progress deserves to be seen

## Kaggle Gemma 4 Good Hackathon Submission

**Video & Demo Production:**
- 📹 **[VIDEO-SCRIPT.md](docs/VIDEO-SCRIPT.md)** — Complete 3-minute video script with shot list, narration, timing breakdown, and emotional arc (30 points of scoring)
- ✅ **[VIDEO-PRODUCTION-CHECKLIST.md](docs/VIDEO-PRODUCTION-CHECKLIST.md)** — Production day-by-day checklist, equipment list, screen recording guide, editing specs

**Key Submission Materials:**
- Live demo: [Streamlit Community Cloud](https://classlens-asd.streamlit.app) (deploy when ready)
- GitHub: [github.com/jeffallan/classlens-asd](https://github.com/jeffallan/classlens-asd)
- Video: YouTube (unlisted link TBD)

**Deadline:** May 18, 2026 | **Prize Pool:** $200K | **Track:** Future of Education + Special Tech (edge computing)

## License

Apache 2.0
