# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 18:35:20 2026

@author: Caroline Adams
"""

from pathlib import Path
import streamlit as st

# =========================================================
# PAGE CONFIG  
# =========================================================
st.set_page_config(
    page_title="Wheelchair Racing Testing Report",
    layout="wide"   # forces left-aligned layout
)

# =========================================================
# LOGO (LEFT-ALIGNED)
# =========================================================
logo_path = Path(__file__).resolve().parent / "images" / "Logo.png"

if logo_path.exists():
    st.image(
        str(logo_path),
        width=400
    )
else:
    st.error(f"Logo not found at: {logo_path}")

# =========================================================
# TITLE AND SUBTITLE
# =========================================================
st.title("Wheelchair Racing Performance Testing Reports")
st.subheader("Athlete Feedback")

# =========================================================
# DIVIDER
# =========================================================
st.markdown("---")

# =========================================================
# INTRO TEXT
# =========================================================
st.write(
    """
    This report provides feedback and highlights performance opportunities 
    for wheelchair racing athletes based on track and laboratory testing. 
    This report presents your baseline values and we will continue to test 
    thorughout the sesason to monitor change.
    """
)

st.write("Use the menu on the left to move between pages.")