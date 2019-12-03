from os import path

from harvest.harvest import *


def test_folder_exists():
    folder()
    assert str(path.exists('harvest_files')) == 'True'


def test_folder_type(self):
    folder()
    assert str(path.isfile('harvest_files')) == 'False'
