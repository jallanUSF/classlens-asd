# Deployment Security Checklist — ClassLens ASD

Use this checklist before deploying to Streamlit Community Cloud or any public environment.

## Pre-Deployment (Before Commit)

- [ ] **Git Setup**
  - [ ] `.gitignore` file exists and includes `.env`
  - [ ] `.env` file is NOT committed to history
  - [ ] Run: `git log -p --all -S "GOOGLE_AI_STUDIO_KEY"` → No results
  - [ ] Run: `git log -p --all -S "api_key"` → No results
  - [ ] `.streamlit/secrets.toml` is in `.gitignore`

- [ ] **Environment Variables**
  - [ ] `.env.example` exists with placeholder text only
  - [ ] `.env` file has actual API key locally
  - [ ] Never commit `.env` file
  - [ ] Never paste API key in documentation or comments

- [ ] **Code Review**
  - [ ] All API calls use `os.getenv()` or `st.secrets[]` for credentials
  - [ ] No hardcoded API keys in Python files
  - [ ] No API key in error messages or logging statements
  - [ ] No real student names hardcoded in app code
  - [ ] Sample data uses only synthetic names (Maya, Jaylen, Sofia)

- [ ] **Documentation**
  - [ ] `PRIVACY-NOTICE.md` exists at repo root
  - [ ] `SECURITY-REVIEW.md` exists in `docs/`
  - [ ] README mentions demo is for synthetic data only
  - [ ] API key setup instructions in README or `CONTRIBUTING.md`

- [ ] **Configuration Files**
  - [ ] `.streamlit/config.toml` has security settings:
    - [ ] `enableXsrfProtection = true`
    - [ ] `showErrorDetails = false`
    - [ ] `logger.level = "error"`
    - [ ] `maxUploadSize = 10` (10 MB limit)

- [ ] **Dependencies**
  - [ ] `requirements.txt` uses pinned versions (no wildcards like `streamlit>=1.0`)
  - [ ] No development packages in production requirements
  - [ ] All packages are from official PyPI (no git URLs to untrusted repos)

## Streamlit Cloud Setup

- [ ] **Repository**
  - [ ] Fork or mirror is public (if judges need to review)
  - [ ] `.gitignore` is committed and working
  - [ ] Sensitive files are NOT in repo

- [ ] **Secrets Management**
  - [ ] Go to app settings → Secrets
  - [ ] Add `GOOGLE_AI_STUDIO_KEY` as a secret (NOT in config file)
  - [ ] Secret marked as "private"
  - [ ] Do NOT paste key in advanced settings or config.toml

- [ ] **URL & Sharing**
  - [ ] App URL is available publicly
  - [ ] Judges have the direct link (e.g., `https://classlens-asd-demo.streamlit.app`)
  - [ ] URL is NOT behind authentication (demo must be accessible)

## Runtime (After Deployment)

- [ ] **Smoke Test**
  - [ ] Load app in browser: does it load without errors?
  - [ ] Try uploading a test image: does it process?
  - [ ] Check Streamlit logs: any API key exposed? → Should see nothing
  - [ ] Test error handling: does app show unhelpful error messages?

- [ ] **Google Cloud Console**
  - [ ] Check API quota usage (should be low for demo)
  - [ ] Set up usage alerts (warn at 80% of quota)
  - [ ] Save API key for later rotation (monthly best practice)

- [ ] **Monitoring (Optional for Hackathon)**
  - [ ] Set up CloudWatch or Datadog to monitor errors
  - [ ] Configure alerts for unusual API usage spikes
  - [ ] Log unexpected 500 errors

## Post-Deployment

- [ ] **Monitoring**
  - [ ] Check Streamlit logs daily during hackathon week
  - [ ] Monitor Google API usage in Cloud Console
  - [ ] Look for error patterns or suspicious activity

- [ ] **Security Incident Response**
  - [ ] If API key is leaked:
    1. Immediately revoke key in Google Cloud Console
    2. Create new API key
    3. Update Streamlit Cloud secrets
    4. Document incident in INCIDENT-LOG.md
  - [ ] If data breach occurs:
    1. Record details (what, when, who, how)
    2. Assess impact (real student data exposed? → FERPA breach)
    3. Notify involved parties
    4. Store incident report

## Monthly Maintenance (If Running Past Hackathon)

- [ ] **Key Rotation**
  - [ ] Generate new Google API key
  - [ ] Update Streamlit Cloud secrets
  - [ ] Revoke old key
  - [ ] Document rotation date

- [ ] **Dependency Updates**
  - [ ] Check for security updates: `pip list --outdated`
  - [ ] Update `requirements.txt` with patched versions
  - [ ] Test app after updates
  - [ ] Commit and redeploy

- [ ] **Code Review**
  - [ ] Check git logs for any accidental commits
  - [ ] Verify `.env` is never checked in
  - [ ] Review recent code changes for security issues

- [ ] **Compliance Check**
  - [ ] Are all student data in demo still synthetic? (Never added real students?)
  - [ ] Is privacy notice still accurate?
  - [ ] Are security docs up to date?

## Production Deployment (Beyond Hackathon)

If deploying to a real school, STOP and complete this first:

- [ ] **Institutional Review**
  - [ ] Legal review of Data Use Agreement (DUA)
  - [ ] IT security assessment by school IT team
  - [ ] FERPA compliance audit

- [ ] **Infrastructure**
  - [ ] Move to self-hosted Streamlit or Streamlit Enterprise
  - [ ] Set up PostgreSQL with field-level encryption
  - [ ] Implement VPC isolation
  - [ ] Configure SSL/TLS 1.3

- [ ] **Authentication & Authorization**
  - [ ] Implement SSO (Okta, Google Workspace, district provider)
  - [ ] Role-based access control (teacher sees only their students)
  - [ ] MFA (multi-factor authentication) for sensitive accounts

- [ ] **Data Protection**
  - [ ] Encrypt student data at rest (AES-256)
  - [ ] Encrypt in transit (TLS 1.3)
  - [ ] Implement audit logging
  - [ ] Set up data retention and deletion policies

- [ ] **Testing & QA**
  - [ ] Penetration testing by third party
  - [ ] Load testing under realistic school usage
  - [ ] Disaster recovery and backup testing
  - [ ] FERPA compliance testing

---

## Quick Reference: Common Mistakes to Avoid

| Mistake | Why It's Bad | How to Fix |
|---|---|---|
| API key in `.env` committed to git | Public exposure; easy to steal | Ensure `.env` is in `.gitignore` |
| API key in code as string | Visible in source; hard to rotate | Use environment variables only |
| Real student names in demo | Could match actual students; FERPA issue | Use common synthetic names |
| No file upload validation | DOS attacks via huge files; malware | Implement MIME type check + size limit |
| Detailed error messages in logs | PII exposure; debugging info leaked | Set `logger.level = "error"` |
| No privacy documentation | Judges assume you didn't think about it | Include `PRIVACY-NOTICE.md` |
| Uploaded images stored permanently | Data accumulation; privacy leak | Use temp storage only |
| No XSRF protection | Cross-site attacks possible | Enable `enableXsrfProtection = true` |

---

## Checklist Sign-Off

- [ ] All items completed
- [ ] No API key in code
- [ ] Privacy documentation ready
- [ ] Security config applied
- [ ] Tests passing locally
- [ ] Ready for Streamlit Cloud deployment

**Deployed By:** ________________________
**Date:** ________________________
**Notes:** ________________________________________________________________

---

For questions, see `docs/SECURITY-REVIEW.md` or contact the team.
