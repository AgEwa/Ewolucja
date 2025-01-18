import unittest

from evolution.test_Operators import TestOperators
from population.test_Layer import *
from population.test_NeuralNetwork import TestNeuralNetwork, TestDecodeConnection
from population.test_Sensor import TestSensor
from population.test_Specimen import TestSpecimen
from utils.test_Save import TestSingleSaving, TestWriterSaving
from utils.test_utils import TestUtils
from world.test_Grid import TestGrid
from world.test_Pheromones import TestPheromones


def run_all_tests():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    suite.addTest(loader.loadTestsFromTestCase(TestSensor))
    suite.addTest(loader.loadTestsFromTestCase(TestSpecimen))
    suite.addTest(loader.loadTestsFromTestCase(TestUtils))
    suite.addTest(loader.loadTestsFromTestCase(TestGrid))
    suite.addTest(loader.loadTestsFromTestCase(TestHelpFunctions))
    suite.addTest(loader.loadTestsFromTestCase(TestLayer))
    suite.addTest(loader.loadTestsFromTestCase(TestLateralConnections))
    suite.addTest(loader.loadTestsFromTestCase(TestDirectConnections))
    suite.addTest(loader.loadTestsFromTestCase(TestNetworksWithEmptyLayers))
    suite.addTest(loader.loadTestsFromTestCase(TestDecodeConnection))
    suite.addTest(loader.loadTestsFromTestCase(TestNeuralNetwork))
    suite.addTest(loader.loadTestsFromTestCase(TestOperators))
    suite.addTest(loader.loadTestsFromTestCase(TestPheromones))
    suite.addTest(loader.loadTestsFromTestCase(TestSingleSaving))
    suite.addTest(loader.loadTestsFromTestCase(TestWriterSaving))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == '__main__':
    run_all_tests()
