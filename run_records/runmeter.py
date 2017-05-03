#!/usr/bin/python3
""" mysql.py: Class and methods to connect to and query a mySQL database
"""

# Import Required Libraries (Standard, Third Party, Local) ********************
import asyncio
import datetime
import csv
import logging
import mysql.connector
import mysql.connector.errorcode as errorcode
import os
import shutil
import run_records


# Authorship Info *************************************************************
__author__ = "Christopher Maue"
__copyright__ = "Copyright 2017, The rpihome Project"
__credits__ = ["Christopher Maue"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Christopher Maue"
__email__ = "csmaue@gmail.com"
__status__ = "Development"


# Main event loop function ****************************************************
async def import_runmeter_records(folder, logger):
    """ Monitors folder for run capture files to import """
    file_count = 0
    # Search capture dir for capture files
    dir_contents = os.listdir(folder)
    # Count files in found contents (ignore directories)
    for item in dir_contents:
        if os.path.isfile(os.path.join(folder, item)):
            file_count += 1
    if file_count > 0:
        logger.debug('Found [%s] files to import', str(file_count))
        for file in dir_contents:
            with open((os.path.join(folder, file)), newline='') as csvfile:
                csvr = csv.reader(csvfile)
                for row in csvr:
                    print(row)
