# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 18:35:20 2026

@author: Caroline Adams
"""

from pathlib import Path
import streamlit as st

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
logo_path = Path(__file__).resolve().parent / "images" / "Logo.png"

if logo_path.exists():
    st.image(str(logo_path), width=380)
else:
    st.error(f"Logo not found at: {logo_path}")

# =========================================================
# TITLE
# =========================================================
st.title("🏁 Wheelchair Racing Performance Monitoring Report")

st.markdown("---")

# =========================================================
# HERO INSIGHT (NEW - this makes it pop)
# =========================================================
st.info(
    "🎯 **Track your propulsion performance, understand how you move, and identify where to improve.**"
)

# =========================================================
# INTRO (TIGHTENED + CLEAN)
# =========================================================
st.markdown(
    """
This report combines **track sprint testing** and **lab-based ergometer analysis**  
to give you a clear picture of your current performance.

It provides:
- A **baseline snapshot** of your propulsion  
- Insight into **how you generate speed**  
- Clear **opportunities for improvement**

Testing will be repeated throughout the season to track your progress over time.
"""
)

# =========================================================
# NAVIGATION GUIDANCE (VISUAL)
# =========================================================
st.markdown("### 📂 Explore your report")

col1, col2, col3 = st.columns(3)

with col1:
    st.success("📊 Track Testing\n\nView sprint performance across reps")

with col2:
    st.success("🔎 Lab Testing\n\nExplore push mechanics and symmetry")

with col3:
    st.success("🎯 Summary\n\nKey findings and coaching priorities")

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# NAV PROMPT
# =========================================================
st.caption("Use the menu on the left to navigate between sections of your report.")


# # =========================================================
# # PAGE CONFIG  
# # =========================================================
# st.set_page_config(
#     page_title="Wheelchair Racing\ Performance Monitoring Report",
#     layout="wide"   # forces left-aligned layout
# )

# # =========================================================
# # LOGO (LEFT-ALIGNED)
# # =========================================================
# logo_path = Path(__file__).resolve().parent / "images" / "Logo.png"

# if logo_path.exists():
#     st.image(
#         str(logo_path),
#         width=400
#     )
# else:
#     st.error(f"Logo not found at: {logo_path}")

# # =========================================================
# # TITLE AND SUBTITLE
# # =========================================================
# st.title("Wheelchair Racing Performance Monitoring Report")

# # =========================================================
# # DIVIDER
# # =========================================================
# st.markdown("---")

# # =========================================================
# # INTRO TEXT
# # =========================================================
# st.write(
#     """
#     This report provides feedback and highlights performance opportunities 
#     for wheelchair racing athletes based on track and laboratory performance monitroing. 
#     This report presents your baseline values, a snapshot in time of where you are now and we will continue to test 
#     thorughout the sesason to monitor change.
#     """
# )

# st.write("Use the menu on the left to move between pages.")