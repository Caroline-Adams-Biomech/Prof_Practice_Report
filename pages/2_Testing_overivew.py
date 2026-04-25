# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 13:07:06 2026

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
#st.header("What These Metrics Mean 🔎") #Update for each page
st.markdown("---")
# =========================================================

# paths for images
base_path = Path(__file__).resolve().parents[1]
trackstart_path = base_path / "images" / "track_start.png"
test_path = base_path / "images" / "Test_session.jpg"
wcerg_path = base_path / "images" / "WC_ergometer.png"

 # =========================================================
# --- Title
st.subheader("Track Session")
# --- Test Session image
if trackstart_path.exists():
        st.image(str(trackstart_path), width=800,)
else:
        st.warning(f"Track start image not found at: {trackstart_path }")

st.write(
    "To establish your baseline sprint profile at the start of the season you will do four  "
    "60m max efforts. By doing four reps we can develop a clear picture of your push profile,  "
    "explore variation between reps, and have confidence that anything we are seeing isn't just a one off random event."
    "Three cameras will be used one set up in the saggital plane to view the accerlarion phase over the first 10m,"
    "a second also in the sagital plane between  35-45m and a third panning camera to capture the full 60m."
    "It is important to note that due to cameras only being set up on one side all data will be related to the left hand side."
    "In the future after training interventions we can repeat this setup to evaluate if anything has changed."
)
 # =========================================================
# --- Title
st.subheader("Lab Session")
# --- Test Session image
if wcerg_path.exists():
        st.image(str(wcerg_path), width=800,)
else:
        st.warning(f"Track start image not found at: {trackstart_path }")
        

st.write(
    "Using the Lode Esseda instrumented ergometer allows us to to look at your left and right side independently and measure the amount of torque"
    "you are able to drive through the push. After a warm-up and familiarisation with the ergometer the test setup will invovle you "
    "completing two different 30 second efforts of pushing. The first at a resistance typical of an athletics track and the second at an increased resistance."
    "This will enable us to explore three different things. Firsty to establish a baseline push profile for you which we can then monitor overtime with longitudinal testing."
    "Secondly the erg setup means we are able to determine if any left and right assymetries exist in your stroke. Thirdly testing at two different resistances enable us to see "
    "how you cope at when the demands increase."
 )
