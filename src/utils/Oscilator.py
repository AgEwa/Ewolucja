import math


class Oscillator:
    def __init__(self, frequency=1.0):
        self.frequency = frequency
        self.time = 0.0

    def get_value(self) -> float:
        self.time += 0.1
        sine_wave = math.sin(self.frequency * self.time)
        return sine_wave

    def set_frequency(self, frequency: float):
        self.frequency = frequency
