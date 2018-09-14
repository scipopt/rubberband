"""URL routes for rubberband tornado app."""
import rubberband.handlers.fe as fe
import rubberband.handlers.api as api

routes = [
    # The following Views all inherit from BaseHandler (in base.py)
    # Frontend views
    (r"/", fe.MainView),
    (r"/compare", fe.CompareView),
    (r"/display/(?P<mode>[^\/]+)/(?P<id>[^\/]+)", fe.DisplayView),
    (r"/download?(?P<arg>[^\/]+)", fe.DownloadView),
    (r"/eval/(?P<eval_id>[^\/]+)", fe.EvaluationView),
    (r"/file/(?P<file_id>[^\/]+)", fe.FileView),
    (r"/help", fe.HelpView),
    (r"/result/(?P<parent_id>[^\/]+)", fe.ResultView),
    (r"/result/(?P<parent_id>[^\/]+)/instance/?(?P<child_id>[^\/]+)?", fe.InstanceView),
    (r"/search", fe.SearchView),
    (r"/statistics/(?P<parent_id>[^\/]+)", fe.StatisticsView),
    (r"/upload", fe.UploadView),
    (r"/user", fe.UserView),
    (r"/visualize", fe.VisualizeView),

    # for typeahead in statistic.js
    (r"/instances/?(?P<parent_id>[^\/]+)", fe.InstanceEndpoint),

    # for typeahead in visualize.js
    (r"/instances/names", fe.InstanceNamesEndpoint),

    # API Endpoints
    (r"/api/upload/async", api.UploadAsyncEndpoint),
    (r"/api/upload", api.UploadEndpoint),
    (r"/api/search", api.SearchEndpoint),
]
