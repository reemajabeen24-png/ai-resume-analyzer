import streamlit as st
from datetime import datetime
from utils.extractor import extract_resume_text
from utils.nlp_processor import clean_text, basic_resume_stats, extract_skills, calculate_ats_score
from utils.ai_analyzer import analyze_resume

# Page configuration
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="centered"
)

# ---- Custom styling ----
st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .subtitle {
        color: #6b7280;
        margin-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# ---- Header ----
st.markdown('<p class="main-title">📄 AI Resume Analyzer</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Upload your resume and get instant AI-powered feedback to improve it.</p>', unsafe_allow_html=True)

# ---- Sidebar ----
with st.sidebar:
    st.header("About")
    st.caption("Built with Python, Streamlit, spaCy & Gemini AI")

# ---- Job role input ----
job_role = st.text_input("🎯 Target job role (optional)", placeholder="e.g. Data Analyst")
st.caption("Tip: Adding a target role helps the AI tailor its feedback.")

# ---- File uploader ----
uploaded_file = st.file_uploader(
    "Upload your resume (PDF or DOCX)",
    type=["pdf", "docx"]
)
if uploaded_file is not None:
    with st.spinner("Extracting text from your resume..."):
        resume_text = extract_resume_text(uploaded_file)

    if resume_text:
        cleaned_text = clean_text(resume_text)

        with st.expander("📄 Extracted Resume Text (click to view)"):
            st.text_area("Preview", resume_text, height=250, label_visibility="collapsed")

        st.subheader("📊 Quick Resume Stats")
        stats = basic_resume_stats(resume_text)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Words", stats["word_count"])
        col2.metric("Sentences", stats["sentence_count"])
        col3.metric("Email", "✅" if stats["has_email"] else "❌")
        col4.metric("Phone", "✅" if stats["has_phone"] else "❌")

        # ATS Score
        ats_result = calculate_ats_score(resume_text, stats)
        score = ats_result["score"]
        skills = ats_result["skills_found"]

        st.subheader("🎯 ATS Compatibility Score")

        if score >= 75:
            st.success(f"Score: {score}/100 — Good ATS compatibility")
        elif score >= 50:
            st.warning(f"Score: {score}/100 — Moderate ATS compatibility")
        else:
            st.error(f"Score: {score}/100 — Needs improvement")

        st.progress(score / 100)

        if ats_result["reasons"]:
            with st.expander("⚠️ Issues affecting your score"):
                for reason in ats_result["reasons"]:
                    st.write(f"- {reason}")

        # Skills found
        st.subheader("🛠️ Detected Skills")
        if skills:
            st.write(", ".join([f"`{s}`" for s in skills]))
        else:
            st.write("No common skill keywords detected.")

        st.divider()

        # ---- AI Analysis ----
        if "feedback" not in st.session_state:
            st.session_state.feedback = None

        if st.button("🔍 Analyze Resume with AI", type="primary", use_container_width=True):
            with st.spinner("Analyzing your resume with Gemini AI... this may take a few seconds"):
                try:
                    st.session_state.feedback = analyze_resume(
                        cleaned_text, job_role if job_role else None
                    )
                except Exception as e:
                    error_str = str(e)
                    if "503" in error_str or "UNAVAILABLE" in error_str:
                        st.error("⚠️ Gemini's servers are temporarily overloaded (high demand). Please wait a moment and click 'Analyze Resume with AI' again.")
                    else:
                        st.error(f"Something went wrong while analyzing: {e}")

        if st.session_state.feedback:
            st.subheader("🤖 AI Feedback")
            st.markdown(st.session_state.feedback)

            # Prepare downloadable report (includes stats + ATS + AI feedback)
            report_date = datetime.now().strftime("%Y-%m-%d %H:%M")
            skills_text = ", ".join(skills) if skills else "None detected"
            reasons_text = "\n".join([f"- {r}" for r in ats_result["reasons"]]) if ats_result["reasons"] else "None"

            report_content = f"""AI RESUME ANALYSIS REPORT
Generated on: {report_date}
Target Role: {job_role if job_role else "Not specified"}
File: {uploaded_file.name}

{'-' * 50}
QUICK STATS
{'-' * 50}
Word Count: {stats['word_count']}
Sentence Count: {stats['sentence_count']}
Email Found: {"Yes" if stats['has_email'] else "No"}
Phone Found: {"Yes" if stats['has_phone'] else "No"}

{'-' * 50}
ATS COMPATIBILITY SCORE: {score}/100
{'-' * 50}
Issues:
{reasons_text}

{'-' * 50}
DETECTED SKILLS
{'-' * 50}
{skills_text}

{'-' * 50}
AI FEEDBACK
{'-' * 50}
{st.session_state.feedback}
"""
            st.download_button(
                label="⬇️ Download Full Report as Text File",
                data=report_content,
                file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True
            )

    else:
        st.error("Could not extract text. Please upload a valid PDF or DOCX file.")
else:
    st.info("👆 Upload a resume file above to get started.")

st.divider()
st.caption("⚠️ This tool provides AI-generated suggestions and should be used as guidance, not a guarantee of job application success.")