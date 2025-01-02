from math import tanh
from unittest import TestCase

from src.population.Layer import *
from src.population.SensorActionEnums import SensorType, ActionType


class TestHelpFunctions(TestCase):
    def test_execute_connections(self):
        # given
        inputs = {
            1: 1.0,
            2: 2.0,
            3: 3.0
        }
        links = [(2, 0.5), (1, 0.3), (3, 1.5)]
        expected_value = 0.3 + 1.0 + 4.5
        # when
        value = execute_connections(inputs, links)
        # then
        self.assertEqual(expected_value, value)

    def test_is_reachable(self):
        # given
        links = [(2, 0.5), (1, 0.3), (3, 1.5)]
        reached = {1, 2}
        expected_links_left = [(2, 0.5), (1, 0.3)]
        # when
        reachable = is_reachable(links, reached)
        # then
        self.assertTrue(reachable)
        self.assertListEqual(expected_links_left, links)
        # given
        reached = {4, 5}
        # when
        reachable = is_reachable(links, reached)
        # then
        self.assertFalse(reachable)
        self.assertTrue(len(links) == 0)

    def test_get_node_name(self):
        result = get_node_name(1, NeuronType.SENSOR)
        self.assertEqual(SensorType(1).name, result)

        result = get_node_name(1, NeuronType.INNER)
        self.assertEqual(1, result)

        result = get_node_name(1, NeuronType.ACTION)
        self.assertEqual(ActionType(1).name, result)


class TestLayer(TestCase):

    def setUp(self):
        self.connections = {
            1: [(0, 0.5), (1, 1.0)],
            2: [(1, 2.0)],
        }
        self.layer = Layer(self.connections)

        self.next_layer_connections = {
            3: [(1, 1.0), (2, 1.5)]
        }
        self.next_layer = Layer(self.next_layer_connections)
        self.layer.next(self.next_layer)

    def test_process(self):
        # given
        inputs = {0: 2.0, 1: 3.0}
        # when
        self.layer._process(inputs)
        # then
        # '1' = 0.5*2.0 + 1.0*3.0 = 4.0
        # '2' = 2.0*3.0 = 6.0
        self.assertEqual(4.0, self.layer._outputs[1])
        self.assertEqual(6.0, self.layer._outputs[2])

    def test_run_with_chaining(self):
        # given
        inputs = {0: 2.0, 1: 3.0}
        # when
        outputs = self.layer.run(inputs)
        # then
        # first layer outputs: '1' = 4.0, '2' = 6.0
        # second layer outputs: '3' = 1.0*4.0 + 1.5*6.0 = 13.0
        self.assertEqual(outputs, {3: 13.0})

    def test_optimize_for_non_redundant_network(self):
        # given
        # all sources of first layer are always forward reachable
        source_ids = {0, 1}
        # when
        used_sources = self.layer.optimize(source_ids)
        # then
        # as there are no unused connections / unreachable neurons
        # nothing changes
        self.assertIn(2, self.layer._connections)
        self.assertIn(1, self.layer._connections)
        self.assertIn(3, self.next_layer._connections)
        self.assertSetEqual(used_sources, source_ids)

    def test_optimize_for_redundant_network(self):
        # given
        source_ids = {0, 1, 2}  # always forward reachable
        connections = {
            2: [(0, 2.0)],
            3: [(0, 2.0), (1, 2.0)],
            4: [(1, 2.0), (2, 2.0)]
            # no connections to '4' in the next layer
            # source '2' only feeds '4'
        }
        next_layer_connections = {
            1: [(1, 1.0), (2, 1.0), (3, 1.0)],
            # connection to '1' that does not exist in previous layer
            2: [(1, 1.0)],
            # '2' is only connected to nonexistent '1'
            3: [(2, 1.0), (3, 1.0)]
        }
        layer = Layer(connections)
        next_layer = Layer(next_layer_connections)
        layer.next(next_layer)
        # when
        used_sources = layer.optimize(source_ids)
        # then
        # deletes source '2' only
        self.assertNotIn(2, used_sources)
        self.assertIn(0, used_sources)
        self.assertIn(1, used_sources)
        # deletes connections to '4' in first layer, does not add '1'
        self.assertNotIn(4, layer._connections)
        self.assertNotIn(1, layer._connections)
        self.assertIn(2, layer._connections)
        self.assertIn(3, layer._connections)
        # deletes connections to '2' in second layer
        self.assertNotIn(2, next_layer._connections)
        self.assertIn(1, next_layer._connections)
        self.assertIn(3, next_layer._connections)
        # deletes connection between nonexistent '1' in frst layer and '1' in second layer
        self.assertNotIn((1, 1.0), next_layer._connections.get(1))

    def test_mark_reachable(self):
        # given
        reached_ids = {0, 7}
        # when
        marked = self.layer._mark_reachable(reached_ids)
        # then
        # '1' is reachable (depends on source '0')
        # '2' is not reachable (depends on source '1' that was not marked reachable)
        self.assertIn(1, marked)
        self.assertNotIn(2, marked)

    def test_prune_unmarked(self):
        # given
        marked = {2}
        # when
        backward_reachable = self.layer._prune_unmarked(marked)
        # then
        # Only '2' should remain in connections
        self.assertIn(2, self.layer._connections)
        self.assertNotIn(1, self.layer._connections)
        # Backward reachable sources for '2' are '1'
        self.assertEqual(backward_reachable, {1})


class TestLateralConnections(TestCase):
    def setUp(self):
        self.connections = {
            1: [(0, 0.5), (1, 1.0)],
            2: [(1, 2.0)],
        }
        self.layer = Layer(self.connections)

        self.lateral_connections = {
            2: [(1, 0.5), (2, 1.0)],  # '1' pushes to '2' and self-loop on '2'
        }
        self.lateral_layer = LateralConnections(self.lateral_connections)
        self.lateral_layer.add_activation_func(tanh)

        self.next_layer_connections = {
            3: [(1, 1.5), (2, 1.0)]
        }
        self.next_layer = Layer(self.next_layer_connections)
        self.layer.next(self.lateral_layer).next(self.next_layer)

    def test_process_with_lateral(self):
        # given
        inputs = {1: 2.0, 2: 3.0}
        self.lateral_layer._activation_func = None
        # when
        self.lateral_layer._process(inputs)
        # then
        # lateral connection from '1' to '2' adds 0.5*2.0 = 1.0
        # self-loop on '2' adds 1.0*3.0 = 3.0
        # final: '2' = 3.0 + 1.0 + 3.0 = 7.0
        #        '1' = 2.0 (not changed)
        self.assertEqual(self.lateral_layer._outputs[1], 2.0)
        self.assertEqual(self.lateral_layer._outputs[2], 7.0)

    def test_run_with_activation(self):
        # given
        inputs = {0: 1.0, 1: 2.0}
        # when
        outputs = self.layer.run(inputs)
        # then
        # first layer:
        # '1' = 1.0*2.0 + 0.5*1.0 = 2.5, '2' = 2.0*2.0 = 4.0
        # lateral connection from '1' to '2' adds 0.5*2.5 = 1.25
        # self-loop on '2' adds 1.0*4.0 = 4.0
        # final: '2' = 4.0 + 4.0 + 1.25 = 9.25-> tanh -> 0.999999981525...
        #        '1' = 2.5 -> tanh -> 0.9866143...
        # next layer:
        # '3' = 1.0*tanh(9.25) + 1.5*tanh(2.5) = 2.4799...
        self.assertIn(3, outputs)
        self.assertAlmostEqual(1.0 * tanh(9.25) + 1.5 * tanh(2.5), outputs.get(3), 4)

    def test_optimize_for_non_redundant_network(self):
        # given
        source_ids = {0, 1}  # always forward reachable
        initial_lateral_connections = {2: [(1, 0.5), (2, 1.0)]}
        # when
        self.layer.optimize(source_ids)
        # then
        # nothing changes in lateral layer
        self.assertDictEqual(initial_lateral_connections, self.lateral_layer._connections)

    def test_optimize_for_redundant_network(self):
        # given
        source_ids = {0, 1, 2}  # always forward reachable
        connections = {
            2: [(0, 2.0)],
            3: [(0, 2.0), (1, 2.0)],
            4: [(1, 2.0), (2, 2.0)]
            # no connections to '4' in the next layer
            # source '2' only feeds '4'
        }
        lateral_connections = {
            1: [(2, 1.5)],
            2: [(1, 0.5)],
            # '1' is not connected with any source
            3: [(3, 1.5), (0, 1.0)],
            # '0' is not connected with any source
            4: [(3, 0.5), (4, 1.5)],
            # '4' is not connected in th nxt layer
            5: [(3, 2.0)]
        }
        next_layer_connections = {
            0: [(0, 2.0)],
            # connection to '0' that's not fed by any source
            1: [(1, 1.0), (2, 1.0), (3, 1.0)],
            # connection to '1' that is not
            2: [(1, 1.0), (5, 2.0)],
            # '2' is only connected to nonexistent '1'
            3: [(2, 1.0), (3, 1.0), (0, 0.5)]
        }
        layer = Layer(connections)
        lateral_layer = LateralConnections(lateral_connections)
        next_layer = Layer(next_layer_connections)
        layer.next(lateral_layer).next(next_layer)
        # when
        used_sources = layer.optimize(source_ids)
        # then
        # deletes source '2' only
        self.assertNotIn(2, used_sources)
        self.assertIn(0, used_sources)
        self.assertIn(1, used_sources)
        # deletes connections to '4' in first layer, does not add '1' or '5'
        self.assertNotIn(4, layer._connections)
        self.assertNotIn(1, layer._connections)
        self.assertNotIn(5, layer._connections)
        self.assertIn(2, layer._connections)
        self.assertIn(3, layer._connections)
        # deletes '4', '0' and '2' from lateral layer, does not delete '1' or '5'
        self.assertNotIn(0, lateral_layer._connections)
        self.assertNotIn(4, lateral_layer._connections)
        self.assertNotIn(2, lateral_layer._connections)
        self.assertIn(1, lateral_layer._connections)
        self.assertIn(5, lateral_layer._connections)
        # deletes connection between '0' and '3' in lateral layer
        self.assertNotIn((0, 1.0), lateral_layer._connections.get(3))
        # deletes connections to '0' in second layer
        self.assertNotIn(0, next_layer._connections)
        self.assertIn(1, next_layer._connections)
        self.assertIn(3, next_layer._connections)
        # deletes connection between '0' and '3' in second layer
        self.assertNotIn((0, 0.5), next_layer._connections.get(3))

    def test_prune_unmarked_with_self_loops(self):
        # given
        marked = {2}
        # when
        backward_reachable = self.lateral_layer._prune_unmarked(marked)
        # then
        # connections are still there
        self.assertIn(2, self.lateral_layer._connections)
        self.assertIn((1, 0.5), self.lateral_layer._connections.get(2))
        self.assertIn((2, 1.0), self.lateral_layer._connections.get(2))
        # both marked as reachable
        self.assertIn(1, backward_reachable)
        self.assertIn(2, backward_reachable)


def make_redundant_network():
    connections = {
        2: [(0, 2.1)],
        3: [(0, 1.3), (1, 0.4)],
        4: [(1, 0.5), (2, 1.5), (3, 1.75)]
        # no connections to '4' in the next layer
        # source '3' and '2' only feeds '4'
    }
    last_layer_connections = {
        0: [(0, 2.0)],
        # connection to '0' that's not fed by any source
        1: [(1, 1.0), (2, 1.0), (3, 1.0)],
        # connection from '1' that is nonexistent in first layer
        2: [(1, 1.0), (5, 2.0)],
        # '2' is only connected to nonexistent '1' and '5'
        3: [(2, 1.0), (3, 1.0), (0, 0.5)]
    }

    first_layer = Layer(connections)
    last_layer = Layer(last_layer_connections)
    return first_layer, last_layer


class TestDirectConnections(TestCase):
    def set_up_simple_network(self):
        self.direct_connections = {
            3: [(0, 0.5)],
            4: [(2, 2.0)],
        }
        self.direct_layer = DirectConnections(self.direct_connections)
        self.direct_layer.add_activation_func(tanh)

        self.connections = {
            1: [(0, 0.5), (1, 1.0)],
            2: [(1, 2.0)],
        }
        self.first_layer = Layer(self.connections)

        self.last_layer_connections = {
            3: [(1, 1.5), (2, 1.0)]
        }
        self.last_layer = Layer(self.last_layer_connections)
        self.direct_layer.next(self.first_layer).next(self.last_layer)
        # visualize_neural_network(self.direct_layer.get_network())

    def test_run_for_simple_network_with_activation(self):
        # given
        self.set_up_simple_network()
        inputs = {0: 1.0, 1: 2.0, 2: 1.5}
        # when
        outputs = self.direct_layer.run(inputs)
        # then
        # first layer:
        # '1' = 1.0*0.5 + 2.0*1.0 = 2.5, '2' = 2.0*2.0 = 4.0
        # last layer:
        # '3' = 2.5*1.5 + 4.0*1.0 = 7.75
        # direct connections:
        # from sensor '0' to final '3' adds 1.0*0.5 = 0.5
        # from sensor '2' to final '4' adds 1.5*2.0 = 3.0
        # final:
        # '3' = 7.75 + 0.5 = 8.25 -> tanh -> 0.999999863488...
        # '4' = 3.0 -> tanh -> 0.9950547536867305
        self.assertIn(3, outputs)
        self.assertIn(4, outputs)
        self.assertAlmostEqual(tanh(8.25), outputs.get(3))
        self.assertAlmostEqual(tanh(3.0), outputs.get(4))

    def test_optimize_for_redundant_network(self):
        # given
        source_ids = {0, 1, 2, 3, 4, 5}  # always forward reachable
        direct_connections = {
            1: [(0, 1.5), (5, 0.5)],
            2: [(2, 2.5)],
            4: [(4, 1.2)]
        }
        direct_layer = DirectConnections(direct_connections)
        first_layer, last_layer = make_redundant_network()
        direct_layer.next(first_layer).next(last_layer)

        expected_first_layer, expected_last_layer = make_redundant_network()
        expected_first_layer.next(expected_last_layer)
        expected_first_layer.optimize(source_ids)
        initial_direct_connections = direct_connections.copy()

        # when
        used_sources = direct_layer.optimize(source_ids)
        # then
        # deletes source '3' only
        self.assertSetEqual({0, 1, 2, 4, 5}, used_sources)
        # optimization for inner layers is the same
        # no matter if they're in sequence with direct layer
        self.assertDictEqual(expected_first_layer._connections, first_layer._connections)
        self.assertDictEqual(expected_last_layer._connections, last_layer._connections)
        # direct connections stay the same
        self.assertDictEqual(initial_direct_connections, direct_layer._connections)

    def test_run_for_optimized_redundant_network(self):
        # given
        source_ids = {0, 1, 2, 3, 4, 5}
        inputs = {source: 1.0 for source in source_ids}
        direct_connections = {
            1: [(0, 1.5), (5, 0.5)],
            2: [(2, 2.5)],
            4: [(4, 1.2)]
        }
        direct_layer = DirectConnections(direct_connections)
        first_layer, last_layer = make_redundant_network()
        direct_layer.next(first_layer).next(last_layer)
        direct_layer.optimize(source_ids)
        expected_result = {1: 5.8, 2: 2.5, 3: 3.8, 4: 1.2}
        # when
        result = direct_layer.run(inputs)
        # then
        self.assertNotIn(0, result)
        self.assertIn(1, result)
        self.assertIn(2, result)
        self.assertIn(3, result)
        self.assertIn(4, result)
        for key in result:
            self.assertAlmostEqual(expected_result.get(key), result.get(key))


def get_network_without_direct_layer():
    connections = {
        2: [(0, 2.0)],
        3: [(0, 2.0), (1, 2.0)],
        4: [(1, 2.0), (2, 2.0)]
        # no connections to '4' in the next layer
        # source '2' only feeds '4'
    }
    lateral_connections = {
        1: [(2, 1.5)],
        2: [(1, 0.5)],
        # '1' is not connected with any source
        3: [(3, 1.5), (0, 1.0)],
        # '0' is not connected with any source
        4: [(3, 0.5), (4, 1.5)],
        # '4' is not connected in th nxt layer
        5: [(3, 2.0)]
    }
    next_layer_connections = {
        0: [(0, 2.0)],
        # connection to '0' that's not fed by any source
        1: [(1, 1.0), (2, 1.0), (3, 1.0)],
        2: [(1, 1.0), (5, 2.0)],
        3: [(2, 1.0), (3, 1.0), (0, 0.5)]
        # connection to '0' that's not fed by any source

    }
    layer = Layer(connections)
    lateral_layer = LateralConnections(lateral_connections)
    next_layer = Layer(next_layer_connections)
    return lateral_layer, layer, next_layer


def get_network_with_empty_lateral_connections():
    source_ids = {0, 1, 2, 3, 4, 5}  # always forward reachable
    direct_connections = {
        1: [(0, 1.5), (5, 0.5)],
        2: [(2, 2.5)],
        4: [(4, 1.2)]
    }
    direct_layer = DirectConnections(direct_connections)
    first_layer, last_layer = make_redundant_network()
    direct_layer.next(first_layer).next(LateralConnections()).next(last_layer)
    # visualize_neural_network(direct_layer.get_network())
    return direct_layer, first_layer, last_layer, source_ids


class TestNetworksWithEmptyLayers(TestCase):
    def test_optimize_with_empty_lateral(self):
        # given
        direct_layer, first_layer, last_layer, source_ids = get_network_with_empty_lateral_connections()
        expected_first_layer, expected_last_layer = make_redundant_network()
        expected_first_layer.next(expected_last_layer)
        expected_first_layer.optimize(source_ids)
        initial_direct_connections = direct_layer._connections.copy()

        # when
        used_sources = direct_layer.optimize(source_ids)
        # then
        # visualize_neural_network(direct_layer.get_network())
        # deletes source '3' only
        self.assertNotIn(3, used_sources)
        self.assertSetEqual({0, 1, 2, 4, 5}, used_sources)
        # optimization for inner layers is the same
        # no matter if they're in sequence with direct layer
        self.assertDictEqual(expected_first_layer._connections, first_layer._connections)
        self.assertDictEqual(expected_last_layer._connections, last_layer._connections)
        # direct connections stay the same
        self.assertDictEqual(initial_direct_connections, direct_layer._connections)

    def test_optimize_with_empty_direct(self):
        # given
        source_ids = {0, 1, 2}  # always forward reachable
        direct_layer = DirectConnections()
        lateral_layer, first_layer, next_layer = get_network_without_direct_layer()
        direct_layer.next(first_layer).next(lateral_layer).next(next_layer)
        # visualize_neural_network(direct_layer.get_network())
        # when
        used_sources = direct_layer.optimize(source_ids)
        # then
        # visualize_neural_network(direct_layer.get_network())
        # deletes source '2' only
        self.assertNotIn(2, used_sources)
        self.assertIn(0, used_sources)
        self.assertIn(1, used_sources)
        # deletes connections to '4' in first first_layer, does not add '1' or '5'
        self.assertNotIn(4, first_layer._connections)
        self.assertNotIn(1, first_layer._connections)
        self.assertNotIn(5, first_layer._connections)
        self.assertIn(2, first_layer._connections)
        self.assertIn(3, first_layer._connections)
        # deletes '4', '0' and '2' from lateral first_layer, does not delete '1' or '5'
        self.assertNotIn(0, lateral_layer._connections)
        self.assertNotIn(4, lateral_layer._connections)
        self.assertNotIn(2, lateral_layer._connections)
        self.assertIn(1, lateral_layer._connections)
        self.assertIn(5, lateral_layer._connections)
        # deletes connection between '0' and '3' in lateral first_layer
        self.assertNotIn((0, 1.0), lateral_layer._connections.get(3))
        # deletes connections to '0' in second first_layer
        self.assertNotIn(0, next_layer._connections)
        self.assertIn(1, next_layer._connections)
        self.assertIn(3, next_layer._connections)
        # deletes connection between '0' and '3' in second first_layer
        self.assertNotIn((0, 0.5), next_layer._connections.get(3))

    def test_run_with_empty_lateral(self):
        # given
        source_ids = {0, 1, 2, 3, 4, 5}
        inputs = {source: 1.0 for source in source_ids}
        direct_connections = {
            1: [(0, 1.5), (5, 0.5)],
            2: [(2, 2.5)],
            4: [(4, 1.2)]
        }
        direct_layer = DirectConnections(direct_connections)
        first_layer, last_layer = make_redundant_network()
        direct_layer.next(first_layer).next(LateralConnections()).next(last_layer)
        # visualize_neural_network(direct_layer.get_network())
        direct_layer.optimize(source_ids)
        # visualize_neural_network(direct_layer.get_network())
        expected_result = {1: 5.8, 2: 2.5, 3: 3.8, 4: 1.2}
        # when
        result = direct_layer.run(inputs)
        # then
        self.assertNotIn(0, result)
        self.assertIn(1, result)
        self.assertIn(2, result)
        self.assertIn(3, result)
        self.assertIn(4, result)
        for key in result:
            self.assertAlmostEqual(expected_result.get(key), result.get(key))

    def test_run_with_empty_direct(self):
        # given
        source_ids = {0, 1, 2}
        direct_layer = DirectConnections()
        lateral_layer, first_layer, next_layer = get_network_without_direct_layer()
        direct_layer.next(first_layer).next(lateral_layer).next(next_layer)

        # visualize_neural_network(direct_layer.get_network())
        used_surces = direct_layer.optimize(source_ids)
        inputs = {source: 1.0 for source in used_surces}
        # visualize_neural_network(direct_layer.get_network())

        exp_lateral_layer, exp_first_layer, exp_next_layer = get_network_without_direct_layer()
        exp_first_layer.next(exp_lateral_layer).next(exp_next_layer)
        exp_first_layer.optimize(source_ids)
        expected_result = exp_first_layer.run(inputs)

        # when
        result = direct_layer.run(inputs)
        # then
        self.assertDictEqual(expected_result, result)
