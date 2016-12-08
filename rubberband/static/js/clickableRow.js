var re = /([^&=]+)=?([^&]*)/g;
var decode = function(str) {
  return decodeURIComponent(str.replace(/\+/g, ' '));
};
var parseParams = function(query) {
  var params = {}, e;
  if (query) {
    if (query.substr(0, 1) == '?') {
	query = query.substr(1);
    }

    while (e = re.exec(query)) {
	var k = decode(e[1]);
	var v = decode(e[2]);
	if (params[k] !== undefined) {
	    if (!$.isArray(params[k])) {
		params[k] = [params[k]];
	    }
	    params[k].push(v);
	} else {
	    params[k] = v;
	}
    }
  }
  return params;
};

$(".clickable-row").click(function() {
    window.document.location = $(this).data("url");
});

// search form pre-fill
var form = $("form");
if (form.length) {
  var params = parseParams(document.location.search);
  $.each(params, function( key, value ) {
    if (value !== "") {
      var domElem = $(`[name="${key}"]`).get(0)
      var elemType = domElem.tagName.toLowerCase()
      if (elemType == "select") {
        $(`[name="${key}"] option[value="${value}"]`).attr("selected", "selected");
      } else if (elemType == "input") {
        domElem.value = value;
      }
    }
  });
}


