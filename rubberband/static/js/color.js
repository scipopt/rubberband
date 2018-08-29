
function Color(red, green, blue) {
    var r, g, b;
    var setColors = function(red, green, blue) {
        r = red; g = green; b = blue;
    };

    setColors(red, green, blue);

    this.getColors = function() {
        var colors = { r: r, g: g, b: b };
        return colors;
    };

    this.getColorString = function() {
        return r + "," + g + "," + b;
    };
}

function getBackgroundColor(colorBase, factor) {
  // Get interpolated background color between colorBase and white scaled by factor.
  // A factor of 1 gives baseColor, a factor of 0 gives white.
  // Factor is capped below by 0.1.
  if (factor < .1) {
    factor = .1;
  }
  return interpolateColor(color_white, colorBase, factor);
}

function interpolateColor(colorOne, colorTwo, factor) {
  // Interpolate the colorBase by the factor to make it lighter.
  // A factor of 1 gives baseColor, a factor of 0 gives white.
  if (factor >= 1) {
    return colorOne;
  } else {
    percentage = factor * 100;
    var color_one = colorOne.getColors();
    var color_two = colorTwo.getColors();
    var r = interpolate(color_one.r, color_two.r, 100, percentage);
    var g = interpolate(color_one.g, color_two.g, 100, percentage);
    var b = interpolate(color_one.b, color_two.b, 100, percentage);
    return new Color(r, g, b);
  }
}

function interpolate(start, end, steps, count) {
  // Interpolate between start and end in steps.
  var s = start, e = end;
  var interpolated = s + (((e - s) / steps) * count);
  return Math.floor(interpolated);
}

// Custom defined colors:
/*
color_red = new Color(245, 50, 50);
color_green = new Color(50, 245, 50);
*/
color_dark_gray = new Color(160, 160, 160);
color_gray = new Color(200, 200, 200);
color_white = new Color(255, 255, 255);
color_red = new Color(240, 40, 150);
color_green = new Color(130, 200, 30);
