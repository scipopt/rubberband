import rubberband.handlers.fe as fe
import rubberband.handlers.api as api

routes = [
    # Frontend views
    (r"/", fe.MainView),
    (r"/newest", fe.NewestView),
    (r"/visualize", fe.VisualizeView),
    (r"/compare", fe.CompareView),
    (r"/statistics", fe.StatisticsView),
    (r"/faq", fe.FAQView),
    (r"/instances/names", fe.InstanceNamesEndpoint),
    (r"/instances/?(?P<parent_id>[^\/]+)", fe.InstanceEndpoint),
    (r"/result/(?P<parent_id>[^\/]+)", fe.ResultView),
    (r"/result/(?P<parent_id>[^\/]+)/instance/?(?P<child_id>[^\/]+)?", fe.InstanceView),
    (r"/file/(?P<file_id>[^\/]+)", fe.FileView),
    (r"/search", fe.SearchView),
    (r"/upload", fe.UploadView),
    # API Endpoints
    (r"/api/upload/async", api.UploadAsyncEndpoint),
    (r"/api/upload", api.UploadEndpoint),
    (r"/api/executor", api.ExecutorEndpoint),
    (r"/api.*", api.MiscEndpoint),
]
