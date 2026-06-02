import streamlit as st
import ui_components as ui
import physics_engine as phy
import config

# ১. পেজ কনফিগারেশন সেটআপ (সবার আগে থাকতে হবে)
st.set_page_config(
    page_title=config.APP_TITLE, 
    page_icon=config.PAGE_ICON, 
    layout="wide"
)

# ২. কাস্টম CSS লোড করা (এরর হ্যান্ডলিং সহ, যেন সিএসএস মিস হলেও অ্যাপ ক্র্যাশ না করে)
try:
    st.markdown(f"<style>{config.load_css()}</style>", unsafe_allow_html=True)
except Exception as e:
    st.warning(f"CSS could not be loaded: {e}")

# ৩. ক্রিস্টাল ল্যাটিস কম্পিউটেশন লেয়ার (Streamlit-এর স্ট্যান্ডার্ড ক্যাশিং)
@st.cache_data
def compute_lattice(params):
    atoms, volume = phy.generate_lattice(params)
    return atoms, volume

# ৪. মেইন অ্যাপ লজিক
def main():
    # সেশন স্টেট ইনিশিয়ালাইজেশন (রান হবে মাত্র একবার)
    if "params" not in st.session_state:
        st.session_state["params"] = config.DEFAULT_PARAMS.copy()
    if "lattice_data" not in st.session_state:
        st.session_state["lattice_data"] = ([], 0.0)
    
    # সাইডবার কন্ট্রোলস (TypeError থেকে বাঁচতে বুলেটপ্রুফ ট্রাই-ক্যাচ)
    try:
        params = ui.sidebar_controls(config)
    except TypeError:
        try:
            params = ui.sidebar_controls()
        except TypeError:
            params = ui.sidebar_controls(__import__("config"))
    
    # প্যারামিটার চেঞ্জ হলে রি-কম্পিউট করা
    atoms, volume = compute_lattice(params)
    st.session_state["lattice_data"] = (atoms, volume)
    
    # ট্যাব নেভিগেশন
    explore, info, raw = st.tabs(["Explore", "Info", "Raw Data"])
    
    with explore:
        try:
            ui.explore_tab(params, phy, config)
        except TypeError:
            ui.explore_tab(params, phy)
            
    with info:
        try:
            ui.about_tab()
        except TypeError:
            ui.about_tab(config)
            
    with raw:
        st.subheader("Raw lattice coordinates")
        st.write(atoms)
        st.subheader("Unit‑cell volume")
        st.write(f"{volume:.4f} Å³")

if __name__ == "__main__":
    main()
