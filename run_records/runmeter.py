#!/usr/bin/python3
""" mysql.py: Class and methods to connect to and query a mySQL database
"""

# Import Required Libraries (Standard, Third Party, Local) ********************
import asyncio
import copy
import datetime
import csv
import logging
import mysql.connector
import mysql.connector.errorcode as errorcode
import os
import re
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
async def import_runmeter_records(folder, database, logger):
    """ Monitors folder for run capture files to import """
    logger.info('Starting tomtom import script on folder: %s', folder)
    # Set up archive directory for processed files
    archive_dir = os.path.join(folder, "archive")
    os.makedirs(archive_dir, exist_ok=True)
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
        cursor = database.cursor()
        # Loop though files
        for file in dir_contents:
            if os.path.isfile(os.path.join(folder, file)):
                # Extract date and time from filename
                dt_start = get_dt_from_filename(file)
                logger.info('File datetime: %s', str(dt_start))
                # Import individual records from file
                logger.info('Importing records from: [%s]', str(os.path.join(folder, file)))
                with open((os.path.join(folder, file)), newline='') as csvfile:
                    csvr = csv.reader(csvfile)
                    # Set default pointer values for field headers
                    datetime_ptr = 0
                    activitytyp_ptr = 99
                    distance_ptr = 8
                    speed_ptr = 12
                    calories_ptr = 17
                    latitude_ptr = 5
                    longitude_ptr = 6
                    elevation_ptr = 7
                    heartrate_ptr = 99
                    # Process rows in file
                    for index, row in enumerate(csvr):
                        if index == 0:
                            for i, val in enumerate(row):
                                if val.lower() == "time":
                                    datetime_ptr = copy.copy(i)
                                    logger.debug(
                                        'Found datetime at column [%s]', str(datetime_ptr))
                                if val.lower() == "distance (miles)":
                                    distance_ptr = copy.copy(i)
                                    logger.debug(
                                        'Found distance at column [%s]', str(distance_ptr))
                                if val.lower() == "speed (mph)":
                                    speed_ptr = copy.copy(i)
                                    logger.debug(
                                        'Found distance at column [%s]', str(speed_ptr))
                                if val.lower() == "calories":
                                    calories_ptr = copy.copy(i)
                                    logger.debug(
                                        'Found distance at column [%s]', str(calories_ptr))
                                if val.lower() == "latitude":
                                    latitude_ptr = copy.copy(i)
                                    logger.debug(
                                        'Found distance at column [%s]', str(latitude_ptr))
                                if val.lower() == "longtude":
                                    longitude_ptr = copy.copy(i)
                                    logger.debug(
                                        'Found distance at column [%s]', str(longitude_ptr))
                                if val.lower() == "elevation":
                                    elevation_ptr = copy.copy(i)
                                    logger.debug(
                                        'Found distance at column [%s]', str(elevation_ptr))
                                if val.lower() == "heart rate (bpm)":
                                    heartrate_ptr = copy.copy(i)
                                    logger.debug(
                                        'Found distance at column [%s]', str(heartrate_ptr))
                        else:
                            logger.debug(
                                'Importing row with timestamp: %s',
                                str(datetime.datetime.strptime(
                                    row[datetime_ptr], '%Y-%m-%d %H:%M:%S')))
                            query = ("INSERT INTO run_log "
                                     "(datetime, activitytype, distance, speed, calories, "
                                     "latitude, longitude, elevation, heartrate) "
                                     "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);")
                            data = (
                                str(datetime.datetime.strptime(
                                    row[datetime_ptr], '%Y-%m-%d %H:%M:%S')),
                                '0',
                                str(float(row[distance_ptr]) * 1609.34),
                                str(float(row[speed_ptr]) * 0.44704),
                                row[calories_ptr],
                                row[latitude_ptr],
                                row[longitude_ptr],
                                row[elevation_ptr],
                                heartrate(heartrate_ptr, row)
                                )
                            logger.debug(query % data)
                            try:
                                cursor.execute(query, data)
                            except:
                                logger.warning(
                                    'Could not execute query [%s]', (query % data))

                # Move file so it's not processed again
                logger.info(
                    'Moving file [%s] to archive folder after processing',
                    str(os.path.join(folder, file)))
                move_file(file, folder, archive_dir, logger)
        # Commit changes to database and close connection
        database.commit()
        cursor.close()


def heartrate(ptr, row):
    if ptr != 99:
        return row[ptr]
    else:
        return ""


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


def get_dt_from_filename(filename):
    dt_regex = r'\b-([2][0][0-9][0-9])([0-1][0-9])([0-3][0-9])' \
                        r'-([0-1][0-9])([0-6][0-9])\.'
    dt_match = re.search(dt_regex, filename)
    if dt_match is not None:
        date = datetime.date(int(dt_match.group(1)), int(dt_match.group(2)), int(dt_match.group(3)))
        time = datetime.time(int(dt_match.group(4)), int(dt_match.group(5)), 0)
        dt = datetime.datetime.combine(date, time)
    else:
        dt = None
    return dt