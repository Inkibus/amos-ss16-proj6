/*
   This file is part of Rogue Vision.

   Copyright (C) 2016 Daniel Reischl, Rene Rathmann, Peter Tan,
       Tobias Dorsch, Shefali Shukla, Vignesh Govindarajulu,
       Aleksander Penew, Abinav Puri

   Rogue Vision is free software: you can redistribute it and/or modify
   it under the terms of the GNU Affero General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   Rogue Vision is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU Affero General Public License for more details.

   You should have received a copy of the GNU Affero General Public License
   along with Rogue Vision.  If not, see <http://www.gnu.org/licenses/>.
*/



/* This file contains all AngularJS Services*/

angular.module('app')

.service('percentageService', function(sessionService, $timeout, $http) {
    /*
      Provides percentage data of carriers
    */
    var percentageDataPromise;
    var percentageData = [];
    var flag = false;
    var percentageDataType = "percentages_creeping";
    function getFromDB() {
        /*
          Fetches data from backend and sends it to the controller. This will only be done, once the parsing is completed
          So far this is called each time when getAll is called, but this is probably not necessary
        */
	percentageDataPromise = $http.get('django/dataInterface/percentages.json?session=' +sessionService.getCurrentSession() + '&type='+percentageDataType);
    }
    
    this.getAll = function() {
        getFromDB(percentageDataType);
	percentageDataPromise.then(function(result) {percentageData = result.data});
        return percentageData;
    }
    
    this.getPercentagePromise = function() {
	return $http.get('django/dataInterface/percentages.json?session=' +sessionService.getCurrentSession() + '&type='+percentageDataType);
    }

    this.getColorOfCarrier = function(percentageOfEnergy) {
        var color = {'border-color': 'rgb(255,255,0)'};
        if(percentageOfEnergy > 1.05) {
            color = {'border-color' : 'rgb(229, 28, 52)'};
        }

        if(percentageOfEnergy <= 1.025 ) {
            color = {'border-color' : 'rgb(178,255,89)'};
        }
        return color;
    }

    this.setPercentageType = function(newType) {
	percentageDataType = newType;
    }

    return {
        getAll: this.getAll,
        getColorOfCarrier: this.getColorOfCarrier,
	getPercentagePromise: this.getPercentagePromise,
	setPercentageType: this.setPercentageType,
    };
});

/* The carrierService, proved carrier data to all controllers
For now it is used to saves the carriers for comparison, chosen by the user and proved them to all controller
who need the data.
*/

angular.module('app')

// service that provides iteration data to all controllers
.service ('iterationService', function (){
    var iterationsForComparison = [];

     // function adds a iteration with a given ID to iterationsForComparison
    this.addIteration = function(newIteration) {
        for(var i = 0; i < iterationsForComparison.length; i++) {
            if (iterationsForComparison[i] == newIteration) {
                return false;
            }
        }
        iterationsForComparison.push(newIteration);
        return true;
    };

    // returns the array with IterationIDs to be compared
    this.getIterations = function(){
        return iterationsForComparison;
    };

    // this function empties the array, so that no iteration item is left inside anymore.
    this.emptyIterationArray = function() {
        iterationsForComparison.splice(0,iterationsForComparison.length);
    };

    // this service returns these functions to the caller for use
    return {
        addIteration: this.addIteration,
        getIterations: this.getIterations,
        emptyIterationArray: this.emptyIterationArray
    };

});

angular.module('app')

.service('carrierService', function(percentageService) {
    var carriersForComparison = [];

    this.containsCarrier = function(carrierID){
        for(var i = 0; i < carriersForComparison.length; i++) {
            if (carriersForComparison[i].carrierNumber == carrierID) {
                return true;
            }
        }
        return false;
    }

    this.hasCarrier = function(carrierId) {
	    return carriersForComparison.some(function(carrier){return carrier.carrierNumber == carrierId;});
    }
    
    // function adds a carrier with a given ID
    this.addCarrier = function(newCarrier) {
        for(var i = 0; i < carriersForComparison.length; i++) {
            if (carriersForComparison[i].carrierNumber == newCarrier) {
                return false;
            }
        }
        carriersForComparison.push({carrierNumber: newCarrier});
        return true;
    }

    // returns the array with CarrierIDs to be compared
    this.getCarrier = function(){
        return carriersForComparison;
    }

    // return whether carriersForComparison is empty or not
    this.isEmpty = function() {
	return (carriersForComparison.length == 0);
    }

    // return whether all carriers with index 1 .. carrierIndex are selected
    this.containsAllUpTo = function(carrierIndex) {
	for (var i = 0; i <= carrierIndex; i++) {
	    if (!this.hasCarrier(carrierIndex)) {
		return false;
	    }
	}
	return true;
    }

    // deletes a carrier with a given ID
    this.deleteCarrier = function(removeCarrier) {
        for(var i = 0; i < carriersForComparison.length; i++) {
            if (carriersForComparison[i].carrierNumber == removeCarrier) {
                carriersForComparison.splice(i,1);
                return true;
            }
        }
        return false;
    }

    // this function selects all Carriers
    this.selectAll = function() {
	percentageService.getPercentagePromise().then(
	    function(result) {
		carriersForComparison = [];
		for (var carrierId in result.data) {
		    carriersForComparison.push({carrierNumber: carrierId});
		}
	    }
	);
    }
    
    // this function empties the array, so that no carrier item is left inside anymore.
    this.emptyCarrierArray = function() {
        carriersForComparison = [];
    }

    // this service returns these functions to the caller for use
    return {
        containsCarrier: this.containsCarrier,
        hasCarrier: this.hasCarrier,
	containsAllUpTo: this.containsAllUpTo,
	isEmpty: this.isEmpty,
        addCarrier: this.addCarrier,
        getCarrier: this.getCarrier,
        deleteCarrier: this.deleteCarrier,
	selectAll: this.selectAll,
        emptyCarrierArray: this.emptyCarrierArray
    };
});


angular.module('app')

.service('sessionService', function($http) {
    var numberOfSessions = 0;
    var currentSession = 1;
    var sessionDataPromise;

    function update () {
	// once sessions are added to database when they are load (instead of when simulation finishes)
	// use sessionData also to set numberOfSessions
	//$http.get("django/dataInterface/rawData.json?table=sessiondata")
	//    .then(function (response){sessionData = response.data;});
	
	var xmlHttp = new XMLHttpRequest();
	// so far session, carrier and iteration have to be set - they are disregarded however
	xmlHttp.open( "GET", 'django/dataInterface/values.request?session=1&carrier=1&iteration=1&value=currentSession', false );
	xmlHttp.send(null);
	//parses Http-ResponseText to a decimal int
	numberOfSessions = parseInt(xmlHttp.responseText,10);
    }
    
    this.getNumberOfSessions = function() {
	update();
	return numberOfSessions;
    }

    this.getCurrentSession = function() {
	return currentSession;
    }

    this.setCurrentSession = function(newSession) {
	currentSession = newSession;
    }
    
    this.getSessionData = function() {
	update();
	var sessionDataPromise = $http.get("django/dataInterface/rawData.json?table=sessiondata");
	return sessionDataPromise;
    }

    // Returns the string of session with sessionId
    this.getDataFileNameById = function(id) {
	// Gets the full string of all data paths of all data files on the server
        var xmlHttp = new XMLHttpRequest();
        xmlHttp.open( "GET", 'django/dataInterface/simulation.files', false);
        xmlHttp.send(null);
        var string  = xmlHttp.responseText;

        // Separates the comma separated data files string to an array
        var arraySimulationFileNames = string.split(',');

        // Deletes the file path for every file name so that only the file name is displayed
        for (var i = 0; i < arraySimulationFileNames.length; i++) {
            arraySimulationFileNames[i] = arraySimulationFileNames[i].substring(32);
        }

        return arraySimulationFileNames[id - 1];
    }

    // Returns the string of the currently selected data file name
    this.getCurrentDataFileName = function() {
	return this.getDataFileNameById(currentSession);
    }
    
    return {
        getNumberOfSessions: this.getNumberOfSessions,
        getCurrentSession: this.getCurrentSession,
        setCurrentSession: this.setCurrentSession,
	getSessionData: this.getSessionData,
	getCurrentDataFileName: this.getCurrentDataFileName,
	getDataFileNameById: this.getDataFileNameById,
    };
	
});
