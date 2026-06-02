import streamlit as st
import ui_components as ui
import physics_engine as phy
import config

# ১. পেজ কনফিগারেশন সেটআপ
st.set_page_config(
    page_title=config.APP_TITLE, 
    page_icon=config.PAGE_ICON, 
    layout="wide"
)

# ২. কাস্টম CSS লোড করা (গ্লাস-মরফিজম থিম)
try:
    st.markdown(f"<style>{config.load_css()}</style>", unsafe_allow_html=True)
except Exception as e:
    st.warning(f"CSS could not be loaded: {e}")

# ৩. ক্রিস্টাল ল্যাটিস কম্পিউটেশন লেয়ার (ক্যাশড)
@st.cache_data
def compute_lattice(params):
    return phy.generate_lattice(params)

# ৪. মেইন অ্যাপ লজিক
def main():
    # সেশন স্টেট ইনিশিয়ালাইজেশন
    if "params" not in st.session_state:
        st.session_state["params"] = config.DEFAULT_PARAMS.copy()
    if "lattice_data" not in st.session_state:
        st.session_state["lattice_data"] = ([], 0.0)
    
    # সাইডবার কন্ট্রোলস (কনফিগ মডিউল পাস করা হলো)
    params = ui.sidebar_controls(config)
    
    # প্যারামিটার চেঞ্জ হলে রি-কম্পিউট করা
    atoms, volume = compute_lattice(params)
    st.session_state["lattice_data"] = (atoms, volume)
    
    # ট্যাব নেভিগেশন
    explore, info, raw = st.tabs(["Explore", "Info", "Raw Data"])
    
    with explore:
        try:
            ui.explore_tab(params, phy, config)
        except TypeError:
            ui.explore_tab(params, phy, cfg=config)
            
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
