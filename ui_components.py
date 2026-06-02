import plotly.graph_objects as go
import numpy as np
import math

def draw_crystal_plot(ctype, pts, cats, atom_scale, c_val=None, a_val=1.0):
    fig3d = go.Figure()
    
    # Unit Cell Lines (Clean gray lines)
    if ctype != "HCP":
        ex, ey, ez = [], [], []
        for yv in [0,1]:
            for zv in [0,1]: ex += [0, 1, None]; ey += [yv,yv,None]; ez += [zv,zv,None]
        for xv in [0,1]:
            for zv in [0,1]: ex += [xv,xv,None]; ey += [0,1,None]; ez += [zv,zv,None]
        for xv in [0,1]:
            for yv in [0,1]: ex += [xv,xv,None]; ey += [yv,yv,None]; ez += [0,1,None]
        fig3d.add_trace(go.Scatter3d(x=ex, y=ey, z=ez, mode='lines', line=dict(color='#888888', width=2), name='Unit Cell'))
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
        fig3d.add_trace(go.Scatter3d(x=ex, y=ey, z=ez, mode='lines', line=dict(color='#888888', width=2), name='HCP Prism'))

    # Atoms with professional color palette
    COLOR_MAP = {
        "Corner": ("#1f77b4", "Corner"), "Body Center": ("#ff7f0e", "Body Center"), 
        "Face Center": ("#2ca02c", "Face Center"), "HCP Base": ("#1f77b4", "HCP Base"), 
        "HCP Top": ("#2ca02c", "HCP Top"), "HCP Mid": ("#d62728", "HCP Mid")
    }
    
    for cat_key, (col, lbl) in COLOR_MAP.items():
        mask = [c == cat_key for c in cats]
        sel = pts[mask]
        if len(sel) > 0:
            fig3d.add_trace(go.Scatter3d(x=sel[:,0], y=sel[:,1], z=sel[:,2], mode='markers', 
                                         marker=dict(size=atom_scale*130, color=col, opacity=0.9, 
                                                     line=dict(color='black', width=1)), name=lbl))

    fig3d.update_layout(margin=dict(l=0,r=0,b=0,t=0), height=550, scene=dict(aspectmode='cube'))
    return fig3d

def draw_xrd_plot(peaks):
    fig_xrd = go.Figure()
    x_val = np.linspace(10, 90, 800)
    y_val = np.zeros_like(x_val)
    
    for p in peaks:
        two_theta = p[0]
        intensity = p[1]
        planes = p[2]
        y_val += intensity * np.exp(-0.5 * ((x_val - two_theta) / 0.4)**2)
        fig_xrd.add_annotation(x=two_theta, y=intensity+4, text=planes, showarrow=False, font=dict(size=11))

    fig_xrd.add_trace(go.Scatter(x=x_val, y=y_val, mode='lines', line=dict(color='#d62728', width=2), name='XRD Spectrum'))
    
    fig_xrd.update_layout(
        xaxis_title="2-Theta (2θ) / Degrees",
        yaxis_title="Relative Intensity (%)",
        yaxis=dict(range=[0, 115]),
        margin=dict(l=40, r=20, t=30, b=40),
        height=450,
        showlegend=False
    )
    return fig_xrd
