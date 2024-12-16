import numpy as np
from bitstring import BitArray, Bits
from ldpc.decoder import DecoderWiFi, bsc_llr
from ldpc.encoder import EncoderWiFi
from ldpc.wifi_spec_codes import WiFiSpecCode
from ldpc.utils.custom_exceptions import IncorrectLength

INFO_BITS_LENGTH = 324  # Number of information bits for a rate-1/2 code
MAX_BYTES = INFO_BITS_LENGTH // 8  # Maximum bytes for the input string (40 bytes)
BER = 0.02
SPEC = WiFiSpecCode.N648_R34

def string_to_bits(s):
    if len(s) > MAX_BYTES:
        raise ValueError(f"Input string is too long! Max length is {MAX_BYTES} bytes.")
    byte_data = s.encode()
    padded_byte_data = byte_data.ljust(MAX_BYTES, b'\x00')
    return np.array(Bits(bytes=padded_byte_data)[:INFO_BITS_LENGTH], dtype=np.int_)


def bits_to_string(bits):
    padding = (8 - len(bits) % 8) % 8
    padded_bits = np.pad(bits, (0, padding), constant_values=0)
    byte_array = Bits(padded_bits.tolist()).bytes
    return byte_array.decode(errors='ignore').rstrip('\x00')

def apply_bsc(encoded_bits, p):
    corrupted = BitArray(encoded_bits)
    no_errors = int(len(corrupted) * p)
    rng = np.random.default_rng()
    error_idx = rng.choice(len(corrupted), size=no_errors, replace=False)
    for idx in error_idx:
        corrupted[idx] = not corrupted[idx]
    return corrupted


if __name__ == "__main__":
    input_string = "Macarena"

    info_bits = string_to_bits(input_string)
    print(f"Information bits: {info_bits}")

    enc = EncoderWiFi(SPEC)

    #Ensure the input bits are up to spec
    if len(info_bits) < enc.k:
        #Pad with zeros if info_bits is too short
        info_bits = np.pad(info_bits, (0, enc.k - len(info_bits)), constant_values=0)
    elif len(info_bits) > enc.k:
        #Raise error if info_bits is too long
        raise ValueError(f"Input bits are too long! Expected {enc.k} bits, got {len(info_bits)} bits.")
    #Encode
    encoded = enc.encode(info_bits)
    print(f"Encoded bits: {encoded}")
    #Check error syndrome
    h = enc.h
    print(f"Codeword validity check (syndrome): {np.dot(h, np.array(encoded)) % 2}")  #Should be only zeros
    #Go through BSC channel
    corrupted = apply_bsc(encoded, BER)
    decoder = DecoderWiFi(spec=SPEC, max_iter=20, channel_model=bsc_llr(p=BER))
    #Decode corrupted message
    decoded, llr, decode_success, num_of_iterations, syndrome, vnode_validity = decoder.decode(corrupted)
    print(f"Decoding successful: {decode_success}")
    print(f"Decoded matches original: {Bits(decoded) == Bits(encoded)}")
    decoded_info_bits = decoder.info_bits(decoded)
    #Decode back to readable format
    decoded_string = bits_to_string(decoded_info_bits)
    print(f"Decoded string: {decoded_string}")