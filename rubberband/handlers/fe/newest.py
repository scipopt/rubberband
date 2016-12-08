from rubberband.models import TestSet
from .base import BaseHandler


class MainView(BaseHandler):
    '''
    Home
    '''
    def get(self):
        self.redirect("newest", status=301)


class NewestView(BaseHandler):
    '''
    Most recently uploaded files
    '''
    def get(self):
        results = TestSet.search().sort("-index_timestamp")[:100].execute()
        self.render("table_view.html", page_title="Recent Results", results=results)
