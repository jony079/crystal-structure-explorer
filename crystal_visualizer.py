# main.py
"""Streamlit entry point for the Crystal Structure Explorer.

Keeps UI thin: imports ``ui_components`` for layout, ``physics_engine`` for the
calculations, and ``config`` for constants. Session state stores the generated
lattice data so that heavy geometry is computed only when parameters change.
"""
import streamlit as st
from config import APP_TITLE, PAGE_ICON, load_css, THEME, DEFAULT_PARAMS
import ui_components as ui
import physics_engine as phy
from cache import cached


# ---------------------------------------------------------------------------
# Streamlit page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=PAGE_ICON,
    layout="centered",
    initial_sidebar_state="expanded",
)
# Inject custom CSS
st.markdown(f"<style>{load_css()}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Helper to compute lattice data only when parameters change (cached)
# ---------------------------------------------------------------------------
@cached
def compute_lattice(params):
    atoms, volume = phy.generate_lattice(params)
    return atoms, volume


# ---------------------------------------------------------------------------
# Main app logic
# ---------------------------------------------------------------------------
def main():
    # Initialise session state defaults (run only once)
    if "params" not in st.session_state:
        st.session_state["params"] = DEFAULT_PARAMS.copy()
    if "lattice_data" not in st.session_state:
        st.session_state["lattice_data"] = ([], 0.0)

    # Sidebar controls – returns the current parameter dict
    params = ui.sidebar_controls(__import__("config"))

    # Re‑compute geometry only when any parameter changed
    atoms, volume = compute_lattice(params)
    st.session_state["lattice_data"] = (atoms, volume)

    # Tab navigation
    explore, info, raw = st.tabs(["Explore", "Info", "Raw Data"])
    with explore:
        ui.explore_tab(params, phy, cfg=__import__("config"))
    with info:
        ui.about_tab()
    with raw:
        st.subheader("Raw lattice coordinates")
        st.write(atoms)
        st.subheader("Unit‑cell volume")
        st.write(f"{volume:.4f} Å³")


if __name__ == "__main__":
    main()
