// ####################################### global vars

button1 = document.getElementById("ipet-eval-button");
button2 = document.getElementById("ipet-eval-show-button");
button3 = document.getElementById("ipet-eval-download-button");
button4 = document.getElementById("ipet-eval-latex-button");
button1.disabled = false;
button2.disabled = false;
button3.disabled = false;
button4.disabled = false;
var ipetlongtable;
var ipetaggtable;
var logchart;
var plainchart;

modal = document.getElementById("info-modal");
evalid = "";
defaultrun = "";

// ####################################### functions
function get_selected_column() {
  selectedcol = $('select#selectcolumn').val();
  if (selectedcol == undefined){
    selectedcol = 2;
  }
  console.log("selectedcol "+selectedcol);
  return selectedcol;
}

function get_chart_data() {
  selectedrows = ipetlongtable.rows({filter:'applied', sort:'applied'})[0];
  selectedcol = get_selected_column();
  data = ipetlongtable.data();

  coldata = Array();

  // get data from dataframe
  for(var i=0; i<selectedrows.length;i++) {
    coldata[i] = [data[selectedrows[i]][0], +data[selectedrows[i]][selectedcol]];
  }
  return coldata;
}

function redraw_charts() {
  coldata = get_chart_data();
  plainchart.series[0].setData(coldata);
  coldata = get_chart_data();
  logchart.series[0].setData(coldata);
}

function initialize_charts() {
  coldata = get_chart_data();
  selectedcolumn = get_selected_column();
  logchart = Highcharts.chart('logchart', {
    chart: { type: 'column', },
    exporting: { fallbackToExportServer: false },
    title: { text: null, },
    yAxis: {
      type: 'logarithmic',
      plotLines: [{ color: 'black', value: 1, width: 2, }],
    },
    credits: { enabled: false },
    series: [{ name: 'value', showInLegend: false, data: coldata, }]
  });
  plainchart = Highcharts.chart('plainchart', {
    chart: { type: 'column', },
    exporting: { fallbackToExportServer: false },
    title: { text: null, },
    yAxis: {
      plotLines: [{ color: 'black', value: 1, width: 2, }],
    },
    credits: { enabled: false },
    series: [{ name: 'value', showInLegend: false, data: coldata, }]
  });
}

function processResponse(data, pos) {
  stamp = data.substring(0, 32);
  arr = data.split(stamp);
  return arr[pos];
};

function fillModal(data) {
  setButtonsDisabled(true);
  showModal();
  document.getElementById("info-modal-content").innerHTML = data;
};

function formattol(val) {
  newval = Number("1e" + String(val));
  return newval.toExponential(0);
}

function hideModal() {
  $(modal).modal("hide");
};

function showModal() {
  $(modal).modal("show");
};

// format ipet tables
function formatIpetTable() {
  console.log("formatting");
  ipetlongtable = $('table.ipet-long-table').DataTable({
    columnDefs: [{ targets: [-1],
      searchable: true,
      visible: false, } ],
    scrollY: '80vh',
    scrollX: true,
    scroller: true,
    scrollCollapse: true,
    paging:         false,
    fixedColumns:   {
      leftColumns: 1,
    },
    order: [1, "desc"],
    dom: '<"ipet-long-toolbar">frtip',
  });
  ipetaggtable = $('table.ipet-aggregated-table').DataTable({
    scrollY: '80vh',
    scrollX: true,
    scroller: true,
    scrollCollapse: true,
    paging:         false,
    fixedColumns:   {
      leftColumns: 2,
    },
    dom: 'frtip',
  });
  initialize_charts();
  $('#ipet-long-table').on( 'draw.dt', function () {
    console.log("event draw.id");
    redraw_charts();
  });
  $('table.ipet-long-table').on( 'draw.dt', function () {
    console.log("event draw.class")
    redraw_charts();
  });
};

function setButtonsDisabled(stat) {
  button1.disabled = stat;
  button2.disabled = stat;
  button3.disabled = stat;
  button4.disabled = stat;
};

function getTolerance() {
  val = $("#eval-tolerance-slider");
  return formattol(val[0].value);
};

function getData(e) {
  e.preventDefault();

  // get data from form
  form_data = $("#ipet-eval-form").serializeArray();
  evalid = $("#ipet-eval-file-select").val();
  defaultrun = $("#ipet-eval-form input[type='radio']:checked").val();
};

function getEvalUrl(e) {
  getData(e);
  tol = getTolerance();

  // get data from url
  currurl = window.location.href;
  path = window.location.pathname.split("/");
  id = path[2];
  getstr = (location.search.split("compare"+'=')[1] || '').split('&')[0];
  idlist = "?testruns=" + id;
  if (getstr != "") {
    idlist = idlist + "," + getstr;
  }

  // construct url
  return "/eval/" + evalid + idlist + "&tolerance=" + tol + "&default=" + defaultrun;
};

// ######################## clickable elements

/* TODO
$('#eval-tolerance-slider').slider({
  formatter: function(val) {
    return formattol(val);
  }
});
*/

$('div#summary').on('click', 'button#ipet-long-filter-button', function (e) {
  fg_name = this.innerHTML;
  // The '|' are for avoiding trouble with substrings
  ipetlongtable.search("|"+fg_name+"|").draw()
});

$(document).on({
  mouseenter: function () {
    trIndex = $(this).index()+3;
    $("table.ipet-long-table").each(function(index) {
      row = $(this).find("tr:eq("+trIndex+")")
      row.addClass("hover");
      row.each(function(index) {
        $(this).find("td").addClass("hover");
        $(this).find("th").addClass("hover");
      });
    });
  },
  mouseleave: function () {
    trIndex = $(this).index()+3;
    $("table.ipet-long-table").each(function(index) {
      row = $(this).find("tr:eq("+trIndex+")")
      row.removeClass("hover");
      row.each(function(index) {
        $(this).find("td").removeClass("hover");
        $(this).find("th").removeClass("hover");
      });
    });
  }
}, "table.ipet-long-table tbody tr");

$(document).on({
  mouseenter: function () {
    trIndex = $(this).index()+2;
    $("table.ipet-aggregated-table").each(function(index) {
      row = $(this).find("tr:eq("+trIndex+")")
      row.addClass("hover");
      row.each(function(index) {
        $(this).find("td").addClass("hover");
        $(this).find("th").addClass("hover");
      });
    });
  },
  mouseleave: function () {
    trIndex = $(this).index()+2;
    $("table.ipet-aggregated-table").each(function(index) {
      row = $(this).find("tr:eq("+trIndex+")")
      row.removeClass("hover");
      row.each(function(index) {
        $(this).find("td").removeClass("hover");
        $(this).find("th").removeClass("hover");
      });
    });
  }
}, "table.ipet-aggregated-table tbody tr");

window.onclick = function(event) {
  if (event.target == modal) {
    hideModal();
  }
};

$('button#ipet-eval-show-button').click(function (e) {
  getData(e);

  // construct url
  evalurl = "/display/eval/" + evalid;
  $.ajax({
    type: "GET",
    url: evalurl,
    success:function(data) {
      fillModal(data);
      setButtonsDisabled(false);
    },
    error:function(data){
      fillModal("Something went wrong.");
      setButtonsDisabled(false);
    }
  });
});

$('button#ipet-eval-download-button').click(function (e) {
  getData(e);
  evalurl = "/download?evaluation=" + evalid;
  window.location.href = evalurl;
});

$('button#ipet-eval-button').click(function (e) {
  evalurl = getEvalUrl(e);
  fillModal("Evaluating");

  var xhr = new XMLHttpRequest();
  xhr.open('GET', evalurl);
  xhr.onload = function() {
    setButtonsDisabled(false);
    data = processResponse(xhr.responseText, 2);
    datadict = JSON.parse(data);
    for(var key in datadict) {
      if (key == "buttons") {
        continue;
      }
      var targetel = document.getElementById(key)
      targetel.innerHTML = datadict[key];
    }
    formatIpetTable();
    $("div.ipet-long-toolbar").html(datadict["buttons"]);

    $('#rb-ipet-eval-result').on('shown.bs.collapse', function(e) {
      console.log("collapse");
      redraw_datatables();
    });
  },
    xhr.onerror = function(e) {
      setButtonsDisabled(false);
    }
  xhr.onprogress = function(e) {
    fillModal(processResponse(xhr.responseText,1));
  }
  xhr.send();
});

$('button#ipet-eval-latex-button').click(function (e) {
  evalurl = getEvalUrl(e) + "&style=latex";
  window.open(evalurl, "_blank");
});

$('button#info-modal-close').click(function (e) {
  hideModal();
});

$('button#ipet-eval-show-log').click(function (e) {
  showModal();
});

$('div#summary').on('click', 'select#selectcolumn', function (e) {
  redraw_charts();
});
