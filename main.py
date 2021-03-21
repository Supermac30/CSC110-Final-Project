"""Holds the main function

This file is Copyright (c) 2020 Mark Bedaywi
"""
import logging

from menu import MenuManager
from dataset import DataSet

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    data_set = DataSet()
    menus = MenuManager(data_set)

    logging.info("Done Initialising app!")

    is_done = menus.loop()
    while not is_done:
        is_done = menus.loop()
