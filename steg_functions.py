import numpy as np
from PIL import Image
import pywt
import os

# Special marker pattern for message start/end (harder to corrupt)
START_MARKER = '10101010' * 4  # 32-bit distinct pattern
END_MARKER = '01010101' * 4    # 32-bit distinct pattern

def message_to_binary(message):
    """Convert message to binary with distinct start and end markers"""
    binary = ''.join([format(ord(c), '08b') for c in message])
    # Add padding between message and end marker to prevent truncation
    padding = '00000000' * 2  # Add 2 bytes padding
    return START_MARKER + binary + padding + END_MARKER

def binary_to_message(binary):
    """Extract message from binary data between markers"""
    # Find the start marker
    start_idx = binary.find(START_MARKER)
    if start_idx == -1:
        raise ValueError("Start marker not found. Invalid or corrupted stego image.")
    
    # Find the end marker after the start marker
    content_start = start_idx + len(START_MARKER)
    end_idx = binary[content_start:].find(END_MARKER)
    
    if end_idx == -1:
        raise ValueError("End marker not found. The message may be corrupted.")
    
    # Extract the message bits between markers
    message_bits = binary[content_start:content_start + end_idx]
    
    # Process the message bytes
    message = ""
    for i in range(0, len(message_bits), 8):
        if i + 8 <= len(message_bits):
            byte = message_bits[i:i+8]
            try:
                message += chr(int(byte, 2))
            except ValueError:
                # Skip invalid bytes
                continue
    
    return message

def embed_message(image, message):
    """Embed message into image using DWT with enhanced robustness"""
    # Ensure we're working with an RGB image
    image = image.convert("RGB")
    width, height = image.size
    
    # Check if image is large enough
    if width * height < 10000:  # Require at least 10,000 pixels
        raise ValueError("Image is too small for reliable steganography. Use a larger image.")
    
    # Split image into channels
    r, g, b = image.split()
    g_data = np.array(g).astype(np.float32)  # Use green channel for embedding
    
    # Apply DWT
    coeffs2 = pywt.dwt2(g_data, 'haar')
    LL, (LH, HL, HH) = coeffs2
    
    # Prepare the message
    binary_message = message_to_binary(message)
    total_bits = len(binary_message)
    
    # Check capacity with 85% safety margin
    capacity = min(HH.size, HL.size)  # We'll use both HH and HL for redundancy
    print(f"Message length: {len(message)} chars / {total_bits} bits")
    print(f"Image capacity: ~{capacity} bits")
    
    if total_bits > capacity * 0.85:
        raise ValueError(f"Message too long for this image. Maximum length is about {int(capacity * 0.85 / 8)} characters.")
    
    # Flatten coefficients for easier processing
    flat_HH = HH.flatten()
    flat_HL = HL.flatten()
    
    # Embed message bits with enhanced significance
    for i in range(total_bits):
        if i < len(binary_message):
            bit = int(binary_message[i])
            
            # Embed in HH coefficients with stronger magnitude
            val_hh = flat_HH[i]
            if bit == 0:
                # Make significantly even
                flat_HH[i] = 4.0 * round(val_hh / 4.0)
            else:
                # Make significantly odd
                flat_HH[i] = 4.0 * round(val_hh / 4.0) + 2.0
            
            # Redundant embedding in HL for critical bits (markers)
            if i < len(START_MARKER) or i >= total_bits - len(END_MARKER):
                val_hl = flat_HL[i]
                if bit == 0:
                    flat_HL[i] = 4.0 * round(val_hl / 4.0)
                else:
                    flat_HL[i] = 4.0 * round(val_hl / 4.0) + 2.0
    
    # Reshape and reconstruct
    HH_modified = flat_HH.reshape(HH.shape)
    HL_modified = flat_HL.reshape(HL.shape)
    
    # Reconstruct the modified image
    coeffs2_modified = LL, (LH, HL_modified, HH_modified)
    g_stego = pywt.idwt2(coeffs2_modified, 'haar')
    
    # Clip values to valid image range and convert back to uint8
    g_stego = np.clip(g_stego, 0, 255).astype(np.uint8)
    g_stego = g_stego[:g_data.shape[0], :g_data.shape[1]]
    
    # Create the stego image
    stego_image = Image.merge("RGB", (r, Image.fromarray(g_stego), b))
    return stego_image

def extract_message(image):
    """Extract message from image using DWT with improved robustness"""
    # Ensure we're working with an RGB image
    image = image.convert("RGB")
    
    # Split image into channels
    _, g, _ = image.split()
    g_data = np.array(g).astype(np.float32)
    
    # Apply DWT
    coeffs2 = pywt.dwt2(g_data, 'haar')
    _, (_, HL, HH) = coeffs2
    
    # Flatten HH coefficients
    flat_HH = HH.flatten()
    
    # Improved extraction of bits with threshold
    bits = []
    for val in flat_HH:
        # Enhanced bit extraction with more precise thresholding
        remainder = abs(val % 4)
        if remainder < 1.0 or remainder > 3.0:
            bits.append('0')
        else:
            bits.append('1')
    
    binary_data = ''.join(bits)
    
    # Search for start marker with error tolerance
    start_marker_idx = -1
    error_tolerance = 4
    
    for i in range(min(1000, len(binary_data) - len(START_MARKER))):
        errors = sum(1 for a, b in zip(binary_data[i:i+len(START_MARKER)], START_MARKER) if a != b)
        if errors <= error_tolerance:
            start_marker_idx = i
            break
    
    if start_marker_idx == -1:
        raise ValueError("Could not find start marker. This might not be a valid stego image.")
    
    # Extract from where actual message starts
    content_start = start_marker_idx + len(START_MARKER)
    
    # Search a larger area for end marker
    search_area = binary_data[content_start:content_start + min(250000, len(binary_data) - content_start)]
    
    # Try to find end marker with increased error tolerance
    end_marker_error_tolerance = 6
    
    # Method 1: Try to find END_MARKER with flexible alignment
    end_marker_idx = -1
    for i in range(0, len(search_area) - len(END_MARKER)):
        errors = sum(1 for a, b in zip(search_area[i:i+len(END_MARKER)], END_MARKER) if a != b)
        if errors <= end_marker_error_tolerance:
            # Adjust to nearest byte boundary
            end_marker_idx = (i // 8) * 8
            if i % 8 > 0:  # If not already aligned, add one more byte
                end_marker_idx += 8
            break
    
    # If we couldn't find end marker, use character validity method with larger buffer
    if end_marker_idx == -1:
        valid_message_end = 0
        valid_char_count = 0
        invalid_streak = 0
        max_consecutive_valid = 0
        current_valid_streak = 0
        
        # Scan ahead looking for valid characters
        for i in range(0, min(len(search_area) - 8, 25000), 8):  # Extended search range
            if i + 8 > len(search_area):
                break
                
            try:
                byte = search_area[i:i+8]
                char_code = int(byte, 2)
                
                # If we find a valid printable ASCII character
                if 32 <= char_code <= 126:
                    valid_char_count += 1
                    current_valid_streak += 1
                    valid_message_end = i + 8
                    invalid_streak = 0
                    
                    # Update max streak
                    if current_valid_streak > max_consecutive_valid:
                        max_consecutive_valid = current_valid_streak
                else:
                    invalid_streak += 1
                    current_valid_streak = 0
                    
                # Only stop if we have many consecutive invalid characters after finding valid ones
                if invalid_streak >= 8 and valid_char_count > 8:  # Increased threshold from 6 to 8
                    break
                    
            except ValueError:
                invalid_streak += 1
                current_valid_streak = 0
                if invalid_streak >= 8 and valid_char_count > 8:
                    break
        
        # If we found valid characters, use that plus a more balanced buffer
        if valid_message_end > 0:
            # Use a much larger buffer to ensure we catch the complete message
            end_marker_idx = valid_message_end + 32  # Increased from 16 to 32
            
            # Ensure byte alignment and stay within bounds
            end_marker_idx = min((end_marker_idx // 8) * 8, len(search_area) - 8)
        else:
            # Last resort: extract minimal amount to avoid junk
            expected_chars = 30  # Increased from 20 to 30 for longer messages
            end_marker_idx = min(expected_chars * 8, len(search_area) - 8)
    
    # Extract message bits WITHOUT including the end marker
    message_bits = search_area[:end_marker_idx]  # Fixed: Removed the +16 buffer
    
    # Debug information
    print(f"Start marker at: {start_marker_idx}, content starts at: {content_start}")
    print(f"End marker/content detected at offset: {end_marker_idx}")
    print(f"Total message bits extracted: {len(message_bits)}")
    print(f"Sample of extracted bits: {message_bits[:40]}...")
    
    # Convert binary to text with less aggressive filtering
    message = ""
    consecutive_invalid = 0
    
    for i in range(0, len(message_bits), 8):
        if i + 8 <= len(message_bits):
            byte = message_bits[i:i+8]
            try:
                char_code = int(byte, 2)
                # Accept standard printable ASCII
                if 32 <= char_code <= 126:
                    message += chr(char_code)
                    consecutive_invalid = 0
                else:
                    consecutive_invalid += 1
                    # Less aggressive termination by increasing threshold
                    if consecutive_invalid >= 5 and len(message) > 0:  # Increased from 3 to 5
                        break
            except ValueError:
                consecutive_invalid += 1
                if consecutive_invalid >= 5 and len(message) > 0:
                    break
    
    # Modified post-processing to be much less aggressive with pattern detection
    # Only remove repeating patterns if they're exactly the same character repeated many times
    if len(message) >= 5:
        end_segment = message[-5:]
        if len(set(end_segment)) == 1:  # If all 5 characters are identical
            message = message[:-4]  # Remove 4 of them, keeping one
    
    # Only remove special control characters, not normal text
    while len(message) > 0 and (ord(message[-1]) < 32 or ord(message[-1]) > 126):
        message = message[:-1]
    
    return message
