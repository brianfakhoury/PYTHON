#!/usr/bin/env python3
"""
Stochastic batch simulation of randomly spaced, three
layer, fully connected  network.
"""
import numpy as np
from random import seed, randint

seed(1)


class Neuron(object):
    """
    Instance of shunting neuron with receptive field
    """

    def __init__(self, id, layer, dt=0.01):
        super(Neuron, self).__init__()
        self._id = id
        self._layer = layer
        self.dt = dt
        self.activity = np.float32(0)
        self._inputs = np.array([], dtype=np.float32)
        self._weights = np.array([], dtype=np.float32)

    def __repr__(self):
        return "Neuron: " + self._id

    @property
    def id(self):
        return self._id

    @property
    def layer(self):
        return self._layer

    def weights():
        doc = "The weights property."

        def fget(self):
            return self._weights

        def fset(self, value):
            self._weights = value

        def fdel(self):
            del self._weights
        return locals()
    weights = property(**weights())

    def inputs():
        doc = "The inputs property."

        def fget(self):
            return self._inputs

        def fset(self, value):
            self._inputs = value

        def fdel(self):
            del self._inputs
        return locals()
    inputs = property(**inputs())

    def update(self):
        pass

    # TODO: setters for inputs and weights


class NeuronGrid(object):
    """
    Grid of neurons.
    Instantiation creates random spacing.
    """

    def __init__(self, layer_size, num_layers, max_spacing=3):
        super(NeuronGrid, self).__init__()

        self.layer_size = layer_size
        self.num_layers = num_layers
        self.max_spacing = max_spacing

        grid = [[0 for y in range(num_layers * max_spacing)]
                for x in range(layer_size)]
        loc_lookup = [[(0, 0) for y in range(num_layers)]
                      for x in range(layer_size)]
        for i in range(layer_size):
            locs = [0] * num_layers
            for j in range(num_layers):
                locs[j] = randint(2, max_spacing)
            curr_loc = 0
            for j in range(num_layers):
                curr_loc = curr_loc + locs[j]
                grid[i][curr_loc] = Neuron(
                    "{}-{}".format(i, j), j)
                loc_lookup[i][j] = (i, curr_loc)
        self.grid = grid

        connections = []
        for row in loc_lookup:
            for i, j in row:

                connections = connections + \
                    [[(i, j), (x, y)]
                     for x, y in loc_lookup[:][j] if (x, y) != (i, j)]
                connections = connections + [[(i, j), (x, y)]
                                             for x, y in loc_lookup[:][j + 1]]
        self.connections = connections
        print(self.connections)

    def __repr__(self):
        ret = ""
        for i in range(self.layer_size):
            string = ""
            for j in range(self.num_layers * self.max_spacing):
                if type(self.grid[i][j]) == Neuron:
                    string = string + "x "
                else:
                    string = string + ". "
            ret = ret + "\n" + string
        return ret + "\n"

    def print_activity(self):
        ret = ""
        for i in range(self.layer_size):
            string = ""
            for j in range(self.num_layers * self.max_spacing):
                if type(self.grid[i][j]) == Neuron:
                    string = string + str(self.grid[i][j].activity) + " "
                else:
                    string = string + ". "
            ret = ret + "\n" + string
        print(ret + "\n")

    def connnect_network(self):
        pass

    def tick(self):
        pass


a = NeuronGrid(5, 3)
