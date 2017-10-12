
// global variables
button1 = document.getElementById("ipet-eval-button");
button2 = document.getElementById("ipet-eval-show-button");
button1.disabled = false;
button2.disabled = false;

modal = document.getElementById("show-eval-file-modal");
evalid = "";

// format ipet tables
function formatIpetTable() {
    $('table.ipet-long-table').DataTable({
        scrollY: '50vh',
        scrollX: true,
        scroller: true,
        scrollCollapse: true
    });
    $('table.ipet-aggregated-table').DataTable({
        scrollY: '30vh',
        scrollX: true,
        scroller: true,
        scrollCollapse: true
    });
};

function setButtonsDisabled(stat) {
    button1.disabled = stat;
    button2.disabled = stat;
};

function getData(e) {
    e.preventDefault();
    setButtonsDisabled(true);

    // get data from form
    form_data = $("#ipet-eval-form").serializeArray();
    evalid = form_data[0].value;
};

$('button#ipet-eval-button').click(function (e) {
    getData(e);

    // get data from url
    currurl = window.location.href;
    path = window.location.pathname.split("/");
    id = path[2];
    getstr = (location.search.split("compare"+'=')[1] || '').split('&')[0];
    idlist = "?testruns=" + id;
    if (getstr != "") {
        idlist = idlist + "," + getstr;
    }

    // construct url
    evalurl = "/eval/" + evalid + idlist;
    $.ajax({
        type: "GET",
        url: evalurl,
        success:function(data) {
            setButtonsDisabled(false);
            datadict = JSON.parse(data);
            for(var key in datadict) {
                var el = document.createElement("div");
                el.innerHTML = datadict[key];
                document.getElementById(key).replaceWith(el);
            }
            formatIpetTable();
        },
        error:function(data){
            alert("Something went wrong." + data);
        }
    });
});

$('button#ipet-eval-show-button').click(function (e) {
    getData(e);
    modal.style.display = "block";

    // construct url
    evalurl = "/display/eval/" + evalid;
    $.ajax({
        type: "GET",
        url: evalurl,
        success:function(data) {
            setButtonsDisabled(false);
            document.getElementById("show-eval-file").innerHTML = data;
        },
        error:function(data){
            alert("Something went wrong." + data);
        }
    });
});

$('button#show-eval-file-modal-close').click(function (e) {
    modal.style.display = "none";
});

window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
};
