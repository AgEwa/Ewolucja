import unittest

from population.test_Sensor import TestSensor
from population.test_Specimen import TestSpecimen
from utils.test_utils import TestUtils
from world.test_Grid import TestGrid


def run_all_tests():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    suite.addTest(loader.loadTestsFromTestCase(TestSensor))
    suite.addTest(loader.loadTestsFromTestCase(TestSpecimen))
    suite.addTest(loader.loadTestsFromTestCase(TestUtils))
    suite.addTest(loader.loadTestsFromTestCase(TestGrid))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == '__main__':
    run_all_tests()
