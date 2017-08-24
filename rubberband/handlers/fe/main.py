from .base import BaseHandler


class MainView(BaseHandler):
    '''
    Home view. This is redirected to SearchView.
    '''
    def get(self):
        # 301 permanent redirect
        self.redirect("search/", status=301)
