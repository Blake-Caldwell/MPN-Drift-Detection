# unit lib includes
import unittest
from unittest.mock import mock_open, patch

# lib includes
import os
import yaml

# our includes
from src.config.config import Config


class TestConfigMethods(unittest.TestCase):
    def setUp(self):
        self.file_name = "testing/test.yaml"
        self.test_data = {
            "BOOL": True,
            "STRING": "STRING",
            "ARRAY": ["Item 1", "Item 2"],
            "INT": 8000,
        }

    def test_init(self):
        config = Config(self.file_name)
        self.assertEqual(config.FILE_NAME, self.file_name)
        self.assertEqual(config.data, self.test_data)

    def test_load_data(self):
        with patch("builtins.open", mock_open(read_data=yaml.dump(self.test_data))):
            config = Config(self.file_name)
            self.assertEqual(config.data, self.test_data)

    def test_getitem(self):
        config = Config(self.file_name)
        self.assertEqual(config["BOOL"], True)
        self.assertEqual(config["STRING"], "STRING")
        self.assertEqual(config["ARRAY"], ["Item 1", "Item 2"])
        self.assertEqual(config["INT"], 8000)


if __name__ == "__main__":
    unittest.main()
