from base import TestHandlerBase


class GetTest(TestHandlerBase):
    def test_newest(self):
        response = self.fetch("/newest")
        self.assertEqual(response.code, 200)
        self.assertIn(b"Recent Results", response.body)

    def test_faq(self):
        response = self.fetch("/faq")
        self.assertEqual(response.code, 200)
        self.assertIn(b"Frequently Asked Questions", response.body)

    def test_search(self):
        response = self.fetch("/search")
        self.assertEqual(response.code, 200)
        self.assertIn(b"No results found for given query.", response.body)

    def test_search_query(self):
        response = self.fetch("/search?test_set=&mode=&run_initiator=&settings_short_name=default&"
                              "solver=&solver_version=&git_hash=&lp_solver=&lp_solver_version=&"
                              "tags=")
        self.assertEqual(response.code, 200)
        self.assertIn(b"Compare Selected Runs", response.body)

    def test_visualize(self):
        response = self.fetch("/visualize")
        self.assertEqual(response.code, 200)
        self.assertIn(b"End Date", response.body)

    def test_upload(self):
        response = self.fetch("/upload")
        self.assertEqual(response.code, 200)
        self.assertIn(b"Please select at least 3 files for upload:", response.body)

    def test_notfound(self):
        response = self.fetch("/dsnbhjfsb")
        self.assertEqual(response.code, 404)
        self.assertIn(b"Sorry, that page doesn't exist.", response.body)
