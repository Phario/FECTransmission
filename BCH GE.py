import random
import bchlib

t = 5
m = 7

bch = bchlib.BCH(t=t, m=m)

def bch_encode(data):
    data_bytes = bytearray(data, 'utf-8')
    ecc = bch.encode(data_bytes)
    return data_bytes + ecc

def bch_decode(corrupted_packet):
    data_bytes = corrupted_packet[:-bch.ecc_bytes]
    ecc_bytes = corrupted_packet[-bch.ecc_bytes:]

    n_errors = bch.decode(data_bytes, ecc_bytes)

    if n_errors >= 0:
        corrected_data = bytearray(data_bytes)
        corrected_ecc = bytearray(ecc_bytes)

        bch.correct(corrected_data, corrected_ecc)

        corrected_packet = corrected_data.decode('utf8')
        return corrected_packet, n_errors
    else:
        return None, -1

class GEChannel:
    def __init__(self, p_g, p_b, p_gb, p_bg):
        self.p_g = p_g
        self.p_b = p_b
        self.p_gb = p_gb
        self.p_bg = p_bg
        self.state = "Good"
        self.bit_flips = 0

    def _flip_bit(self, byte):
        bit_to_flip = 1 << random.randint(0, 7)
        self.bit_flips += 1
        return byte ^ bit_to_flip

    def process_byte(self, byte):
        if self.state == "Good":
            error_prob = self.p_g
        else:
            error_prob = self.p_b

        if random.random() < error_prob:
            byte = self._flip_bit(byte)

        if self.state == "Good" and random.random() < self.p_gb:
            self.state = "Bad"
        elif self.state == "Bad" and random.random() < self.p_bg:
            self.state = "Good"

        return byte

    def process_message(self, message):
        return bytearray(self.process_byte(byte) for byte in message)

if __name__ == '__main__':
    message = "Komputer"

    print(f"Original message: {message}")
    encoded_data = bch_encode(message)
    print(f"Encoded Data (with ECC):     {list(encoded_data)}")

    ge_channel = GEChannel(p_g=0.3, p_b=0.3, p_gb=0.3, p_bg=0.3)
    received_data = ge_channel.process_message(encoded_data)
    print(f"Received Data (with errors): {list(received_data)}")

    decoded_damaged_data = ''.join(chr(byte) for byte in received_data if 32 <= byte <= 126)
    print(f"Decoded damaged message: {decoded_damaged_data}")
    print(f"Total flipped bits: {ge_channel.bit_flips}")

    decoded_data, error_amount = bch_decode(received_data)
    if error_amount >= 0:
        print(f"Decoded message: {decoded_data}")
        print(f"Errors corrected: {error_amount}")
    else:
        print("Decoding failed due to excessive errors")