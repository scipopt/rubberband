Array.prototype.allValuesSame = function() {
  for(var i = 1; i < this.length; i++) {
    if(this[i] !== this[0]) {
      return false;
    }
  }
  return true;
}

var table;
var meta_table;
var settings_table;
formatResultTables();
formatMetaTable();
formatSettingsTable();
$(".bs-tooltip").tooltip();
$("a.bs-popover").popover();

function redraw_datatables() {
  $($.fn.dataTable.tables(true)).DataTable().columns.adjust();
}

/* adjust tables */
$('a[data-toggle="tab"]').on('shown.bs.tab', function(e) {
  redraw_datatables();
});
// if compare is in query string, then we are in the compare view but only in a comparison to exactly one
//if ((window.location.search.indexOf("compare") >= 0) && !(window.location.valueOf("compare").toString().includes(","))) {

// if compare is in query string, then we are in the compare view
if (window.location.search.indexOf("compare") >= 0) {
  /* red = new Color(245, 50, 50);
  green = new Color(50, 245, 50); */
  dark_gray = new Color(160, 160, 160);
  gray = new Color(200, 200, 200);
  white = new Color(255, 255, 255);
  red = new Color(240, 40, 150);
  green = new Color(130, 200, 30);
  colorateCells();
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
    settings_table = $('.settings-table').DataTable({
        scrollY: '80vh',
        scrollX: true,
        scroller: true,
        scrollCollapse: true,
        paging: false,
        dom: 'frtip',
    });
}

function formatResultTables() {
    table = $('.results-table').DataTable({
        scrollY: '80vh',
        scrollX: true,
        scroller: true,
        scrollCollapse: true,
        paging: false,
        columnDefs: [
            { type: 'any-number', targets: 'number' },
        ],
        dom: 'frtip',
    });

    $('.nav-tabs').stickyTabs();

    $('#resultNavTabs a').click(function (e) {
          e.preventDefault()
          $(this).tab('show')
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
 * Colorate the result table cells for the compare view
 */
function colorateCells() {
    table.cells().every( function () {
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
            rgb = getRGB(element.attributes["class"].value, values, true);
          } else {
            rgb = getRGB(element.attributes["class"].value, values, false);
          }
          if (rgb) {
            element.style.backgroundColor = "rgb(" + rgb.getColorString() + ")";
          }
      }
  })
}

/*
 * Get an array of values, and translate that to into an RGB array.
 */
function getRGB(valclass, arr_values, invert) {
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
      return computeRGB(valclass, floatValues, invert);
    }
  } else if (arr_values.allValuesSame()) {
      return null;
  } else {
    // mix of floats and strings, or different strings
    return gray;
  }
}

function computeRGB(valclass, arr_values, invert) {
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
    return Interpolate(dark_gray, 0.9);
  }

  // color dual and primal bounds in shades of grey
  if (valclass.includes("Bound")) {
    return Interpolate(dark_gray, factor);
  }

  // finally, decide the color:
  if (value < smallest) {
    // if the value is better than all others
    return Interpolate(green, factor);
  } else if (value > largest) {
    // if the value is worse than all others
    return Interpolate(red, factor);
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
    return Interpolate(dark_gray, relstddev);
  }
}

function Interpolate(colorBase, factor) {
  if (factor >= 1) {
    return colorBase;
  }
  else {
    factor = factor * 100;
    // threshold what the human eye can see
    if (factor < 10) {
        factor = 10;
    }
    var end_color = colorBase.getColors();
    var r = interpolate(255, end_color.r, 100, factor);
    var g = interpolate(255, end_color.g, 100, factor);
    var b = interpolate(255, end_color.b, 100, factor);
    return new Color(r, g, b);
  }
}

// does math
function interpolate(start, end, steps, count) {
  var s = start,
      e = end,
      final = s + (((e - s) / steps) * count);
  return Math.floor(final);
}

// Class to manage an rgb color
function Color(_r, _g, _b) {
    var r, g, b;
    var setColors = function(_r, _g, _b) {
        r = _r;
        g = _g;
        b = _b;
    };

    setColors(_r, _g, _b);
    this.getColors = function() {
        var colors = {
            r: r,
            g: g,
            b: b
        };
        return colors;
    };

    this.getColorString = function() {
        return r + "," + g + "," + b;
    };
}

$(document).ready(function(){
  toggle_ids = ["toggle-meta", "toggle-settings"];

  for (i = 0; i < toggle_ids.length; i++) {
    toggle_id = toggle_ids[i];
    var elements = $("."+toggle_id+"-hide");
    $('span#' + toggle_id).click(function (e) {
      $(this).toggleClass("fa-eye-slash fa-eye");

      var displaystyle = "";
      if ($(this).hasClass('fa-eye')) {
          displaystyle = "none";
      }
      for(var i=0; i<elements.length; i++){
          elements[i].style.display = displaystyle;
      }
      redraw_datatables();
    });
  }
});

