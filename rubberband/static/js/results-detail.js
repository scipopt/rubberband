Array.prototype.allValuesSame = function() {

    for(var i = 1; i < this.length; i++)
    {
        if(this[i] !== this[0])
            return false;
    }

    return true;
}
var table;
formatResultTables();
$(".bs-tooltip").tooltip();
$("a.bs-popover").popover();

// if compare is in query string, then we are in the compare view
if (window.location.search.indexOf("compare") >= 0) {
  red = new Color(245, 50, 50);
  green = new Color(50, 245, 50);
  gray = new Color(170, 170, 170);
  colorateCells();
}

function formatResultTables() {
    table = $('.results-table').DataTable({
      scrollY: 500,
      scrollX: true,
    	scroller: true,
    	scrollCollapse: true
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
               alert("Something went wrong. Go get Cristina.");
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
          var other_values_str = element.attributes["title"].value;
          var values = Array(element.textContent);
          Array.prototype.push.apply(values, other_values_str.split("\n"));
          var rgb;
          if (element.attributes["invert"] !== undefined) {
            rgb = getRGB(values, true);
          } else {
            rgb = getRGB(values, false);
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
function getRGB(arr_values, invert) {
  var contains_floats = false;
  var floatValues = Array();
  for (var i = 0; i < arr_values.length; i++) {
    var floatVal = parseFloat(arr_values[i])
    if (invert) {
        floatVal = -floatVal;
    }
    kif (!isNaN(floatVal)) {
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
      return computeRGB(floatValues);
    }
  } else if (arr_values.allValuesSame()) {
      return null;
  } else {
    // mix of floats and strings, or different strings
    return gray;
  }
}

function computeRGB(arr_values) {
  // The first value of arr_values is the principle value for compare view
  // compute mean of the compare values
  var sum = 0.0;
  var arr_length = arr_values.length;
  for( var i = 0; i < arr_length; i++ ){
    sum += arr_values[i];
  }
  var mean = sum/(arr_length);
  var largest = Math.max(...arr_values);
  var smallest = Math.min(...arr_values);
  var percentage = (largest - smallest)/arr_values[0];
  if (mean < arr_values[0]) {
    return Interpolate(red, percentage);
  } else {
    return Interpolate(green, percentage);
  }
}

function Interpolate(colorBase, percentage) {
  if (percentage >= 1) {
    return colorBase;
  }
  else {
    percentage = percentage * 100;
    var end_color = colorBase.getColors();
    var r = interpolate(255, end_color.r, 100, percentage);
    var g = interpolate(255, end_color.g, 100, percentage);
    var b = interpolate(255, end_color.b, 100, percentage);
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
