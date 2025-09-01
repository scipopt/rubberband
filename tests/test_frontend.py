from base import TestHandlerBase


class GetTest(TestHandlerBase):
    def test_help(self):
        response = self.fetch("/help")
        self.assertEqual(response.code, 200)
        self.assertIn(b"Help", response.body)

    def test_search(self):
        response = self.fetch("/search")
        self.assertEqual(response.code, 200)
        self.assertIn(b"Search", response.body)

    def test_search_query(self):
        response = self.fetch("/search?test_set=&mode=&run_initiator=&settings_short_name=default&"
                              "solver=&solver_version=&git_hash=&lp_solver=&lp_solver_version=&"
                              "tags=")
        self.assertEqual(response.code, 200)
        self.assertIn(b"Compare selected Testruns?", response.body)

    def test_visualize(self):
        response = self.fetch("/visualize")
        self.assertEqual(response.code, 200)
        self.assertIn(b"End Date", response.body)

    def test_upload(self):
        response = self.fetch("/upload")
        self.assertEqual(response.code, 200)
        self.assertIn(b"Please select a set of logfiles for upload:", response.body)

    def test_notfound(self):
        response = self.fetch("/dsnbhjfsb")
        self.assertEqual(response.code, 404)
        self.assertIn(b"Something went wrong, we couldn't find the page you requested.",
                response.body)
