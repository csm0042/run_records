#!/usr/bin/python3
""" mysql.py: Class and methods to connect to and query a mySQL database
"""

# Import Required Libraries (Standard, Third Party, Local) ********************
import asyncio
import copy
import datetime
import csv
import os
import re
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
async def import_tomtom_records(folder, database, logger):
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
                    activity_ptr = 99
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
                                if val.lower() == "activitytype":
                                    activity_ptr = copy.copy(i)
                                    logger.debug(
                                        'Found distance at column [%s]', str(activity_ptr))
                                if val.lower() == "distance":
                                    distance_ptr = copy.copy(i)
                                    logger.debug(
                                        'Found distance at column [%s]', str(distance_ptr))
                                if val.lower() == "speed":
                                    speed_ptr = copy.copy(i)
                                    logger.debug(
                                        'Found distance at column [%s]', str(speed_ptr))
                                if val.lower() == "calories":
                                    calories_ptr = copy.copy(i)
                                    logger.debug(
                                        'Found distance at column [%s]', str(calories_ptr))
                                if val.lower() == "lat":
                                    latitude_ptr = copy.copy(i)
                                    logger.debug(
                                        'Found distance at column [%s]', str(latitude_ptr))
                                if val.lower() == "long":
                                    longitude_ptr = copy.copy(i)
                                    logger.debug(
                                        'Found distance at column [%s]', str(longitude_ptr))
                                if val.lower() == "elevation":
                                    elevation_ptr = copy.copy(i)
                                    logger.debug(
                                        'Found distance at column [%s]', str(elevation_ptr))
                                if val.lower() == "heartrate":
                                    heartrate_ptr = copy.copy(i)
                                    logger.debug(
                                        'Found distance at column [%s]', str(heartrate_ptr))
                        else:
                            seconds = int(row[datetime_ptr])
                            logger.debug(
                                'Importing row with timestamp: %s',
                                str(dt_start + datetime.timedelta(seconds=int(seconds))))
                            query = ("INSERT INTO run_log "
                                     "(datetime, activitytype, distance, speed, calories, "
                                     "latitude, longitude, elevation, heartrate) "
                                     "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);")
                            data = (
                                str(dt_start + datetime.timedelta(seconds=int(seconds))),
                                row[activity_ptr],
                                row[distance_ptr],
                                row[speed_ptr],
                                row[calories_ptr],
                                row[latitude_ptr],
                                row[longitude_ptr],
                                row[elevation_ptr],
                                row[heartrate_ptr])
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
                        r'T([0-2][0-9])([0-6][0-9])([0-6][0-9])\.'
    dt_match = re.search(dt_regex, filename)
    if dt_match is not None:
        date = datetime.date(int(dt_match.group(1)), int(dt_match.group(2)), int(dt_match.group(3)))
        time = datetime.time(int(dt_match.group(4)), int(dt_match.group(5)), int(dt_match.group(6)))
        dt = datetime.datetime.combine(date, time)
    else:
        dt = None
    return dt

