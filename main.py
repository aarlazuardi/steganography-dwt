import streamlit as st
from ui_page import embed_ui, extract_ui

st.sidebar.title("Steganography Application")
page = st.sidebar.radio("Select Mode", ("Embed Message", "Extract Message"))

if page == "Embed Message":
    embed_ui()
else:
    extract_ui()