# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 18:35:20 2026

@author: Caroline Adams
"""
# =========================================================
# PAGE SETUP
# =========================================================
from pathlib import Path
import streamlit as st

logo_path = Path(__file__).resolve().parents[1] / "images" / "Logo.png"

# --- Logo centred at top
if logo_path.exists():
    st.image(str(logo_path), width=400)
else:
    st.error(f"Logo not found at: {logo_path}")

# --- Page title & subtitle
st.title("Wheelchair Racing Performance Testing Report")
#st.subheader("Athlete Feedback") Update for each page

# =========================================================

# paths for images
base_path = Path(__file__).resolve().parents[1]
profile_path = base_path / "images" / "athlete profile.png"

st.set_page_config(
    page_title="Athlete Profile",
    layout="wide"
)

# --- Title
st.subheader("Athlete Profile")
# --- Athlete profile image
if profile_path.exists():
    st.image(str(profile_path), width=800,)
else:
    st.warning(f"Athlete profile image not found at: {profile_path}")
    

    
