import random

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

        #change state
        if self.state == "Good" and random.random() < self.p_gb:
            self.state = "Bad"
        elif self.state == "Bad" and random.random() < self.p_bg:
            self.state = "Good"

        return byte

    def process_message(self, message):
        return bytearray(self.process_byte(byte) for byte in message)