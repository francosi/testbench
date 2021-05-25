import unittest
import sys
sys.path.append('..')
from module_scenario import (get_scenario, check_scenario_keys)


class Test_module_scenario(unittest.TestCase):

    def test_get_scenario_file_not_found(self):
        scenario = get_scenario('no_file.json')
        self.assertIsNone(scenario)

    def test_get_scenario_file_found(self):
        scenario = get_scenario('../scenario.json')
        self.assertIsNotNone(scenario)

    def test_get_scenario_bad_json(self):
        scenario = get_scenario('ressources/lorem_ipsum.txt')
        self.assertIsNone(scenario)

    def test_get_scenario_bad_keys(self):
        scenario = get_scenario('ressources/bad_keys.json')
        self.assertFalse(check_scenario_keys(scenario))

    def test_get_scenario_good_keys(self):
        scenario = get_scenario('../scenario.json')
        self.assertTrue(check_scenario_keys(scenario))
