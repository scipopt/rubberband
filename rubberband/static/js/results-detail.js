Array.prototype.allValuesSame = function() {
  for(var i = 1; i < this.length; i++) {
    if(this[i] !== this[0]) {
      return false;
    }
  }
  return true;
}

// ####################################### global vars
var modal = document.getElementById("info-modal");

var ipetlongtable;
var ipetaggtable;
var detailstable;

// ####################################### functions
function format_dt_searchfield(tableident) {
  $(tableident+'_filter label').addClass("col-form-label text-left");
  $(tableident+'_filter label input').addClass("m-0 form-control");
}

function construct_columns_toggle(tablename) {
  /* add columns toggle buttons to datatable with id tableident */
  var tableident = "#"+tablename;
  var table = $(tableident).DataTable();

  var toolbar = $('.'+tablename+'-toolbar');
  toolbar.addClass("float-right rb-dt-custom row");

  var out = toolbar.html()+'<label class="col-form-label text-left col">Toggle columns:<select id="'+tablename+'-select" class="custom-select">';

  ncols = table.columns().count()
  // ipet long table has an invisible column for filtering
  if (tablename.includes('ipet-long')) { ncols = ncols-1; }
  for (colindex = 1; colindex < ncols; colindex = colindex+1) {
    column = table.column(colindex);

    coltitle = $(column.header()).text().split('\n')[0]
    if (tablename.includes('ipet-long')) {
      if (colindex == 1) {
        coltitle = 'id';
      } else {
        arr = $('#'+tablename+'_wrapper .dataTables_scrollHead table thead tr th.col'+(colindex-1).toString());
        coltitle = Array.prototype.join.call(arr.map((x,y) => $(y).text()),",")
      }
    }

    out = out+'<option value="'+colindex+'">'+coltitle+"</option>";
  }
  out = out+"</select></label>";
  toolbar.html(out);

  $(tableident+'-select').on('change', function(e) {
    colindex = this.value;
    currcol = table.column(colindex);
    currcol.visible( !currcol.visible() );
  });

}

function formattolerance(val) {
  /* make a number 1eN from a number N */
  newval = Number("1e" + String(val));
  return newval.toExponential(0);
}

function buttonsDisable() { setButtons("disable"); }
function buttonsEnable() { setButtons("enable"); }

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

  // construct evaluation url
  getstr = (url.split("compare"+'=')[1] || '').split('&')[0];
  idlist = "?testruns=" + path.split("/")[2];
  if (getstr != "") {
    idlist = idlist + "," + getstr;
  }
  evalurl = "/eval/" + evalid + idlist + "&tolerance=" + tolerance + "&default=" + defaultrun;

  return {
    form: { evalid: evalid, defaultrun: defaultrun, tolerance: tolerance, },
    url: { full: url, search: search, evalurl: evalurl, }
  }
};

function processResponse(data, pos) {
  /* process the raw response of the ipet evaluation */
  stamp = data.substring(0, 32);
  arr = data.split(stamp);
  return arr[pos];
};


function modalShow() { modalAction("show"); }
function modalHide() { modalAction("hide"); }

function modalAction(action) {
  /* action can be hide and show for modal to be displayed or hidden */
  if (action == "hide" || action == "show") {
    $(modal).modal(action);
  } else {
    return false;
  }
};

function fillModal(content) {
  /* set modal contents to content */
  buttonsDisable();
  document.getElementById("info-modal-content").innerHTML = content;
  modalShow();
};

function add_ipet_eventlisteners() {
  /* add event listeners for long table */
  // plot_custom_charts defined in ipet-custom-plot.js
  ipetlongtable.on('search.dt', plot_custom_charts);
  // for now we don't replot on order because this will have no effect on the graphs
  //ipetlongtable.on('order.dt', plot_custom_charts);
}

function hoverTable(index, name) {
  /* method to toggle the hover class in a row */
  function toggleRow() {
    /* hovering for ipet tables */
    trIndex = $(this).index()+index;
    $("#"+name+'_wrapper table.dataTable').each(function(index) {
      row = $(this).find("tr:eq("+trIndex+")")
      row.toggleClass("hover");
      row.each(function(index) {
        $(this).find("td").toggleClass("hover");
      });
    });
  }
  return toggleRow;
}

function redraw_datatables() {
  $($.fn.dataTable.tables(true)).DataTable().columns.adjust();
  $($.fn.dataTable.tables(true)).DataTable().fixedColumns().relayout();
}

function initIpetTables(ipetlongtoolbartext) {
  /* initialize ipet tables */
  ipetlongtable = $('table#ipet-long-table').DataTable({
    columnDefs: [
      { targets: [-1], searchable: true, visible: false, },
      //{ targets: 0, width: '15%', },
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

  format_dt_searchfield('#ipet-long-table');
  format_dt_searchfield('#ipet-aggregated-table');

  $('.ipet-long-table-toolbar').html(ipetlongtoolbartext);
  construct_columns_toggle('ipet-long-table');
  add_ipet_eventlisteners();
};

function initSimpleTable(tableident) {
  $(tableident).DataTable({
    scrollY: '80vh', scrollX: true, scroller: true, scrollCollapse: true,
    paging: false,
    dom: 'frtip',
  });
}

function initDetailsTable(tablename) {
  var tableident = "#"+tablename;
  detailstable = $(tableident).DataTable({
    scrollY: '80vh', scrollX: true, scroller: true, scrollCollapse: true,
    paging: false,
    columnDefs: [
      { type: 'any-number', targets: 'number' },
      { targets: 0, }
    ],
    fixedColumns:   {
      leftColumns: 1,
    },
    dom: 'f<"'+tablename+'-toolbar">rtip',
    autoWidth: false,
  });

  /* want to be able to hide columns */
  construct_columns_toggle(tablename);
  /* we need to do this for tables with fixed columns by hand */
  $(document).on('mouseenter mouseleave', 'table#'+tablename+' tbody tr', hoverTable(1, tablename));
}

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

/*
 * Colorate the details table cells for the compare view
 */
function colorateCells() {
  detailstable.cells().every( function () {
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
  });
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

function construct_row_toggle(toggleident) {
  $('span#' + toggleident).click(function (e) {
    $(this).toggleClass("fa-eye-slash fa-eye");

    var displaystyle = "";
    if ($(this).hasClass('fa-eye')) {
      displaystyle = "none";
    }

    var elements = $("." + toggleident + "-hide");
    for(var i=0; i<elements.length; i++){
      elements[i].style.display = displaystyle;
    }
    redraw_datatables();
  });
}

// ######################## on document ready

$(document).ready(function(){
  /* init datatables */
  initDetailsTable('details-table');
  initSimpleTable('.meta-table, #settings-table');
  format_dt_searchfield(".dataTables");
  construct_row_toggle("toggle-settings");
  construct_row_toggle("toggle-meta");

  $(".bs-tooltip").tooltip();
  $("a.bs-popover").popover();

  /* adjust tables */
  /* when window is resized */
  $(window).resize(redraw_datatables);
  /* tab is toggled */
  $('a[data-toggle="tab"]').on('shown.bs.tab', redraw_datatables);
  /* something is uncollapsed in evaluation tab */
  $('#rb-ipet-eval-result').on('shown.bs.collapse', redraw_datatables);

  // if compare is in query string, then we are in the compare view
  if (window.location.search.indexOf("compare") >= 0) { colorateCells(); }

  /* update the number */
  $('#eval-tolerance-slider').on('input', function() {
    document.getElementById('ipet-tolerance-value').innerHTML = formattolerance(this.value);
  });

  // ######################## clickable elements

  $('div#evaluation').on('change', 'select#ipet-long-filter-select', function (e) {
    /* make long table searchable for filtergroups */
    fg_name = this.value;
    // The '|' are for avoiding trouble with substrings
    ipetlongtable.search("|"+fg_name+"|").draw()
  });

  /* hide modal on click into window */
  window.onclick = function(event) {
    if (event.target == modal) {
      modalHide();
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
        buttonsEnable();
      },
      error:function(data){
        fillModal("Something went wrong.");
        buttonsEnable();
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
      buttonsEnable();
      modalHide();
      data = processResponse(xhr.responseText, 2);
      datadict = JSON.parse(data);
      for(var key in datadict) {
        if (key == "rb-ipet-buttons") {
          continue;
        }
        var targetel = document.getElementById(key)
        targetel.innerHTML = datadict[key];
      }
      initIpetTables(datadict["rb-ipet-buttons"]);
      initialize_custom_chart(); // from ipet-custom-plot.js
    };
    xhr.onerror = buttonsDisable;
    xhr.onprogress = function(e) {
      fillModal(processResponse(xhr.responseText,1));
    };
    xhr.send();
  });

  $('button#ipet-eval-latex-button').click(function (e) {
    window.open( getData().url.evalurl + "&style=latex" , "_blank");
  });

  $('button#ipet-eval-show-log').click(modalShow);
  $('button#info-modal-close').click(modalHide);

  /* hovering for ipet tables */
  /* note: by binding these to document, we don't have to wait until after the evaluation */
  $(document).on('mouseenter mouseleave', '#ipet-aggregated-table_wrapper tbody tr', hoverTable(2, 'ipet-aggregated-table'));
  $(document).on('mouseenter mouseleave', '#ipet-long-table_wrapper tbody tr', hoverTable(3, 'ipet-long-table'));
});
