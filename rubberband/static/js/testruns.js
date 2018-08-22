
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

function toggle_tr_cookie(tr_id) {
  key = "starred-testruns";
  value = get_cookie(key);

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

// ======================================================
// listeners for elements

// -- click on stars in search view
// listen to form.compare because span.rb-tr-star may not be present at time of execution of
//        below lines
$('body').on('click', 'span.rb-tr-star', function (e) {
  name = e.target.attributes["name"].value;
  toggle_tr_cookie(name);
  toggle_tr_stars_by_name(name);
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
  console.log(document.cookie);
  init_all_stars();
  select_all_compares();
});
