from base import TestHandlerBase
import json
import os.path

DATADIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")


class GetAPITest(TestHandlerBase):
    def test_instance_names(self):
        '''
        Test that the expected content type is recieved.
        ["blend2", "rgn", "dcmulti", "misc03", "stein27", "vpm2", "enigma", "bell5", ...]
        '''
        response = self.fetch("/instances/names")
        self.assertEqual(response.code, 200)
        data = json.loads(response.body.decode("utf-8"))
        self.assertTrue(isinstance(data, list))
        self.assertTrue(len(data) > 50)


class UploadAPITest(TestHandlerBase):
    def test_upload_exception_handling(self):
        '''
        Test that the api can gracefully handle exceptions.
        '''
        response = self.fetch("/api/upload",
                              method="PUT",
                              body="something")
        self.assertEqual(response.code, 400)
        data = json.loads(response.body.decode("utf-8"))
        self.assertTrue(isinstance(data, dict))
        self.assertIn("status", data)
        self.assertIn("errors", data)
        self.assertIn("url", data)
        self.assertIn("Missing required files:", data["errors"]["_"][0])


class SearchAPITest(TestHandlerBase):
    def test_search(self):
        '''
        Test that the api can gracefully handle exceptions.
        '''
        response = self.fetch("/api/search?test_set=short",
                              method="GET")
        self.assertEqual(response.code, 200)
        data = json.loads(response.body.decode("utf-8"))
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 3)
