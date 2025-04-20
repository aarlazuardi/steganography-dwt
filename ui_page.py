import streamlit as st
from PIL import Image
from steg_functions import embed_message, extract_message
from io import BytesIO

# Function to reset session state when switching pages
def reset_session_state_on_page_change(current_page):
    if st.session_state.get("current_page") != current_page:
        st.session_state.pop("stego_image", None)
        st.session_state.pop("downloaded", None)  # Reset download status
        st.session_state["current_page"] = current_page

def embed_ui():
    reset_session_state_on_page_change("embed")
    st.title("Embed Message into Image (DWT Method)")

    uploaded_file = st.file_uploader("Upload Image (PNG/JPG/BMP)", type=["png", "jpg", "jpeg", "bmp"])

    # Clear stego_image if a different file is uploaded
    if uploaded_file is not None:
        uploaded_filename = uploaded_file.name
        if st.session_state.get("last_uploaded_filename") != uploaded_filename:
            st.session_state.pop("stego_image", None)
            st.session_state.pop("downloaded", None)  # Reset download status
        st.session_state["last_uploaded_filename"] = uploaded_filename

    col1, col2 = st.columns(2)

    image = None
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        with col1:
            st.image(image, caption="Cover Image", use_container_width=True)

    message = st.text_area("Enter the message to embed:")

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
            st.session_state.downloaded = False  # Reset download status
            st.success("✅ Message successfully embedded into the image!")

        except Exception as e:
            st.error(f"❌ Failed to embed message: {e}")

    if "stego_image" in st.session_state:
        with col2:
            st.image(st.session_state.stego_image, caption="Stego Image", use_container_width=True)

        buffered = BytesIO()
        st.session_state.stego_image.save(buffered, format="PNG")

        # Logic to hide the download button after one click
        if not st.session_state.get("downloaded", False):
            if st.download_button(
                label="⬇️ Download Stego Image",
                data=buffered.getvalue(),
                file_name="stego_image.png",
                mime="image/png"
            ):
                st.session_state.downloaded = True  # Mark download as completed
        else:
            st.warning("Stego image has already been downloaded.")

def extract_ui():
    reset_session_state_on_page_change("extract")
    st.title("🔍 Extract Message from Image")

    uploaded_file = st.file_uploader("Upload Image (PNG only for accurate results)", type=["png"])
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