import streamlit as st

from pages.1_Athlete_profile import render as render_profile
from pages.3_60m_Comparison import render as render_track

st.set_page_config(layout="wide")

# =========================================================
# PRINT STYLING
# =========================================================
st.markdown("""
<style>
@media print {
    header, footer, .stToolbar {
        display: none !important;
    }

    .stAlert {
        page-break-inside: avoid !important;
    }

    details {
        display: block !important;
    }
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================
st.title("Full Performance Report")

st.info("📄 Press Ctrl+P → Save as PDF")

# =========================================================
# ATHLETE PROFILE
# =========================================================
render_profile(pdf_mode=True)

st.markdown('<div style="page-break-before: always;"></div>', unsafe_allow_html=True)

# =========================================================
# TRACK COMPARISON
# =========================================================
render_track(pdf_mode=True)
