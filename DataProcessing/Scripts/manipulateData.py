#!/usr/bin/env python

# This script processes all csv-files that are produced by dataProcessing.py on the fly.
# Therefor it reads out all csv-files and calculates all necessary measures before loading the data into the database.
# The input files have to follow the following convention:
# Naming: Session_X_Carrier_Y_Iteration_Z.csv (X, Y, Z = int of Session, Carrier & Iteration)
# CSV-Columns: 'timeStamp','positionAbsolute','positonOnDrive','energyConsumption'

# Imports libraries
# Imports os for Operating System independent absolute file paths
import os
# Imports sys to let the script die
import sys
# Imports glob to enable the script to search for all csv files in a particular folder
import glob
# Imports sleep for sleeping
from time import sleep
# Imports Pandas for Data handling
import pandas as pd
# Imports setConstants to import the Constants
import setConstants


# Function that checks if new csv files are in the folder
def check_folder():
    for files in glob.glob("CarrierData/*.csv"):
        # Adds each file to the list dataFileNames
        dataFileNames.append(files)

    # Returns False or True depending on whether or not files are stored in dataFileNames
    if not dataFileNames:
        print "No new files found"
        return False
    else:
        print str(len(dataFileNames)) + " Files found"
        return True


# Function to process each file
def process_file(fileName):
    print "Processing " + fileName
    # Loading Path of the file
    filePath = os.path.abspath(fileName)
    # Loading data into a dataFrame
    data = pd.read_csv(filePath, setConstants.CSV_SEPARATOR)
    # Change name of Columns to fit DataBaseModel
    data.columns = ['timeStamp', 'positionAbsolute', 'positonOnDrive', 'energyConsumption']
    # Reads out session of file name and adds column to DataFrame after Casting from str to int
    session = int(fileName.split('_')[1])
    data['fidSession'] = session
    # Reads out carrier of file name and adds column to DataFrame after Casting from str to int
    carrier = int(fileName.split('_')[3])
    data['fidCarrier'] = carrier
    # Reads out iteration of file name and aadds column to DataFrame after Casting from str to int
    iteration = int(fileName.split('_')[5].replace('.csv', ''))
    data['fidIteration'] = iteration
    # Calculates the speed between two datapoints (Way/Time)
    data['speed'] = data['positionAbsolute'].diff().divide(data['timeStamp'].diff())
    # Calculates acceleration (SpeedEnd * SpeedEnd - SpeedBeginn * SpeedBeginn))/distance * 2
    data['acceleration'] = data['speed'].multiply(data['speed']).diff().divide(
        data['positionAbsolute'].diff().multiply(2))

    # Rearanges the columns to fit them to the new database model
    # Reads out Columns to a list
    cols = data.columns.tolist()
    # Rearanges the columms
    cols = cols[4:7] + cols[0:1] + cols[2:3] + cols[1:2] + cols[7:9] + cols[3:4]
    # Reananges the dataframe data
    data = data[cols]

    # calls function to load the data into the database
    load_to_database(data)

    # Creating DataFrame for the commulated Data
    # Calculating Measures
    # Calculates Average Energy Consumption
    averageEnergyConsumption = data['energyConsumption'].abs().mean()
    # Calculates Comulated Energy Consumption
    totalEnergyConsumption = data['energyConsumption'].sum()
    # Calculates Average Speed
    averageSpeed = data['speed'].mean()
    # Calculates Average Acceleration
    averageAcceleration = data['acceleration'].mean()

    # Inizialize DataFrame comulatedData with columns based on new DataBaseModel
    comaulatedData = pd.DataFrame(
        columns=['fidSession', 'fidCarrier', 'fidIteration', 'averageSpeed', 'averageAcceleration',
                 'totalEnergyConsumption', 'averageEnergyConsumptionAbsolute'], index=['1'])
    # Adding previous extracted and calculated values to DataFrame
    comaulatedData.loc['1'] = pd.Series(
        {'fidSession': session, 'fidCarrier': carrier, 'fidIteration': iteration, 'averageSpeed': averageSpeed,
         'averageAcceleration': averageAcceleration, 'totalEnergyConsumption': totalEnergyConsumption,
         'averageEnergyConsumptionAbsolute': averageEnergyConsumption})

    # calls function to load the processed data into the database
    load_to_database_comulated(comaulatedData)

    # TODO: moves the file to the Archive


# Loads data into the Database. Input = DataFrame
def load_to_database(data):
    # TODO: Load data to database
    print "Loading DataFrame into Database..."


# Loads comaulatesData into the database.
def load_to_database_comulated(data):
    # TODO: Load data to database
    print "Loading DataFrame into Database..."


#########################################################
############# START OF SCRIPT ###########################
#########################################################

# Putting Script a sleep for 0.5 sec to ensure that Running.txt is already created
sleep(0.5)

# Initialize dataFileNames as list. (List has to be available for all functions thats why it's declared global
dataFileNames = []

# Check if Running.txt exist.
while os.path.isfile("Running.txt"):
    # Running.txt exists -> Check if there are already files distributed by dataProcessing.py
    print "dataProcessing.py is still running"
    if check_folder():
        # If there are files which are not processed yet, call for each file process_file
        for filename in dataFileNames:
            process_file(str(filename))

    # put the script a sleep for setConstants.WAIT_TIME_IN_SECONDS_MPY before it checks the folder again for new files
    print "manipulateData.py goes asleep for " + str(setConstants.WAIT_TIME_IN_SECONDS_MPY) + "Sec"
    sleep(setConstants.WAIT_TIME_IN_SECONDS_MPY)

    # Terminates script for test purposes
    sys.exit()

else:

    # Running.txt does not exist. -> Check if the folder has files which hasn't been processed yet.
    print "dataProcessing.py is not running"
    if check_folder():
        # If there are files which are not processed yet, call for each file process_file
        for filename in dataFileNames:
            process_file(filename)
    print "manipulateData.py: Shut down"
