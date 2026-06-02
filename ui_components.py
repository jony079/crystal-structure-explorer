# ui_components.py
"""Reusable Streamlit UI components for the Crystal Visualizer.

All visual elements are encapsulated here to keep `main.py` focused on
application flow and state management.
"""
import streamlit as st
from typing import Dict, List, Tuple
import config  # the unified config module


# ---------------------------------------------------------------------------
# Helper to inject the custom CSS defined in ``config.py``
# ---------------------------------------------------------------------------
def inject_css(css: str) -> None:
    """Inject a raw CSS string into the Streamlit page."""
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar – user input controls
# ---------------------------------------------------------------------------
def sidebar_controls(cfg) -> Dict:
    """Render the sidebar widgets and return a dictionary of parameters.

    Values are stored in ``st.session_state`` so they survive Streamlit reruns.
    """
    with st.sidebar:
        st.title("🔧 Settings")
        lattice_type = st.selectbox(
            "Lattice type",
            options=list(cfg.LATTICE_TYPES.keys()),
            format_func=lambda k: cfg.LATTICE_TYPES[k],
        )

        # Load defaults for the selected lattice
        defaults = cfg.DEFAULT_PARAMS.copy()
        defaults["lattice_type"] = lattice_type

        a = st.number_input("a (Å)", min_value=0.1, value=float(defaults["a"]))
        b = st.number_input("b (Å)", min_value=0.1, value=float(defaults["b"]))
        c = st.number_input("c (Å)", min_value=0.1, value=float(defaults["c"]))
        alpha = st.number_input("α (°)", min_value=0.0, max_value=180.0, value=float(defaults["alpha"]))
        beta = st.number_input("β (°)", min_value=0.0, max_value=180.0, value=float(defaults["beta"]))
        gamma = st.number_input("γ (°)", min_value=0.0, max_value=180.0, value=float(defaults["gamma"]))

        st.caption(
            "All inputs are cached; changing any value recomputes the heavy calculations only when necessary."
        )

        params = {
            "lattice_type": lattice_type,
            "a": a,
            "b": b,
            "c": c,
            "alpha": alpha,
            "beta": beta,
            "gamma": gamma,
        }

        # Persist for other modules
        st.session_state["params"] = params
        return params


# ---------------------------------------------------------------------------
# KPI cards – a compact grid of key metrics
# ---------------------------------------------------------------------------
def kpi_grid(kpis: Dict) -> None:
    """Render a responsive grid of KPI cards.

    ``kpis`` mapping: label → (value, unit, colour)
    """
    cols = st.columns(len(kpis))
    for col, (label, (value, unit, colour)) in zip(cols, kpis.items()):
        with col:
            st.markdown(
                f"""
                <div class='kpi-card'>
                  <div class='kpi-label'>{label}</div>
                  <div class='kpi-value' style='color:{colour}'>{value}</div>
                  <div class='kpi-unit'>{unit}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# 3‑D visualisation placeholder (the real rendering uses ``py3Dmol``)
# ---------------------------------------------------------------------------
def render_3d(atoms: List[Tuple[float, float, float]]) -> None:
    """Render atom coordinates with an interactive 3‑D viewer."""
    import py3Dmol

    view = py3Dmol.view(width=600, height=400)
    for x, y, z in atoms:
        view.addSphere(
            {"center": {"x": x, "y": y, "z": z}, "radius": 0.3, "color": "#ff6f61"}
        )
    view.zoomTo()
    view.render()
    html = view._make_html()
    st.components.v1.html(html, height=420)


# ---------------------------------------------------------------------------
# XRD plot using Altair (lightweight and interactive)
# ---------------------------------------------------------------------------
def render_xrd(peaks: List[Tuple[float, float, float]]) -> None:
    """Render an X‑ray diffraction pattern."""
    import altair as alt
    import pandas as pd

    df = pd.DataFrame(peaks, columns=["TwoTheta", "Intensity", "d"])
    chart = (
        alt.Chart(df)
        .mark_bar(color=config.ACCENT_COLOR)
        .encode(x=alt.X("TwoTheta:Q", title="2θ (deg)"), y=alt.Y("Intensity:Q", title="Intensity"))
        .properties(width=700, height=300)
    )
    st.altair_chart(chart, use_container_width=True)


# ---------------------------------------------------------------------------
# Assemble the full layout for the "Explore" tab
# ---------------------------------------------------------------------------
def explore_tab(params: Dict, physics, cfg) -> None:
    """Compose the UI for the main exploration tab."""
    atoms, volume = st.session_state.get("lattice_data", ([], 0.0))

    from cache import cached

    @cached
    def compute_kpis(p):
        n_atoms = len(atoms)
        apf_val = physics.apf(p)
        packing = physics.packing_fraction(p)
        return {
            "Atoms / Unit Cell": (n_atoms, "atoms", cfg.ACCENT_COLOR),
            "Unit‑Cell Volume": (f"{volume:.4f}", "Å³", cfg.PRIMARY_COLOR),
            "APF": (f"{apf_val:.4f}", "", cfg.ACCENT_COLOR),
            "Packing": (f"{packing:.2%}", "", cfg.ACCENT_COLOR),
        }

    kpis = compute_kpis(params)
    kpi_grid(kpis)
    st.divider()
    st.subheader("3‑D Structure")
    render_3d(atoms)
    st.divider()
    st.subheader("Simulated XRD Pattern")
    peaks = physics.simulate_xrd(params)
    render_xrd(peaks)


# ---------------------------------------------------------------------------
# Helper to display the about / info tab
# ---------------------------------------------------------------------------
def about_tab() -> None:
    st.markdown(
        """
        ### 📚 About this app
        * Visualise crystal lattices and simulate X‑ray diffraction patterns.  
        * Built with **Streamlit**, **py3Dmol**, **Altair**, and a fully cached physics engine.  
        * Designed for educational use and quick prototyping of crystal structures.  
        """
    )
