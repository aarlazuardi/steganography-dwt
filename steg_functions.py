import numpy as np
from PIL import Image
import pywt

# Ubah pesan ke biner + EOF
def message_to_binary(message):
    binary = ''.join([format(ord(c), '08b') for c in message])
    return binary + '11111110'  # EOF marker

# Ubah biner ke string sampai EOF
def binary_to_message(binary):
    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    message = ''
    for byte in chars:
        if byte == '11111110':
            break
        message += chr(int(byte, 2))
    return message

# Embedding dengan threshold ±1.5 (tidak terlalu kasar)
def embed_message(image, message):
    image = image.convert("RGB")
    r, g, b = image.split()
    g_data = np.array(g).astype(np.float32)

    coeffs2 = pywt.dwt2(g_data, 'haar')
    LL, (LH, HL, HH) = coeffs2

    binary_message = message_to_binary(message)
    capacity = HH.size
    print(f"Binary message: {binary_message}")  # Debugging log
    print(f"Capacity of HH: {capacity}")  # Debugging log

    if len(binary_message) > capacity:
        raise ValueError("Pesan terlalu panjang untuk gambar ini.")

    flat_HH = HH.flatten()

    for i in range(len(binary_message)):
        bit = int(binary_message[i])
        val = flat_HH[i]
        if bit == 0:
            flat_HH[i] = np.floor(val / 2) * 2
        else:
            flat_HH[i] = np.floor(val / 2) * 2 + 1

    HH_modified = flat_HH.reshape(HH.shape)
    coeffs2_modified = LL, (LH, HL, HH_modified)
    g_stego = pywt.idwt2(coeffs2_modified, 'haar')
    g_stego = np.clip(g_stego, 0, 255).astype(np.uint8)

    g_stego = g_stego[:g_data.shape[0], :g_data.shape[1]]
    stego_image = Image.merge("RGB", (r, Image.fromarray(g_stego), b))
    return stego_image

# Ekstraksi berdasarkan nilai paritas HH
def extract_message(image):
    image = image.convert("RGB")
    _, g, _ = image.split()
    g_data = np.array(g).astype(np.float32)

    coeffs2 = pywt.dwt2(g_data, 'haar')
    _, (_, _, HH) = coeffs2

    flat_HH = HH.flatten()
    bits = [str(int(np.floor(val) % 2)) for val in flat_HH]
    binary_data = ''.join(bits)
    print(f"Extracted binary data: {binary_data[:100]}...")  # Debugging log

    eof_index = binary_data.find('11111110')
    if eof_index != -1:
        binary_data = binary_data[:eof_index + 8]
    else:
        raise ValueError("EOF marker tidak ditemukan. Pesan mungkin rusak.")

    return binary_to_message(binary_data)