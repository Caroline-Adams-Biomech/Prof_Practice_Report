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

st.title("Wheelchair Racing Performance Testing Report")
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

st.write(
    "To establish your sprint baseline at the start of the season, you will complete four "
    "60 m maximum‑effort sprints. Completing multiple repetitions helps build a clear picture "
    "of how you push, how consistent your technique is, and whether differences between efforts "
    "are meaningful rather than just one‑off variations. Two cameras are used during the test. One captures the early acceleration phase over the "
    "first 0–10 m, another focuses on your pushing pattern between 35–45 m when speed is higher."
    "Because the cameras are positioned on one side only, all movement data relates to the left "
    "side of your body. This same setup can be repeated after training blocks later in the season to see monitor changes on your sprint performance."
)
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

st.write(
    "Testing on the Lode Esseda ergometer allows us to look at how each side contributes to the push "
    "independently. It measures how much turning force you apply through the wheels during each push."
    "After a warm‑up and time to get comfortable on the ergometer, you will complete two separate "
    "30‑second pushing efforts. The first uses a resistance similar to what you experience on the "
    "track, and the second uses a higher resistance."
    "This helps us: (1) build a clear baseline profile that we can track over time, "
    "(2) identify potential left‑right asymmetries, and "
    "(3) understand how your pushing changes when the external demands are increased"
)
