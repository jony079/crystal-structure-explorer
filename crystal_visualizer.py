"""
=============================================================================
  Main Executable File ─ Crystal Structure Explorer
  Combines UI layout elements with high-speed backend calculation engines.
=============================================================================
"""

import streamlit as st
import math
import time

# মডুলার আর্কিটেকচার ইমপোর্ট (Abstraction boundary)
import physics_engine as phys
import ui_components as ui

# 1. Start core runtime instrumentation hook (Observability)
start_runtime = time.perf_counter()

# Page UI configurations
ui.inject_premium_css()

st.markdown("# ⚛️ Crystal Structure Explorer")
st.markdown("<div class='info-pill'>Modularized High-Performance Engine for Crystallography Mapping.</div>", unsafe_allow_html=True)

# Presets Management Configuration
PRESETS = {
    "Custom":              {"type": "FCC", "a": 4.05, "c": None},
    "Aluminum (Al) – FCC": {"type": "FCC", "a": 4.05, "c": None},
    "Copper (Cu) – FCC":   {"type": "FCC", "a": 3.61, "c": None},
    "Gold (Au) – FCC":     {"type": "FCC", "a": 4.08, "c": None},
    "Iron α (Fe) – BCC":  {"type": "BCC", "a": 2.87, "c": None},
    "Chromium (Cr) – BCC": {"type": "BCC", "a": 2.88, "c": None},
    "Polonium (Po) – SC":  {"type": "SC",  "a": 3.35, "c": None},
    "Titanium (Ti) – HCP": {"type": "HCP", "a": 2.95, "c": 4.68},
    "Magnesium (Mg) – HCP":{"type": "HCP", "a": 3.21, "c": 5.21},
}

st.sidebar.markdown("## 🔬 Controls")
preset = st.sidebar.selectbox("Element Preset", list(PRESETS.keys()))
P = PRESETS[preset]
locked = (preset != "Custom")

TYPES = ["SC", "BCC", "FCC", "HCP"]
ctype = st.sidebar.radio("Crystal Type", TYPES, index=TYPES.index(P["type"]), disabled=locked)

a_val = st.sidebar.number_input("Lattice parameter a (Å)", 0.5, 20.0, float(P["a"]), 0.01, disabled=locked)
c_val = None
if ctype == "HCP":
    c_default = float(P["c"]) if P["c"] else round(a_val * 1.633, 3)
    c_val = st.sidebar.number_input("Lattice parameter c (Å)", 0.5, 30.0, c_default, 0.01, disabled=locked)

# Miller Indices inputs
st.sidebar.markdown("### Miller Indices (hkl)")
hkl_cols = st.sidebar.columns(3)
with hkl_cols[0]: h = st.number_input("h", -5, 5, 1, 1)
with hkl_cols[1]: k = st.number_input("k", -5, 5, 1, 1)
with hkl_cols[2]: l = st.number_input("l", -5, 5, 0, 1)

atom_scale = st.sidebar.slider("Atom scale size", 0.05, 0.55, 0.18, 0.01)
xrd_lambda = st.sidebar.number_input("X-ray wavelength λ (Å)", 0.5, 3.0, 1.5406, 0.0001)

if h == 0 and k == 0 and l == 0:
    st.error("⚠️ Miller Indices cannot all be zero.")
    st.stop()

# 2. Pipeline Computing Execution calls
d = phys.d_spacing(a_val, h, k, l, crystal_type=ctype, c=c_val)
r = phys.atomic_radius(a_val, ctype, c=c_val)
apf = {"SC": 0.524, "BCC": 0.68, "FCC": 0.74, "HCP": 0.74}[ctype]
cn = {"SC": 6, "BCC": 8, "FCC": 12, "HCP": 12}[ctype]
cpd = {"SC": "[100]", "BCC": "[111]", "FCC": "[110]", "HCP": "[11̄20]"}[ctype]
n_atoms = {"SC": 1, "BCC": 2, "FCC": 4, "HCP": 6}[ctype]
F_sq, F_rel, F_rule = phys.structure_factor(ctype, h, k, l)

# Render KPI Grid Layout Dashboard
ui.render_kpi_dashboard(d, r, apf, cn, n_atoms, cpd)

tabs = st.tabs(["🔮 3D Structure", "📐 Calculations", "📡 XRD Simulator", "⚡ Structure Factor Rules"])

with tabs[0]:
    st.markdown("## 3D Unit Cell Mapping")
    pts, cats = phys.get_lattice_points(ctype, a_val, c_val)
    fig3d = ui.draw_crystal_plot(ctype, pts, cats, atom_scale, c_val, a_val)
    st.plotly_chart(fig3d, use_container_width=True)

with tabs[1]:
    st.markdown("## Calculation & Bragg Analysis")
    st.latex(rf"d_{{{h}{k}{l}}} = {d:.4f}\,\text{{Å}}")
    if d and d > 0:
        sinT = xrd_lambda / (2*d)
        if 0 < sinT <= 1:
            st.success(f"✅ Bragg Peak Location 2θ: {2 * math.degrees(math.asin(sinT)):.3f}°")

with tabs[2]:
    st.markdown("## High-Performance XRD Peaks (Memoized Lookup)")
    peaks = phys.generate_xrd_peaks_cached(ctype, a_val, xrd_lambda, 90, c=c_val)
    if peaks:
        st.dataframe(peaks, column_config={"0": "2-Theta", "1": "Relative Intensity (%)", "2": "Reflecting Planes"})

with tabs[3]:
    st.markdown("## Geometrical Structure Factor Status")
    if F_rel < 0.01:
        st.error(f"🚫 Forbidden reflection: {F_rule}")
    else:
        st.success(f"✅ Allowed reflection: {F_rule}")

# 3. Terminate Runtime profiling trace (Observability)
runtime_duration = (time.perf_counter() - start_runtime) * 1000

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Engine Observability")
st.sidebar.markdown(f"""
<div class='perf-hud'>
⚙️ Compute Hook: {runtime_duration:.2f} ms<br>
💾 Cache Framework: Active (Isolated)<br>
🛡️ Abstraction Leak: Resolved
</div>
""", unsafe_allow_html=True)
