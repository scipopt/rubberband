
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

function favorite_action(name) {
  let cookie_key = "starred-testruns";
  let cookie_value = get_cookie(cookie_key);

  if (!cookie_value) { // cookie is empty
    set_cookie(cookie_key, name);
    process_starred_to(name, true);
  } else if (cookie_value == name) { // cookie is `name`
    delete_cookie(cookie_key)
    process_starred_to(name, false);
  } else if (cookie_value.includes(name + ',')) { // cookie contains `name,`
    testruns = cookie_value.split(name + ',');
    set_cookie(cookie_key, testruns.join(""));
    process_starred_to(name, false);
  } else if (cookie_value.includes(',' + name)) { // cookie contains `,name`
    testruns = cookie_value.split(',' + name);
    set_cookie(cookie_key, testruns.join(""));
    process_starred_to(name, false);
  } else { // cookie does not contain `name`
    set_cookie(cookie_key, cookie_value + ',' + name);
    process_starred_to(name, true);
  }
}

function process_checkbox_to(name, checkval) {
  $('input.rb-tr-checkbox[name="' + name + '"]').each(function(index) {
    this.checked = checkval
  });
}

function process_starred_to(name, is_favorited) {
  $('span.rb-tr-star[name="' + name + '"]').each(function(index) {
    set_star(this, is_favorited);
  });
  if (is_favorited) {
    child = $($('span.rb-tr-star[name="' + name + '"]')[0]).parent().parent()
    $('#rb-starred-table').append(child.clone());
  } else {
    $('#rb-starred-table span.rb-tr-star[name="' + name + '"]').parent().parent().remove();
  }
}

function set_star(target, is_favorited) {
  target = $(target);
  if (is_favorited) {
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
    set_star(this, favorited);
  });
}

function select_all_compares() {
  $('#rb-compares-table input.rb-tr-checkbox').each(function(index) {
    name = this.attributes["name"].value;
    process_checkbox_to(name, true);
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
  favorite_action(name);
});

// -- click on checkboxes in search view
// listen to form.compare because span.rb-tr-star may not be present at time of execution of
//        below lines
$('form#compare').on('change', 'input.rb-tr-checkbox', function (e) {
  name = e.target.attributes["name"].value;
  checked_val = this.checked;
  process_checkbox_to(name, checked_val);
});

// ======================================================
// when document is ready do ...
$(document).ready(function(){
  init_all_stars();
  select_all_compares();
});
