// ipetlongtable defined in static/js/evaluation.js

var customplot; // user defined plot

function get_plot_data() {
  var xdata = document.getElementById("plotx-select").value;
  var ydata = document.getElementById("ploty-select").value;
  var rb_plot_type = document.getElementById("rb-plot-type").value;

  selectedrows = ipetlongtable.rows({filter:'applied', sort:'applied'})[0];
  data = ipetlongtable.data();

  coldata = Array();

  // get data from dataframe
  if (rb_plot_type === "scatter") {
    console.log("scatter");
    for(var i=0; i<selectedrows.length;i++) {
      coldata[i] = [{
        x: +data[selectedrows[i]][xdata],
        y: +data[selectedrows[i]][ydata],
        name: data[selectedrows[i]][0],
      }];
      console.log(coldata[i]);
    }
  } else {
    console.log("column");
    for(var i=0; i<selectedrows.length;i++) {
      coldata[i] = [data[selectedrows[i]][0], +data[selectedrows[i]][selectedcol]];
      console.log(coldata[i]);
    }
  }
  return coldata;
}

function plot_custom_chart() {
  var rb_plot_type = document.getElementById("rb-plot-type").value;
  var xlogarithmic = document.getElementById("plotx-log").checked;
  var ylogarithmic = document.getElementById("ploty-log").checked;

  coldata = get_plot_data();

  customplot = Highcharts.chart("customplot", {
    chart: {
      type: rb_plot_type,
    },
    exporting: { fallbackToExportServer: false },
    title: { text: null, },
    credits: { enabled: false },
    series: [{
      name: 'value',
      showInLegend: false,
      data: coldata,
    }],
  });

  // options that are different
  if (rb_plot_type === "scatter") {
    customplot.update({
      chart: {
        zoomType: 'xy',
      },
      xAxis: {
        type: ((xlogarithmic) ? 'logarithmic' : 'linear'),
      },
      yAxis: {
        type: ((ylogarithmic) ? 'logarithmic' : 'linear'),
      }
    });
  } else { // 'column' plot
    customplot.update({
      yAxis: {
        type: ((xlogarithmic) ? 'logarithmic' : 'linear'),
      },
    });
  }

}

function update_user_plot() {
  plot.series[0].setData(coldata);
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
$('#rb-ipet-eval-result').on('click', '#rb-custom-plot-button', function(e) {
  // listen to `plot` button on ipet result page
  plot_custom_chart();
});

$('#rb-ipet-eval-result').on('click', '#rb-plot-type-select', function(e) {
  // listen to `plot` button on ipet result page
  show_hide_y_select()
});

