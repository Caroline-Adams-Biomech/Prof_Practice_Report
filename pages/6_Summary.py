# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 18:38:52 2026

@author: Caroline Adams
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from utils.pdf_report import create_full_report



# =========================================================
# PAGE CONFIG 
# =========================================================
st.set_page_config(
    page_title="Performance Monitoring Summary",
    layout="wide"
)
# =========================================================

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
# =========================================================
# PDF Report Builder
# =========================================================
# =========================================================
# PDF Export (SUMMARY ONLY TEST)
# =========================================================
st.markdown("---")
st.subheader("📄 Export Report")

# ✅ Build summary content manually (matches page)


summary_blocks = [

    {"type": "text", "content": "This session provides a baseline snapshot of your push profile. Repeat testing every 6–8 weeks to monitor progression toward LA 2028."},

    {"type": "divider"},

    {"type": "heading", "content": "Key Performance Insight"},

    {"type": "text", "content": "Your speed is driven by effective pushing, not just cycle frequency."},

    {"type": "success", "content": "✅ Fastest rep decided in the first 10 m — 0.04 s quicker, driven by higher frequency."},

    {"type": "divider"},

    {"type": "heading", "content": "Opportunities"},

    {"type": "info", "content": "1️⃣ Maximise the first 10 m — focus on explosive high-frequency start."},

    {"type": "info", "content": "2️⃣ Maintain full push length — avoid shortening late in the cycle."},

    {"type": "info", "content": "3️⃣ Investigate asymmetry across strength, range of motion and setup."},

    {"type": "divider"},

    {"type": "heading", "content": "Recommendations"},

    {"type": "text", "content": "• Re-test every 6–8 weeks"},
    {"type": "text", "content": "• Extend testing beyond 60 m"},
    {"type": "text", "content": "• Ensure full recovery between reps"},
]



if st.button("📄 Generate Summary PDF"):

    pdf_path = create_full_report(summary_blocks)

    with open(pdf_path, "rb") as f:
        pdf_data = f.read()

    st.download_button(
        label="⬇️ Download PDF",
        data=pdf_data,
        file_name="performance_summary.pdf",
        mime="application/pdf"
    )