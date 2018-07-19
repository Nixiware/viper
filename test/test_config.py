import sys
sys.path.append(".")

import unittest

from nx.viper.config import Config


class ConfigTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_configurationMerge(self):
        dict1 = {"key1": "value1"}
        dict2 = {"key2": "value2"}
        dict3 = {"key3": "value3"}

        merged1 = Config.mergeDictionaries(dict1, dict2)
        merged2 = Config.mergeDictionaries(merged1, dict3)

        # length
        self.assertEqual(len(merged2), 3)

        # items existance
        self.assertIn("key1", merged2)
        self.assertIn("key2", merged2)
        self.assertIn("key3", merged2)

        # items values
        self.assertEqual(merged2["key1"], "value1")
        self.assertEqual(merged2["key2"], "value2")
        self.assertEqual(merged2["key3"], "value3")
