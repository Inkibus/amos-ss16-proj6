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

from django.conf.urls import url
from . import views

urlpatterns = [
    # this returns a csv-file of the requested data for multiple carriers and/or iterations- for details see views.py
    # this is for the continuous graph view and has relative time as X axis
    url(r'^continuousData.csv', views.continuousData, name='data'),
    # TODO align with views.py and test
    # this returns a csv-file of the requested data for multiple carriers and/or iterations- for details see views.py
    # this is for the flexibility view and has absolute time as X axis
    url(r'^continuousDataAbsoluteTime.csv', views.continuousDataAbsoluteTime, name='dataAbsoluteTime'),
    # this returns a csv-file of raw database tables - for details see views.py 
    url(r'^rawData.csv', views.rawData, name='rawData'),
    # This returns the DataProcessing Logfile
    url(r'^log.txt', views.logs, name='DataProcessingLog'),
    # Added the url values to enable the frontend to request values like LastIterationOfaCarrier
    # Calls views.db2values (Further Information views.py)
    url(r'^values.request', views.db2values, name='values'),
    # URL that enables to delete values out of database
    url(r'^deleteTables.request', views.deleteDatabaseValues, name='deleteTables'),
    # URL that provides data to the AverageEnergyConsumptionChart
    url(r'^averageEnergyConsumption.csv', views.averageEnergyConsumption, name='averageEnergyConsumption'),
    # URL that provides the creeping percentages for the Circle View and Bar Chart
    url(r'^percentages_creeping.csv', views.percentage_creeping, name='percentageForCircleAndBarChart'),
    # URL that provides the continuing percentages for the Circle View and Bar Chart as csv File
    url(r'^percentages_cont.csv', views.percentage_cont, name='percentageForCircleAndBarChart'),
    # URL that provides the continuing percentages for the Circle View and Bar Chart as JSON file
    url(r'^percentages.json', views.percentages_json, name='percentageForCircleAndBarChart'),
    # URL that resets the simulation
    url(r'^simulation.reset', views.resetSimulation, name='simulationReset'),
    # URL that provides rawData as JSON
    url(r'^rawData.json', views.rawDataJson, name='rawDataJSON'),
    # URL that starts the simulation
    url(r'^simulation.start', views.startSimulation, name='startSimulation'),
    # URL that returns all files as a string
    url(r'^simulation.files', views.simulationFiles, name='simulationFiles'),
    # URL that True or False depending on if the Simulation is still running
    url(r'^simulation.running', views.simulationRuns, name='SimulationRunning'),
    # URL for file upload
     url(r'^fileUpload.html', views.fileUpload, name='fileUpload'),
    # URL that provides a json file for the spike contamination page
    url(r'^spikeContamination.json', views.spikeContamination, name='spikeContamination'),

]
