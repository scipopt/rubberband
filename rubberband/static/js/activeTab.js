// define global variables
let path = window.location.pathname;
let end = path.split("/");
set_active_tab(end[1]);

function set_active_tab(route) {
    $(".nav-sidebar li").removeClass("active");
    $(`.nav-sidebar li a[href="/${route}"]`).parent("li").addClass("active");
}
