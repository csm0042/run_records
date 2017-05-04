#!/usr/bin/python3
""" mysql.py: Class and methods to connect to and query a mySQL database
"""

# Import Required Libraries (Standard, Third Party, Local) ********************
import asyncio
import datetime
import csv
import os
import shutil
import mysql.connector
import mysql.connector.errorcode as errorcode
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
async def import_tomtom_records(folder, logger):
    """ Monitors folder for run capture files to import """
    logger.info('Starting tomtom import script on folder: %s', folder)
    # Set up archive directory for processed files
    archive_dir = os.path.join(folder, "archive")
    logger.info('Setting up archive folder at: %s', archive_dir)
    # Search capture dir for capture files
    dir_contents = os.listdir(folder)
    logger.info('Found the following in capture folder: %s', dir_contents)

    # Count files in found contents (ignore directories)
    file_count = 0
    for item in dir_contents:
        if os.path.isfile(os.path.join(folder, item)):
            file_count += 1
    # Import records from found files
    if file_count > 0:
        logger.info('Found [%s] files to import', str(file_count))
        for file in dir_contents:
            if os.path.isfile(os.path.join(folder, file)):
                logger.info('Importing records from: [%s]', str(os.path.join(folder, file)))
                with open((os.path.join(folder, file)), newline='') as csvfile:
                    csvr = csv.reader(csvfile)
                    for row in csvr:
                        logger.debug('Importing: %s', row)
                logger.info('Moving file [%s] to archive folder after processing', str(os.path.join(folder, file)))
                move_file(file, folder, archive_dir, logger)



def move_file(filename, source_dir, dest_dir, logger):
    try:
        if os.path.isfile(os.path.join(source_dir, filename)):
            shutil.move(
                os.path.join(source_dir, filename),
                os.path.join(dest_dir, filename)
                )
            logger.info('Successfully moved capture file')
    except:
        logger.warning('Oh crap, couldn\'t remove the requested file')
