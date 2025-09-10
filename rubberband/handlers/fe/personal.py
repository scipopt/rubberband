"""Contains HelpView."""

from .base import BaseHandler


class PersonalView(BaseHandler):
    """Request handler holding the personal page."""

    def get(self):
        """
        Answer to GET requests.

        Renders `personal.html`.
        """
        rst = self.get_testrun_table(
            self.get_starred_testruns(), tablename="rb-starred-table", checkboxes=False
        )

        self.render(
            "personal.html",
            page_title="Personal space",
            mycookies=self.get_all_cookies(),
            starred_table=rst,
        )

    def post(self):
        """
        Answer to POST requests.

        Renders `personal.html`.
        """
        self.clear_all_cookies()
        next_url = "{}/personal".format(self.application.base_url)
        self.redirect(next_url)
