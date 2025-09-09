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
    (r"/result/(?P<testset_id>[^\/]+)", fe.ResultView),
    (r"/instance/?(?P<result_id>[^\/]+)?", fe.InstanceView),
    (r"/search", fe.SearchView),
    (r"/upload", fe.UploadView),
    (r"/personal", fe.PersonalView),
    (r"/visualize", fe.VisualizeView),

    # for typeahead in visualize.js
    (r"/instances/names", fe.InstanceNamesEndpoint),

    # for typeahead in statistic.js
    (r"/instances/?(?P<testset_id>[^\/]+)", fe.InstanceEndpoint),

    # API Endpoints
    (r"/api/comparison/(?P<base_id>[^\/]+)", api.ComparisonEndpoint),
    (r"/api/upload/async", api.UploadAsyncEndpoint),
    (r"/api/upload", api.UploadEndpoint),
    (r"/api/search", api.SearchEndpoint),
]
