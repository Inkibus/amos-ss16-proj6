/* This file should list all main controllers */

angular.module('app')

.controller("MainController", function(){
    var vm = this;
    vm.title = 'Welcome to the Main Page';
})

/* The side navigation should appear on button click */

.controller('sideNavController', function($scope, $mdSidenav) {
 $scope.openLeftMenu = function() {
        $mdSidenav('menue').toggle();
        };
})

/* controller for the graph example. This should show the files in the dropdown menue.
 The user is then able to chose from one, which will be displayed on the page*/


   


.controller('visuController', function($scope) {
    $scope.graphs = [
        {name : "Acceleration", file : "sections/graphExample/dummy.csv"},
        {name : "Power", file : "sections/graphExample/dummy2.csv"},
    ];
    $scope.carriers = [
	{id : "1", name : "Carrier 1"},
	{id : "2", name : "Carrier 2"},
    ];
    $scope.paintGraph = function(file) {
	    g2 = new Dygraph(
	    document.getElementById("graphdiv2"), file, {});
        
        /* $scope.paintGraph = function(file) {
             g3 = new Dygraph(
                 document.getElementById("graphdiv3"), file, {});
         }*/
        
    }
    $scope.paintGraphDynamic = function(carrier) {
	    g2 = new Dygraph(
	    document.getElementById("graphdiv2"), "django/helloWorld/position.csv?carrier="+carrier, {});
    }
})

   /* .controller('myController', function ($scope) {
				Highcharts.chart('container', {

				    xAxis: {
				        categories: ['1', '2', '3', '4', '5', '6',
				            '7', '8', '9', '10', '11', '12']
				    },

				    series: [{
				        data: [29.9, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4]
				    }]
				});
    		})
    */
    
    .controller('myController', function ($scope) {
				Highcharts.chart('container', {
                    title: {
            text: 'Carrier Comparison',
            x: -20 //center
        },
        subtitle: {
            text: '',
            x: -20
        },
        xAxis: {
            categories: ['1', '2', '3', '4', '5', '6',
                '7', '8', '9', '10', '11', '12']
        },
        yAxis: {
            title: {
                text: 'Average Energy Consumption'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }]
        },
        tooltip: {
            valueSuffix: ''
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle',
            borderWidth: 0
        },
        series: [{
            name: 'Carrier1',
            data: [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6]
        }, {
            name: 'Carrier2',
            data: [-0.2, 0.8, 5.7, 11.3, 17.0, 22.0, 24.8, 24.1, 20.1, 14.1, 8.6, 2.5]
        }, {
            name: 'Carrier3',
            data: [-0.9, 0.6, 3.5, 8.4, 13.5, 17.0, 18.6, 17.9, 14.3, 9.0, 3.9, 1.0]
        }, {
            name: 'Carrier4',
            data: [3.9, 4.2, 5.7, 8.5, 11.9, 15.2, 17.0, 16.6, 14.2, 10.3, 6.6, 4.8]
        }]
    });
})
                
              

    
   
   

/* controller for the popupGraphs. Displays the carrier number and 2 Buttons. Depending on which button is pressed,
the carrier Id will be put into the comparison sidebar or the drill down chart*/

.controller('circlePopUpController', function($scope, $mdDialog, $mdSidenav, circleId, carrierService) {
    var id = circleId;
    var carrierId = id.substr(7, 8); // This method is necessary, because the string is "carrier_x" To extract x, I need to get the subsstring
    $scope.carrierNumber =  carrierId;

    $scope.addToComparison = function() {  //This function will add the carrier to the Side Panel "Compare". It will also check, if the item is already inside the comaprison pane.
        if(!carrierService.addCarrier(carrierId)) {         //check if carrier is already in list. If it already exists, then show a message.
            alert('Carrier: ' +carrierId+ ' is already in the comparison sidebar')
       }
        $mdDialog.hide();
        $mdSidenav('comparisonSidebar').toggle();
    }

    $scope.drillDown = function() {         //This function will take the carrier to the drilldown pane.
        alert("Moving to Drill Down Window, yet to be implemented");
        $mdDialog.hide();
    }
})

/* Refresh the circle Page. The purporse of this controller is listen to the Button
 and upon receiving an event, it should trigger the update circle button*/


.controller('circleGraphController', function($scope, $compile, $mdDialog, $mdMedia, $timeout, $mdSidenav, carrierService) {

/* open up a dialogue window upon triggering it via button click or via the hover function. The event is delayed by a timer
 if the the user is not leaving the hover area by the time the timer runs out, it will open up the popup. Else it will be canceled */
    var timer;

    $scope.openDialog = function(event) {
        var id = event.target.id;
        timer = $timeout(function () {
            $mdDialog.show({
                controller: "circlePopUpController",
                templateUrl: 'sections/circlePage/circlePopUp.html',
                clickOutsideToClose:true,
                locals: {circleId: id
                }
            });
        }, 1000)
    }

    $scope.closeDialog = function() {
        $timeout.cancel(timer);
    }


/* create the circle page upon page load. */

    $scope.circleGraph = function() {

    // create circle graphs and give them a unique ID

    var arrayCarrier = ["carrier1", "carrier2", "carrier3", "carrier4", "carrier5", "carrier6", "carrier7", "carrier8"];
    var arrayEnergy = [2, 42, 24, 10, 6, 4, 3, 23];
    var arrayAverageEnergy =[2, 30, 25, 11, 2, 7, 23, 87]
    var idCounter = 0;

    for (x in arrayCarrier) {

        var circleId = "carrier " + idCounter;
        var fragmenthtml = '<canvas class="circleDashboard" id="'+circleId+'" ng-click="openDialog($event)" ng-mouseenter="openDialog($event)" ng-mouseleave="closeDialog()"></canvas>';
        var temp = $compile(fragmenthtml)($scope);
        angular.element(document.getElementById('circleGraphs')).append(temp);

        createCircle(circleId, arrayEnergy[idCounter], arrayAverageEnergy[idCounter]);
        idCounter = idCounter+1;
    }

    /*  This function will create the circle graph, depending on the input parameters from the databse (right now it is hard coded*/

    function createCircle(carrier, energy, averageEnergy) {

      var canvas = document.getElementById(carrier);
      var context = canvas.getContext('2d');
      var centerX = canvas.width / 2;
      var centerY = canvas.height / 2;
      var radius = 60;
      var percentageEnergy =  Math.round((energy/averageEnergy) * 100);

      context.beginPath();
      context.arc(centerX, centerY, radius, 0, 2 * Math.PI, false);
      context.lineWidth = 2;
      context.strokeStyle = '#003300';
      context.stroke();

      if( energy  > averageEnergy) {
         context.fillStyle = '#FF1744';
      } else if(energy  < averageEnergy ) {
             context.fillStyle = '#00BFA5';
      } else {
            context.fillStyle = "#FFFF8D";
      }

      context.fill();
      context.lineWidth = 5;
      context.lineWidth=1;
      context.fillStyle="#212121";
      context.lineStyle="#212121";
      context.font="15px sans-serif";
      context.fillText(carrier, centerX - 15, centerY);
      context.fillText(percentageEnergy + "%", centerX - 15, centerY + 20);
    }
}

/* This function is for the side comparison navigation*/


    $scope.carriersForComparison = carrierService.getCarrier;

    $scope.removeCarrier = function(carrier) {
        carrierService.deleteCarrier(carrier);
    }

    $scope.openComparisonSideBar = function() {
        $mdSidenav('comparisonSidebar').toggle();
    }

})





