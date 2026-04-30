# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 18:38:52 2026

@author: Caroline Adams
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
# =========================================================
# PAGE CONFIG 
# =========================================================
st.set_page_config(
    page_title="Performance Monitoring Summary",
    layout="wide"
)
# =========================================================
# PAGE CONFIG  
# =========================================================
st.set_page_config(
    page_title="Wheelchair Racing Performance Monitoring Report",
    layout="wide"
)

# =========================================================
# LOGO
# =========================================================
logo_path = Path(__file__).resolve().parents[1] / "images" / "Logo.png"
if logo_path.exists():
    st.image(str(logo_path), width=380)
else:
    st.error(f"Logo not found at: {logo_path}")

# ===============
st.title("Performance Monitoring Summary")

# =========================================================
# BASELINE CONTEXT
# =========================================================
st.markdown("""
This session provides a **baseline snapshot** of your push profile.  
To track meaningful changes, we recommend **repeat testing every 6–8 weeks** to monitor progression across the season and build toward **LA 2028**.
""")

st.markdown("---")

# =========================================================
# KEY PERFORMANCE INSIGHT
# =========================================================
st.markdown("### 🧠 Key Performance Insight")

st.markdown("""
Your speed is driven by **effective pushing**, not just cycle frequency.  

You generate speed through a **large push range and increasing cycle length**, with frequency rising early before stabilising — a strong and efficient profile.
""")

st.success("""
✅ **Fastest rep decided in the first 10 m**  
0.04 s quicker, driven by higher cycle frequency while maintaining push length
""")

st.markdown("---")

# =========================================================
# OPPORTUNITIES
# =========================================================
st.markdown("### 🎯 Opportunities")

st.info("""
**1️⃣ Maximise the first 10 m**  
Biggest opportunity to improve performance  
*Focus: explosive, high-frequency start without losing push quality*
""")


st.info("""
**2️⃣ Maintain full push length**  
Avoid shortening stroke late in the cycle  
*Stay patient — don’t rush final pushes*
""")
st.info("""
**3️⃣ Investigate asymmetry**  
Work with Physio, Chair Fitter and S&C to assess:  
- Strength  
- Range of motion  
- Technique / Setup
\nBased on the multi-dispplinary team assessment we can tailor next steps moving forwards.
""")

st.markdown("---")

# =========================================================
# TESTING RECOMMENDATIONS
# =========================================================
st.markdown("### 💡Recommendations")

st.markdown("""
- 📅 **Re-test every 6–8 weeks** to track progression  
- 📏 **Extend distance beyond 60 m** to capture true max velocity  
- ⏱ **Ensure full recovery between reps** to reduce fatigue effects  
""")
