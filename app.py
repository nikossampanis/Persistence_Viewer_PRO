import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from ripser import ripser
from persim import plot_diagrams
import time
import io

st.set_page_config(page_title="Persistence Viewer PRO", page_icon="🎮", layout="wide")

# Sidebar: Dataset selection
st.sidebar.title("🧪 Dataset Selection")
dataset = st.sidebar.selectbox("Choose a demo dataset or upload your own CSV:", 
                                ["demo2d.csv", "demo3d.csv", "Upload CSV"])

uploaded_file = None
if dataset == "Upload CSV":
    uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

# Initialize radius in session state
if 'radius' not in st.session_state:
    st.session_state['radius'] = 0.05

# Sidebar controls
st.sidebar.markdown("---")
radius_slider = st.sidebar.slider("Filtration Radius", 0.01, 1.0,
                                   st.session_state['radius'], 0.01)
st.session_state['radius'] = radius_slider  # update session
autoplay = st.sidebar.checkbox("▶️ Auto-play")
show_h0 = st.sidebar.checkbox("Show H₀ (Connected)", value=True)
show_h1 = st.sidebar.checkbox("Show 🟠 H₁ (Loops)", value=True)
show_h2 = st.sidebar.checkbox("Show H₂ (Voids)", value=True)
st.sidebar.markdown("---")
st.sidebar.markdown("Developed by **Nikolaos Sampanis**")
st.sidebar.markdown("🧠 Learn topology through animation!")

# Load data
@st.cache_data
def load_demo(name):
    if name == "demo2d.csv":
        return np.array([[0.1,0.2],[0.3,0.8],[0.6,0.1],[0.9,0.5],[0.4,0.4],[0.2,0.9]])
    elif name == "demo3d.csv":
        return np.array([[0.1,0.2,0.3],[0.4,0.6,0.2],[0.5,0.8,0.7],[0.9,0.3,0.5],[0.2,0.7,0.9],[0.8,0.5,0.4]])

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file, header=None).values
else:
    data = load_demo(dataset)

dim = data.shape[1]
st.subheader("🔍 Input Point Cloud")
st.write(f"Dimension: {dim}D — Points: {len(data)}")
st.dataframe(pd.DataFrame(data), height=150)

# Visualization: Geometric growth
st.subheader("📈 Geometric Growth")
fig = go.Figure()
if dim == 2:
    for i, p in enumerate(data):
        fig.add_trace(go.Scatter(x=[p[0]], y=[p[1]], mode='markers', marker=dict(size=6), name=f"P{i+1}"))
        fig.add_shape(type="circle",
                      xref="x", yref="y",
                      x0=p[0]-radius_slider, y0=p[1]-radius_slider,
                      x1=p[0]+radius_slider, y1=p[1]+radius_slider,
                      line_color="LightSkyBlue", opacity=0.5)
    fig.update_layout(width=500, height=500)
    st.plotly_chart(fig, use_container_width=True)
elif dim == 3:
    fig3d = go.Figure()
    for p in data:
        fig3d.add_trace(go.Scatter3d(x=[p[0]], y=[p[1]], z=[p[2]],
                                     mode='markers', marker=dict(size=3)))
    fig3d.update_layout(scene=dict(aspectmode='data'), width=500, height=500)
    st.plotly_chart(fig3d, use_container_width=True)
else:
    st.error("Only 2D or 3D point clouds are supported.")

# Persistence diagram
st.subheader("🔬 Persistence Diagram")
rips = ripser(data, maxdim=2, thresh=2*radius_slider)
dgms = rips['dgms']

fig2, ax = plt.subplots()
labels = ['H₀', 'H₁', 'H₂']
for i, dgm in enumerate(dgms):
    if (i == 0 and show_h0) or (i == 1 and show_h1) or (i == 2 and show_h2):
        plot_diagrams([dgm], ax=ax, show=False, lifetime=True, xy_range=[0,1,0,1])
ax.set_title("Persistence Diagram")
buf = io.BytesIO()
fig2.savefig(buf, format="png")
st.image(buf)

# Auto-play animation
if autoplay:
    for r in np.arange(0.01, 1.01, 0.05):
        st.session_state['radius'] = r
        time.sleep(0.4)
        st.experimental_rerun()
