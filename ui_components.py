import streamlit as st
import plotly.graph_objects as go
import numpy as np
import math

def inject_premium_css():
    """Injects core layout adjustments and performance HUD styling."""
    st.markdown("""
    <style>
    .perf-hud { 
        background-color: #f0fdf4; 
        border: 1px dashed #16a34a; 
        border-radius: 8px; 
        padding: 10px; 
        font-family: monospace; 
        font-size: 0.85rem; 
        color: #16a34a; 
        margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

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
        fig3d.add_trace(go.Scatter3d(x=ex, y=ey, z=ez, mode='lines', line=dict(color='gray', width=3), name='Unit Cell'))
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
        fig3d.add_trace(go.Scatter3d(x=ex, y=ey, z=ez, mode='lines', line=dict(color='gray', width=3), name='HCP Prism'))

    COLOR_MAP = {
        "Corner": ("blue", "Corner"), "Body Center": ("orange", "Body Center"), 
        "Face Center": ("green", "Face Center"), "HCP Base": ("blue", "HCP Base"), 
        "HCP Top": ("cyan", "HCP Top"), "HCP Mid": ("red", "HCP Mid")
    }
    
    for cat_key, (col, lbl) in COLOR_MAP.items():
        mask = [c == cat_key for c in cats]
        sel = pts[mask]
        if len(sel) > 0:
            fig3d.add_trace(go.Scatter3d(x=sel[:,0], y=sel[:,1], z=sel[:,2], mode='markers', marker=dict(size=atom_scale*130, color=col, opacity=0.8), name=lbl))

    fig3d.update_layout(margin=dict(l=0,r=0,b=0,t=0), height=500, scene=dict(aspectmode='cube'))
    return fig3d

def draw_xrd_plot(peaks):
    """Generates the standard continuous XRD 2-Theta Spectrum intensity chart."""
    fig_xrd = go.Figure()
    x_val = np.linspace(10, 90, 800)
    y_val = np.zeros_like(x_val)
    
    for p in peaks:
        two_theta = p[0]
        intensity = p[1]
        planes = p[2]
        y_val += intensity * np.exp(-0.5 * ((x_val - two_theta) / 0.4)**2)
        fig_xrd.add_annotation(x=two_theta, y=intensity+3, text=planes, showarrow=False, font=dict(size=10))

    fig_xrd.add_trace(go.Scatter(x=x_val, y=y_val, mode='lines', line=dict(color='red', width=2), name='XRD Spectrum'))
    fig_xrd.update_layout(
        xaxis=dict(title="2-Theta (2θ) / Degrees"),
        yaxis=dict(title="Relative Intensity (%)", range=[0, 115]),
        margin=dict(l=40, r=20, t=30, b=40),
        height=400
    )
    return fig_xrd
