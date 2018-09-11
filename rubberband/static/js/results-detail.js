Array.prototype.allValuesSame = function() {
  for(var i = 1; i < this.length; i++) {
    if(this[i] !== this[0]) {
      return false;
    }
  }
  return true;
}

// ####################################### global vars
var ipetlongtable;
var ipetaggtable;

var modal = document.getElementById("info-modal");

var details_table;
var meta_table;
var settings_table;
formatDetailsTable();
formatMetaTable();
formatSettingsTable();
$(".bs-tooltip").tooltip();
$("a.bs-popover").popover();

// ####################################### functions
function formattolerance(val) {
  /* make a number 1eN from a number N */
  newval = Number("1e" + String(val));
  return newval.toExponential(0);
}

function setButtons(val) {
  /* enable and disable ipet eval buttons */
  var value = false;
  if (val == "enabled") {
    var value = true;
  }
  $("#ipet-eval-menu .rb-wait").each(function() {
    this.disabled = value;
  });
};

function getData() {
  /* get data from eval form */
  evalid = $("#ipet-eval-file-select").val();
  defaultrun = $("#rb-legend-table input[type='radio']:checked").val();
  tolerance = formattolerance( $("#eval-tolerance-slider")[0].value);

  /* get data from url */
  url = window.location.href;
  search = window.location.search;
  path = window.location.pathname.split("/");

  // construct evaluation url
  getstr = (url.split("compare"+'=')[1] || '').split('&')[0];
  idlist = "?testruns=" + path[2];
  if (getstr != "") {
    idlist = idlist + "," + getstr;
  }
  evalurl = "/eval/" + evalid + idlist + "&tolerance=" + tolerance + "&default=" + defaultrun;

  return {
    form: { evalid: evalid, defaultrun: defaultrun, tolerance: tolerance, },
    url: { full: url, search: search, path: path, evalurl: evalurl, }
  }
};

function processResponse(data, pos) {
  /* process the raw response of the ipet evaluation */
  stamp = data.substring(0, 32);
  arr = data.split(stamp);
  return arr[pos];
};

function fillModal(content) {
  /* set modal contents to content */
  setButtons("disabled");
  modalAction("show");
  document.getElementById("info-modal-content").innerHTML = content;
};

function modalAction(action) {
  /* action can be hide and show for modal to be displayed or hidden */
  if (action != "hide" && action != "show") {
    $(modal).modal(action);
  }
  return false;
};

function add_ipet_eventlisteners() {
  /* add event listeners for long table */
  // plot_custom_chart defined in ipet-custom-plot.js
  ipetlongtable.on('search.dt', plot_custom_chart);
  ipetlongtable.on('order.dt', plot_custom_chart);

  /* hovering for ipet tables */
  $(document).on(hoverTable(2), "table#ipet-aggregated-table tbody tr");
  $(document).on(hoverTable(3), "table#ipet-long-table tbody tr");
}

function hoverTable(index) {
  /* method to toggle the hover class in a row */
  function toggleRow() {
    /* hovering for ipet tables */
    trIndex = $(this).index()+index;
    $(this).parent().parent().each(function(index) {
      row = $(this).find("tr:eq("+trIndex+")")
      row.toggleClass("hover");
      row.each(function(index) {
        $(this).find("td").toggleClass("hover");
        $(this).find("th").toggleClass("hover");
      });
    });
  }
  /* return the dictionary for the eventlisteners */
  return {
    mouseenter: toggleRow,
    mouseleave: toggleRow,
  }
}

function initIpetTables() {
  /* initialize ipet tables */
  ipetlongtable = $('table#ipet-long-table').DataTable({
    columnDefs: [
      { targets: [-1], searchable: true, visible: false, },
    ],
    scrollY: '80vh', scrollX: true, scroller: true, scrollCollapse: true,
    paging:         false,
    fixedColumns:   {
      leftColumns: 1,
    },
    order: [1, "desc"],
    dom: '<"ipet-long-table-toolbar">frtip',

  });
  ipetaggtable = $('table#ipet-aggregated-table').DataTable({
    scrollY: '80vh', scrollX: true, scroller: true, scrollCollapse: true,
    paging:         false,
    fixedColumns:   {
      leftColumns: 2,
    },
    dom: 'frtip',
  });

  console.log("eins");
  add_ipet_eventlisteners();
  console.log("zwei");
  format_dt_searchfield('#ipet-long-table');
  format_dt_searchfield('#ipet-aggregated-table');
  add_columns_toggle('ipet-long-table', ipetlongtable);
};

function redraw_datatables() {
  $($.fn.dataTable.tables(true)).DataTable().columns.adjust();
}

function formatMetaTable() {
    meta_table = $('.meta-table').DataTable({
        scrollY: '80vh',
        scrollX: true,
        scroller: true,
        scrollCollapse: true,
        paging: false,
        dom: 'frtip',
    });
}

function formatSettingsTable() {
    settings_table = $('#settings-table').DataTable({
        scrollY: '80vh',
        scrollX: true,
        scroller: true,
        scrollCollapse: true,
        paging: false,
        dom: 'frtip',
    });
}

function formatDetailsTable() {
  details_table = $('#details-table').DataTable({
    scrollY: '80vh',
    scrollX: true,
    scroller: true,
    scrollCollapse: true,
    paging: false,
    columnDefs: [
      { type: 'any-number', targets: 'number' },
      { targets: 0, }
    ],
    fixedColumns:   {
      leftColumns: 1,
    },
    dom: 'f<"rb-details-toolbar">rtip',
    autoWidth: false,
  });

  $('button#delete-result').click(function (e) {
    e.preventDefault()
    $.ajax({
      type: "DELETE",
      url: "/result/" + end[2],
      success: function (data){ window.location.href = "/search";},
      error:function(){
        alert("Something went wrong.");
      }
    });
  });

  $('button#reimport-result').click(function (e) {
    e.preventDefault()
    button = document.getElementById("reimport-result")
    button.disabled = true;
    currurl = window.location.href;
    $.ajax({
      type: "PUT",
      url: "/result/" + end[2],
      success: function (data){
        alert("Reimport complete");
        window.location.href = currurl;
      },
      error:function(){
        alert("Something went wrong.");
      }
    });
  });

  $('a[href="#settings-filtered"]').click(function (e) {
    e.preventDefault();
    $("tr.default-value").remove();
  });
}

/*
 * Colorate the details table cells for the compare view
 */
function colorateCells() {
    details_table.cells().every( function () {
      // determine if tooltip is string or number
      var element = $(this.node())[0];
      if (element.attributes["title"] !== undefined) {
          // these are the compare values, one value or many separated by '\n'.
          // currently we only do this for one compare value
          var other_values_str = element.attributes["title"].value;
          var values = Array(element.textContent);
          Array.prototype.push.apply(values, other_values_str.split("\n"));
          var rgb;
          if (element.attributes["invert"] !== undefined) {
            rgb = getRGBColor(element.attributes["class"].value, values, true);
          } else {
            rgb = getRGBColor(element.attributes["class"].value, values, false);
          }
          if (rgb) {
            element.style.backgroundColor = rgb.getColorString();
          }
      }
  })
}

// Get an array of values, and translate that to into an RGB array.
function getRGBColor(valclass, arr_values, invert) {
  var contains_floats = false;
  var floatValues = Array();
  for (var i = 0; i < arr_values.length; i++) {
    var floatVal = parseFloat(arr_values[i]);
    if (!isNaN(floatVal)) {
      contains_floats = true;
      floatValues.push(floatVal);
    }
  }
  // if array is all floats
  if (floatValues.length === arr_values.length) {
    if (floatValues.allValuesSame()) {
      // all values the same, no color needed
      return null;
    } else {
      // compute the appropriate color
      return computeColor(valclass, floatValues, invert);
    }
  } else if (arr_values.allValuesSame()) {
      return null;
  } else {
    // mix of floats and strings, or different strings
    return color_gray;
  }
}

function computeColor(valclass, arr_values, invert) {
  // The first value of arr_values is the principle value for compare view
  var arr_length = arr_values.length;
  if (valclass.includes("Time")) {
    // shift the time values by 1 second
    for( var i = 0; i < arr_length; i++ ) {
      arr_values[i] = arr_values[i]+1;
    }
  } else if (valclass.includes("Nodes")) {
    // shift the node values by 100 nodes
    for( var i = 0; i < arr_length; i++ ) {
      arr_values[i] = arr_values[i]+100;
    }
  } else if (valclass.includes("Bound")) {
    // for dual and primal bounds calculate with the absolute values
    for( var i = 0; i < arr_length; i++ ) {
      arr_values[i] = Math.abs(arr_values[i]);
    }
  }

  var largest = Math.max(...arr_values.slice(1));
  var smallest = Math.min(...arr_values.slice(1));
  var value = arr_values[0];

  var factor = 1;
  // in case we only have two values, the base and one compare value
  // largest and smallest compare values are equal
  // devide the smaller by the larger value, so that factor is in [0,1]
  if ( smallest != 0 && largest != 0 && value != 0 ) {
    if (value < smallest) {
      factor = value/smallest;
    } else if (value > largest) {
      factor = largest/value;
    }
  }
  factor = 1-factor;

  // if one of the values is zero we cannot compare
  if ( smallest == 0 || largest == 0 || value == 0) {
    return getBackgroundColor(color_dark_gray, 0.9);
  }

  // color dual and primal bounds in shades of grey
  if (valclass.includes("Bound")) {
    return getBackgroundColor(color_dark_gray, factor);
  }

  // finally, decide the color:
  if (value < smallest) {
    // if the value is better than all others
    return getBackgroundColor(color_green, factor);
  } else if (value > largest) {
    // if the value is worse than all others
    return getBackgroundColor(color_red, factor);
  } else {
    // otherwise we do not give a color but a shade of gray
    var relstddev = 0;
    if (arr_length > 2) {
      // in case we have more than two values we compute the mean
      var sum = 0.0;
      var arr_length = arr_values.length;
      for( var i = 0; i < arr_length; i++ ) {
        sum += arr_values[i];
      }
      var mean = sum/(arr_length);

      // ... compute the standard deviation and relative standard deviation
      var sum_of_squares = 0.0;
      for( var i = 0; i < arr_length; i++ ){
        sum_of_squares += Math.pow( (arr_values[i]-smallest), 2);
      }

      var stddeviation = Math.pow(sum_of_squares/(arr_length), 1/2);
      relstddev = stddeviation/smallest;
    }
    return getBackgroundColor(color_dark_gray, relstddev);
  }
}

function construct_toggle(toggle_id) {
  $('span#' + toggle_id).click(function (e) {
    $(this).toggleClass("fa-eye-slash fa-eye");

    var displaystyle = "";
    if ($(this).hasClass('fa-eye')) {
      displaystyle = "none";
    }

    var elements = $("." + toggle_id + "-hide");
    for(var i=0; i<elements.length; i++){
      elements[i].style.display = displaystyle;
    }
    redraw_datatables();
  });
}

function add_columns_toggle() {
  var toolbar = $('.rb-details-toolbar');
  toolbar.addClass("float-right rb-dt-custom");
  var out = '<label class="col-form-label text-left">Toggle columns:<select id="rb-details-select" class="custom-select">';
  for (colindex = 1; colindex < details_table.columns().count(); colindex = colindex+1) {
    column = details_table.column(colindex);
    coltitle = $(column.header()).text().split('\n')[0]
    out = out+'<option value="'+colindex+'">'+coltitle+"</option>";
  }
  out = out+"</select></label>";

  $('.rb-details-toolbar').html(out);
  $('#rb-details-select').on('change', function(e) {
    colindex = this.value;
    currcol = details_table.column(colindex);
    currcol.visible( !currcol.visible() );
  });

  $('#details-table_filter label').addClass("col-form-label text-left");
  $('#details-table_filter label input').addClass("m-0 form-control");
}

$(document).ready(function(){
  construct_toggle("toggle-settings");
  construct_toggle("toggle-meta");
  add_columns_toggle();
});

// when window is resized
$(window).resize(function(){
  redraw_datatables();
});

/* adjust tables */
$('a[data-toggle="tab"]').on('shown.bs.tab', function(e) {
  redraw_datatables();
});

// if compare is in query string, then we are in the compare view but only in a comparison to exactly one
//if ((window.location.search.indexOf("compare") >= 0) && !(window.location.valueOf("compare").toString().includes(","))) {

// if compare is in query string, then we are in the compare view
if (window.location.search.indexOf("compare") >= 0) {
  colorateCells();
}

// ######################## clickable elements

/* TODO
$('#eval-tolerance-slider').slider({
  formatter: function(val) {
    return formattolerance(val);
  }
});
*/

$('div#evaluation').on('change', 'select#ipet-long-filter-select', function (e) {
  /* make long table searchable for filtergroups */
  console.log();
  fg_name = this.value;
  // The '|' are for avoiding trouble with substrings
  ipetlongtable.search("|"+fg_name+"|").draw()
});

/* hide modal on click into window */
window.onclick = function(event) {
  if (event.target == modal) {
    modalAction("hide");
  }
};

$('button#ipet-eval-show-button').click(function (e) {
  localdata = getData();

  // construct url
  evalurl = "/display/eval/" + localdata.form.evalid;
  $.ajax({
    type: "GET",
    url: evalurl,
    success:function(data) {
      fillModal(data);
      setButtons("enable");
    },
    error:function(data){
      fillModal("Something went wrong.");
      setButtons("enable");
    }
  });
});

$('button#ipet-eval-download-button').click(function (e) {
  data = getData();
  evalurl = "/download?evaluation=" + data.form.evalid;
  window.location.href = evalurl;
});

$('button#ipet-eval-button').click(function (e) {
  evalurl = getData().url.evalurl;
  fillModal("Evaluating");

  var xhr = new XMLHttpRequest();
  xhr.open('GET', evalurl);
  xhr.onload = function() {
    setButtons("enable");
    data = processResponse(xhr.responseText, 2);
    datadict = JSON.parse(data);
    for(var key in datadict) {
      if (key == "rb-ipet-buttons") {
        continue;
      }
      var targetel = document.getElementById(key)
      targetel.innerHTML = datadict[key];
    }

    initIpetTables();

    $("div.ipet-long-table-toolbar").html(datadict["rb-ipet-buttons"]);

    $('#rb-ipet-eval-result').on('shown.bs.collapse', function(e) {
      redraw_datatables();
    });
  };
  xhr.onerror = function(e) {
    setButtons("enable");
  };
  xhr.onprogress = function(e) {
    fillModal(processResponse(xhr.responseText,1));
  };
  xhr.send();
});

$('button#ipet-eval-latex-button').click(function (e) {
  evalurl = getData().url.evalurl + "&style=latex";
  window.open(evalurl, "_blank");
});

$('button#info-modal-close').click(function (e) {
  modalAction("hide");
});

$('button#ipet-eval-show-log').click(function (e) {
  modalAction("show");
});
