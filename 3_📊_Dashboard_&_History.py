import streamlit as st
st.markdown('<style>[data-testid="stAppViewContainer"] { background-color: #f5f6fa !important; }</style>', unsafe_allow_html=True)
import streamlit as st
import database as db
import pandas as pd

st.set_page_config(page_title="Dashboard & History", layout="wide")

# Load Custom CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css("style.css")

st.title("📊 Dashboard & History | PlacementIQ")
st.write("View all past resume analyses and track your shortlisting process.")

all_data = db.get_all_analyses()

if all_data.empty:
    st.warning("No analyses found. Please check a resume on the 'Resume Checker' page.")
else:
    st.dataframe(all_data, use_container_width=True)