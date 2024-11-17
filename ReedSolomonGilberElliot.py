import reedsolo
import GilbertElliottChannel

#Bit transition probability
p_g = 0.1
p_b = 0.5
#State transition probability
p_gb = 0.1
p_bg = 0.2

#Encode
def reed_solomon_encode(data, n=32, k=16):
    data_bytes = bytearray(data, 'utf-8')
    rs = reedsolo.RSCodec(n - k)
    encoded_data = rs.encode(bytes(data_bytes))
    return encoded_data


#Decode
def reed_solomon_decode(encoded_data, n=32, k=16):
    rs = reedsolo.RSCodec(n - k)
    try:
        decoded_data = rs.decode(encoded_data)[0]
        decoded_message = decoded_data.decode('utf-8')
        return decoded_message
    except reedsolo.ReedSolomonError:
        print("Decoding failed due to excessive errors.")
        return None


if __name__ == "__main__":

    message = "Macarena"
    print(f"Original message: {message}")

    encoded_message = reed_solomon_encode(message)
    print(f"Encoded data (with ECC):     {list(encoded_message)}")

    GEChannel = GilbertElliottChannel.GEChannel(p_g, p_b, p_gb, p_bg)
    damaged_message = GEChannel.process_message(encoded_message)
    print(f"Received data (with errors): {list(damaged_message)}")
    print(f"Total flipped bits: {GEChannel.bit_flips}")

    damaged_decoded_message = ''.join(chr(i) for i in damaged_message)
    damaged_decoded_message = damaged_decoded_message[:len(message)]
    print(f"Decoded damaged message: {damaged_decoded_message}")
    decoded_message = reed_solomon_decode(damaged_message)
    print(f"Decoded message: {decoded_message}")
