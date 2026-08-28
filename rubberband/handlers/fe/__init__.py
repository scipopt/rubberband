"""Contains RequestHandlers for Webinterface (fe for FrontEnd)."""

from .analyze import AnalyzeExternalView  # noqa
from .compare import CompareView  # noqa
from .display import DisplayView  # noqa
from .download import DownloadView  # noqa
from .error import ErrorView  # noqa
from .evaluation import EvaluationView  # noqa
from .file import FileView  # noqa
from .help import HelpView  # noqa
from .instance import InstanceEndpoint, InstanceNamesEndpoint, InstanceView  # noqa
from .main import MainView  # noqa
from .personal import PersonalView  # noqa
from .result import ResultView  # noqa
from .search import SearchView  # noqa
from .upload import UploadView  # noqa
from .visualize import VisualizeView  # noqa
