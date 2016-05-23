/* This File is for routing purposes. It should enable the one page view.
If the user clicks on a link to another html site, instead of loading the whole new webpage,
only a snippet will be loaded and sent to the index.html file.
*/


'use strict';

angular
    .module('app.routes', ['ngRoute'])

    .config(['$routeProvider', function($routeProvider) {
    $routeProvider

      .when('/Graph', {
        templateUrl: 'sections/graphExample/GraphExample.html',
      })

      .when('/Dashboard', {
        templateUrl: 'sections/dashboard/dashboard.html'
      })

      .when('/', {
        templateUrl: 'sections/barCirclePage/HomePageIcons.html'
      })

      .when('/CircleCarrier', {
        templateUrl: 'sections/circlePage/circleCarrier.html'
      })

      .when('/BarCarrier', {
        templateUrl: 'sections/barPage/Barchart.html'
      })
        
      .when('/CompareCarrier', {
        templateUrl: 'sections/compareCarrier/CompareCarrier.html'
      })

      .when('/drillDownChart', {
        templateUrl: 'sections/drillDownChart/drillDownChart.html'
      })

      .otherwise({
        redirectTo: '/',

       });
    }]);