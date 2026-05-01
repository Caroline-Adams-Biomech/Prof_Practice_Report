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


# ✅ Base path (always do this once)
BASE_PATH = Path(__file__).resolve().parents[1]

# ✅ Paths
logo_path = BASE_PATH / "images" / "Logo.png"
profile_path = BASE_PATH / "images" / "athlete_profile.png"  # ✅ adjust filename if needed


logo_path = Path(__file__).resolve().parents[1] / "images" / "Logo.png"

# --- Logo centred at top
if logo_path.exists():
    st.image(str(logo_path), width=400)
else:
    st.error(f"Logo not found at: {logo_path}")

# --- Page title & subtitle
st.title("Athlete Profile")

# =========================================================
# DIVIDER
# =========================================================
st.markdown("---")


if profile_path.exists():
    st.image(str(profile_path), width=800,)
else:
    st.warning(f"Athlete profile image not found at: {profile_path}")
    

    
