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
    for(var i=0; i<selectedrows.length;i++) {
      var x_dat = +data[selectedrows[i]][xdata];
      var y_dat = +data[selectedrows[i]][ydata];
      var name_dat = data[selectedrows[i]][0];
      if ((x_dat != 0) && (y_dat != 0)) {
        dist = (x_dat - y_dat)/Math.max(x_dat, y_dat);
        if (dist > 0) {
          color = interpolateColor(color_gray, color_green, dist);
        } else {
          color = interpolateColor(color_gray, color_red, -dist);
        }
        coldata.push({
          x: x_dat,
          y: y_dat,
          name: name_dat,
          color: color.getColorString(),
        });
      }
    }
  } else {
    for(var i=0; i<selectedrows.length;i++) {
      coldata[i] = [data[selectedrows[i]][0], +data[selectedrows[i]][xdata]];
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
      type: ((rb_plot_type === "scatter") ? 'scatter' : 'column'),
      height: (9/16*100)+'%', // 16:9 ratio
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
        gridLineWidth: 1,
      },
      yAxis: {
        type: ((ylogarithmic) ? 'logarithmic' : 'linear'),
      },
    });
  } else { // 'column' plot
    customplot.update({
      chart: {
        zoomType: 'x',
      },
      yAxis: {
        type: ((xlogarithmic) ? 'logarithmic' : 'linear'),
      },
    });
  }
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

$('#rb-ipet-eval-result').on('change', '#rb-plot-type-select', function(e) {
  // listen to `plot` button on ipet result page
  show_hide_y_select()
});
