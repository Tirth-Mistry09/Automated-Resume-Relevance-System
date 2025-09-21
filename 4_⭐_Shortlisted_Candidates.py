import streamlit as st
import database as db
import pandas as pd

st.set_page_config(page_title="Shortlisted Candidates", layout="wide")


# Load Custom CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css("style.css")

# Force light theme background
st.markdown('<style>[data-testid="stAppViewContainer"] { background-color: #f5f6fa !important; }</style>', unsafe_allow_html=True)

st.title("⭐ Shortlisted Candidates | PlacementIQ")
st.write("These are the candidates you've marked for an interview.")

shortlisted_data = db.get_shortlisted()

if shortlisted_data.empty:
    st.info("No candidates have been shortlisted yet.")
else:
    st.dataframe(shortlisted_data, use_container_width=True)