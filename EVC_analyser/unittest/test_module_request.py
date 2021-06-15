import unittest
import sys
sys.path.append('..')
from module_request import (get_measure, get_log, get_start, get_config, change_config, get_bearer)


class Test_module_request(unittest.TestCase):

    def test_get_bearer(self):
        bearer = get_bearer('../bearer.txt')
        self.assertIsNotNone(bearer)

    def test_get_log(self):
        bearer = get_bearer('../bearer.txt')
        log = get_log('2004E2', bearer)
        self.assertIsNotNone(log)

    def test_get_start(self):
        bearer = get_bearer('../bearer.txt')
        log = get_log('2004E2', bearer)
        self.assertIsNotNone(get_start(log))

    def test_get_config(self):
        bearer = get_bearer('../bearer.txt')
        conf = get_config('2004E2', bearer)
        self.assertIsNotNone(conf)

    def test_get_measure(self):
        bearer = get_bearer('../bearer.txt')
        mes = get_measure('2004E2', bearer)
        self.assertIsNotNone(mes)

    def test_change_config(self):
        bearer = get_bearer('../bearer.txt')
        conf = get_config('1D89FDB', bearer)
        # conf['actuatorConfig']['agenda']['duration'] = '1'
        self.assertTrue(change_config('2004E2', bearer, conf))
