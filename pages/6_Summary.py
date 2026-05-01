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
# PRINT + LAYOUT STYLING
# =========================================================
st.markdown("""
<style>

/* =========================================================
GLOBAL PRINT SETTINGS
========================================================= */
@media print {

    header, footer, .stToolbar, .stDeployButton {
        display: none !important;
    }

    .block-container {
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }

    body {
        font-size: 14px !important;
        line-height: 1.5;
    }

    .stAlert {
        page-break-inside: avoid !important;
    }

    h1, h2, h3 {
        page-break-after: avoid;
    }

    .element-container {
        margin-bottom: 15px !important;
    }
}

/* CLEAN LAYOUT */
.block-container {
    max-width: 900px;
    margin: auto;
}

hr {
    margin-top: 30px;
    margin-bottom: 30px;
}

.no-break {
    page-break-inside: avoid;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOGO
# =========================================================
logo_path = Path(__file__).resolve().parents[1] / "images" / "Logo.png"
if logo_path.exists():
    st.image(str(logo_path), width=380)

# =========================================================
# TITLE
# =========================================================
st.title("Performance Monitoring Summary")

# =========================================================
# EXPORT INSTRUCTIONS (REPLACES PDF BUTTON)
# =========================================================
st.info("""
📄 **Export this report as a PDF**

1. Press **Ctrl + P** (Windows) or **Cmd + P** (Mac)  
2. Set Destination = **Save as PDF**  
3. Enable **Background graphics ✅**  
""")

# =========================================================
# BASELINE CONTEXT
# =========================================================
st.markdown("""
This session provides a **baseline snapshot** of your push profile.  
To track meaningful changes, we recommend **repeat testing every 6–8 weeks** to monitor progression across the season and build toward **LA 2028**.
""")

st.markdown("<hr>", unsafe_allow_html=True)

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

st.markdown("<hr>", unsafe_allow_html=True)

# =========================================================
# OPPORTUNITIES (NO BREAK BLOCK)
# =========================================================
st.markdown('<div class="no-break">', unsafe_allow_html=True)

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

Based on multidisciplinary team assessment we can tailor next steps.
""")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# =========================================================
# TESTING RECOMMENDATIONS
# =========================================================
st.markdown("### 💡 Recommendations")

st.markdown("""
- 📅 **Re-test every 6–8 weeks**  
- 📏 **Extend testing beyond 60 m**  
- ⏱ **Ensure full recovery between reps**  
""")