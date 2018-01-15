"""URL routes for rubberband tornado app."""
import rubberband.handlers.fe as fe
import rubberband.handlers.api as api

routes = [
    # The following Views all inherit from BaseHandler (in base.py)
    # Frontend views
    (r"/", fe.MainView),
    (r"/visualize", fe.VisualizeView),
    (r"/compare", fe.CompareView),
    (r"/help", fe.HelpView),
    # for typeahead in visualize.js
    (r"/instances/names", fe.InstanceNamesEndpoint),
    # for typeahead in statistic.js
    (r"/instances/?(?P<parent_id>[^\/]+)", fe.InstanceEndpoint),
    (r"/result/(?P<parent_id>[^\/]+)", fe.ResultView),
    (r"/result/(?P<parent_id>[^\/]+)/instance/?(?P<child_id>[^\/]+)?", fe.InstanceView),
    (r"/file/(?P<file_id>[^\/]+)", fe.FileView),
    (r"/statistics/(?P<parent_id>[^\/]+)", fe.StatisticsView),
    (r"/search", fe.SearchView),
    (r"/upload", fe.UploadView),
    (r"/eval/(?P<eval_id>[^\/]+)", fe.EvaluationView),
    (r"/display/(?P<mode>[^\/]+)/(?P<id>[^\/]+)", fe.DisplayView),
    # API Endpoints
    (r"/api/upload/async", api.UploadAsyncEndpoint),
    (r"/api/upload", api.UploadEndpoint),
    (r"/api/search", api.SearchEndpoint),
]
