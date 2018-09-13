/* ############### global vars ############### */
let path = window.location.pathname;
let end = path.split("/");
let debug = "";

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

/* ############### exeuction ############### */

set_active_tab(end[1]);

