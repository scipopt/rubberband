
function init_scatter_plot() {
  scatterplot = Highcharts.chart('scatterplot', {
    chart: {
      type: 'scatter',
      zoomType: 'xy',
    },
    exporting: { fallbackToExportServer: false },
    title: { text: null, },
    yAxis: {
      type: 'logarithmic',
    },
    credits: { enabled: false },
    series: [{
      name: 'value',
      showInLegend: false,
      data: coldata,
    }]
  });
}
function init_column_plot() {
  columnplot = Highcharts.chart('columnplot', {
    chart: { type: 'column', },
    exporting: { fallbackToExportServer: false },
    title: { text: null, },
    yAxis: {
      type: 'logarithmic',
    },
    credits: { enabled: false },
    series: [{
      name: 'value',
      showInLegend: false,
      data: coldata,  // [[x1,y1],[x2,y2],...]
    }]
  });
}

function update_user_plot() {
  plot.series[0].setData(coldata);
}
