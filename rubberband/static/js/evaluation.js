// global variables
button1 = document.getElementById("ipet-eval-button");
button2 = document.getElementById("ipet-eval-show-button");
button3 = document.getElementById("ipet-eval-download-button");
button4 = document.getElementById("ipet-eval-latex-button");
button1.disabled = false;
button2.disabled = false;
button3.disabled = false;
button4.disabled = false;
var ipetlongtable;
var ipetaggtable;

modal = document.getElementById("show-eval-file-modal");
evalid = "";
defaultrun = "";

function display_modal(data) {
    setButtonsDisabled(true);
    modal.style.display = "block";
    document.getElementById("show-eval-file").innerHTML = data;
};

function hide_modal() {
    modal.style.display = "none";
};

// format ipet tables
function formatIpetTable() {
    ipetlongtable = $('table.ipet-long-table').DataTable({
        columnDefs: [{ targets: [-1],
                       searchable: true,
                       visible: false, } ],
        scrollY: '80vh',
        scrollX: true,
        scroller: true,
        scrollCollapse: true,
        paging:         false,
        fixedColumns:   {
            leftColumns: 1,
        },
        order: [1, "desc"],
        dom: '<"ipet-long-toolbar">frtip',
    });
    ipetaggtable = $('table.ipet-aggregated-table').DataTable({
        scrollY: '80vh',
        scrollX: true,
        scroller: true,
        scrollCollapse: true,
        paging:         false,
        fixedColumns:   {
            leftColumns: 2,
        }
    });
};

$('button#ipet-eval-show-button').click(function (e) {
    getData(e);

    // construct url
    evalurl = "/display/eval/" + evalid;
    $.ajax({
        type: "GET",
        url: evalurl,
        success:function(data) {
            display_modal(data);
            setButtonsDisabled(false);
        },
        error:function(data){
            display_modal("Something went wrong.");
            setButtonsDisabled(false);
        }
    });
});

$('button#ipet-eval-download-button').click(function (e) {
    getData(e);
    evalurl = "/download?evaluation=" + evalid;
    window.location.href = evalurl;
});


$(document).on({
    mouseenter: function () {
        trIndex = $(this).index()+3;
        $("table.ipet-long-table").each(function(index) {
            row = $(this).find("tr:eq("+trIndex+")")
            row.addClass("hover");
            row.each(function(index) {
                $(this).find("td").addClass("hover");
                $(this).find("th").addClass("hover");
            });
        });
    },
    mouseleave: function () {
        trIndex = $(this).index()+3;
        $("table.ipet-long-table").each(function(index) {
            row = $(this).find("tr:eq("+trIndex+")")
            row.removeClass("hover");
            row.each(function(index) {
                $(this).find("td").removeClass("hover");
                $(this).find("th").removeClass("hover");
            });
        });
    }
}, "table.ipet-long-table tbody tr");

$(document).on({
    mouseenter: function () {
        trIndex = $(this).index()+2;
        $("table.ipet-aggregated-table").each(function(index) {
            row = $(this).find("tr:eq("+trIndex+")")
            row.addClass("hover");
            row.each(function(index) {
                $(this).find("td").addClass("hover");
                $(this).find("th").addClass("hover");
            });
        });
    },
    mouseleave: function () {
        trIndex = $(this).index()+2;
        $("table.ipet-aggregated-table").each(function(index) {
            row = $(this).find("tr:eq("+trIndex+")")
            row.removeClass("hover");
            row.each(function(index) {
                $(this).find("td").removeClass("hover");
                $(this).find("th").removeClass("hover");
            });
        });
    }
}, "table.ipet-aggregated-table tbody tr");

function setButtonsDisabled(stat) {
    button1.disabled = stat;
    button2.disabled = stat;
    button3.disabled = stat;
    button4.disabled = stat;
};

function getData(e) {
    e.preventDefault();

    // get data from form
    form_data = $("#ipet-eval-form").serializeArray();
    evalid = $("#ipet-eval-file-select").val();
    defaultrun = $("#ipet-eval-form input[type='radio']:checked").val();
};

$('div#summary').on('click', 'button#ipet-long-filter-button', function (e) {
    fg_name = this.innerHTML;
    // The '|' are for avoiding trouble with substrings
    ipetlongtable.search("|"+fg_name+"|").draw()
});

$('button#ipet-eval-button').click(function (e) {
    getData(e);
    display_modal("Please wait, generating table");

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
    evalurl = "/eval/" + evalid + idlist + "&default=" + defaultrun;
    $.ajax({
        type: "GET",
        url: evalurl,
        success:function(data) {
            hide_modal();
            setButtonsDisabled(false);
            datadict = JSON.parse(data);
            for(var key in datadict) {
                if (key == "buttons") {
                    continue;
                }
                var el = document.createElement("div");
                el.innerHTML = datadict[key];
                document.getElementById(key).replaceWith(el);
            }
            formatIpetTable();
            $("div.ipet-long-toolbar").html(datadict["buttons"]);
        },
        error:function(data){
            display_modal("Something went wrong.");
            setButtonsDisabled(false);
        }
    });
});

$('button#ipet-eval-latex-button').click(function (e) {
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
    evalurl = "/eval/" + evalid + idlist + "&default=" + defaultrun + "&style=latex";
    window.open(evalurl, "_blank");
});

$('button#show-eval-file-modal-close').click(function (e) {
    hide_modal();
});

window.onclick = function(event) {
    if (event.target == modal) {
        hide_modal();
    }
};
