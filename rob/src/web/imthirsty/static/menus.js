
var app = angular.module('imthirsty', ['ngResource']);

app.controller('BeerMenu',
  ['$scope', 'Regions', 'Brewers', 'Beers', 'Recommendations',
  function($scope, Regions, Brewers, Beers, Recommendations) {
    $scope.data = {};
   
    $scope.data.current_region = null;
    $scope.data.regions = Regions.query();
    
    $scope.setBrewers = function(region_id) {
      console.log("! " + region_id);
      $scope.data.current_region = region_id;
      $scope.data.brewers = Brewers.query({}, { region_id: region_id },
        function(res) {
          console.log(res);
        });
    };
    
    $scope.setBeers = function(brewer_id) {
      console.log("! " + brewer_id);
      $scope.data.current_brewer = brewer_id;
      $scope.data.brewers = Beers.query({}, { brewer_id: brewer_id },
        function(res) {
          console.log(res);
        });
    };
    
    $scope.setRecs = function(beer_id, style_id) {
      console.log("! " + beer_id + " " + style_id);
      $scope.data.current_beer = beer_id;
      $scope.data.current_style = style_id;
      $scope.data.brewers = Recommendations.query({}, { beer_id: beer_id, style_id: style_id },
        function(res) {
          console.log(res);
        });
    };

}]);

app.factory('Regions', function($resource){
    return $resource(
        'http://107.170.156.226:5000/brewer_regions',
        {}
    );
});

app.factory('Brewers', function($resource){
    return $resource(
        'http://107.170.156.226:5000/brewers/:region_id',
        { region_id: '@region_id' }
    );
});

app.factory('Beers', function($resource){
    return $resource(
        'http://107.170.156.226:5000/beers/:brewer_id',
        { brewer_id: '@brewer_id' }
    );
});

app.factory('Recommendations', function($resource){
    return $resource(
        'http://107.170.156.226:5000/recommend/:beer_id/:style_id',
        { beer_id: '@beer_id', style_id: '@style_id' }
    );
});