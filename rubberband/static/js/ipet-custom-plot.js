// ipetlongtable defined in static/js/evaluation.js

var customplot; // user defined plot
var customplotdata = {}; // data for user defined plot

function initialize_custom_chart() {
  var rb_plot_type = document.getElementById("rb-plot-type").value;
  rb_plot_type = 'column';

  // get data from dataframe
  data = ipetlongtable.data();
  coldata = Array();
  for(var i=0; i<data.length;i++) {
    entry = {
      name: data[i][0],
    };
    for(var j=1; j<data[i].length-1;j++) {
      entry[j] = +data[i][j];
    }
    coldata.push(entry);
  }

  // set default color scheme
  dc.config.defaultColors(d3.schemeSet1);

  // manage data with crossfilter; fill with array of dicts:
  // crossfilter([
  //   { x: 1, y: 2, name: "n" },
  //   { x: 3, y: 9, name: "x" },
  //   { x: 28, y: 19, name: "sdf" }, ...])
  customplotdata.data = crossfilter(coldata);

  // dimensions and groups
  customplotdata.nameDim = customplotdata.data.dimension(function(d) {return d.name;});
  customplotdata.groups = {};
  for(var xdata=1;xdata<data[0].length-1;xdata++) {// TODO
    customplotdata.groups[xdata] = customplotdata.nameDim.group().reduceSum(function(d) {
      n = Math.log( d[""+xdata]);
      if (n == "NaN" || n == -Infinity) {
        return 0;
      } else {
        return n;
      }
    });
    jsonlog(customplotdata.groups[xdata].all());
  }
}

function plot_custom_chart() {
  //TODO for filtering
  selectedrows = ipetlongtable.rows({filter:'applied', sort:'applied'})[0];

  // selected options
  var rb_plot_type = document.getElementById("rb-plot-type").value;
  var xlogarithmic = document.getElementById("plotx-log").checked;
  var ylogarithmic = document.getElementById("ploty-log").checked;
  var xdata = document.getElementById("plotx-select").value;
  var ydata = document.getElementById("ploty-select").value;

  if (rb_plot_type === "scatter") {
    //TODO
  } else { // 'column' plot
    //TODO
    customplot = dc.barChart("#customplot");
    customplot.width(800)
      .height(600)
      .dimension(customplotdata.nameDim)
      .group(customplotdata.groups[xdata])
      .ordering(function (d) {return +d.value})
      .xAxisLabel('x')
      .renderHorizontalGridLines(true)
      .xUnits(dc.units.ordinal)
      .x(d3.scaleBand())
      .yAxisLabel('y')
      .title(function (d) {
        return d.key + " " + Math.exp(d.value).toFixed(3);
      })
      //.y(d3.scaleLog().domain([1.1,10]))

    customplot.yAxis()
      .tickFormat(function (v) {
        return Math.exp(v).toFixed(2);
      })
      .tickValues([
        Math.log(0.001),
        Math.log(0.01),
        Math.log(0.1),
        Math.log(1),
        Math.log(10),
        Math.log(100),
        Math.log(1000),
        Math.log(10000)])

  }
  // render all plots on this page
  dc.renderAll();
}

function show_hide_y_select() {
  var plot_form_y = document.getElementById("custom-plot-form-y");

  if (document.getElementById("rb-plot-type").value === "column") {
    plot_form_y.style.display = "none";
  } else {
    plot_form_y.style.display = "block";
  }
}

// ------------------ listeners
$(document).ready(function() {
  $('#rb-ipet-eval-result').on('change', '#rb-plot-type-select', function(e) {
    // listen to plot type select in plot form
    show_hide_y_select();
  });
  $('#rb-ipet-eval-result').on('change', '#rb-plot-form', function(e) {
    // listen to plot form
    plot_custom_chart();
  });
});
