import streamlit as st
import database as db

# Initialize the database
db.init_db()

# Page Configuration
st.set_page_config(
    page_title="AI Resume Checker Pro",
    page_icon="🤖",
    layout="wide"
)

# Load Custom CSS
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS file '{file_name}' not found.")

load_css("style.css")

# --- HOME PAGE CONTENT ---
st.title("Welcome to the AI Resume Checker Pro 🤖")
st.header("Your intelligent assistant for talent acquisition.")

st.markdown("""
### How to Use This App
1.  **Open the Sidebar:** Click the `>` arrow in the top-left corner.
2.  **Navigate:** Select the page you want to visit, like **'Resume Checker'** or **'Dashboard & History'**.
""")