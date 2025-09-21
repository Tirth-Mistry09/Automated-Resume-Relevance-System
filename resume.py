import streamlit as st
import fitz  # PyMuPDF
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import database as db # Import your database helper
import re

# --- Page Configuration and Styling ---
st.set_page_config(page_title="Resume Checker: PlacementIQ", layout="wide")

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css("style.css")

st.title("Resume Checker: PlacementIQ 💼")

# --- Helper Functions ---
def extract_text_from_file(file_object):
    """Reads a file-like object (PDF or TXT) and returns its text content."""
    try:
        if file_object.type == "application/pdf":
            pdf_document = fitz.open(stream=file_object.read(), filetype="pdf")
            text = "".join(page.get_text() for page in pdf_document)
            return text
        elif file_object.type == "text/plain":
            return file_object.read().decode("utf-8")
    except Exception as e:
        st.error(f"Error reading the file: {e}")
    return None

def get_gemini_analysis(api_key, resume_text, jd_text):
    """Calls the Gemini API to get the analysis."""
    try:
        os.environ["GOOGLE_API_KEY"] = api_key
        prompt = f"""
        You are an expert ATS (Applicant Tracking System) with a deep understanding of recruitment.
        Your task is to analyze the following resume against the provided job description.
        
        Provide a detailed analysis in the following format, using these exact headings:
        **Relevance Score:** A score from 0 to 100.
        **Verdict:** A short verdict, either "High Fit", "Medium Fit", or "Low Fit".
        **Summary:** A brief, 2-3 sentence summary.
        **Missing Skils:** A list of the top 3-5 missing skills.
        ---
        **Job Description:**
        {jd_text}
        ---
        **Resume:**
        {resume_text}
        ---
        """
        model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        response = model.invoke(prompt)
        return response.content
    except Exception as e:
        st.error(f"An error occurred during AI analysis: {e}")
        return "Error: Could not get response from AI model."

def parse_analysis(analysis_text):
    """Parses the AI's text response into a dictionary."""
    try:
        score_match = re.search(r"Relevance Score\s*:?\s*[*]*\s*(\d+)", analysis_text)
        verdict_match = re.search(r"Verdict:\s*[*]*\s*(.*)", analysis_text)
        summary_match = re.search(r"Summary:\s*[*]*\s*([\s\S]*?)Missing Skills:", analysis_text)
        missing_keywords_match = re.search(r"Missing Skills:\s*[*]*\s*([\s\S]*)", analysis_text)

        score = int(score_match.group(1)) if score_match else 0
        verdict = verdict_match.group(1).strip() if verdict_match else "N/A"
        summary = summary_match.group(1).strip() if summary_match else "N/A"
        missing_keywords = missing_keywords_match.group(1).strip() if missing_keywords_match else "N/A"
        return {
            "score": score,
            "verdict": verdict,
            "summary": summary,
            "missing_keywords": missing_keywords
        }
    except Exception as e:
        st.error(f"Error parsing AI response: {e}")
        return None

# --- Main App UI ---
st.title("🔎 Resume Checker")
st.write("Upload a resume and a job description to get an instant analysis.")

try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except (KeyError, FileNotFoundError):
    st.error("🔴 Your Google API Key is not set! Please add it to your Streamlit secrets.")
    st.stop()

col1, col2 = st.columns(2)
with col1:
    st.header("📄 Upload Resume")
    resume_file = st.file_uploader("Choose a PDF file", type=["pdf"])
with col2:
    st.header("📋 Upload Job Description")
    jd_file = st.file_uploader("Choose a PDF or TXT file", type=["pdf", "txt"])

if st.button("✨ Analyze Now", use_container_width=True):
    if resume_file is not None and jd_file is not None:
        with st.spinner("Analyzing... This may take a moment."):
            resume_content = extract_text_from_file(resume_file)
            jd_content = extract_text_from_file(jd_file)
            
            if resume_content and jd_content:
                # Get the raw analysis from the AI
                analysis_result = get_gemini_analysis(API_KEY, resume_content, jd_content)
                
                # Parse the raw text into structured data
                parsed_data = parse_analysis(analysis_result)
                
                if parsed_data:
                    # Save to database and get the ID of the new record
                    record_id = db.add_analysis(
                        resume_name=resume_file.name,
                        jd_name=jd_file.name,
                        score=parsed_data["score"],
                        verdict=parsed_data["verdict"],
                        summary=parsed_data["summary"],
                        missing_keywords=parsed_data["missing_keywords"]
                    )
                    st.session_state.last_analysis_id = record_id
                    st.toast('Analyzation saved to History (Dashboard & History)', icon='✅')
                    st.divider()
                    st.markdown("""
### 📊 Analysis Result
**Relevance Score:** {score}

**Verdict:** {verdict}

**Summary:**
{summary}

**Missing Skills:**
{missing_list}
""".format(
    score=parsed_data["score"],
    verdict=parsed_data["verdict"],
    summary=parsed_data["summary"],
    missing_list="\n".join([f"- {kw.strip('- ')}" for kw in parsed_data["missing_keywords"].split("\n") if kw.strip()])
), unsafe_allow_html=False)
                else:
                    st.error("Could not parse the AI's response.")
    else:
        st.warning("⚠️ Please upload both the resume and the job description files.")

# Add a checkbox to shortlist the candidate after analysis
if 'last_analysis_id' in st.session_state:
    st.divider()
    record_id = st.session_state.last_analysis_id
    # Always get shortlist status from DB for persistence
    import sqlite3
    conn = sqlite3.connect('resume_data.db')
    c = conn.cursor()
    c.execute('SELECT shortlisted FROM analyses WHERE id = ?', (record_id,))
    row = c.fetchone()
    conn.close()
    db_shortlisted = bool(row[0]) if row else False
    is_shortlisted = st.checkbox("⭐ Shortlist this Candidate for Interview", value=db_shortlisted, key=f"shortlist_{record_id}")
    db.update_shortlist_status(record_id, is_shortlisted)
    if is_shortlisted:
        st.success("Candidate has been added to the Shortlisted page!")



## Remove theme toggle, always use light theme
st.markdown('<style>[data-testid="stAppViewContainer"] { background-color: #f5f6fa !important; }</style>', unsafe_allow_html=True)