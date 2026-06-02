"""
=============================================================================
  UI & Plotly Visualization Components
  Manages styling blueprints, 3D structure layout meshes, and XRD charts.
=============================================================================
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import math

def inject_premium_css():
    """Injects high-end engineering stylesheet UI rules."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: #080c14; color: #cbd5e1; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0f1520 0%, #0a0f1a 100%); border-right: 1px solid #1e293b; }
    h1 { font-family: 'Outfit', sans-serif; font-weight: 800; background: linear-gradient(135deg, #00f2fe 0%, #4facfe 50%, #a855f7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-size: 2.1rem !important; }
    .kpi-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 18px; }
    .kpi-card { background: linear-gradient(135deg, rgba(14,165,233,0.08) 0%, rgba(99,102,241,0.08) 100%); border: 1px solid rgba(99,102,241,0.25); border-radius: 14px; padding: 18px 16px; }
    .kpi-label { font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 6px; }
    .kpi-value { font-family: 'Outfit', sans-serif; font-size: 1.7rem; font-weight: 700; color: #00f2fe; }
    .kpi-unit  { font-size: 0.8rem; color: #475569; margin-top: 3px; }
    .info-pill { background: rgba(14,165,233,0.1); border-left: 3px solid #0ea5e9; border-radius: 0 8px 8px 0; padding: 10px 14px; font-size: 0.88rem; color: #94a3b8; margin-bottom: 16px; }
    .perf-hud { background: rgba(16, 185, 129, 0.06); border: 1px dashed rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 6px 12px; font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #34d399; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)


def render_kpi_dashboard(d, r, apf, cn, n_atoms, cpd):
    """Renders data metrics visually on screen."""
    st.markdown("""
    <div class='kpi-grid'>
      <div class='kpi-card'><div class='kpi-label'>Interplanar Spacing d<sub>hkl</sub></div><div class='kpi-value'>{d:.4f}</div><div class='kpi-unit'>Angstroms (Å)</div></div>
      <div class='kpi-card'><div class='kpi-label'>Atomic Radius r</div><div class='kpi-value'>{r:.4f}</div><div class='kpi-unit'>Angstroms (Å)</div></div>
      <div class='kpi-card'><div class='kpi-label'>Packing Factor (APF)</div><div class='kpi-value'>{apf:.4f}</div><div class='kpi-unit'>{apf_pct:.1f}% filled</div></div>
    </div>
    <div class='kpi-grid'>
      <div class='kpi-card'><div class='kpi-label'>Coordination Number</div><div class='kpi-value' style='color:#a855f7'>{cn}</div><div class='kpi-unit'>Nearest neighbours</div></div>
      <div class='kpi-card'><div class='kpi-label'>Atoms / Unit Cell</div><div class='kpi-value' style='color:#f97316'>{n_atoms}</div><div class='kpi-unit'>Effective count</div></div>
      <div class='kpi-card'><div class='kpi-label'>Close-Packed Direction</div><div class='kpi-value' style='color:#10b981;font-size:1.4rem'>{cpd}</div><div class='kpi-unit'>Max linear density</div></div>
    </div>
    """.format(d=d if d else 0, r=r, apf=apf, apf_pct=apf*100, cn=cn, n_atoms=n_atoms, cpd=cpd), unsafe_allow_html=True)


def draw_crystal_plot(ctype, pts, cats, atom_scale, c_val=None, a_val=1.0):
    """Generates the interactive Plotly 3D scatter/mesh diagram."""
    fig3d = go.Figure()
    
    if ctype != "HCP":
        ex, ey, ez = [], [], []
        for yv in [0,1]:
            for zv in [0,1]: ex += [0, 1, None]; ey += [yv,yv,None]; ez += [zv,zv,None]
        for xv in [0,1]:
            for zv in [0,1]: ex += [xv,xv,None]; ey += [0,1,None]; ez += [zv,zv,None]
        for xv in [0,1]:
            for yv in [0,1]: ex += [xv,xv,None]; ey += [yv,yv,None]; ez += [0,1,None]
        fig3d.add_trace(go.Scatter3d(x=ex, y=ey, z=ez, mode='lines', line=dict(color='#334155', width=3), name='Unit Cell'))
    else:
        c_r = (c_val or a_val*1.633) / a_val
        angles_hex = [math.radians(i*60) for i in range(6)]
        hex_x = [math.cos(a_) for a_ in angles_hex]
        hex_y = [math.sin(a_) for a_ in angles_hex]
        ex, ey, ez = [], [], []
        for i in range(6):
            ex += [hex_x[i], hex_x[(i+1)%6], None]; ey += [hex_y[i], hex_y[(i+1)%6], None]; ez += [0, 0, None]
            ex += [hex_x[i], hex_x[(i+1)%6], None]; ey += [hex_y[i], hex_y[(i+1)%6], None]; ez += [c_r, c_r, None]
            ex += [hex_x[i], hex_x[i], None]; ey += [hex_y[i], hex_y[i], None]; ez += [0, c_r, None]
        fig3d.add_trace(go.Scatter3d(x=ex, y=ey, z=ez, mode='lines', line=dict(color='#334155', width=3), name='HCP Prism'))

    COLOR_MAP = {
        "Corner": ("#94a3b8", "Corner"), "Body Center": ("#f97316", "Body Center"), 
        "Face Center": ("#06b6d4", "Face Center"), "HCP Base": ("#94a3b8", "HCP Base"), 
        "HCP Top": ("#38bdf8", "HCP Top"), "HCP Mid": ("#f59e0b", "HCP Mid")
    }
    
    for cat_key, (col, lbl) in COLOR_MAP.items():
        mask = [c == cat_key for c in cats]
        sel = pts[mask]
        if len(sel) > 0:
            fig3d.add_trace(go.Scatter3d(x=sel[:,0], y=sel[:,1], z=sel[:,2], mode='markers', marker=dict(size=atom_scale*130, color=col, opacity=0.9), name=lbl))

    fig3d.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,b=0,t=0), height=500, scene=dict(aspectmode='cube'))
    return fig3d
