// define global variables
let solvedStatusesChart, optModeChart, resultsTable, resultsCount, solvingNodesChart,
    solvingTimesChart, runModesChart, tableDimension, all_data, query_params;

// collect names of instances for field 'data name'
function initializeTypeahead() {
    // jquery 'get' is just a wrapper for jquery 'ajax'
    $.get('/instances/names', function(data){
        $('.typeahead').typeahead({source:data});
    }, "json");
}

function getParts(query_string) {
    /* utility method that parses a query string */
    var match,
        pl     = /\+/g,  // Regex for replacing addition symbol with a space
        search = /([^&=]+)=?([^&]*)/g,
        decode = function (s) { return decodeURIComponent(s.replace(pl, " ")); },
        query  = query_string.substring(1);

    params = {};
    while (match = search.exec(query))
        params[decode(match[1])] = decode(match[2]);

    return params;
}

function generateCharts(request_data) {
    /* makes an ajax request for data and then draws charts */
    $.ajax({
        type: "POST",
        url: "visualize",
        data: request_data,
        success: function (data){makeCharts(JSON.parse(data));},
        error:function(){
            alert("Something went wrong.");
        }
    });
}

function makeCharts(data) {
    // bind data to global variable for easier console debugging
    all_data = data;

    //re-populate the form with previously submitted values
    $("[name=data-name]").val(query_params["data-name"]);
    $("[name=start-date]").val(query_params["start-date"]);
    $("[name=end-date]").val(query_params["end-date"]);

    if (!data.length) {
        alert("No results found :(");
        return;
    }

    // show chart stuff
    $("#charts").removeAttr("hidden");

    // data preprocessing
    var dateTimeFormat = d3.timeFormat("%Y-%m-%dT%H:%M:%S");
    data.forEach(function(d) {
        d.git_commit_timestamp = d.git_commit_timestamp.split("+")[0];
        d.git_commit_timestamp = dateTimeFormat(d.git_commit_timestamp);
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
    solvedStatusesChart = dc.pieChart('#solved-statuses');

    var solvedStatuses = ndx.dimension(function (d) {
        return d.Status;
    });

    var solvedStatusesGroup = solvedStatuses.group();

    solvedStatusesChart
        .width(300)
        .height(300)
        .radius(100)
        .innerRadius(50)
        .dimension(solvedStatuses)
        .group(solvedStatusesGroup)
        .renderLabel(true);
}

function makeRunModeChart(data, ndx) {
    runModesChart = dc.pieChart('#opt-mode');

    var runModes = ndx.dimension(function (d) {
        return d.opt_flag;
    });

    var runModeGroup = runModes.group();

    runModesChart
        .width(300)
        .height(300)
        .radius(100)
        .innerRadius(50)
        .dimension(runModes)
        .group(runModeGroup)
        .renderLabel(true);

}

function makeResultsCount(data, ndx) {
    resultsCount = dc.dataCount('.dc-results-count');

    var all = ndx.groupAll();

    resultsCount
        .dimension(ndx)
        .group(all);

}

function makeSolvingTimesChart(data, ndx) {
    solvingTimesChart = dc.scatterPlot("#solving-times");

    var dateFormat= d3.timeFormat("%Y-%m-%d");
    var solvingTimes = ndx.dimension(function (d) { return [d.git_commit_timestamp, d.TotalTime_solving]; });
    var solvingTimesGroup = solvingTimes.group();

    var max = Math.max.apply(Math, data.map(function(o){return o.TotalTime_solving;}))
    var min = Math.min.apply(Math, data.map(function(o){return o.TotalTime_solving;}))

    var padding = (max - min);

    if (padding){
        padding = padding*.1;
    }
    else {
        padding = 1;
    }

    solvingTimesChart
        .width(600)
        .height(300)
        .dimension(solvingTimes)
        .group(solvingTimesGroup)
        .x(d3.scaleTime().domain([dateFormat(query_params["start-date"]), dateFormat(query_params["end-date"])]))
        .yAxisPadding(padding)
        .renderHorizontalGridLines(true)
        .yAxisLabel("solving time (seconds)")
        .xAxisLabel("git commit timestamp");

    solvingTimesChart.xAxis().tickFormat(d3.timeFormat('%b-%y'));

}

function makeSolvingNodesChart(data, ndx) {
    solvingNodesChart = dc.scatterPlot("#solving-nodes");

    var dateFormat= d3.timeFormat("%Y-%m-%d");
    var solvingNodes = ndx.dimension(function (d) { return [d.git_commit_timestamp, d.Nodes]; });
    var solvingNodesGroup = solvingNodes.group();

    var max = Math.max.apply(Math, data.map(function(o){return o.Nodes;}))
    var min = Math.min.apply(Math, data.map(function(o){return o.Nodes;}))

    var padding = (max - min);

    if (padding){
        padding = padding*.1;
    }
    else {
        padding = 1;
    }

    solvingNodesChart
        .width(600)
        .height(300)
        .dimension(solvingNodes)
        .group(solvingNodesGroup)
        .x(d3.scaleTime().domain([dateFormat(query_params["start-date"]), dateFormat(query_params["end-date"])]))
        .renderHorizontalGridLines(true)
        .yAxisLabel("# solving nodes")
        .xAxisLabel("git commit timestamp")
        .yAxisPadding(padding);

    solvingNodesChart.xAxis().tickFormat(d3.timeFormat('%b-%y'));
}

function makeResultsTable(data, ndx) {
    resultsTable = $('#results-table');

    tableDimension = ndx.dimension(
        function (d) {
            return d.opt_flag + ' ' + d.Nodes + ' ' + d.TotalTime_solving + ' ' + d.Iterations +
                ' ' + d.file_path;
        }
    );

    var dataTableOptions = {
        "bFilter": false,
        "bInfo": true,
        "bSort": true,
        columnDefs: [
            {
                targets: 0,
                data: function (d) { return "<a href='/result/" + d.parent_id + "'>" + d.filename + "</a>"; },
                defaultContent: ''
            },
            {
                targets: 1,
                data: function (d) { return d.git_commit_timestamp_formatted; },
                type: 'date',
                defaultContent: 'Not found'
            },
            {
                targets: 2,
                data: function (d) { return d.opt_flag; },
                defaultContent: ''
            },
            {
                targets: 3,
                data: function (d) { return d.Nodes; },
                defaultContent: ''
            },
            {
                targets: 4,
                data: function (d) { return d.TotalTime_solving;},
                defaultContent: ''
            },
            {
                targets: 5,
                data: function (d) {return d.Iterations;},
                defaultContent: ''
            },
            /*
            {
                targets: 5, //search column
                data: function (d) {return d.file_path;},
                defaultContent: '',
                visible: false
            }
            */
        ]
    };
    resultsTable.dataTable(dataTableOptions);
}

function RefreshTable() {
    dc.events.trigger(function () {
        alldata = tableDimension.top(Infinity);
        resultsTable.fnClearTable();
        resultsTable.fnAddData(alldata);
        resultsTable.fnDraw();
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
    var parts = getParts(window.location.search);
    if (Object.keys(parts).length == 4) {
      query_params = parts;
      generateCharts(parts);
    }
    else {
      alert("All fields are required to execute a search!");
    }
  }

  initializeTypeahead();
  init_datetimepicker("datetimepicker_start");
  init_datetimepicker("datetimepicker_end");
});
