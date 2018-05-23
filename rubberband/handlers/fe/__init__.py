"""Contains RequestHandlers for Webinterface (fe for FrontEnd)."""
from .fourohfour import FourOhFourView  # noqa
from .compare import CompareView  # noqa
from .instance import InstanceView, InstanceNamesEndpoint, InstanceEndpoint  # noqa
from .file import FileView  # noqa
from .help import HelpView  # noqa
from .result import ResultView  # noqa
from .main import MainView  # noqa
from .statistics import StatisticsView  # noqa
from .search import SearchView  # noqa
from .upload import UploadView  # noqa
from .download import DownloadView # noqa
from .visualize import VisualizeView  # noqa
from .evaluation import EvaluationView # noqa
from .display import DisplayView # noqa
