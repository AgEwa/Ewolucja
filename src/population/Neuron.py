class Neuron:
    def __init__(self, neuron_type):
        self.type = neuron_type
        self.value = 0
        self.connections = []  # pairs, neuron and weight

    def receive_input(self, input_val):
        self.value += input_val

    def forward(self):
        # math operations if needed on value
        for neuron, weight in self.connections:
            neuron.receive_input(weight * self.value)
