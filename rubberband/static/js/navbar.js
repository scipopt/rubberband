// define global variables
let path = window.location.pathname;
let end = path.split("/");
set_active_tab(end[1]);

function set_active_tab(route) {
    $(".rb-navbar li").removeClass("active");
    $(`.rb-navbar li a[href="/${route}"]`).parent("li").addClass("active");
}

function goBack() {
  window.history.back();
}
