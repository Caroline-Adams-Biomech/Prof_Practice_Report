# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 15:23:59 2026

@author: Caroline Adams
"""
# =========================================================
# PAGE SETUP
# =========================================================
from pathlib import Path
import streamlit as st

st.set_page_config(layout="wide")

# =========================================================
# Helper: robust image loader (png / jpg / jpeg)
# =========================================================
def load_image(image_dir: Path, stem: str):
    """
    Attempt to load an image using common extensions.
    Returns the Path if found, otherwise None.
    """
    for ext in [".png", ".jpg", ".jpeg"]:
        candidate = image_dir / f"{stem}{ext}"
        if candidate.exists():
            return candidate
    return None

# =========================================================
# Base paths (multipage-safe)
# =========================================================
PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMAGES_DIR = PROJECT_ROOT / "images"

# =========================================================
# Load images safely
# =========================================================
logo_path = load_image(IMAGES_DIR, "Logo")
trackstart_path = load_image(IMAGES_DIR, "track_start")
test_path = load_image(IMAGES_DIR, "Test_session")
wcerg_path = load_image(IMAGES_DIR, "WC_ergometer")

# =========================================================
# Header / Logo
# =========================================================
if logo_path:
    st.image(str(logo_path), width=400)
else:
    st.error(
        "Logo image not found. Expected one of:\n"
        "Logo.png / Logo.jpg / Logo.jpeg\n"
        f"in {IMAGES_DIR}"
    )
# --- Page title & subtitle
st.title("Performance Monitroing Protocols")

# =========================================================
# DIVIDER
# =========================================================
st.markdown("---")
# =========================================================
# TEST SESSION (COMPACT SUMMARY)
# =========================================================
st.markdown("### 📊 Test Session")

st.markdown("""
- 📅 **Date:** 22 March 2026  
- 📍 **Location:** Loughborough Indoor Track & PHC Lab  
- 🏁 **Track:** 4 × 60 m max effort  
- 🔎 **Lab:** 2 × 30 s efforts (baseline + high resistance)  
- 🎯 **Purpose:** Baseline & identify improvement opportunities  
""")

    
    

st.info("**Purpose:** Baseline pre-season & identify improvement opportunities")

st.subheader("Track Session")

col1, col2 = st.columns([1, 2])

with col1:
    if trackstart_path:
        st.image(str(trackstart_path), width=400)
    else:
        st.warning(
            "Track start image not found.\n"
            "Checked for: track_start.png / track_start.jpg / track_start.jpeg\n"
            f"in {IMAGES_DIR}"
        )
   
with col2:
    st.markdown("""
    **4 × 60 m sprint efforts** to establish your sprint baseline.

    **What we assess:**
    - Acceleration (0–10 m)
    - High-speed phase (35–45 m)
    - Consistency across repetitions

    📹 Data is captured from the left side for consistent analysis.
    """)

st.subheader("Lab Session")

col1, col2 = st.columns([1, 2])

with col1:
    if wcerg_path:
        st.image(str(wcerg_path), width=400)
    else:
        st.warning(
            "Wheelchair ergometer image not found.\n"
            "Checked for: WC_ergometer.png / WC_ergometer.jpg / WC_ergometer.jpeg\n"
            f"in {IMAGES_DIR}"
        )
 
with col2:
    st.markdown("""
    Testing on the **Lode Esseda ergometer** allows independent analysis of each side.

    **What we assess:**
    - Left–right contribution
    - Force application patterns
    - Response to increased resistance

    You complete:
    - Baseline resistance effort
    - Higher resistance effort
    """)


