import tornado.web
from tornado.escape import json_encode, json_decode

from .base import BaseHandler, authenticated


class ExecutorEndpoint(BaseHandler):
    '''
    Listens for @bender mentions in new comments, then initiates and instance run.
    '''
    @authenticated
    def post(self):
        '''
        Validate webhook
        '''
        headers = dict(self.request.headers.get_all())

        if headers.get("X-Gitlab-Token") != self.application.webhook_secret:
            raise tornado.web.HTTPError(status_code=401, log_message="Invalid webhook token")

        body_data = json_decode(self.request.body.decode('utf-8'))
        project = body_data["project"]["name"]
        object_kind = body_data["object_kind"]
        note_body = body_data["object_attributes"].get("note")
        if project == "scip" and object_kind == "notes" and note_body:
            if "@bender" in note_body:
                pass
        return self.write(json_encode([]))
