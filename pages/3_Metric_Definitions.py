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
st.header("What These Metrics Mean 🔎") #Update for each page
st.markdown("---")
# =========================================================


# paths for images
base_path = Path(__file__).resolve().parents[1]
logo_path = base_path / "images" / "Logo.png"
cycle_path = base_path / "images" / "cycle_definitions_image.png"
pushangle_path = base_path / "images" / "push_angle.png"

# st.title("What These Metrics Mean")

st.write("This page explains the key metrics used in this report.")

st.subheader("⏱️ Cumulative Time (seconds)")
st.write("Time taken to travel from 0m to specified distance (i.e. time from 0-10m, 0-20m etc).")

st.subheader("⏱️ Interval Time (seconds)")
st.write("Time taken to travel from start to end of segment, effectively a split time (i.e. time from 0-10m, 10-20m etc). ")


# --- Cycle image
if cycle_path.exists():
    st.image(str(cycle_path), width=1200,)
else:
    st.warning(f"Cycle definition image not found at: {cycle_path}")

st.subheader("🔂 Cycle")
st.write("One cycle is both the push phase (where the hands are on the push rim) and the rolling phase (where the hands are not in contact with the push rim and the chair is freewheeling). ")

st.subheader("🔁 Average Cycle Frequency (CPM - cycles per minute)")
st.write("The number of cycles completed per minute (RPM), basically an arm speed or cadence measure. Where the average is the average number of cycles per second for the segment of interest (i.e. 0-10m, 30-40m).")

st.subheader("🔂📏 Cycle Length (m)")
st.write("The distance travelled during each cycle. The average cycle length is average distance travelled for a given segment of interest ")

st.subheader("👊📏 Push Length")
st.write(" Distance travelled during the push phase where the hands are in contact with the push rim.")

st.subheader("🌀📏 Rolling Length")
st.write("Distance travelled during the push phase where the hands are in contact with the push rim.")

st.subheader("🔂 💨 Cycle Velocity (m/s)")
st.write("The speed the athlete and chair are moving during a complete cycle.")


st.subheader("👊 💨 Push Velocity (m/s)")
st.write("The speed the athlete and chair are moving during a push.")

st.subheader("🌀 💨 Rolling Velocity (m/s)")
st.write("The speed the athlete and chair are moving during the rolling phase.")

st.subheader("👊 📐 Push Angle (degrees)")
st.write("Total number of degrees the athlete pushes the wheel through whilst their hands are in contact with the push rim, doesn’t describe where the push started or ended just the number of degress travelled.")
st.write("The push angle could be the same value for 2 very different push techniques as shown by the shaded blue area below, in both cases the wheel was pushed through 105 degrees, but where the push occurred is different.")

# --- Push angle image
if pushangle_path.exists():
    st.image(str(pushangle_path), width=800,)
else:
    st.warning(f"Push angle definition image not found at: {pushangle_path}")

st.subheader("🚀 Torque")
"The metric we get from the instrumented ergometer which allows us to assess your engine output. It’s how much turning power your shoulder, arm, and trunk are putting into the wheel or ergometer at any moment."
"Torque is a helpful metric as it isn't just pure strength, but a compination of strength, technique and timing."
 



