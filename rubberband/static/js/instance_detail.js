$("a.bs-tooltip").tooltip();

formatInstanceResults();

function formatInstanceResults() {
    $('.instance-result').DataTable({
	scrollY: 500,
	scroller: true,
	scrollCollapse: true
    });
}

