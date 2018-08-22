$("a.bs-tooltip").tooltip();

formatInstanceResults();

function formatInstanceResults() {
    $('.instance-result').DataTable({
        scrollY: '80vh',
        scroller: true,
        scrollCollapse: true,
        paging: false,
        dom: 'frtip',
    });
}

