
// global vars
customplot = {}; // user defined plots
// private vars
var cplotdata = {}; // data for user defined plots
var tickValues = [0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000];

function initialize_custom_chart() {
  // get data from dataframe
  // ipetlongtable defined in static/js/evaluation.js
  data = ipetlongtable.data();
  coldata = Array();
  for(let ii=0; ii<data.length; ii++) {
    let i = ""+ii;
    entry = {
      name: data[i][0],
      id: +i,
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
  cplotdata.iddim = cplotdata.data.dimension(function(d) {return d.id ;});
  cplotdata.bar.dim = cplotdata.data.dimension(function(d) {return d.id ;});
  cplotdata.bar.groups = {};
  for(let ii=1; ii<data[0].length-1; ii++) {
    let i = ""+ii;
    // for logarithmic and regular plot
    cplotdata.bar.groups[i] = {};

    cplotdata.bar.groups[i][true] = cplotdata.bar.dim.group().reduceSum(function(d) {
      n = Math.log( d[i]);
      if (n == "NaN" || n == -Infinity) return 0; else return n;
    });
    cplotdata.bar.groups[i][false] = cplotdata.bar.dim.group().reduceSum(function(d) {
      return d[i];
    });
  }

  //-------------------------------scatterplot
  cplotdata.scatter = {};
  // for scatter plot let the dimension return [x,y] for an x-y-scatterplot
  // initialize everything to 0 here
  cplotdata.scatter.dims = {};
  cplotdata.scatter.groups = {};
  for(let ii=1; ii<data[0].length-1; ii++) {
    let i = ""+ii;
    cplotdata.scatter.dims[i] = {};
    cplotdata.scatter.groups[i] = {};
    for(let jj=1; jj<data[0].length-1; jj++) {
      let j = ""+jj;
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
  cplotdata.scatter.dims[x][y] = cplotdata.data.dimension(function(d) {
    return [d[x], d[y]];
  });

  // generate group for scatterplot
  cplotdata.scatter.groups[x][y] = cplotdata.scatter.dims[x][y].group().reduce(
    function (p, v) {
      let x_dat = v[x];
      let y_dat = v[y];
      if ((x_dat != 0) && (y_dat != 0)) {
        dist = 1.0*(x_dat - y_dat)/Math.max(x_dat, y_dat);
      } else {
        dist = 0;
      }
      p[x] = v[x];
      p[y] = v[y];
      p.color = dist.toFixed(2);
      p.name = v.name;
      return p;
    },
    function (p, v) {
      p[x] = 0.0;
      p[y] = 0.0;
      p.color = 2;
      p.name = "-";
      return p;
    },
    function () {
      p = {}
      p[x] = 0.0;
      p[y] = 0.0;
      p.color = 2;
      p.name = "-";
      return p;
    }
  );
}

function plot_custom_charts() {
  // options
  width = 600;
  height = 400;

  // selected options
  var xlogarithmic = document.getElementById("plotx-log").checked;
  var ylogarithmic = document.getElementById("ploty-log").checked;
  var xdata = document.getElementById("plotx-select").value;
  var ydata = document.getElementById("ploty-select").value;

  prepare_scatter_plot(xdata, ydata);

  // undo filtering everywhere
  cplotdata.bar.dim.filterAll();
  cplotdata.scatter.dims[xdata][ydata].filterAll();

  // apply filters for selected rows
  selectedrows = ipetlongtable.rows({filter:'applied', sort:'applied'})[0];
  cplotdata.iddim.filter(function(d) {
    return selectedrows.indexOf(d) > -1;
  });

  customplot.bar = dc.barChart("#custombarplot");
  customplot.bar.width(width)
    .height(height)
    .dimension(cplotdata.bar.dim)
    .group(cplotdata.bar.groups[xdata][xlogarithmic])
    //.data(function(group) {
    //  return group.all().filter(function(d){
    //      return selectedrows.indexOf(d.key) > -1;
    //    })
    //})
    .ordering(function (d) {return +d.value})
    .renderHorizontalGridLines(true)
    .xUnits(dc.units.ordinal)
    .brushOn(true)
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
  } else {
    customplot.bar.title(function (d) {
      return d.key + ": " + d.value;
    })
  }

  xmin = d3.min(cplotdata.rawdata, function (d) { return d[xdata]; })
  ymin = d3.min(cplotdata.rawdata, function (d) { return d[ydata]; })
  xmax = d3.max(cplotdata.rawdata, function (d) { return d[xdata]; })
  ymax = d3.max(cplotdata.rawdata, function (d) { return d[ydata]; })

  customplot.scatter = dc.scatterPlot("#customscatterplot");
  customplot.scatter.width(width)
    .height(height)
    .dimension(cplotdata.scatter.dims[xdata][ydata])
    .group(cplotdata.scatter.groups[xdata][ydata])
    .data(function(group) {
      return group.all()
        .filter(function(d){
          return ((d.key[0]>0 && d.key[1]>0));
        })
    })
    .symbolSize(8)
    .elasticX(true)
    .elasticY(true)
    .brushOn(true)
    .renderHorizontalGridLines(true)
    .renderVerticalGridLines(true)
    .title(function (d) {
      return d.value.name + ": " + d.key;
    })
    .colorAccessor(function (d) {
      return d.value.color;
    })
    .existenceAccessor(function(d) {
      return d.value[ydata];
    })
    .colors(d3.scaleLinear()
      .domain([
        -1,-0.9,-0.8,-0.7,-0.6,-0.5,-0.4,-0.3,-0.2,-0.1,
        0,
        0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,
        2])
      .range([
        "#ff5555",//red 1.0
        "#ee5555",//red 0.9
        "#dd5555",//red 0.8
        "#cc5555",//red 0.7
        "#bb5555",//red 0.6
        "#aa5555",//red 0.5
        "#995555",//red 0.4
        "#885555",//red 0.3
        "#775555",//red 0.2
        "#665555",//red 0.1
        "#555555",//black
        "#556655",//green 1.0
        "#557755",//green 0.9
        "#558855",//green 0.8
        "#559955",//green 0.7
        "#55aa55",//green 0.6
        "#55bb55",//green 0.5
        "#55cc55",//green 0.4
        "#55dd55",//green 0.3
        "#55ee55",//green 0.2
        "#55ff55",//green 0.1
        "#ffffff",// white
      ]));

  if (xlogarithmic){
    customplot.scatter.x(d3.scaleLog().domain([Math.max(xmin, 0.01), xmax]))
      .xAxisPadding("10%")
      .xAxis().tickFormat(function (v) {
        for (var i in tickValues) {
          if (v == tickValues[i]) return tickValues[i];
        }
        return "";
      })
      .tickValues(tickValues);
  } else {
    var xpadding = (xmax - xmin);
    if (xpadding){ xpadding = xpadding*.1; } else { xpadding = 1; }

    customplot.scatter.x(d3.scaleLinear().domain([xmin,xmax]).nice())
      .xAxisPadding(xpadding)
  }
  if (ylogarithmic){
    customplot.scatter.y(d3.scaleLog().domain([Math.max(ymin, 0.01), ymax]).nice())
      .yAxisPadding("10%")
      .yAxis().tickFormat(function (v) {
        for (var i in tickValues) {
          if (v == tickValues[i]) return tickValues[i];
        }
        return "";
      })
      .tickValues(tickValues);
  } else {
    var ypadding = (ymax - ymin);
    if (ypadding){ ypadding = ypadding*.1; } else { ypadding = 1; }

    customplot.scatter.y(d3.scaleLinear().domain([ymin,ymax]).nice())
      .yAxisPadding(ypadding)
  }

  // render all plots on this page
  dc.renderAll();
}

function exportfunction(id) {
  var html = d3.select("#"+id+" svg")
    .attr('title', 'Rubberband plot')
    .attr("version", 1.1)
    .attr("xmlns", "http://www.w3.org/2000/svg")
    .node().outerHTML;
  var imgsrc = 'data:image/svg+xml;base64,'+ btoa(html);
  var a = document.createElement("a");
  a.download = id+"_image.svg";
  a.href = imgsrc;
  a.click();
}

// ------------------ listeners
$(document).ready(function() {
  // listen to plot form
  $('#rb-ipet-eval-result').on('change', '#rb-plot-form', function(e) {
    // reset filters
    if ((customplot.bar != undefined) && (customplot.scatter != undefined)) {
      customplot.bar.filterAll();
      customplot.scatter.filterAll();
    }
    plot_custom_charts();
  });

  $('#rb-ipet-eval-result').on('click', '#exportbarplot', function(e) {
    exportfunction("custombarplot");
  });
  $('#rb-ipet-eval-result').on('click', '#exportscatterplot', function(e) {
    exportfunction("customscatterplot");
  });
});
