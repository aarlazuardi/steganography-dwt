import streamlit as st
from PIL import Image
from steg_functions import embed_message, extract_message
from io import BytesIO

def reset_session_state_on_page_change(current_page):
    if st.session_state.get("current_page") != current_page:
        st.session_state.pop("stego_image", None)
        st.session_state.pop("downloaded", None)
        st.session_state["current_page"] = current_page

# Komponen header branding
def render_header(title, subtitle):
    st.markdown(f"""
        <div style="text-align: center; margin-top: 20px; margin-bottom: 10px;">
            <h1 style="font-size: 3em; margin-bottom: 0px;">🧠 SteCU</h1>
            <p style="font-size: 1.1em; color: #6c757d; font-style: italic; margin-top: 0px; margin-bottom: 20px;">
                Steganography Conceal Utility
            </p>
            <p style="font-size: 1.2em; color: #888;">{subtitle}</p>
            <hr style="border: 1px solid #444; margin-top: 20px;">
        </div>
    """, unsafe_allow_html=True)
    st.subheader(title)


def embed_ui():
    reset_session_state_on_page_change("embed")
    render_header("Embed Message into Image", "Steganography using DWT Method")

    uploaded_file = st.file_uploader("📤 Upload Image (PNG / JPG / JPEG / BMP)", type=["png", "jpg", "jpeg", "bmp"])

    if uploaded_file is not None:
        uploaded_filename = uploaded_file.name
        if st.session_state.get("last_uploaded_filename") != uploaded_filename:
            st.session_state.pop("stego_image", None)
            st.session_state.pop("downloaded", None)
        st.session_state["last_uploaded_filename"] = uploaded_filename

    image = None
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")

    col1, col2 = st.columns(2)

    if image:
        with col1:
            st.image(image, caption="Cover Image", use_container_width=True)

    message = st.text_area("💬 Enter the message to embed:")

    if st.button("📥 Embed Message"):
        if uploaded_file is None:
            st.warning("Please upload an image first.")
            return
        if message.strip() == "":
            st.warning("Message cannot be empty.")
            return

        try:
            stego_image = embed_message(image, message)
            st.session_state.stego_image = stego_image
            st.session_state.downloaded = False
            st.success("✅ Message successfully embedded into the image!")

        except Exception as e:
            st.error(f"❌ Failed to embed message: {e}")

    if "stego_image" in st.session_state:
        with col2:
            st.image(st.session_state.stego_image, caption="Stego Image", use_container_width=True)

        buffered = BytesIO()
        st.session_state.stego_image.save(buffered, format="PNG")

        if not st.session_state.get("downloaded", False):
            if st.download_button(
                label="⬇️ Download Stego Image",
                data=buffered.getvalue(),
                file_name="stego_image.png",
                mime="image/png"
            ):
                st.session_state.downloaded = True
        else:
            st.info("📁 Stego image has already been downloaded.")

def extract_ui():
    reset_session_state_on_page_change("extract")
    render_header("Extract Message from Image", "Steganography using DWT Method")

    uploaded_file = st.file_uploader("📤 Upload Image (PNG only for accurate results)", type=["png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Stego Image", use_container_width=True)

    if st.button("📤 Extract Message"):
        if uploaded_file is None:
            st.warning("Please upload an image first.")
            return

        try:
            image = Image.open(uploaded_file)

            if image.format != "PNG":
                st.error("Only PNG format images are supported for extraction.")
                return

            message = extract_message(image)
            st.text_area("📩 Extracted Message:", value=message, disabled=True, height=150)
            st.success("✅ Message successfully extracted!")

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
