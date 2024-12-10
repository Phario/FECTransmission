import random

import numpy as np
import ldpc.codes
import ldpc.code_util
from ldpc import BpDecoder


def check_errors(array1, array2):
    # Ensure the arrays are of the same length
    if len(array1) != len(array2):
        raise ValueError("Arrays must have the same length.")

    # Count the number of errors (where the elements are different)
    errors = np.sum(array1 != array2)

    return errors

def encode_word(word, k):
    # Create an empty list to hold the encoded binary values
    encoded = []

    # Loop through each character in the word
    for char in word:
        # Get the ASCII value of the character and convert it to binary
        bin_value = bin(ord(char))[2:]  # bin() returns a string starting with '0b', so we remove '0b'

        # Pad the binary string with leading zeros to make sure it has 8 bits
        bin_value = bin_value.zfill(8)

        # Convert each character in the binary string into an integer and append to the list
        encoded.extend([int(b) for b in bin_value])

    # Check if the encoded message exceeds the max number of bits
    if len(encoded) > k:
        raise ValueError(f"Encoding failed: The message exceeds the maximum allowed {k} bits.")

    # If the encoded message is shorter than k, pad with zeros
    while len(encoded) < k:
        encoded.append(0)

    # Convert the list to a NumPy array
    return np.array(encoded)

def encode_to_array(word, row_count, col_count):

    binary_str = ''.join(f'{ord(c):08b}' for c in word)

    total_bits = row_count * col_count
    if len(binary_str) < total_bits:
        binary_str = binary_str.ljust(total_bits, '0')
    elif len(binary_str) > total_bits:
        binary_str = binary_str[:total_bits]

    binary_list = [int(bit) for bit in binary_str]

    binary_array = np.array(binary_list).reshape((row_count, col_count))

    return binary_array

def apply_bsc(encoded_data, BER):
    # Ensure encoded_data is a numpy array
    encoded_data = np.asarray(encoded_data)

    # Flatten the array into a 1D array of bits (0s and 1s)
    flattened_data = encoded_data.flatten()

    flipped_bits = 0

    # Loop over each bit and flip it based on BER
    for i in range(len(flattened_data)):
        if random.random() < BER:
            flattened_data[i] ^= 1  # Flip the bit (0 -> 1 or 1 -> 0)
            flipped_bits += 1

    # Return the flipped data as a numpy array and the count of flipped bits
    return flattened_data, flipped_bits

H = ldpc.codes.hamming_code(6)
n, k, d_estimate = ldpc.code_util.compute_code_parameters(H)

bpd = BpDecoder(
    H, #the parity check matrix
    error_rate=0.3, # the error rate on each bit
    max_iter=n, #the maximum iteration depth for BP
    bp_method="product_sum", #BP method. The other option is `minimum_sum'
)


b = encode_word("macaren", k)
print(b)
print(f"Code parameters: [n = {n}, k = {k}, d <= {d_estimate}]")
G = ldpc.code_util.construct_generator_matrix(H)
G.toarray()

c = G.T@b % 2
print(c)

d, flipped_bits = apply_bsc(c, 0.3)
print (d)
print("flipped bits: ", flipped_bits)
decoded_codeword=bpd.decode(c)

print(decoded_codeword)
print("errors between original and received: ", check_errors(decoded_codeword, c))