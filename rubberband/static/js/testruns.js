
var colclasses = {};

// function definitions ================================================

function delete_cookie(key) {
  set_cookie(key, "", "Thu, 01 Jan 1970 00:00:01 GMT");
};

function get_cookie(key) {
  search = "; " + document.cookie;
  parts = search.split("; " + key + "=");
  if (parts.length == 2) return parts.pop().split(";").shift();
  return ""
};

function set_cookie(key, value, expiry) {
  document.cookie = key + "=" + value + ((expiry) ? "; expiry=" + expiry : "") + ";";
};

function toggle_favorited_tr(name) {
  console.log(name);

  toggle_tr_stars_by_name(name);
  let tr_id=name;

  let key = "starred-testruns";
  let value = get_cookie(key);
  console.log(get_cookie(key));

  if (!value) {
    set_cookie(key, tr_id);
  } else if (value == tr_id) {
    delete_cookie(key)
  } else if (value.includes(tr_id + ',')) {
    testruns = value.split(tr_id + ',');
    set_cookie(key, testruns.join(""));
  } else if (value.includes(',' + tr_id)) {
    testruns = value.split(',' + tr_id);
    set_cookie(key, testruns.join(""));
  } else {
    set_cookie(key, value + ',' + tr_id);
  }
}

function toggle_tr_checkbox_by_name(name, checkval) {
  $('input.rb-tr-checkbox[name="' + name + '"]').each(function(index) {
    this.checked = checkval
  });
}

function toggle_tr_stars_by_name(name) {
  $('span.rb-tr-star[name="' + name + '"]').each(function(index) {
    $(this).toggleClass("far fa");
  });
}

function init_tr_star_single(target, favorited) {
  target = $(target);
  if (favorited) {
    target.removeClass("far");
    target.addClass("fa");
  } else {
    target.removeClass("fa");
    target.addClass("far");
  }
}

function init_all_stars() {
  // cookie key
  key = "starred-testruns";
  cookie = get_cookie(key);
  $('span.rb-tr-star').each(function(index) {
    name = this.attributes["name"].value;
    favorited = cookie.includes(name);
    init_tr_star_single(this, favorited);
  });
}

function select_all_compares() {
  $('#rb-compares-table input.rb-tr-checkbox').each(function(index) {
    name = this.attributes["name"].value;
    toggle_tr_checkbox_by_name(name, true);
  });
}

function get_all_cookies() {
  cookies = {};
  rawcookies = document.cookie.split("; ");
  for(var i = 0; i < rawcookies.length; i++) {
    ingredients = rawcookies[i].split("=");
    cookies[ingredients[0]] = ingredients[1];
  }
  return cookies;
}

function init_colclasses(id, tables) {
  for (let i in tables) {
    $("#"+tables[i]+" table").addClass("dataTable no-footer");
  }
  colclasses[id] = [];
  $($("#"+id+" thead tr")[0].children).each(function() {
    classes = $(this).attr("class").split(" ")
    for (let i in classes) {
      if (classes[i].startsWith("rb-table-")) {
        colclasses[id].push(classes[i]);
      }
    }
  });
}

function align_table_columns_to(id, others) {
  // collect the column classes
  if (colclasses[id] === undefined) {
    init_colclasses(id, others);
  }

  for (let c in colclasses[id]) {
    let rbclass = colclasses[id][c];
    let width = $("#"+id+" th."+rbclass)[0].style["width"]
    if (width == "0px") {
      width = ".1px";
    }

    for (let i in others) {
      $("#"+others[i]+" th."+rbclass+", #"+others[i]+" td."+rbclass).each( function() {
        this.style["width"] = width;
      });
    }
  }
}

// ======================================================
// listeners for elements

// -- click on stars in search view
// listen to form.compare because span.rb-tr-star may not be present at time of execution of
//        below lines
$('body').on('click', 'span.rb-tr-star', function (e) {
  name = e.target.attributes["name"].value;
  toggle_favorited_tr(name);
});

// -- click on checkboxes in search view
// listen to form.compare because span.rb-tr-star may not be present at time of execution of
//        below lines
$('form#compare').on('change', 'input.rb-tr-checkbox', function (e) {
  name = e.target.attributes["name"].value;
  checked_val = this.checked;
  toggle_tr_checkbox_by_name(name, checked_val);
});

// ======================================================
// when document is ready do ...
$(document).ready(function(){
  init_all_stars();
  select_all_compares();
});
