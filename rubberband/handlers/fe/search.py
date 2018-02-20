"""Contains SearchView."""
from rubberband.models import TestSet
from rubberband.utils import get_uniques
from rubberband.handlers.common import search
from .base import BaseHandler


class SearchView(BaseHandler):
    """Request handler handling the search."""

    def get(self):
        """
        Answer to GET requests.

        The initial search view, possibly prefilled with query string options.
        Renders `search_form.html`.
        """
        options = get_options()

        self.render("search_form.html", page_title="Search", search_options=options)

    def post(self):
        """
        Answer to POST requests, this serves as the ajax backend that provides the results table.

        Searches according to form fields in POST request.
        Writes `results_table.html`.
        """
        query = self.fill_query()
        results = search(query)
        exclude = self.get_argument("exclude_testset", default=None)
        if exclude:
            results = [r for r in results if r.meta.id != exclude]

        self.write(self.render_string("results_table.html", tablename="search-result",
            results=results, checkboxes=True))

    def fill_query(self, all_fields=None):
        """
        Fill out query with from POST data.

        Parameters
        ----------
        all_fields : list
            List of fields that are supposed to be contained in the query.

        Returns
        -------
        dict
            query as dict
        """
        if all_fields is None:
            all_fields = query_fields + additional_fields
        query = {}
        for f in all_fields:
            value = self.get_argument(f, default=None)
            if value:
                query[f] = value
        return query


query_fields = [
    "test_set",
    "mode",
    "uploader",
    "settings_short_name",
    "solver",
    "solver_version",
    "lp_solver",
    "lp_solver_version",
    "run_environment",
    "limit",
]

additional_fields = [
    "git_hash",
    "tags",
]


def get_options(fields=None):
    """
    Get the selection options for the search, the five most used ones and all of them.

    Parameters
    ----------
    fields : list
        List of fields to get the options for

    Returns
    -------
    dict
        Dictionary containing the selection options.
    """
    if fields is None:
        fields = query_fields
    options = {}
    for field in fields:
        values, hot_values = get_uniques(TestSet, field)
        # version sorting
        if field.endswith("_version"):
            values.sort(reverse=True)
            hot_values.sort(reverse=True)
        else:
            values.sort()
            hot_values.sort()
        options[field] = []
        if len(hot_values) > 0:
            options[field] = hot_values + ["---------"]
        options[field].extend(values)
    options["defaults"] = {}
    return options
