// Load the Visualization API and the piechart package.
google.load('visualization', '1.0', {'packages':['corechart']});
      
// Set a callback to run when the Google Visualization API is loaded.
//google.setOnLoadCallback(drawChart);


// Callback that creates and populates a data table,
// instantiates the pie chart, passes in the data and
// draws it.
function drawChart(data_source, dest_id, size) {
  // load json chart info
  $.ajax({
    'async': false,
    'global': false,
    'url': data_source,
    'dataType': "json",
    'success': function (data) {
        cj = null;
        cj = data;
      }
  });
  
  // Create the data table.
  var data = new google.visualization.DataTable();
  for (i = 0; i < cj.cols.length; i++) {
    data.addColumn(cj.cols[i].type, cj.cols[i].name)
  }
  
  data.addRows(cj.arrayRows)
  
  var formatter = new google.visualization.NumberFormat(
      { "pattern": cj.numFt.pattern[0] });

  if (cj.numFt.pattern[1].length === undefined) {
    formatter.format(data, cj.numFt.pattern[1]);
  } else {
    for (i = 0; i < cj.numFt.pattern[1].length; i++) {
      formatter.format(data, cj.numFt.pattern[1][i]);
    }
  }
  
  isStacked = false;
  if ("isStacked" in cj) {
    isStacked = cj.isStacked;
  }
  
  // Set chart options
  var options = {
    title: cj.title,
    hAxis: cj.hAxis,
    vAxis: cj.vAxis,
    legend: cj.legend,
    width:size.width,
    height:size.height,
    isStacked:isStacked
  };
  
  // Instantiate and draw our chart, passing in some options.
  var chart = new google.visualization.ColumnChart(document.getElementById(dest_id));
  chart.draw(data, options);
}