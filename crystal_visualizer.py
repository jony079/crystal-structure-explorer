import streamlit as st
import math
import physics_engine as phys
import ui_components as ui

# 1. Page Configuration (Wide Layout)
st.set_page_config(page_title="Cubic Crystal Visualizer", page_icon="⚛️", layout="wide")

st.title("⚛️ Crystal Structure & XRD Simulator")
st.markdown("Interactive visualization of crystal lattices, parameters, and X-ray Diffraction (XRD) peaks.")
st.markdown("---")

# 2. Sidebar Controls
PRESETS = {
    "Custom":              {"type": "FCC", "a": 4.05, "c": None},
    "Aluminum (Al) – FCC": {"type": "FCC", "a": 4.05, "c": None},
    "Copper (Cu) – FCC":   {"type": "FCC", "a": 3.61, "c": None},
    "Gold (Au) – FCC":     {"type": "FCC", "a": 4.08, "c": None},
    "Iron α (Fe) – BCC":   {"type": "BCC", "a": 2.87, "c": None},
    "Chromium (Cr) – BCC": {"type": "BCC", "a": 2.88, "c": None},
    "Polonium (Po) – SC":  {"type": "SC",  "a": 3.35, "c": None},
    "Titanium (Ti) – HCP": {"type": "HCP", "a": 2.95, "c": 4.68},
    "Magnesium (Mg) – HCP":{"type": "HCP", "a": 3.21, "c": 5.21},
}

st.sidebar.header("⚙️ Controls")
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

st.sidebar.subheader("Miller Indices (hkl)")
hkl_cols = st.sidebar.columns(3)
with hkl_cols[0]: h = st.number_input("h", -5, 5, 1, 1)
with hkl_cols[1]: k = st.number_input("k", -5, 5, 1, 1)
with hkl_cols[2]: l = st.number_input("l", -5, 5, 0, 1)

atom_scale = st.sidebar.slider("Atom scale size", 0.05, 0.55, 0.18, 0.01)
xrd_lambda = st.sidebar.number_input("X-ray wavelength λ (Å)", 0.5, 3.0, 1.5406, 0.0001)

if h == 0 and k == 0 and l == 0:
    st.sidebar.error("Miller Indices cannot all be zero.")
    st.stop()

# 3. Backend Calculations
d = phys.d_spacing(a_val, h, k, l, crystal_type=ctype, c=c_val)
r = phys.atomic_radius(a_val, ctype, c=c_val)
apf = {"SC": 0.524, "BCC": 0.68, "FCC": 0.74, "HCP": 0.74}[ctype]
cn = {"SC": 6, "BCC": 8, "FCC": 12, "HCP": 12}[ctype]
n_atoms = {"SC": 1, "BCC": 2, "FCC": 4, "HCP": 6}[ctype]
F_sq, F_rel, F_rule = phys.structure_factor(ctype, h, k, l)

# 4. Main UI Layout (Two Columns)
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("🔮 3D Crystal Lattice")
    pts, cats = phys.get_lattice_points(ctype, a_val, c_val)
    fig3d = ui.draw_crystal_plot(ctype, pts, cats, atom_scale, c_val, a_val)
    st.plotly_chart(fig3d, use_container_width=True)

with col2:
    st.subheader("📐 Crystal Parameters")
    
    # Using Streamlit Native Metrics for a clean, professional look
    m1, m2 = st.columns(2)
    m1.metric(label="Interplanar Spacing (d)", value=f"{d:.4f} Å" if d else "N/A")
    m2.metric(label="Atomic Radius (r)", value=f"{r:.4f} Å")
    
    m3, m4 = st.columns(2)
    m3.metric(label="Atomic Packing Factor", value=f"{apf*100:.1f}%")
    m4.metric(label="Coordination Number", value=f"{cn}")
    
    st.metric(label="Atoms per Unit Cell", value=f"{n_atoms}")
    
    st.markdown("---")
    st.subheader("⚡ Bragg Analysis & Structure Factor")
    
    if d and d > 0:
        sinT = xrd_lambda / (2*d)
        if 0 < sinT <= 1:
            st.info(f"📍 **Bragg Peak Location 2θ:** {2 * math.degrees(math.asin(sinT)):.3f}°")

    if F_rel < 0.01:
        st.error(f"🚫 **Forbidden reflection:** {F_rule}")
    else:
        st.success(f"✅ **Allowed reflection:** {F_rule}")

# 5. XRD Pattern Section
st.markdown("---")
st.subheader("📡 Simulated XRD Pattern")

peaks = phys.generate_xrd_peaks_cached(ctype, a_val, xrd_lambda, 90, c=c_val)
if peaks:
    # Render Plotly Graph
    fig_xrd = ui.draw_xrd_plot(peaks)
    st.plotly_chart(fig_xrd, use_container_width=True)
    
    # Render Data Table
    st.markdown("**Peak Intensity Data Table**")
    st.dataframe(
        peaks, 
        column_config={
            "0": "2-Theta (Degrees)", 
            "1": "Relative Intensity (%)", 
            "2": "Planes (hkl)"
        }, 
        use_container_width=True
    )
