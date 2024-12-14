from typing import Callable

import networkx as nx

from src.population.SensorActionEnums import NeuronType, ActionType, SensorType


def execute_connections(inputs: dict[int, float], links: list[tuple[int, float]]) -> float:
    """
    Computes the weighted sum of values from a set of inputs based on provided connections.
    Side Effects:
        - Modifies passed link list
    :param inputs: Dictionary of connection source values with source IDs as keys.
    :param links: List of tuples representing connections. Each consists of:
                  - The source ID.
                  - The weight (float) for that connection.
    :return: The weighted sum of the input values specified in the links.
    """
    value = 0.0
    for source, weight in links:
        value += inputs.get(source) * weight
    return value


def is_reachable(links: list[tuple[int, float]], reached: set[int]) -> bool:
    """
    Filters out links which sources are not in the 'reached' set to check if the target is reachable.
    :param links: List of tuples representing connections, with first element being id of the source.
    :param reached: Set of source IDs that are considered reachable.
    :return: True if any links remain after filtering, else False.
    """
    to_remove = {link for link in links if link[0] not in reached}
    links[:] = [x for x in links if x not in to_remove]
    return len(links) > 0


def get_node_name(neuron, neuron_type: NeuronType):
    if neuron_type is NeuronType.INNER:
        return neuron
    else:
        return neuron_type.value(neuron)


class Layer:
    """
    Base class for layers of connections in neural network.
    Handles optimization of the connections and propagating values between layers.
    :param connections: Dictionary of lists representing connections between this layer and the previous layer.
                        Each consists of:
                         - Key: ID of the target of the connections.
                         - Value: List of (source, weight) tuples representing connections to the target.
    """

    def __init__(self, connections: dict[int, list[tuple[int, float]]] = None):
        self._next_layer = None
        self._outputs = {}
        self._connections = connections if connections else {}  # dict(target: links=list[(source,weight)])

    def next(self, next_layer: 'Layer') -> 'Layer':
        """Sets the next layer in the sequence and returns it"""
        self._next_layer = next_layer
        return self._next_layer

    def run(self, inputs: dict[int, float]) -> dict[int, float]:
        """
        Executes the layer with the given inputs and propagates the outputs to the next layer, if exists.
        :param inputs: Dictionary of layer connections' input values keyed by source IDs.
        :return: Dictionary of outputs after processing the layer.
        """
        self.process(inputs)

        if self._next_layer:
            return self._next_layer.run(self._outputs)
        return self._outputs

    def process(self, inputs: dict[int, float]):
        """
        Processes inputs to compute output values based on the layer's connections.
        :param inputs: Dictionary of connection's inputs keyed by source IDs.
        """
        for target, links in self._connections.items():
            self._outputs[target] = execute_connections(inputs, links)

    def optimize(self, reached_ids: set) -> set:
        """
        Optimizes the layer by removing unreachable/unused connections.
        Propagates the optimization process to the next layer.
        :param reached_ids: Set of IDs from the previous layer that are reachable.
        :return: Set of IDs from previous layer that are reachable for backward propagation from this layer.
        """
        marked = self.mark_reachable(reached_ids)

        if self._next_layer:
            marked_backward = self._next_layer.optimize(marked)
            marked = marked.intersection(marked_backward)

        return self.prune_unmarked(marked)

    def mark_reachable(self, reached: set) -> set:
        """
        Marks connection targets in this layer that have connections from reachable sources.
        :param reached: Set of IDs form previous layer (sources) that are marked as reachable.
        :return: Set of IDs that are reachable in this layer.
        """
        marked = set()
        for target, links in self._connections.items():
            if is_reachable(links, reached):
                marked.add(target)

        return marked

    def prune_unmarked(self, marked: set) -> set:
        """
        Removes targets (with its connections) that are not marked as reachable (forward).
        Marks sources of the connections left as backward-reachable and returns set of theirs ids.
        :param marked: Set of IDs in this layer that are marked as reachable from a forward run.
        :return: Set of source IDs that are backward-reachable.
        """
        marked_backward = set()
        to_remove = set()
        for target, links in self._connections.items():
            if target not in marked:
                to_remove.add(target)
            else:
                for source, _ in links:
                    marked_backward.add(source)

        for target in to_remove:
            del self._connections[target]

        return marked_backward

    def _make_network(self, graph: nx.MultiDiGraph, types: list[NeuronType], step: int):
        for target, links in self._connections.items():
            target_name = get_node_name(target, types[step + 1])
            graph.add_node(target_name, n_type=types[step + 1].name)

            for source, weight in links:
                source_name = get_node_name(source, types[step])
                graph.add_node(source_name, n_type=types[step].name)
                graph.add_edge(source_name, target_name, weight=weight)

        if self._next_layer:
            self._next_layer._make_network(graph, types, step+1)
        return graph


class __ActivationLayer(Layer):

    def __init__(self, connections: dict[int, list[tuple[int, float]]] = None):
        super().__init__(connections)
        self._activation_func = None

    def add_activation_func(self, func: Callable) -> Layer:
        """Sets the next layer in the sequence and returns it"""
        self._activation_func = func
        return self

    def process(self, inputs: dict):
        """
        Processes connections by modifying output values.
        Applies activation function to all outputs afterward.
        :param inputs: Dictionary of layer connections' input values keyed by source IDs
        """
        for target, links in self._connections.items():

            if target not in self._outputs:
                self._outputs[target] = 0

            self._outputs[target] += execute_connections(inputs, links)

        if self._activation_func:
            for target in self._outputs:
                self._outputs[target] = self._activation_func(self._outputs[target])


class LateralConnections(__ActivationLayer):
    """
    Sublayer that allows processing lateral connections (links between neurons of the same layer) in neural network.
    """

    def process(self, inputs: dict):
        """
        Processes lateral connections for inputs by using them as starting outputs and modifying their values.
        :param inputs: Dictionary of layer connections' input values keyed by source IDs
        """
        self._outputs = inputs.copy()

        super().process(self._outputs)


class DirectConnections(__ActivationLayer):
    """
    Specialized layer in neural network wrapped around other layers to allow processing direct connections from
    sensors to the final layer. Acts as a pass-through for input values, propagating them unchanged to subsequent
    layers. Performs its own logic using remembered initial parameters and the final result of the sequence to ensure
    these connections are included in both the execution and optimization phases of the network.
    """

    def run(self, sensor_inputs: dict[int, float]) -> dict[int, float]:
        """
        Remembers sensor's inputs and propagates them to the next layer, if exists.
        Executes the direct sensor - last layer connections with the remembered inputs and returned last layer outputs.
        :param sensor_inputs: Dictionary of layer connections' input values keyed by sensor IDs.
        :return: Dictionary of outputs after processing the layer.
        """
        inputs = sensor_inputs.copy()

        if self._next_layer:
            self._outputs = self._next_layer.run(inputs)

        self.process(sensor_inputs)

        return self._outputs

    def optimize(self, sensor_ids: set) -> set:
        """
        Remembers sensor IDs, propagates them to the next layer for optimization process.
        Adds sensors used in direct connections, if they were not backward-reachable for other layers.
        :param sensor_ids: Set of existing sensor's IDs.
        :return: Set of sensor's IDs that are used in the network.
        """
        used = sensor_ids.copy()

        if self._next_layer:
            used = self._next_layer.optimize(sensor_ids)

            for _, links in self._connections.items():
                for source, _ in links:
                    used.add(source)

        return used

    def get_network(self):
        types = [NeuronType.SENSOR, NeuronType.INNER, NeuronType.INNER, NeuronType.ACTION]
        graph = self._next_layer._make_network(nx.MultiDiGraph(), types, 0)

        for target, links in self._connections.items():
            target_name = ActionType(target)
            graph.add_node(target_name, n_type=NeuronType.ACTION.name)

            for source, weight in links:
                source_name = SensorType(source)
                graph.add_node(source_name, n_type=NeuronType.SENSOR.name)
                graph.add_edge(source_name, target_name, weight=weight)

        return graph
