"""Define data models and methods, also used by elasticsearch_dsl."""
import gzip
import json
import datetime
from elasticsearch_dsl import Boolean, Document, Text, Keyword, Date, Nested, Integer
from ipet import Key

from rubberband.constants import INFINITY_KEYS, INFINITY_MASK, INFINITY_FLOAT, \
    FILE_INDEX, RESULT_INDEX, TESTSET_INDEX, SETTINGS_INDEX


class File(Document):
    """The definition of a File object. A `File` contains the raw contents of a log file."""

    type = Keyword(required=True)  # out, set, err, solu
    filename = Keyword(required=True)  # check.MMM.scip-021ace1...out
    hash = Keyword(required=True)  # computed hash
    testset_id = Keyword(required=True)  # for application-side joins
    text = Text(index=False, required=True)  # this field is not indexed and is not searchable

    class Index:
        name = FILE_INDEX

    def __str__(self):
        """Return a string description of the file object."""
        return "File {} {}".format(self.filename, self.type)


class Result(Document):
    """
    The definition of a result object. A `Result` is the result of a single instance run.

    Attributes:
        instance_name
        instance_type
        SoluFileStatus
        Status
        Datetime_Start
        Datetime_End
        ...

    Methods:
        raw
        json
        csv
        gzip
    """

    testset_id = Keyword(required=True)
    instance_name = Keyword(required=True)  # mcf128-4-1
    instance_id = Keyword(required=True)  # mcf128-4-1
    instance_type = Keyword()  # CIP
    SoluFileStatus = Keyword()
    Status = Keyword()
    Datetime_Start = Date()
    Datetime_End = Date()

    class Index:
        name = RESULT_INDEX

    def __str__(self):
        """Return a string description of the result object."""
        return "Result {}({})".format(self.instance_name, self.instance_id)

    def raw(self, ftype=".out"):
        """
        Return a log of Result object from logfile.

        Parameters
        ----------
        ftype : str
            extension of file to get data from (default ".out")
        """
        testset = TestSet.get(id=self.testset_id)
        whole_file = testset.raw(ftype=".out")
        # TODO: remove this once integer/ipet#20 is resolved
        # this is a hack for optimization/rubberband#41
        if hasattr(self, "LineNumbers_BeginLogFile") and hasattr(self, "LineNumbers_EndLogFile"):
            parts = whole_file.splitlines()[int(self.LineNumbers_BeginLogFile):
                                            int(self.LineNumbers_EndLogFile)]
            return "\n".join(parts)
        else:
            return "Unable to locate instance in out file :("

    def json(self, ftype=".out"):
        """
        Return a data of Result object from logfile in JSON format.

        Parameters
        ----------
        ftype : str
            extension of file to get data from (default ".out")
        """
        return json.dumps(self.to_dict(), default=date_handler)

    def csv(self, ftype=".out"):
        """
        Return a data of Result object from logfile in CSV format.

        Parameters
        ----------
        ftype : str
            extension of file to get data from (default ".out")
        """
        raise NotImplementedError()

    def gzip(self, ftype=".out"):
        """
        Return a gzipped log of Result object.

        Parameters
        ----------
        ftype : str
            extension of file to get data from (default ".out")
        """
        raise NotImplementedError()


class TestSet(Document):
    """Define TestSet object, derived from Document."""

    id = Keyword(required=True)
    filename = Keyword(required=True)
    solver = Keyword(required=True)  # scip
    run_initiator = Keyword(required=True)  # Gregor Hendel, last editor
    tags = Keyword(multi=True)  # user-provided tags
    test_set = Keyword()  # 'MMM', 'short', 'miplib2010', 'bugs', 'SAP-MMP'
    solver_version = Keyword()  # 3.0.1.1
    run_environment = Keyword()
    os = Keyword()
    architecture = Keyword()
    mode = Keyword()
    opt_flag = Keyword()  # spx1, spx2, cpx
    time_limit = Keyword()
    time_factor = Keyword()
    lp_solver = Keyword()  # SoPlex
    lp_solver_version = Keyword()  # 1.7.0.2
    lp_solver_githash = Keyword()
    git_hash = Keyword()  # af21b01
    git_hash_dirty = Boolean()
    git_commit_author = Keyword()  # Gregor Hendel
    settings_short_name = Keyword()  # default
    index_timestamp = Date(required=True)
    git_commit_timestamp = Date()  # required for plotting
    upload_timestamp = Date()
    uploader = Keyword()
    settings_id = Keyword()
    default_settings_id = Keyword()
    seed = Integer()
    permutation = Integer()
    metadata = Nested()
    expirationdate = Date()
    result_ids = Keyword()

    class Index:
        name = TESTSET_INDEX

    def __str__(self):
        """Return a string description of the testset object."""
        return "TestSet {}".format(self.filename)

    @property
    def get_uploader(self):
        """Return original uploader TestSet object."""
        if self.uploader is not None:
            return self.uploader
        else:
            return self.run_initiator

    def get_filename(self, ending=".out"):
        """
        Return filename of file associated to TestSet object.

        Parameters
        ----------
        ending : str
            extension of file to get data from (default ".out")
        """
        if not ending or ending == ".out":
            return self.filename
        else:
            return self.filename.rsplit(".", 1)[0] + ending

    def raw(self, ftype=".out"):
        """
        Return raw content of file assiociated to TestSet object.

        Parameters
        ----------
        ftype : str
            extension of file to get data from (default ".out")
        """
        s = File.search()
        s = s.filter("term", testset_id=self.meta.id)
        s = s.filter("term", type=ftype.lstrip("."))
        try:
            contents = s.execute()[0].text
        except IndexError:
            contents = None

        return contents

    def gzip(self, ftype=".out"):
        """
        Return the data contained in the TestSet object in Gzip format.

        Parameters
        ----------
        ftype : str
            extension of file to get data from (default ".out")
        """
        data = self.raw(ftype=ftype)
        return gzip.compress(data.encode("utf-8"))

    def get_data(self, key=None, add_data=None):
        """
        Get the data of the TestSet.

        Parameters
        ----------
        key : str
            the key of the requested data (default None)
        add_data : dict
            the key of the requested data (default None)
        """
        if key is None:
            all_instances = {}
            self.load_results()
            instances = self.results.to_dict().keys()
            count = 0
            for i in instances:
                all_instances[i] = self.results[i].to_dict()
                if "instance_id" not in all_instances[i].keys():
                    all_instances[i]["instance_id"] = count
                    count = count + 1
                if "ProblemName" not in all_instances[i].keys():
                    all_instances[i]["ProblemName"] = all_instances[i]["instance_name"]
                if "TimeLimit" not in all_instances[i].keys():
                    all_instances[i]["TimeLimit"] = self.get_data("TimeLimit")
                if "TimeFactor" not in all_instances[i].keys():
                    all_instances[i]["TimeFactor"] = self.get_data("TimeFactor")
                if self.lp_solver_githash:
                    all_instances[i]["SpxGitHash"] = self.lp_solver_githash

                further_keys = [Key.GitHash, "CommitTime", Key.LPSolver, Key.LogFileName,
                        Key.Settings, "RubberbandMetaId", "Seed", "Permutation"]
                for fk in further_keys:
                    all_instances[i][fk] = self.get_data(fk)

                if add_data is not None:
                    for k, v in add_data.items():
                        all_instances[i][k] = v
            return all_instances

        if key == Key.LPSolver:
            out = []
            if self.lp_solver is not None:
                out.append(self.lp_solver)
            if self.lp_solver_version is not None:
                out.append(self.lp_solver_version)
            return " ".join(out)
        if key == Key.Settings:
            if self.settings_short_name is not None:
                return self.settings_short_name
            else:
                return "none"
        if key == Key.LogFileName:
            return self.filename
        if key == "RubberbandMetaId":
            return self.meta.id
        if key == "Seed":
            return self.seed or str(0)
        if key == "Permutation":
            return self.permutation or str(0)
        if key == "TimeLimit":
            return self.time_limit or str(0)
        if key == "TimeFactor":
            return self.time_factor or str(1)
        if key == "CommitTime":
            return str(self.git_commit_timestamp)
        if key == "SpxGitHash":
            return self.lp_solver_githash or ""
        if key == Key.GitHash:
            return self.git_hash
        if key == "ReportVersion":
            if self.lp_solver is None:
                if self.solver_version is None:
                    return "\\{}".format(str.lower(self.solver))
                else:
                    return "\\{}~{}".format(str.lower(self.solver),
                            self.solver_version)
            else:
                return "\\{}~{}+\\{}~{}".format(str.lower(self.solver),
                        self.solver_version,
                        str.lower(self.lp_solver),
                        self.lp_solver_version)

    def json(self, ftype=".out"):
        """
        Return the data contained in the TestSet object as JSON.

        Parameters
        ----------
        ftype : str
            extension of file to get data from (default ".out")
        """
        if ftype == ".set":
            output = {}
            self.load_settings()
            for k in list(self.settings):
                setting = getattr(self.settings, k)
                default = getattr(self.settings_default, k)

                if k in INFINITY_KEYS:
                    if setting == INFINITY_MASK:
                        setting = INFINITY_FLOAT
                    if default == INFINITY_MASK:
                        default = INFINITY_FLOAT

                if k == "conflict/uselocalrows":
                    if setting == 0:
                        setting = True
                    else:
                        setting = False
                    if default == 0:
                        default = True
                    else:
                        default = False

                output[k] = {
                    "setting": setting,
                    "default": default,
                }

            return json.dumps(output)

        elif ftype == ".out":
            all_instances = {self.test_set: {}}
            all_instances[self.test_set] = self.get_data()
            return json.dumps(all_instances, default=date_handler)

        elif ftype == ".err":
            # TODO
            raise NotImplementedError()

    def csv(self, ftype=".out"):
        """
        Return the data contained in the TestSet object as CSV.

        Parameters
        ----------
        ftype : str
            extension of file to get data from (default ".out")
        """
        raise NotImplementedError()

    def delete_all_associations(self):
        """Delete all objects associated with a TestSet object, i.e. Result, Settings, and File."""
        self.delete_all_results()
        self.delete_all_files()
        self.delete_all_settings()

    def delete_all_results(self):
        """Delete all Result objects associated with a TestSet object."""
        self.load_results()
        for k, v in self.results.to_dict().items():
            v.delete()

    def delete_all_files(self):
        """Delete all File objects associated with a TestSet object."""
        self.load_files()
        for ft in self.files:
            f = self.files[ft]
            f.delete()

    def delete_all_settings(self):
        """Delete all File objects associated with a TestSet object."""
        self.load_settings()
        for ft in self.settings:
            f = self.settings[ft]
            f.delete()

    def load_results(self):
        """Load Results associated with a TestSet object."""
        try:
            if self.results is not None:
                return self.results
        except AttributeError:
            pass

        s = Result.search()
        # it's generally discouraged to return a large number of elements from a search query
        s = s.filter("term", testset_id=self.meta.id)
        self.results = {}

        results = {}
        results['ids'] = {}
        results['names'] = {}
        # this uses pagination/scroll
        for hit in s.scan():
            results['ids']["{} ({})".format(hit.instance_name, hit.instance_id)] = hit
            results['names']["{}".format(hit.instance_name)] = hit

        if len(results['ids'].keys()) == len(results['names'].keys()):
            self.results = results['names']
        else:
            self.results = results['ids']

    def load_files(self):
        """Load the files of a TestSet object."""
        try:
            if self.files is not None:
                return self.files
        except AttributeError:
            pass

        s = File.search()
        s = s.filter("term", testset_id=self.meta.id)

        self.files = {}
        # this uses pagination/scroll
        for hit in s.scan():
            self.files[hit.type] = hit

    def load_settings(self):
        """Load all settings associated with the TestSet."""
        self.settings = Settings.get(id=self.settings_id)
        self.settings_default = Settings.get(id=self.default_settings_id)


class Settings(Document):
    """Define Settings object, derived from Document."""

    testset_id = Keyword(required=True)

    class Index:
        name = SETTINGS_INDEX

    def update(self, **kwargs):
        """
        Extend update method, to deal with infinities before saving in elasticsearch.

        Parameters
        ----------
        kwargs
            keyword arguments
        """
        self.mask_settings(**kwargs)
        return super().update(**kwargs)

    def save(self, **kwargs):
        """
        Extend save method, to deal with infinities before saving in elasticsearch.

        Parameters
        ----------
        kwargs
            keyword arguments
        """
        self.mask_settings(**kwargs)
        return super().save(**kwargs)

    def mask_settings(self, **kwargs):
        """
        Substitute infinities in fields for elasticsearch to be able to deal with them.

        Cast infinity to INFINITY_MASK, since databases don't like infinity.
        This is likely ok, because fields that could contain infinity, are [0, inf)
        and mask is -1.

        Parameters
        ----------
        kwargs
            keyword arguments
        """
        for i in INFINITY_KEYS:
            if getattr(self, i, None) == INFINITY_FLOAT:
                setattr(self, i, INFINITY_MASK)
            if kwargs != {} and i in kwargs.keys():
                if kwargs[i] == INFINITY_FLOAT:
                    kwargs[i] = INFINITY_MASK

        key = "conflict/uselocalrows"
        if getattr(self, key, None) == True:
            setattr(self, key, 0)
        else:
            setattr(self, key, 1)

        if kwargs != {} and key in kwargs.keys():
            if kwargs[key] == True:
                kwargs[key] = 0
            else:
                kwargs[key] = 1


date_handler = lambda obj: (  # noqa
    obj.isoformat()
    if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date)
    else None
)
