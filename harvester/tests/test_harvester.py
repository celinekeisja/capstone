import unittest
from harvester import *
from os import path


class TestFolder(unittest.TestCase):
    """Tests for `harvester.py`."""
    def test_folder_exists(self):
        self.assertTrue(str(path.exists('harvest_files')))

    def test_folder_type(self):
        self.assertFalse(str(path.isfile('harvest_files')))


if __name__ == '__main__':
    unittest.main()
