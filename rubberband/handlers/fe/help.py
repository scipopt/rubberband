"""Contains HelpView."""

from .base import BaseHandler


class HelpView(BaseHandler):
    """Request handler holding the help page."""

    def get(self):
        """
        Answer to GET requests.

        Renders `help.html`.
        """
        questions = {
            "What is Rubberband?": "Rubberband is a flexible web view and analysis platform for solver log files of mathematical optimization software, backed by Elasticsearch.",  # noqa
            "Where do i report errors and other issues?": "Rubberband is a project developed on GitHub, you can post your issue <a href='https://github.com/scipopt/rubberband/issues'>here</a>.",  # noqa
            "How do I interpret the IPET tables in the evaluation view of the results?": """<p>
                In the IPET long table all instances are displayed. These that are only present in one testrun have a NaN in one of the columns (i.e. Time).
                </p><p>
                In the IPET aggregated table however only the filtergroups are displayed.
                These take into account only instances with the highest number of occurrences, in most cases that will be the number of testruns.
                So generally in the aggregated table you will get statistics for the instances that are present in all testruns.</p>""",  # noqa
            "How do I interpret the detailed table in the comparison view?": """<p>
                The color of the cell represents how the value for that particular instance compares.
                </p><p>
                A green cell indicates that the value of the baserun is better than all the comparisons, red means that it is the worse than all the others.
                The color intensity corresponds to the quotient of the basevalue to the nearest comparison value.
                </p><p>
                For green cells the nearest comparison value is the smallest of the comparisons;
                for red cells the nearest comparison value is the largest of the comparisons.
                </p><p>
                A grey cell indicates uncomparable values or that one of the values is zero.
                For the primal and dual bounds columns, the intensity reflects the relative difference between the values.
                In a comparison of more than two testruns, the grey scale value is chosen according to the magnitude of the relative standard deviation.
                </p><p>
                The color intensities in nodes and time columns are computed after a shift of 100 nodes and 1 second, respectively.
                </p>""",  # noqa
        }

        self.render(
            "help.html", questions=questions, page_title="Frequently Asked Questions"
        )
