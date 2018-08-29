$("a.bs-tooltip").tooltip();

formatInstanceResults();

function formatInstanceResults() {
  $('.instance-result').DataTable({
    scrollY: '80vh',
    scrollX: true,
    scroller: true,
    scrollCollapse: true,
    paging: false,
    dom: 'frtip',
    autoWidth: false,
  });
}

