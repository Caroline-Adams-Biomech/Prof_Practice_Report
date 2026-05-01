from pathlib import Path
import streamlit as st


def render(pdf_mode=False):

    base_path = Path(__file__).resolve().parents[1]
    profile_path = base_path / "images" / "athlete_profile.png"

    st.title("Athlete Profile")
    st.markdown("---")

    if profile_path.exists():
        st.image(str(profile_path), width=800)
    else:
        st.warning("Profile image not found")


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    render(pdf_mode=False)