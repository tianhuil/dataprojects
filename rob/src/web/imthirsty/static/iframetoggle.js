
var app = angular.module('stylemap', ['ngResource', 'ui.bootstrap']);

var sheet_src = [];

app.controller('StyleMap',
  ['$scope', function($scope) {
    
    // data structure for all regions/brewers/beers
    $scope.data = []
    $scope.data.sheets = [
      {
        'name':'amport',
        'disp':'American Porter',
        'src':"//docs.google.com/spreadsheets/d/1RtZdyKQrRTKIZIN8dzjS9Y0r0wJjoA2wyhGoA3Szyxc/gviz/chartiframe?oid=89332469"
      },
      {
        'name':'russimp',
        'disp':'Russ Imp. Stout',
        'src':"//docs.google.com/spreadsheets/d/18ekSiXu_FpfklUPhunYEIqm422FVAHd7tlNHC79CVWI/gviz/chartiframe?oid=89332469"
      },
      {
        'name':'amimp',
        'disp':'Amer. Imp. Stout',
        'src':"//docs.google.com/spreadsheets/d/18uAOCwONEEj4v7_ARL8k8T-Kc2X0vpkcvGeGs6zmOHE/gviz/chartiframe?oid=89332469"
      },
      {
        'name':'bsda',
        'disp':'Belgian SDA',
        'src':"//docs.google.com/spreadsheets/d/1nuh0Tg5-F-Zkztr7hkccyVU3m__ksSFz8Za8gQdoWyo/gviz/chartiframe?oid=89332469"
      },
      {
        'name':'tripel',
        'disp':'Tripel',
        'src':"//docs.google.com/spreadsheets/d/1-lZW4NqJjMnrI_rqL81V-wlDykAmr8Eb9m1rSc8W5yI/gviz/chartiframe?oid=89332469"
      },
      {
        'name':'fruitveg',
        'disp':'Fruit/Veg',
        'src':"//docs.google.com/spreadsheets/d/13Pl8OGfDE3mhZ-SNHmb_Mja_Kxt2pXN35U-7dSZ8QqA/gviz/chartiframe?oid=89332469"
      },
      {
        'name':'amred',
        'disp':'Amer. Red Ale',
        'src':"//docs.google.com/spreadsheets/d/1F-jAIduE3zp5fWUFGSNROsrfzsEA7qeL7kgUtZoabys/gviz/chartiframe?oid=89332469"
      },
      {
        'name':'apa',
        'disp':'Amer. Pale Ale',
        'src':"//docs.google.com/spreadsheets/d/1LnBLiHYvvRhmcrwLKWVt64QR_PUB3G5B5aSSjHs8XoM/gviz/chartiframe?oid=89332469"
      },
      {
        'name':'aipa',
        'disp':'Amer. IPA',
        'src':"//docs.google.com/spreadsheets/d/1Kql7uFdcGuqUW8-PJfODA69PSwbpbmnQI9r2_MXX1A8/gviz/chartiframe?oid=89332469"
      },
      {
        'name':'adipa',
        'disp':'Amer. DIPA',
        'src':"//docs.google.com/spreadsheets/d/1AAedrbv7Vbei5y5LEKjCRWz3uLbks-WYADm_IpKO7YA/gviz/chartiframe?oid=89332469"
      }
    ];
    
      for (i = 0; i < $scope.data.sheets.length; i++) {
        sheet_src.push($scope.data.sheets[i].src);
      }
      
    $scope.getSrc = function (index) {
      return sheet_src[index]
    }
    
    //$sceProvider.enabled(false)
    
  }]);

