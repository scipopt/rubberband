
button = document.getElementById("ipet-eval-button");
button.disabled = false;

$('button#ipet-eval-button').click(function (e) {
    e.preventDefault();
    button = document.getElementById("ipet-eval-button");
    button.disabled = true;

    // get data from url
    currurl = window.location.href;
    path = window.location.pathname.split("/");
    id = path[2];
    getstr = (location.search.split("compare"+'=')[1] || '').split('&')[0];
    idlist = "?testruns=" + id;
    if (getstr != "") {
        idlist = idlist + "," + getstr;
    }

    // get data from form
    form_data = $("#ipet-eval-form").serializeArray();
    evalid = form_data[0].value;

    // construct url
    evalurl = "/eval/" + evalid + idlist;
    $.ajax({
       type: "GET",
       url: evalurl,
       success:function(data) {
           $("#ipet-eval-result").replaceWith(data);
           button.disabled = false;
       },
       error:function(){
           alert("Something went wrong.");
       }
    });
});
