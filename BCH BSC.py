import random
import bchlib

t = 5  #Error correcting capability
m = 7  #Galois field order (5<=m<=15)

bch = bchlib.BCH(t=t, m=m)

#Encode method
def bch_encode(data):
    data_bytes = bytearray(data, 'utf-8')  # Convert data to bytes
    ecc = bch.encode(data_bytes)          # Compute the error correction code (ECC)
    return data_bytes + ecc               # Combine data and ECC for transmission

#Decode method
def bch_decode(corrupted_packet):
    data_bytes = corrupted_packet[:-bch.ecc_bytes]
    ecc_bytes = corrupted_packet[-bch.ecc_bytes:]

    n_errors = bch.decode(data_bytes, recv_ecc=ecc_bytes)

    #Correct errors if there were any
    if n_errors >= 0:
        corrected_data = bytearray(data_bytes)
        corrected_ecc = bytearray(ecc_bytes)

        bch.correct(corrected_data, corrected_ecc)

        corrected_packet = corrected_data.decode('utf8')
        return corrected_packet, n_errors
    else:
        #Return -1 if packet can't be corrected
        return None, -1


#BSC channel
def apply_bsc(encoded_data, BER):
    flipped_data = bytearray(encoded_data)
    flipped_bits = 0
    #Flips random bits according to BER
    for i in range(len(flipped_data) * 8):
        if random.random() < BER:
            byte_index = i // 8
            bit_index = i % 8
            flipped_data[byte_index] ^= (1 << bit_index)  #Bit flip
            flipped_bits += 1
    return flipped_data, flipped_bits

#Converts decoded damaged packet to "readable" text
def list_to_text(list, ecc):
    ecc_amount = len(ecc)
    data_part = list[:-ecc_amount] if ecc_amount > 0 else list
    return ''.join(chr(i) for i in data_part)

if __name__ == '__main__':
    message = "Macarena"

    print(f"Original message: {message}")
    #Encode
    encoded_data = bch_encode(message)
    print(f"Encoded Data (with ECC):     {list(encoded_data)}")

    #Go through BSC channel
    received_data, flipped_bits = apply_bsc(encoded_data, BER=0.03)
    print(f"Received Data (with errors): {list(received_data)}")
    print(f"Total flipped bits: {flipped_bits}")

    #Display decoded damaged message
    decoded_damaged_data = list_to_text(received_data, encoded_data[-bch.ecc_bytes:])
    print(f"Decoded damaged message: {decoded_damaged_data}")

    #Attempt to decode
    decoded_data, error_amount = bch_decode(received_data)
    #If successful: display decoded message and amount of errors corrected
    if error_amount >= 0:
        print(f"Decoded message: {decoded_data}")
        print(f"Errors corrected: {error_amount}")
    #Else: just say it couldn't do it
    else:
        print("Decoding failed due to excessive errors")
