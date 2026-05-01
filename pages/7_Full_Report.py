import streamlit as st

# ✅ Import your PDF-ready pages
from pages.1_Athlete_profile_PDF_ready import render as render_profile
from pages.3_60m_Comparison_pdf_ready import render as render_track

# -------------------------------------------------------
# Page setup
# -------------------------------------------------------
st.set_page_config(layout="wide")

# -------------------------------------------------------
# Print styling
# -------------------------------------------------------
st.markdown("""
<style>
@media print {
    header, footer, .stToolbar {
        display: none !important;
    }

    /* Keep sections together */
    .stAlert {
        page-break-inside: avoid !important;
    }

    /* Force expanders open */
    details {
        display: block !important;
    }
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# Title
# -------------------------------------------------------
st.title("Full Performance Report")

st.info("""
📄 Export this report:
→ Press Ctrl + P  
→ Select "Save as PDF"  
→ Enable background graphics ✅
""")

# -------------------------------------------------------
# 1. ATHLETE PROFILE
# -------------------------------------------------------
render_profile(pdf_mode=True)

st.markdown(
    '<div style="page-break-before: always;"></div>',
    unsafe_allow_html=True
)

# -------------------------------------------------------
# 2. 60M COMPARISON
# -------------------------------------------------------
render_track(pdf_mode=True)