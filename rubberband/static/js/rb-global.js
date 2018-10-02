/* ############### global vars ############### */
var path = window.location.pathname;
var end = path.split("/");
var debug = "";

/* ############### functions ############### */

function set_active_tab(route) {
  /* highlight the current page in the navbar */
  $(".rb-navbar li").removeClass("active");
  $(`.rb-navbar li a[href="/${route}"]`).parent("li").addClass("active");
}

function goBack() {
  /* go back in history */
  window.history.back();
}

function init_datetimepicker(id) {
  $('#'+id).datetimepicker({ format: 'YYYY-MM-DD' });
}

function jsonlog(val) {
  console.log(JSON.stringify(val));
}

/* ############### exeuction ############### */

set_active_tab(end[1]);

