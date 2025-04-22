import streamlit as st
from ui_page import embed_ui, extract_ui

# Konfigurasi tampilan halaman
st.set_page_config(
    page_title="SteCU - Steganography with DWT",
    page_icon="🧠",
    layout="wide"
)

# Sidebar branding
with st.sidebar:
    st.markdown("""
        <div style="text-align:center;">
            <h2 style="color:#fff;">🧠 <span style="color:#4CAF50;">SteCU</span></h2>
            <p style="font-size:14px; color:#ccc;">Steganography using DWT Method</p>
        </div>
    """, unsafe_allow_html=True)

    page = st.radio("📌 Select Mode", ("Embed Message", "Extract Message"))

# Routing ke UI
if page == "Embed Message":
    embed_ui()
else:
    extract_ui()
