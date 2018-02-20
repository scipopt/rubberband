
updateResultsTable();

function updateResultsTable() {
    // get formdata by selecting element with id 'search-form'
    form_data = $("#search-form").serializeArray();
    request_data = {};
    $.each( form_data, function( i, field ) {
        request_data[field.name] = field.value;
    });
    sb = $("#search-base").serializeArray();
    if (sb != "") {
        request_data["exclude_testset"] = sb[0].value;
    }
    $.ajax({
        type: "POST",
        url: "search",
        // get request_data from search form
        data: request_data,
        success: function (data){fillResultTable(data);},
        error:function(){
            alert("Something went wrong.");
        }
    });
}

function fillResultTable(data) {
    // fill resultTable with data,
    // while data should be a htmlstring that just has to be poured into the right container
    //$("#results-table").replaceWith(data);
    $("#results-table").html(data);
    tmp = $("#search-result");
    $.fn.dataTable.moment( 'D. MMM YYYY, HH:mm' );
    if (tmp[0].tagName == "TABLE") {
        tmp.DataTable({
            scrollY: '80vh',
            scrollX: true,
            scroller: true,
            scrollCollapse: true,
            paging: false,
            searching: false,
        });
    }
}

$("#search-button").click(function() {
    // on click on search-button, please update the resultstable according to the search fields
    updateResultsTable();
});

$("#reset-search-button").click(function() {
    $("#search-form")[0].reset();
    $("#search-button").click();
});
