import random
import reedsolo

# Encode
def reed_solomon_encode(data, n=32, k=16):
    data_bytes = bytearray(data, 'utf-8')
    rs = reedsolo.RSCodec(n - k)
    encoded_data = rs.encode(bytes(data_bytes))
    return encoded_data


# Decode
def reed_solomon_decode(encoded_data, n=32, k=16):
    rs = reedsolo.RSCodec(n - k)
    try:
        decoded_data = rs.decode(encoded_data)[0]
        decoded_message = decoded_data.decode('utf-8')
        return decoded_message
    except reedsolo.ReedSolomonError:
        print("Decoding failed due to excessive errors.")
        return None

# BSC Channel
def apply_bsc(encoded_data, BER):
    flipped_data = bytearray(encoded_data)
    flipped_bits = 0
    # Flip random bits according to BER
    for i in range(len(flipped_data) * 8):
        if random.random() < BER:
            byte_index = i // 8
            bit_index = i % 8
            flipped_data[byte_index] ^= (1 << bit_index)  #Bit flip
            flipped_bits += 1
    return flipped_data, flipped_bits

# Converts decoded damaged packet to "readable" text
def list_to_text(data_list, ecc):
    ecc_amount = len(ecc)
    data_part = data_list[:-ecc_amount] if ecc_amount > 0 else list
    return ''.join(chr(i) for i in data_part)

# Main function
if __name__ == "__main__":

    message = "Macarena"
    print(f"Original message: {message}")

    # Encode
    encoded_message = reed_solomon_encode(message)
    print(f"Encoded data (with ECC):     {list(encoded_message)}")

    # Pass through BSC
    BER = 0.03  # Bit Error Rate
    received_data, flipped_bits = apply_bsc(encoded_message, BER)
    print(f"Received data (with errors): {list(received_data)}")
    print(f"Total flipped bits: {flipped_bits}")

    # Display decoded damaged message
    damaged_decoded_message = list_to_text(received_data, encoded_message[-(len(encoded_message) - len(message)):])
    print(f"Decoded damaged message: {damaged_decoded_message}")

    # Attempt to decode
    decoded_message = reed_solomon_decode(received_data)
    if decoded_message is not None:
        print(f"Decoded message: {decoded_message}")
    else:
        print("Decoding failed due to excessive errors.")