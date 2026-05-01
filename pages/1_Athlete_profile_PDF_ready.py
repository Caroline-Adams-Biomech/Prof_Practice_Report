# =========================================================
# Athlete Profile Page
# =========================================================
from pathlib import Path
import streamlit as st

def render(pdf_mode=False):

    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    profile_path = PROJECT_ROOT / "images" / "athlete_profile.png"

    st.title("Athlete Profile")
    st.markdown("<hr>", unsafe_allow_html=True)

    if profile_path.exists():
        st.image(str(profile_path), width=800)
    else:
        st.warning(f"Athlete profile image not found at: {profile_path}")


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    render(pdf_mode=False)
``