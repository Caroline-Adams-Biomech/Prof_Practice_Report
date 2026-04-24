# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 18:35:20 2026

@author: Caroline Adams
"""

from pathlib import Path
import streamlit as st

logo_path = Path(__file__).resolve().parent / "images" / "Logo.png"

st.set_page_config(
    page_title="Wheelchair Racing Testing Report",
    layout="wide"
)

# --- Logo centred at top
if logo_path.exists():
    st.image(str(logo_path), width=400)
else:
    st.error(f"Logo not found at: {logo_path}")

# --- Title and subtitle
st.title("Wheelchair Racing Performance Testing Reports")
st.subheader("Athlete Feedback")

# --- Divider
st.markdown("---")

st.write(
    "This report provides feedback and highlights performance opportunities "
    "for wheelchair racing athletes based on track and laboratory testing."
)

st.write("Use the menu on the left to move between pages.")