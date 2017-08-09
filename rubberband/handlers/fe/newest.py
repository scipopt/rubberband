from rubberband.models import TestSet
from .base import BaseHandler


class MainView(BaseHandler):
    '''
    Home view. This is redirected to NewestView.
    '''
    def get(self):
        # 301 permanent redirect
        self.redirect("newest", status=301)

class NewestView(BaseHandler):
    '''
    Most recently uploaded files
    '''
    def get(self):
        # TestSet extends the DocType class of elasticsearch_dsl.
        # TestSet.search() returns a search-object that searches only for TestSets
        # The search-object can be defined independently from execution and returns TestSets
        results = TestSet.search().sort("-index_timestamp")[:100].execute()
        # render template with given variables
        self.render("table_view.html", page_title="Recent Results", results=results)
