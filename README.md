# Steganography with DWT (Discrete Wavelet Transform)

This project implements a steganography application using the Discrete Wavelet Transform (DWT) method. The application allows users to embed secret messages into images and extract them later. It is built using Python and Streamlit for an interactive user interface.

# Demo
   ```
   https://steganography-dwt.streamlit.app/
   ```

---

## Installation and Running the Application

### Prerequisites

- Python 3.8 or higher must be installed on your system.
- Install Git if you plan to clone the repository.

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/aarlazuardi/steganography-dwt.git
   cd steganography-dwt
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt (Windows) or
   pip3 install -r requirements.txt (Linux/Mac)
   ```
   to install the required packages.
3. Run the application using Streamlit:
   ```
   streamlit run main.py
   ```
4. Open your web browser and navigate to http://localhost:8501 to access the application.

# Features
   - Embed Message: Hide a secret message inside an image using DWT.
   - Extract Message: Retrieve the hidden message from a stego image.
   - Supported Image Formats: PNG, JPG, BMP.

# How It Works

1. Embedding Messages:
   - The application uses the Discrete Wavelet Transform (DWT) to decompose the green channel of the image into frequency sub-bands.
   - The secret message is converted into binary and embedded into the high-frequency sub-band (HH) using parity-based encoding.
2. Extracting Messages:
   - The application extracts the binary data from the HH sub-band of the stego image.
   - The binary data is converted back into a readable message.

# Usage

1. Embed Message:
   - Upload an image (PNG/JPG/BMP).
   - Enter the secret message you want to embed.
   - Click "Embed Message" to generate the stego image.
   - Download the stego image.
2. Extract Message:
   - Upload a stego image (PNG format recommended).
   - Click "Extract Message" to retrieve the hidden message.
