
// define global variables
let charts = {};
let dtp = {};
let dtf = {};
let query_params;

// -- date time parsers
dtp.detail = d3.timeParse("%Y-%m-%dT%H:%M:%S");
dtp.month_year = d3.timeParse('%b-%y');
dtp.date = d3.timeParse("%Y-%m-%d");

dtf.detail = d3.timeFormat("%Y-%m-%d %H:%M")

// ----------------------- functions

// collect names of instances for field 'data name'
function initializeTypeahead() {
  // jquery 'get' is just a wrapper for jquery 'ajax'
  $.get('/instances/names', function(data){
    $('.typeahead').typeahead({source:data});
  }, "json");
}

function setButtons(val) {
  /* enable and disable ipet eval buttons */
  var value = true;
  if (val == "enabled") {
    var value = false;
  }
  $("#visualize button").each(function() {
    this.disabled = value;
  });
};

function generateCharts(request_data) {
  setButtons("disabled");
  request_data._xsrf = getCookie("_xsrf");
  /* makes an ajax request for data and then draws charts */
  $.ajax({
    type: "POST",
    url: "visualize",
    data: request_data,
    success: function (data){
      makeCharts(JSON.parse(data));
      setButtons("enabled");
    },
    error:function(){
      alert("Something went wrong.");
      setButtons("enabled");
    }
  });
}

function makeCharts(data) {
  //re-populate the form with previously submitted values
  $("[name=data-name]").val(query_params["data-name"]);
  $("[name=start-date]").val(query_params["start-date"]);
  $("[name=end-date]").val(query_params["end-date"]);

  if (!data.length) {
    alert("No results found.");
    return;
  }

  // show charts
  $("#charts").removeAttr("hidden");

  // data preprocessing
  data.forEach(function(d) {
    d.git_commit_timestamp = dtp.detail(d.git_commit_timestamp.split("+")[0]);
    d.git_commit_timestamp_formatted = new Date(d.git_commit_timestamp);
  });

  var ndx = crossfilter(data);

  makeSolvedStatusesChart(data, ndx);
  makeRunModeChart(data, ndx);
  makeSolvingNodesChart(data, ndx);
  makeSolvingTimesChart(data, ndx);
  makeResultsCount(data, ndx);
  makeResultsTable(data, ndx);

  RefreshTable();
  dc.renderAll();

  for (var i = 0; i < dc.chartRegistry.list().length; i++) {
    var chartI = dc.chartRegistry.list()[i];
    chartI.on("filtered", RefreshTable);
  }
}

function makeSolvedStatusesChart(data, ndx) {
  charts.solvedStatusesChart = dc.pieChart('#solved-statuses');

  var solvedStatuses = ndx.dimension(function (d) { return d.Status; });
  var solvedStatusesGroup = solvedStatuses.group();

  charts.solvedStatusesChart
    .width(300)
    .height(300)
    .radius(100)
    .innerRadius(50)
    .dimension(solvedStatuses)
    .group(solvedStatusesGroup)
    .renderLabel(true);
}

function makeRunModeChart(data, ndx) {
  charts.runModesChart = dc.pieChart('#opt-mode');

  var runModes = ndx.dimension(function (d) { return d.opt_flag; });
  var runModeGroup = runModes.group();

  charts.runModesChart
    .width(300)
    .height(300)
    .radius(100)
    .innerRadius(50)
    .dimension(runModes)
    .group(runModeGroup)
    .renderLabel(true);
}

function makeResultsCount(data, ndx) {
  charts.resultsCount = dc.dataCount('.dc-results-count');

  var all = ndx.groupAll();

  charts.resultsCount
    .dimension(ndx)
    .group(all);
}

function makeSolvingTimesChart(data, ndx) {
  charts.solvingTimesChart = dc.scatterPlot("#solving-times");

  var solvingTimes = ndx.dimension(function (d) { return [d.git_commit_timestamp, d.TotalTime_solving]; });
  var solvingTimesGroup = solvingTimes.group();

  var max = Math.max.apply(Math, data.map(function(o){return o.TotalTime_solving;}))
  var min = Math.min.apply(Math, data.map(function(o){return o.TotalTime_solving;}))

  var padding = (max - min);
  if (padding){ padding = padding*.1; } else { padding = 1; }

  charts.solvingTimesChart
    .width(600)
    .height(300)
    .dimension(solvingTimes)
    .group(solvingTimesGroup)
    .x(d3.scaleTime().domain([dtp.date(query_params["start-date"]), dtp.date(query_params["end-date"])]))
    .yAxisPadding(padding)
    .renderHorizontalGridLines(true)
    .yAxisLabel("solving time (seconds)")
    .xAxisLabel("git commit timestamp");

  charts.solvingTimesChart.xAxis().tickFormat(dtp.month_year);
}

function makeSolvingNodesChart(data, ndx) {
  charts.solvingNodesChart = dc.scatterPlot("#solving-nodes");

  var solvingNodes = ndx.dimension(function (d) { return [d.git_commit_timestamp, d.Nodes]; });
  var solvingNodesGroup = solvingNodes.group();

  var max = Math.max.apply(Math, data.map(function(o){return o.Nodes;}))
  var min = Math.min.apply(Math, data.map(function(o){return o.Nodes;}))

  var padding = (max - min);
  if (padding){ padding = padding*.1; } else { padding = 1; }

  charts.solvingNodesChart
    .width(600)
    .height(300)
    .dimension(solvingNodes)
    .group(solvingNodesGroup)
    .x(d3.scaleTime().domain([dtp.date(query_params["start-date"]), dtp.date(query_params["end-date"])]))
    .renderHorizontalGridLines(true)
    .yAxisLabel("# solving nodes")
    .xAxisLabel("git commit timestamp")
    .yAxisPadding(padding);

  charts.solvingNodesChart.xAxis().tickFormat(dtp.month_year);
}

function makeResultsTable(data, ndx) {
  charts.resultsTable = $('#results-table');

  charts.tableDimension = ndx.dimension(
    function (d) {
      return d.opt_flag + ' ' + d.Nodes + ' ' + d.TotalTime_solving + ' ' + d.Iterations +
        ' ' + d.file_path;
    }
  );

  var dataTableOptions = {
    "bFilter": false,
    "bInfo": true,
    "bSort": true,
    columnDefs: [{
        targets: 0,
        data: function (d) { return "<a href='/result/" + d.parent_id + "'>" + d.filename + "</a>"; },
        defaultContent: ''
      }, {
        targets: 1,
        data: function (d) { return dtf.detail(d.git_commit_timestamp_formatted); },
        type: 'date',
        defaultContent: 'Not found'
      }, {
        targets: 2,
        data: function (d) { return d.opt_flag; },
        defaultContent: ''
      }, {
        targets: 3,
        data: function (d) { return d.Nodes; },
        defaultContent: ''
      }, {
        targets: 4,
        data: function (d) { return d.TotalTime_solving;},
        defaultContent: ''
      }, {
        targets: 5,
        data: function (d) {return d.Iterations;},
        defaultContent: ''
      },
    ]
  };
  charts.resultsTable.dataTable(dataTableOptions);
}

function RefreshTable() {
  dc.events.trigger(function () {
    alldata = charts.tableDimension.top(Infinity);
    charts.resultsTable.fnClearTable();
    charts.resultsTable.fnAddData(alldata);
    charts.resultsTable.fnDraw();
  });
}

function set_active_tab(route) {
  $(".nav-sidebar li").removeClass("active");
  $(`.nav-sidebar li a[href="/${route}"]`).parent("li").addClass("active");
}

// ------------------ document ready
$(document).ready(function() {
  // check if url is of right format
  if (window.location.search) {
    // get_query_params defined in rb-global.js
    var parts = get_query_params(window.location.search);
    if (Object.keys(parts).length == 4) {
      query_params = parts;
      dc.config.defaultColors(d3.schemeSet1);
      generateCharts(parts);
    } else {
      alert("All fields are required to execute a search!");
    }
  }

  initializeTypeahead();
  init_datetimepicker("datetimepicker_start");
  init_datetimepicker("datetimepicker_end");
});
