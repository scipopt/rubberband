
// global vars
customplot = {}; // user defined plots
// nonglobal vars
var cplotdata = {}; // data for user defined plots
var tickValues = [0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000];

function initialize_custom_chart() {
  // get data from dataframe
  // ipetlongtable defined in static/js/evaluation.js
  data = ipetlongtable.data();
  coldata = Array();
  for(var ii=0; ii<data.length; ii++) {
    var i = ""+ii;
    entry = {
      name: data[i][0],
    };
    for(var jj=1; jj<data[i].length-1; jj++) {
      var j = ""+jj;
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
  cplotdata.rawdata = coldata;
  cplotdata.data = crossfilter(coldata);

  //-------------------------------barplot
  // dimensions and groups
  cplotdata.bar = {};
  cplotdata.bar.nameDim = cplotdata.data.dimension(function(d) {return d.name;});
  cplotdata.bar.groups = {};
  for(var ii=1; ii<data[0].length-1; ii++) {
    var i = ""+ii;
    // for logarithmic and regular plot
    cplotdata.bar.groups[i] = {};

    cplotdata.bar.groups[i][true] = cplotdata.bar.nameDim.group().reduceSum(function(d) {
      n = Math.log( d[i]);
      if (n == "NaN" || n == -Infinity) return 0; else return n;
    });
    cplotdata.bar.groups[i][false] = cplotdata.bar.nameDim.group().reduceSum(function(d) {
      return d[i];
    });

    // this lines make sure that the data gets copied to crossfilter
    cplotdata.bar.groups[i][true].all();
    cplotdata.bar.groups[i][false].all();
  }

  //-------------------------------scatterplot
  cplotdata.scatter = {};
  // for scatter plot let the dimension return [x,y] for an x-y-scatterplot
  // initialize everything to 0 here TODO
  cplotdata.scatter.dims = {};
  cplotdata.scatter.groups = {};
  for(var ii=1; ii<data[0].length-1; ii++) {
    var i = ""+ii;
    cplotdata.scatter.dims[i] = {};
    cplotdata.scatter.groups[i] = {};
    for(var jj=1; jj<data[0].length-1; jj++) {
      var j = ""+jj;
      cplotdata.scatter.dims[i][j] = 0;
      cplotdata.scatter.groups[i][j] = 0;
    }
  }
}

function prepare_scatter_plot(x, y) {
  // if already generated at some point don't do anything
  if (cplotdata.scatter.dims[x][y] != 0) {
    return;
  }
  // generate dimension for scatterplot
  cplotdata.scatter.dims[x][y] = cplotdata.data.dimension(function(d) {return [+d[x], +d[y]];});

  // generate group for scatterplot
  cplotdata.scatter.groups[x][y] = cplotdata.scatter.dims[x][y].group().reduce(
    function (p, v) {
      x_dat = v[x];
      y_dat = v[y];
      if ((x_dat != 0) && (y_dat != 0)) {
        dist = 1.0*(x_dat - y_dat)/Math.max(x_dat, y_dat);
      }
      p[x] = v[x];
      p[y] = v[y];
      p.color = dist;
      return p;
    },
    function (p, v) {
      p.color = 0;
      return p;
    },
    function () {
      p = {}
      p[x] = 0;
      p[y] = 0;
      p.color = 0;
      return p;
    }
  );
  // this lines make sure that the data gets copied to crossfilter
  // TODO do i need this?
  jsonlog(cplotdata.scatter.groups[x][y].all());
}

function plot_custom_charts() {
  // options
  width = 600;
  height = 400;

  //TODO for filtering
  selectedrows = ipetlongtable.rows({filter:'applied', sort:'applied'})[0];

  // selected options
  var xlogarithmic = document.getElementById("plotx-log").checked;
  var ylogarithmic = document.getElementById("ploty-log").checked;
  var xdata = document.getElementById("plotx-select").value;
  var ydata = document.getElementById("ploty-select").value;

  customplot.bar = dc.barChart("#custombarplot");
  customplot.bar.width(width)
    .height(height)
    .dimension(cplotdata.bar.nameDim)
    .group(cplotdata.bar.groups[xdata][xlogarithmic])
    .ordering(function (d) {return +d.value})
    .renderHorizontalGridLines(true)
    .xUnits(dc.units.ordinal)
    .brushOn(false)
    .x(d3.scaleBand())

  customplot.bar.xAxis().tickValues([]);

  if (xlogarithmic){
    customplot.bar.title(function (d) {
      return d.key + ": " + Math.exp(d.value).toPrecision(2);
    })
    //.y(d3.scaleLog().domain([0.001,1000])) // in the future maybe this works?

    customplot.bar.yAxis()
      .tickFormat(function (v) {
        for (var i in tickValues) {
          if (+Math.exp(v).toPrecision(3) == tickValues[i]) return tickValues[i];
        }
        return "";
      })
      .tickValues([
        Math.log(0.001),
        Math.log(0.01),
        Math.log(0.1),
        Math.log(1),
        Math.log(10),
        Math.log(100),
        Math.log(1000),
        Math.log(10000)]);
  }

  //TODO
  prepare_scatter_plot(xdata, ydata);

  xmin = d3.min(cplotdata.rawdata, function (d) { return d[xdata]; })
  ymin = d3.min(cplotdata.rawdata, function (d) { return d[ydata]; })
  xmax = d3.max(cplotdata.rawdata, function (d) { return d[xdata]; })
  ymax = d3.max(cplotdata.rawdata, function (d) { return d[ydata]; })

  customplot.scatter = dc.scatterPlot("#customscatterplot");
  customplot.scatter.width(width)
    .height(height)
    .dimension(cplotdata.scatter.dims[xdata][ydata])
    .group(cplotdata.scatter.groups[xdata][ydata])
    .symbolSize(8)
    .elasticX(true)
    .elasticY(true)
    .renderHorizontalGridLines(true)
    .renderVerticalGridLines(true)
    .title(function (d) {
      return d.key + ": " + d.value;
    })
    .colorAccessor(function (d) {
      return d.value.color;
    })
    .existenceAccessor(function(d) {
      return d.value[ydata];
    })
    .colors(d3.scaleLinear().domain([-1,1])
      .range(["#ff0000", "#00ff00"]));

  if (xlogarithmic){
    customplot.scatter.x(d3.scaleLog().domain([Math.min(xmin, 0.01), xmax]))
      .xAxis().tickFormat(function (v) {
        for (var i in tickValues) {
          if (v == tickValues[i]) return tickValues[i];
        }
        return "";
      })
      .tickValues(tickValues);
  } else {
    customplot.scatter.x(d3.scaleLinear().domain([xmin,xmax]).nice());
  }
  if (ylogarithmic){
    customplot.scatter.y(d3.scaleLog().domain([Math.min(xmin, 0.01), xmax]))
      .yAxis().tickFormat(function (v) {
        for (var i in tickValues) {
          if (v == tickValues[i]) return tickValues[i];
        }
        return "";
      })
      .tickValues(tickValues);
  } else {
    customplot.scatter.y(d3.scaleLinear().domain([ymin,ymax]).nice());
  }

  // render all plots on this page
  dc.renderAll();
}

// ------------------ listeners
$(document).ready(function() {
  $('#rb-ipet-eval-result').on('change', '#rb-plot-form', function(e) {
    // listen to plot form
    plot_custom_charts();
  });
});
