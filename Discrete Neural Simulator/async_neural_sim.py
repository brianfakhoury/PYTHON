#!/usr/bin/env python3
""""
Testing async nn claims.
Inlcudes NN and Simulator
"""

from queue import PriorityQueue
from random import seed, randint

seed(1)


class NeuralNetwork(object):
    """
    Instance of randomly spaced neurons in single layer.
    Methods for accessing and updating neuron activity
    """

    def __init__(self, num_nodes=100, time_const=10, dt=0.01, A=1, B=1, C=1):

        super(NeuralNetwork, self).__init__()

        self.num_nodes = num_nodes
        self.neurons = [0] * num_nodes
        self.neuron_inputs = [0] * num_nodes
        self.time_const = time_const
        self.axon_lengths = [randint(10, 20) for i in range(100)]
        self.dt = dt
        self.A = A
        self.B = B
        self.C = C

    def getActivity(self, index):
        return self.neurons[index]

    def getAxonLength(self, index):
        return self.axon_lengths[index]

    def updateInput(self, neuron_index, input_value):
        self.neuron_inputs[neuron_index] = input_value

    def updateState(self, time_diff):
        for i in range(self.num_nodes):
            activateNeuron(i)
            if self.neuron_inputs[i] != 0:
                self.neuron_inputs[i] = 0

    def activateNeuron(self, index):
        i = self.neuron_inputs[index]
        prev = self.neurons[index]
        self.neurons[index] = prev + self.dt * (-self.A * prev + (B - prev) *)
        # implement np to do this vectorized


class DiscreteSimulator(object):
    """docstring for DiscreteSimulator."""

    def __init__(self, neural_net, max_simulation_time=10000, stim_freq=10):
        """
        params:
            neural_net : instantiated network
            max_simulation_time : number of milliseconds to run for
            stim_freq : how often to show the input stimulus
        """
        super(DiscreteSimulator, self).__init__()

        self.neural_net = neural_net
        self.max_simulation_time = max_simulation_time
        self.time = 0
        self.stim_freq = stim_freq
        self.queue = PriorityQueue()

        for i in range(self.neural_net.num_nodes):
            self.queue.put((0, "STIM", i))

    def start(self):
        while self.time < self.max_simulation_time:
            event_time, event_type, neuron_index = self.queue.get()
            if event_type == "STIM":
                stimEvent(neuron_index)
            elif event_type == "SYNAP":
                synapEvent(neuron_index)
            self.time = event_time

    def stimEvent(self, neuron_index):
        axon_length = self.neural_net.getAxonLength(neuron_index)
        self.queue.put((axon_length, "SYNAP", neuron_index))
        self.queue.put((self.stim_freq, "STIM", neuron_index))

    def synapEvent(self, neuron_index):
        self.neural_net.updateInput(neuron_index, 0.5)
        self.neural_net.updateState()


def main():
    nn = NeuralNetwork()
    sim = DiscreteSimulator(nn)
    sim.start()


if __name__ == '__main__':
    main()
