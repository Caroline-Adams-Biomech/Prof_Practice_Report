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

st.markdown("""
This protocol combines **track sprint testing** and **lab-based ergometer testing**  
to establish a clear baseline of your propulsion and monitor performance across the season.
""")

# =========================================================
# Track Session Section
# =========================================================
st.subheader("Track Session")

if trackstart_path:
    st.image(str(trackstart_path), width=400)
else:
    st.warning(
        "Track start image not found.\n"
        "Checked for: track_start.png / track_start.jpg / track_start.jpeg\n"
        f"in {IMAGES_DIR}"
    )
# =========================================================
# TRACK SESSION
# =========================================================

st.markdown("""
To establish your sprint baseline, you will complete **four 60 m maximum-effort sprints**.  
Multiple repetitions give a clear picture of your **pushing pattern, consistency, and performance variability**.

📹 **Data capture**
- Camera 1: **0–10 m (acceleration phase)**
- Camera 2: **35–45 m (high-speed phase)**

All movement data is collected from the **left side** due to camera positioning.

This same setup can be repeated after training blocks to **track changes in your sprint performance over time**.
""")

if test_path:
    st.image(str(test_path), width=800)
else:
    st.warning(
        "Track session test overview image not found}"
    )
# =========================================================
# Lab Session Section
# =========================================================
st.subheader("Lab Session")

if wcerg_path:
    st.image(str(wcerg_path), width=400)
else:
    st.warning(
        "Wheelchair ergometer image not found.\n"
        "Checked for: WC_ergometer.png / WC_ergometer.jpg / WC_ergometer.jpeg\n"
        f"in {IMAGES_DIR}"
    )

# =========================================================
# LAB SESSION
# =========================================================

st.markdown("""
To understand how you apply force to the wheels, testing is completed using the  
**Lode Esseda ergometer**.

This allows us to measure how each side contributes independently and identify  
any **left–right differences in your pushing pattern**.

After a warm-up and familiarisation, you will complete **two 30-second efforts**:
- Baseline resistance (similar to track)
- Higher resistance (increased demand)

### Aims
- Build a **baseline push profile** for longitudinal tracking  
- Identify **left–right asymmetries**  
- Understand how your pushing changes under **higher resistance**
""")
