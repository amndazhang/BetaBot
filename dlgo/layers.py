import numpy as np

class Layer:
    def __init__(self):
        self.params = []

        self.previous = None
        self.next = None

        self.input_data = None
        self.output_data = None

        self.input_delta = None
        self.output_delta = None

    def connect(self, layer):
        self.previous = layer
        layer.next = self

    def forward(self):
        raise NotImplementedError

    def get_forward_input(self):
        if self.previous:
            return self.previous.output_data
        else:
            return self.input_data
    
    def backward(self):
        raise NotImplementedError

    def get_backward_input(self):
        if self.next:
            return self.next.input_delta
        else:
            return self.output_delta
        
    def clear_deltas(self):
        pass

    def update_params(self, learning_rate):
        pass

    def describe(self):
        raise NotImplementedError
