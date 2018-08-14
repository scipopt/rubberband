
// function definitions ================================================

function delete_cookie(key) {
  set_cookie(key, "", "Thu, 01 Jan 1970 00:00:01 GMT");
};

function get_cookie(key) {
  search = "; " + document.cookie;
  parts = search.split("; " + key + "=");
  if (parts.length == 2) return parts.pop().split(";").shift();
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

function update_tr_star_single(target, favorited) {
  target = $(target);
  if (favorited) {
    target.addClass("fa");
    target.removeClass("far");
    //console.log("zwei ");
  } else {
    target.addClass("far");
    target.removeClass("fa");
    //console.log("eins");
  }
}

function update_all_stars() {
  key = "starred-testruns";
  $('span.rb-tr-star').each(function(index) {
    name = this.attributes["name"].value;
    cookie = get_cookie(key);
    favorited = cookie.includes(name);
    update_tr_star_single(this, favorited);
  });
}

function update_tr_stars_by_name(name) {
  key = "starred-testruns";
  favorited = get_cookie(key).includes(name);
  $('span.rb-tr-star[name="' + name + '"]').each(function(index) {
    update_tr_star_single(this, favorited);
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
// when document is ready do ...
$(document).ready(function(){
  console.log(document.cookie);
});

// click on stars
$('form#compare').on('click', 'span.rb-tr-star', function (e) {
  name = e.target.attributes["name"].value;

  toggle_tr_cookie(name);
  update_tr_stars_by_name(name);
});
