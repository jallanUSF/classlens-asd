# Privacy Notice — ClassLens ASD

## What This Application Does

ClassLens ASD is a **demo application** for the Gemma 4 Good Hackathon (Education track). It uses Google's Gemma 4 model to help special education teachers analyze student work artifacts and track IEP progress.

## Demo Data

**This demo uses only synthetic student data.** The student profiles (Maya, Jaylen, Sofia) are fabricated examples created for demonstration purposes. No real student names, addresses, or family information are stored or processed.

## How Student Data Would Be Handled (Production)

If ClassLens were deployed in a real school:

- **User Authentication:** Teachers would log in via district SSO (single sign-on).
- **FERPA Compliance:** All student education records would be protected under the Family Educational Rights and Privacy Act (FERPA).
- **Encryption:** Student data would be encrypted at rest and in transit using industry-standard TLS 1.3.
- **Data Retention:** Student data would be automatically deleted after a defined retention period.
- **Audit Logging:** All access to student data would be logged for institutional review.
- **Institutional Agreement:** Schools would sign a Data Use Agreement (DUA) before deploying the tool.
- **Consent:** Parents/guardians would consent to data collection via IEP meetings.

## Current Data Handling

**Uploaded Images:**
- Processed immediately to extract text via Gemma 4.
- Not stored permanently.
- Temporary files deleted automatically by Streamlit.
- Not encrypted (demo only).

**API Key Security:**
- Google AI Studio API key is stored in environment variables, never in code.
- Added to `.gitignore` to prevent accidental sharing.
- Can be rotated or revoked immediately via Google Cloud Console.

**Logging:**
- Streamlit Cloud logs basic usage metrics (page views, errors).
- Student data is not captured in logs.
- Google AI Studio logs your API usage (standard for cloud services).

## Your Privacy

**This application does not:**
- Collect personal information about you (teachers, parents, students).
- Use cookies or tracking pixels.
- Share data with third parties.
- Store uploaded images permanently.
- Require user accounts or logins.

**This application does:**
- Send API requests to Google's servers to run Gemma 4.
- Process images you upload in real time.
- Delete uploaded images from memory after processing.

## Third-Party Services

This demo uses:
- **Google Gemma 4 API** — Your API calls are subject to [Google's Privacy Policy](https://policies.google.com/privacy).
- **Streamlit Community Cloud** — Deployment is subject to [Streamlit's Terms of Service](https://streamlit.io/cloud/terms).

## About FERPA

The Family Educational Rights and Privacy Act protects student education records. This demo is not subject to FERPA because it uses synthetic data. However, any future school deployment would require full FERPA compliance, including:

- Institutional review and approval.
- Data Use Agreement with the school district.
- Teacher training on data security.
- Breach response procedures.

## Questions or Concerns?

This is a student hackathon project. For security issues, contact the team at the Kaggle competition page.

For information about FERPA, visit: https://www2.ed.gov/policy/gen/guid/fpco/ferpa/

---

**Last Updated:** April 4, 2026
**Status:** Hackathon Demo (Not for Production Use)
