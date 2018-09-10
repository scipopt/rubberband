Array.prototype.allValuesSame = function() {
  for(var i = 1; i < this.length; i++) {
    if(this[i] !== this[0]) {
      return false;
    }
  }
  return true;
}

var details_table;
var meta_table;
var settings_table;
formatDetailsTable();
formatMetaTable();
formatSettingsTable();
$(".bs-tooltip").tooltip();
$("a.bs-popover").popover();

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

