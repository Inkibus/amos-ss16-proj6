#!/usr/bin/env python

#   This file is part of Rogue Vision.
#
#   Copyright (C) 2016 Daniel Reischl, Rene Rathmann, Peter Tan,
#       Tobias Dorsch, Shefali Shukla, Vignesh Govindarajulu,
#       Aleksander Penew, Abhinav Puri
#
#   Rogue Vision is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Rogue Vision is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with Rogue Vision.  If not, see <http://www.gnu.org/licenses/>.

# @author AMOSus (Daniel)
# @author Inkibus (Rene)

# This script simulates all sensors of the production system, that are pushing their data for each timestamp to the
# processing unit. This script also serves the purpose of being the processing unit. It maps the drive data
# to different carriers.
# The script calls depending on the amount of drives and waitTime the CompressingAlgorithm all x seconds
# Input: CSV file with the following structure (ms; energy1;...;energyX; pos1;...;posX) (x = Amount of Drives)
# Output: CSV file for each carrier in each iteration with the following structure (time; posAbsolute; energy; drive)
# and the following name Session_X_Carrier_X_Iteration_X.csv

# IMPORTS
# Imports Pandas for Data handling
from __future__ import print_function
import pandas as pd
# Imports OS for Operating System independent absolute file paths
import os
# Imports numpy for Data handling
import numpy as np
# Imports sleep for sleeping
from time import sleep
# Imports sys to terminate the function
import sys
# Imports Csv to Manipulate Initial CSV-File
import csv
# Imports Logging to Log File
import logging
# Imports DataProcessingFunctions
import dataProcessingFunctions
# Imports ConfigParser
import ConfigParser


# Main data processing script. Gets input data of drives and maps it to the carries and saves them as CSV files once
# an iteration is complete
# Input: (time: int, drive: int, position: float, energy: float)
def processData(time, drive, position, energy):
    # Ensures that all modified global variables are called globally
    global iterationNumber
    global carrierData
    global lastPositionOfCarrier
    global currentPositionAtCarrierData

    # If the line has just started, then the first carrier enters the first drive and set iterationNumber to 1
    if iterationNumber == 0:
        print("line has just started: Carrier 1 at Drive 1")
        iterationNumber = 1
        driveXHasCarrier[0] = 1

    # Determine which carrier is currently on the drive
    carrier = int(driveXHasCarrier[drive - 1])

    # If the current drive doesnt have a carrier, it cannot be mapped
    if driveXHasCarrier[drive - 1] == 0:
        return

    # If the timestamp is the same as previously, the data is not recorded
    # This only happens when pushing carries which should not happen in the first place
    if time == carrierData[carrier - 1][0][currentPositionAtCarrierData[carrier - 1] - 1]:
        return

    # If position is zero and it wasn't 0 before, the carrier has left the drive and the drive needs to be reset
    if position == 0 and lastPositionOfCarrier[carrier - 1] != 0:
        #print("Drive " + str(drive) + " Carrier " + str(carrier) + " Time " + str(time))
        #print("Position  " + str(position))
        #print("Energy    " + str(energy))

        # Reset the drive
        evaluateDriveReset(drive, carrier)

        # Reset the last position of the carrier to 0
        lastPositionOfCarrier[carrier - 1] = 0

        # Process the timestamp that caused the drive reset
        # This needs to be done because of the position is 0, this means that the current carrier is not on the drive
        # anymore. Therefore this function is called again after the drive has been reset.
        processData(time, drive, position, energy)
        return

    if position != 0:
        # Ensures enough space in the carrierData array for storing the data
        ensureEnoughSpaceInCarrierData(carrier)

        # Transfer the time of the timeStamp to the carrierData
        carrierData[carrier - 1][0][currentPositionAtCarrierData[carrier - 1]] = time

        # Transfer position to the carrierData
        carrierData[carrier - 1][1][currentPositionAtCarrierData[carrier - 1]] = position

        # Transfer the energy of the timeStamp to the carrierData
        carrierData[carrier - 1][2][currentPositionAtCarrierData[carrier - 1]] = energy

        # Transfer energy consumption of the timeStamp to the carrierData
        carrierData[carrier - 1][3][currentPositionAtCarrierData[carrier - 1]] = drive

        # Transfer the time of the timeStamp for the absolute Time to the carrierData
        carrierData[carrier - 1][4][currentPositionAtCarrierData[carrier - 1]] = time

        # Saves current position for carrier for further processing
        lastPositionOfCarrier[carrier - 1] = position

        # Updates current position in the carrierData array, so that the next data point can be written to the next row
        currentPositionAtCarrierData[carrier - 1] += 1


# Checks if carrier X is currently somewhere on the belt
def carrierXOnBelt(carrier):
    for i in range(0, driveXHasCarrier.size):
        if driveXHasCarrier[i] == carrier or driveXHasCarrierWaiting[i] == carrier:
            return 1
    return 0


def evaluateDriveReset(drive, carrier):
    # Ensures that all modified global variables are called globally
    global driveXHasCarrier
    global iterationNumber
    global driveXHasCarrierWaiting
    global lastCarrierThatEnteredDriveOne

    # Prints out a message that the drive just restarted and which carrier will be leaving the drive
    #print("Drive " + str(drive) + " restarted, with carrier " + str(carrier))

    # Prints out state of carriers on each drive before the evaluation
    #print("Before moving carriers ")
    #print(driveXHasCarrier)

    # If this method is called because a carrier has been waiting to move to the next drive, then there may be the
    # possibility that in the meantime another carrier has entered the drive. So in this case the carrier doesn't leave
    # the drive.
    if drive == amountOfDrives or driveXHasCarrierWaiting[drive - 1 + 1] == 0:
        # The carrier leaves the drive, so the drive doesn't hold the carrier anymore
        driveXHasCarrier[drive - 1] = 0

    # If the carrier is at the last drive, the iteration can be completed
    if drive == amountOfDrives:
        completeIteration(carrier)
        # If all carriers went through the drives, the iteration is complete and the iterationNumber is increased
        if carrier == AMOUNT_OF_CARRIERS:
            iterationNumber += 1
        # If the carrier is carrier 1 and the first drive is empty put him on drive 1
        if driveXHasCarrier[0] == 0:
            # Put the carrier onto the first drive
            # print("Carrier " + str(carrier) + " gets pulled")
            driveXHasCarrier[0] = carrier
            lastCarrierThatEnteredDriveOne = carrier

    # The carrier moves to the next drive; Checks if there is a "next" drive
    if drive < amountOfDrives:
        # If the next drive isn't empty, the carrier gets put on the waiting list (driveXHasCarrierWaiting)
        if driveXHasCarrier[drive - 1 + 1] != 0:
            # Print conflict message
            # print("Carrier " + str(carrier) + " wants to go to drive " + str(drive + 1) + " ,but there is carrier " \
            #      + str(driveXHasCarrier[drive - 1 + 1]) + " on there")
            # Put the carrier on the waiting list for the next drive
            driveXHasCarrierWaiting[drive - 1 + 1] = carrier
            # Print current waiting list
            # print("Carriers waiting: " + str(driveXHasCarrierWaiting))
        else:
            # If the next drive is empty, the carrier moves to the next drive
            driveXHasCarrier[drive - 1 + 1] = carrier

    # If the current drive is drive 1, then a new carrier is pulled onto the drive 1
    if drive == 1:
        # If all carriers already passed the system, the first one enters again
        if lastCarrierThatEnteredDriveOne >= AMOUNT_OF_CARRIERS:
            lastCarrierThatEnteredDriveOne = 1

        # If not all the carrier have passed the system the next one enters
        else:
            # Increase the number of carriers that are in the system
            lastCarrierThatEnteredDriveOne += 1

        if carrierXOnBelt(lastCarrierThatEnteredDriveOne) == 1:
            # Can't put next carrier on drive because he is still on the drive
            # print("Carrier (" + str(
            #    lastCarrierThatEnteredDriveOne) + ") can't get pulled because he is still on the drive")
            driveXHasCarrier[drive - 1] = 0
        else:
            # Put next carrier on drive
            # print("A new carrier (" + str(lastCarrierThatEnteredDriveOne) + ") gets pulled onto drive 1")
            driveXHasCarrier[drive - 1] = lastCarrierThatEnteredDriveOne

    # If the current drive isn't 1 and it has a carrier waiting to go on that drive, the drive before is being evaluated
    # so that the carrier that was waiting can go to the drive
    else:
        if driveXHasCarrierWaiting[drive - 1] != 0:
            # print("Pulling carrier " + str(driveXHasCarrierWaiting[drive - 1]) + " to drive " + str(drive))
            # Calling evaluatingDriveReset for the drive before and the waiting carrier
            evaluateDriveReset(drive - 1, driveXHasCarrierWaiting[drive - 1])
            # Carrier is no longer waiting to go to the drive
            driveXHasCarrierWaiting[drive - 1] = 0

    # Prints out state of carriers on each drive after the evaluation
    # print("After the carriers have moved ")
    # print(driveXHasCarrier)


# If a carrier leaves the last drive, the data for the carrier is compressed, the CSV file is exported and
# the data is cleared
def completeIteration(carrier):
    # Rolls data up to the first timestamp of which the energy consumption is != 0
    rollUpData(carrier)

    # Removes the last 200 timestamps of the data if it is large enough (which contains the last energy spike)
    removeLastEnergySpike(carrier)

    # Compress the data for the carrier and obtain the total energy contained
    energySum = compressData(carrier)

    # Write the total and average energy consumption for the carrier, session, iteration to the DB
    writeEnergyToDatabase(carrier, energySum)

    # Export data for the carrier to CSV file
    exportCSV(carrier)

    # Clear the data array for the carrier with zeros
    clearCarrierData(carrier)


# TODO DANIEL
# Writes total and average energy consumption for carrier, iteration, session to database
def writeEnergyToDatabase(carrier, energySum):
    averageEnergy = float(energySum / currentPositionAtCarrierData[carrier - 1])

    # Table name of iteration data
    tableName = config.get('database_tables','average')
    # Everything needed to write values to the DB
    dataProcessingFunctions.writeCumulatedValuesToDB(tableName,session,carrier,iterationNumber,averageEnergy)


# Removes all the not relevant timestamps at the beginning of the data array by rolling the data up to the top
def rollUpData(carrier):
    global carrierData
    global currentPositionAtCarrierData
    # Select first and relevant timestamp, so the timestamps before can be deleted
    firstRow = findFirstRowInCarrierData(carrier)

    # print("Rolling up, before FirstTS: " + str(firstRow))

    if firstRow != 0:
        # Roll all relevant time stamps to the top
        carrierData[carrier - 1] = np.roll(carrierData[carrier - 1], -firstRow, axis=1)

        # Update current position in Carrier Data (move up by int(firstRow)
        currentPositionAtCarrierData[carrier - 1] -= firstRow

    # print("After rolling: " + str(findFirstRowInCarrierData(carrier)))


# Removes the last 200 timestamps from the data where the energy spike is
def removeLastEnergySpike(carrier):
    removeLastDataRows = 200
    curPos = int(currentPositionAtCarrierData[carrier - 1])

    print("Cutting away the last 200, currentPosInDataBefore: " + str(curPos))

    if curPos > removeLastDataRows:
        for i in range(int(curPos - removeLastDataRows), curPos):
            carrierData[carrier - 1][0][i] = 0
            carrierData[carrier - 1][1][i] = 0
            carrierData[carrier - 1][2][i] = 0
            carrierData[carrier - 1][3][i] = 0
            carrierData[carrier - 1][4][i] = 0

        currentPositionAtCarrierData[carrier - 1] -= removeLastDataRows

    print("After cutting currentPos: " + str(currentPositionAtCarrierData[carrier - 1]))


# Compresses the data, so that only every X-th (KEEP_EVERY_X_ROW) is kept in the data
# Example: rows: 0,1,2,3,4,5,6 --> compressData with KEEP_EVERY_X_ROW == 2 --> rows: 0,2,4,6
# Returns the total energy consumption for the particular carrier
def compressData(carrier):
    global carrierData
    global currentPositionAtCarrierData
    # logging.info("Compressing data of carrier: " + str(carrier))
    print("Compressing data of carrier: " + str(carrier))

    # Determine the first time stamp for overwriting the time stamp to have them all start at 0 and increase accordingly
    firstTimeStamp = carrierData[carrier - 1][0][0]

    # First next stamp value that is being searched for in the carrier data to keep it when aggregating the data
    nextTimeStampValue = 0

    # Add the values to this point in the carrierData array
    saveTo = 0

    # Count the timestamps that are aggregated in order to average the added up energy consumptions
    countedTimeStamps = 1

    # The sum of all timestamps for calculating the total and average energy consumption
    energySum = float(0.0)

    for i in range(0, int(currentPositionAtCarrierData[carrier - 1])):
        # Sums the current value to the sum to calculate average and total energy consumption
        energySum += carrierData[carrier - 1][2][i]

        # If the current value has been found this time stamp is kept and
        if (carrierData[carrier - 1][0][i] - firstTimeStamp) == nextTimeStampValue:
            # Average the time stamps of the last stamp
            carrierData[carrier - 1][2][saveTo] = carrierData[carrier - 1][2][saveTo] / countedTimeStamps
            # Set counted timestamps back to 1 when the energy is saved to a new data row
            countedTimeStamps = 1

            # Change the place where the next energy consumption is being saved to
            saveTo = int(nextTimeStampValue / KEEP_EVERY_X_ROW)

            # Transfer the values to the position
            carrierData[carrier - 1][0][saveTo] = nextTimeStampValue
            carrierData[carrier - 1][1][saveTo] = carrierData[carrier - 1][1][i]
            carrierData[carrier - 1][2][saveTo] = carrierData[carrier - 1][2][i]
            carrierData[carrier - 1][3][saveTo] = carrierData[carrier - 1][3][i]
            carrierData[carrier - 1][4][saveTo] = carrierData[carrier - 1][4][i] - \
                                                  (carrierData[carrier - 1][4][i] % KEEP_EVERY_X_ROW)

            # Increase the next value that is being searched for
            nextTimeStampValue += KEEP_EVERY_X_ROW

        # If the current value cannot be found because the timestamp was not recorded for that carrier
        # The position has to be interpolated
        elif (carrierData[carrier - 1][0][i] - firstTimeStamp) > nextTimeStampValue:
            # Counts the amount of transferred timestamps to average in the end
            # This while loop iterates as long as all the values in the gap were interpolated
            # This is for the case that multiple time stamp values were missed in one gap
            while (carrierData[carrier - 1][0][i] - firstTimeStamp) > nextTimeStampValue:
                # Average the time stamps of the last stamp
                carrierData[carrier - 1][2][saveTo] = carrierData[carrier - 1][2][saveTo] / countedTimeStamps
                # Set counted timestamps back to 1 when the energy is saved to a new data row
                countedTimeStamps = 1

                # Change the place where the next energy consumption is being saved to
                saveTo = int(nextTimeStampValue / KEEP_EVERY_X_ROW)

                # All values necessary for interpolation
                time1 = carrierData[carrier - 1][0][i - 1] - firstTimeStamp
                time2 = carrierData[carrier - 1][0][i] - firstTimeStamp
                pos1 = carrierData[carrier - 1][1][i - 1]
                pos2 = carrierData[carrier - 1][1][i]

                # Linear interpolation of the position that the carrier was at at the missing time stamp
                posInter = pos1 + ((pos2 - pos1) * ((nextTimeStampValue - time1) / (time2 - time1)))

                # Because 1: The energy consumption is the total that was consumed during the last time stamp
                # and 2: The algorithm will continue with the next time stamp in the next iteration cicle
                # therefore: The energy consumption has to be the last energy consumption
                # otherwise energy consumption is lost during the interpolation.
                energyInter = carrierData[carrier - 1][2][i]

                # The interpolated drive is always the 2nd drive because this error only occurs when the drive
                # that the carrier wants to move to is not free.
                driveInter = carrierData[carrier - 1][3][i]

                # Transfer the values to the position
                carrierData[carrier - 1][0][saveTo] = nextTimeStampValue
                carrierData[carrier - 1][1][saveTo] = posInter
                carrierData[carrier - 1][2][saveTo] = energyInter
                carrierData[carrier - 1][3][saveTo] = driveInter
                carrierData[carrier - 1][4][saveTo] = carrierData[carrier - 1][4][i] - \
                                                      (carrierData[carrier - 1][4][i] % KEEP_EVERY_X_ROW)

                # Increase the next value that is being searched for
                nextTimeStampValue += KEEP_EVERY_X_ROW

        else:
            # Add the energy consumption to the current entry
            carrierData[carrier - 1][2][saveTo] += carrierData[carrier - 1][2][i]

            # Increase counted timestamps by 1
            countedTimeStamps += 1

        # Delete the last row (not the current because it may be needed for interpolation) if it is at a position
        # In the array that will be deleted
        if i >= 1 and i - 1 >= 1 + int((currentPositionAtCarrierData[carrier - 1] - 1) / float(KEEP_EVERY_X_ROW)):
            carrierData[carrier - 1][0][i - 1] = 0
            carrierData[carrier - 1][1][i - 1] = 0
            carrierData[carrier - 1][2][i - 1] = 0
            carrierData[carrier - 1][3][i - 1] = 0
            carrierData[carrier - 1][4][i - 1] = 0

        # If the current row is the last one of the array and it is not needed after compression, delete it
        # - 1 because the "currentPositionAtCarrierData" is the position where the next empty space is
        # Therefore the last position filled with data is currentPositionAtCarrierData[carrier - 1] - 1
        if i == int(currentPositionAtCarrierData[carrier - 1]) - 1:
            # Average the last energy row
            carrierData[carrier - 1][2][saveTo] = carrierData[carrier - 1][2][saveTo] / countedTimeStamps

            # Set the values in the carrier data to 0
            carrierData[carrier - 1][0][i] = 0
            carrierData[carrier - 1][1][i] = 0
            carrierData[carrier - 1][2][i] = 0
            carrierData[carrier - 1][3][i] = 0
            carrierData[carrier - 1][4][i] = 0

    return energySum


# Exports the table of the carrier to a CSV file in the form time; posAbsolute; posOnDrive; energy
def exportCSV(carrier):
    # Creates the filename in the form Session_X_Carrier_X_Iteration_X.csv
    fileName = "Session_" + str(session) + "_Carrier_" + str(int(carrier)) + "_Iteration_" + \
               str(int(iterationNumber)) + ".csv"

    # Adds the relative file path to the name that the files are saved to /InitialData/
    fileName = os.path.abspath(os.path.join("CarrierData", fileName))

    # Finds the first relevant row (position != 0) in the carrier data
    firstRow = findFirstRowInCarrierData(carrier)

    # Finds the last relevant row (position != 0) in the carrier data
    lastRow = findLastRowInCarrierData(carrier)

    # Only selects the relevant sub selection from carrier data (without position == 0) to export to csv
    # Commented out for testing
    export = np.transpose(carrierData[carrier - 1][:, firstRow:lastRow + 1])

    # Export carrier data with file name to csv file
    np.savetxt(fileName, export, fmt='%0.5f', delimiter=DATA_SEPARATOR, newline='\n',
               header='time;posAbsolute;energy;drive;timeAbsolute', footer='', comments='# ')

    # Write the filename to the console and the log file
    print("Exported: " + str(fileName))
    logging.info("Exported: " + str(fileName))


# Finds the first row of the array that will be exported as CSV, where pos and energy consumption != 0
def findFirstRowInCarrierData(carrier):
    if carrierData[carrier - 1][1][0] != 0 and carrierData[carrier - 1][2][0] != 0:
        return 0

    lastRowWithZero = 0

    for i in range(0, int(carrierData.shape[2]) - 1):
        position = carrierData[carrier - 1][1][i]
        energy = carrierData[carrier - 1][2][i]

        if position == 0 or energy == 0:
            lastRowWithZero = i
        else:
            if lastRowWithZero + 1 >= (carrierData.shape[2]) - 1:
                return (carrierData.shape[2]) - 1
            else:
                return lastRowWithZero + 1

    print("Couldn't find first row.")
    return 0


# Finds the first row of the array that will be exported as CSV, where pos and energy consumption != 0
def findLastRowInCarrierData(carrier):
    print("Finding last row")

    if carrierData[carrier - 1][1][currentPositionAtCarrierData[carrier - 1] - 1] != 0 and \
                    carrierData[carrier - 1][2][currentPositionAtCarrierData[carrier - 1] - 1] != 0:
        return currentPositionAtCarrierData[carrier - 1] - 1

    lastRowWithZero = currentPositionAtCarrierData[carrier - 1] - 1

    for i in range(1, int(currentPositionAtCarrierData[carrier - 1] + 1)):
        position = carrierData[carrier - 1][1][currentPositionAtCarrierData[carrier - 1] - i]
        energy = carrierData[carrier - 1][2][currentPositionAtCarrierData[carrier - 1] - i]

        if position == 0 or energy == 0:
            lastRowWithZero = currentPositionAtCarrierData[carrier - 1] - i
        else:
            if lastRowWithZero - 1 <= 0:
                return 0
            else:
                return lastRowWithZero - 1

    print("Couldn't find last row.")
    return (carrierData.shape[2]) - 1


# Clear the carrier data array for a certain carrier to all 0.0
def clearCarrierData(carrier):
    for i in range(0, int(carrierData.shape[2]) - 1):
        carrierData[carrier - 1][0][i] = 0
        carrierData[carrier - 1][1][i] = 0
        carrierData[carrier - 1][2][i] = 0
        carrierData[carrier - 1][3][i] = 0
        carrierData[carrier - 1][4][i] = 0

    # Set the current position that is being filled to 0 so that the array can be filled again
    currentPositionAtCarrierData[carrier - 1] = 0


# Ensures enough space in the carrier data array for a certain carrier
def ensureEnoughSpaceInCarrierData(carrier):
    global carrierData
    # If the current position at the carrier data is equal to the size of the array, the array size is doubled
    if currentPositionAtCarrierData[carrier - 1] >= carrierData.shape[2]:
        extend = np.zeros((AMOUNT_OF_CARRIERS, 5, int(carrierData.shape[2])))
        carrierData = np.concatenate((carrierData, extend), axis=2)


# Renames the csv file headers to structure: (ms; energy1;...;energyX; pos1;...;posX) (X = Amount of Drives)
def modifyCSVFile(filename):
    # InputFileName und OutputFileName of CSV
    inputFileName = filename
    outputFileName = os.path.splitext(inputFileName)[0] + "_modified.csv"

    # Opens File
    with open(inputFileName, 'rb') as inFile, open(outputFileName, 'wb') as outfile:
        # defines reading file and writing file
        r = csv.reader(inFile, delimiter=DATA_SEPARATOR)
        w = csv.writer(outfile, delimiter=DATA_SEPARATOR)

        # Copys first row
        first_row = next(r)

        # Initialize Array for new ColumnNames
        newColNames = []

        # Counter of Columns
        j = 0

        # Initialize amount of drives variable
        amountOfDrives = 0

        # Start position of Position Columns
        startPositionOfColumns = 0

        # Iterates the first row of the initial file and depending on the value writes columns into the file
        for i in first_row:
            # if j is zero
            if j == 0:
                newColNames.append("ms")
            # if column includes "iw4PowerCU" it's an energy sensor
            elif "iw4PowerCU" in i:
                newColNames.append("energy" + str(j - 1))
            # if column includes "ExternalEncoderPosition" it's an position sensor
            elif "ExternalEncoderPosition" in i:
                if startPositionOfColumns == 0:
                    startPositionOfColumns = j
                newColNames.append("position" + str(j - startPositionOfColumns))
                # counts the amount of drives.
                amountOfDrives = j - startPositionOfColumns
            else:
                # If the file is not in the right format, remove modified file and exit system
                os.remove(os.path.splitext(fileName)[0] + "_modified.csv")
                # Initialize DataFrame sessiondata columns based
                sessionData = pd.DataFrame(
                    columns=['session', 'fileName', 'amountOfCarriers', 'status'], index=['1'])
                # Adding previous extracted and calculated values to DataFrame
                nameOfFileInitial = os.path.splitext(fileName)[0]
                sessionData.loc['1'] = pd.Series(
                    {'session': session,
                     'fileName': nameOfFileInitial[12:],
                     'amountOfCarriers': AMOUNT_OF_CARRIERS,
                     'status': 'Failed'})
                # calls function to load the sessiondata data into the database
                dataProcessingFunctions.write_dataframe_to_database(sessionData,
                                                                    config.get('database_tables', 'sessiondata'),
                                                                    'append')

                sys.exit
            j += 1

        # Skips the first row from the reader, the old header
        next(r, None)
        # Writes new header
        w.writerow(newColNames)

        # Copies the rest of reader
        for row in r:
            w.writerow(row)

        return amountOfDrives


def moveFileToFolder(fileName, folderName):
    print("Moving: " + fileName + " to " + os.path.join(folderName, os.path.basename(fileName)))
    logging.info("Moving: " + fileName + " to " + os.path.join(folderName, os.path.basename(fileName)))
    os.rename(fileName, os.path.abspath(os.path.join(folderName, os.path.basename(fileName))))


#########################################################
############# START OF SCRIPT ###########################
#########################################################
# Initialize Log-File
# Creates or loads Log DataProcessing.log
# Format of LogFile: mm/dd/yyyy hh:mm:ss PM LogMessage
logging.basicConfig(filename='/srv/DataProcessing/dataProcessing.log', level=logging.INFO,
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# Calls Function to create Running.txt
dataProcessingFunctions.createRunningFile()

# Reads ConfigFile
config = ConfigParser.ConfigParser()
config.read('settings.cfg')

# CONSTANTS
# WAIT_TIME_IN_SECONDS: Time the script should wait until it calls the function again (in seconds)
WAIT_TIME_IN_SECONDS = config.getfloat('Simulation', 'waittime_compression')
# Input file names of data here
DATA_FILE_NAMES = []
# AMOUNT_OF_CARRIERS: How many Carriers are in the system
AMOUNT_OF_CARRIERS = config.getint('Simulation', 'amount_of_carriers')
# DATA_SEPARATOR: Separator of the CSV-File
DATA_SEPARATOR = config.get('Simulation', 'csv_seperator')
# Every X th row of the data is kept when compressing the data
KEEP_EVERY_X_ROW = config.getint('Simulation', 'keep_every_x_rows')
# Current Session
session = config.getint('Simulation', 'session')
# FileName that should be imported
fileName = config.get('Simulation', 'name_of_imported_file')

# Checks if a File is added to DATA_FILE_NAMES. If not it is terminating the script
if fileName == '':
    print('No File selected')
    # Calls function to remove running file
    dataProcessingFunctions.deleteRunningFile()
    # Terminates the script
    sys.exit()

# Calls modifyCSVFile function
amountOfDrives = modifyCSVFile(fileName) + 1
print("Amount of drives" + str(amountOfDrives))

# Updates Session in ConfigFile
dataProcessingFunctions.updated_config('Simulation', 'session', session + 1)

# Initialize DataFrame sessiondata columns based
sessionData = pd.DataFrame(
    columns=['session', 'fileName', 'amountOfCarriers', 'status'], index=['1'])
# Adding previous extracted and calculated values to DataFrame
nameOfFile = os.path.splitext(fileName)[0]
sessionData.loc['1'] = pd.Series({'session': session,
                                  'fileName': nameOfFile[12:],
                                  'amountOfCarriers': AMOUNT_OF_CARRIERS,
                                  'status': 'OK'})
# calls function to load the sessiondata data into the database
dataProcessingFunctions.write_dataframe_to_database(sessionData, config.get('database_tables', 'sessiondata'), 'append')

# Variables
# Array that saves for every drive which carrier is on it
driveXHasCarrier = np.zeros(amountOfDrives)
# This is where all the data goes before exporting to CSV
# carrierData[carrier number][time = 0, pos = 1, energy consumption = 2][position of array]
carrierData = np.zeros((AMOUNT_OF_CARRIERS, 5, 100))
# Here is stored in which row the last entry of carrier data was made for every carrier
# (This could also be calculated by why not store it, since its used frequently)
currentPositionAtCarrierData = np.zeros(AMOUNT_OF_CARRIERS)
# Saves the last position on the drive of every carrier
lastPositionOfCarrier = np.zeros(AMOUNT_OF_CARRIERS)
# Number of complete runs through the system
driveXHasCarrierWaiting = np.zeros(amountOfDrives)
# Number of Iterations
iterationNumber = 0
# The last carrier that entered the first drive
lastCarrierThatEnteredDriveOne = 1

# First row of data frames
initialData = pd.read_csv(os.path.splitext(fileName)[0] + "_modified.csv", DATA_SEPARATOR, low_memory=False,
                          header=0)
#    Extracting the DriveNo of the first loaded File in DATA_PATH
# Iterates each row and afterwards each drive
#  Calls compressData with a pd.Series. The values are:
# ms, No. of Drive, Energy Consumption, Position
for index, row in initialData.iterrows():
    for drive in range(0, amountOfDrives):
        time = int(float(str(row['ms']).replace(',', '.')))
        position = float(str(row['position' + str(drive)]).replace(',', '.'))
        energy = float(str(row['energy' + str(drive)]).replace(',', '.'))
        processData(time, drive + 1, position, energy)
        sleep(WAIT_TIME_IN_SECONDS)

# Delete the "_modified" csv file
os.remove(os.path.splitext(fileName)[0] + "_modified.csv")

# Requests current session Data
sessionData = dataProcessingFunctions.getSessionData()
# Sets status of current session to "Finished"
sessionData.set_value(session, 'status', "Finished")
# Writes the new data to the database
# Disabled because status Finish doesn't have to be set right now
# dataProcessingFunctions.write_dataframe_to_database(sessionData, config.get('database_tables', 'sessiondata'),'replace')


# Calls Function to remove RunningFile
dataProcessingFunctions.deleteRunningFile()
