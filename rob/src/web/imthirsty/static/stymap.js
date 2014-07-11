
var app = angular.module('stylemap', ['ngResource', 'ui.bootstrap']);

var init = null

app.controller('StyleMap',
  ['$scope', function($scope) {
    
    $scope.data = {}
    $scope.data.curr_style = "";
    $scope.data.sheets = [
      {
        'name':'amport',
        'disp':'American Porter',
        'data':"chartdata/amerporter.json"
      },
      {
        'name':'russimp',
        'disp':'Russ Imp. Stout',
        'data':"chartdata/russimp.json"
      },
      {
        'name':'amimp',
        'disp':'Amer. Imp. Stout',
        'data':"chartdata/amimp.json"
      },
      {
        'name':'bsda',
        'disp':'Belgian SDA',
        'data':"chartdata/bsda.json"
      },
      {
        'name':'tripel',
        'disp':'Tripel',
        'data':"chartdata/tripel.json"
      },
      {
        'name':'fruitveg',
        'disp':'Fruit/Veg Beer',
        'data':"chartdata/fruitveg.json"
      },
      {
        'name':'amred',
        'disp':'Amer. Red Ale',
        'data':"chartdata/amred.json"
      },
      {
        'name':'apa',
        'disp':'Amer. Pale Ale',
        'data':"chartdata/apa.json"
      },
      {
        'name':'aipa',
        'disp':'Amer. IPA',
        'data':"chartdata/aipa.json"
      },
      {
        'name':'adipa',
        'disp':'Amer. DIPA',
        'data':"chartdata/adipa.json"
      }
    ];
    
    $.getScript("gchart.js", function() {
      $scope.plot = function(ix, dest_id, size) {
        data_source =  $scope.data.sheets[ix].data;
        drawChart(data_source, dest_id, {"width":1000, "height":550});
        $scope.data.curr_style = $scope.data.sheets[ix].disp;
      };
      
      init = function() {
        drawChart($scope.data.sheets[0].data, "plot_panel", {"width":1000, "height":550});
      };
    });
    
  }]);

$(document).ready(function() {
  init();
});
