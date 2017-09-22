import gzip
import json
import datetime
from elasticsearch_dsl import DocType, MetaField, String, Date, Float, Nested

from rubberband.constants import INFINITY_KEYS, INFINITY_MASK, ELASTICSEARCH_INDEX
from .model_helpers import compute_stat

from ipet import Key


class File(DocType):
    '''
    The definition of a File object. A `File` contains the raw contents of a log file.
    '''
    type = String(index="not_analyzed", required=True)  # out, set, err, solu
    filename = String(index="not_analyzed", required=True)  # check.MMM.scip-021ace1...out
    hash = String(index="not_analyzed", required=True)  # computed hash
    testset_id = String(index="not_analyzed", required=True)  # for application-side joins
    text = String(index="no", required=True)

    class Meta:
        index = ELASTICSEARCH_INDEX
        # doc_type = "file"

    def __str__(self):
        return "File {} {}".format(self.filename, self.type)


class Result(DocType):
    '''
    The definition of a result object. A `Result` is the result of a single instance run.

    Attributes:
        instance_name
        instance_type
        SoluFileStatus
        Status
        Datetime_Start
        Datetime_End
        dualboundhistory
        PrimalBoundHistory
        ...

    Methods:
        raw
        json
        csv
        gzip
    '''

    instance_name = String(index="not_analyzed", required=True)  # mcf128-4-1
    instance_id = String(index="not_analyzed", required=True)  # mcf128-4-1
    instance_type = String(index="not_analyzed")  # CIP
    SoluFileStatus = String(index="not_analyzed")
    Status = String(index="not_analyzed")
    Datetime_Start = Date()
    Datetime_End = Date()
    dualboundhistory = Float(multi=True)
    PrimalBoundHistory = Float(multi=True)

    class Meta:
        index = ELASTICSEARCH_INDEX
        parent = MetaField(type="testset")
        # doc_type = "result"

    def __str__(self):
        return "Result {}".format(self.instance_name)

    def raw(self, ftype=".out"):
        parent = TestSet.get(id=self.meta.parent)
        whole_file = parent.raw(ftype=".out")
        # TODO: remove this once integer/ipet#20 is resolved
        # this is a hack for optimization/rubberband#41
        if hasattr(self, "LineNumbers_BeginLogFile") and hasattr(self, "LineNumbers_EndLogFile"):
            parts = whole_file.splitlines()[int(self.LineNumbers_BeginLogFile):
                                            int(self.LineNumbers_EndLogFile)]
            return "\n".join(parts)
        else:
            return "Unable to locate instance in out file :("

    def json(self, ftype=".out"):
        return json.dumps(self.to_dict(), default=date_handler)

    def csv(self, ftype=".out"):
        raise NotImplemented()

    def gzip(self, ftype=".out"):
        '''
        Return a gzipped segment of the raw log file.
        '''
        raise NotImplemented()


class TestSet(DocType):
    '''
    The file definition.
    '''
    id = String(index="not_analyzed", required=True)
    filename = String(index="not_analyzed", required=True)
    solver = String(index="not_analyzed", required=True)  # scip
    run_initiator = String(index="not_analyzed", required=True)  # Gregor Hendel
    tags = String(index="not_analyzed", multi=True)  # user-provided tags
    test_set = String(index="not_analyzed")  # 'MMM', 'short', 'miplib2010', 'bugs', 'SAP-MMP'
    solver_version = String(index="not_analyzed")  # 3.0.1.1
    run_environment = String(index="not_analyzed")
    os = String(index="not_analyzed")
    architecture = String(index="not_analyzed")
    mode = String(index="not_analyzed")
    opt_flag = String(index="not_analyzed")  # opt, dbg
    time_limit = String(index="not_analyzed")
    lp_solver = String(index="not_analyzed")  # SoPlex
    lp_solver_version = String(index="not_analyzed")  # 1.7.0.2
    git_hash = String(index="not_analyzed")  # af21b01
    git_commit_author = String(index="not_analyzed")  # Gregor Hendel
    settings_short_name = String(index="not_analyzed")  # default
    index_timestamp = Date(required=True)
    git_commit_timestamp = Date()  # required for plotting
    file_modified_timestamp = Date()
    settings = Nested()
    settings_default = Nested()
    seed = String(index="not_analyzed")
    metadata = Nested()
    expirationdate = Date()

    class Meta:
        index = ELASTICSEARCH_INDEX
        doc_type = "testset"

    def update(self, **kwargs):
        '''
        Cast infinity to INFINITY_MASK, since databases don't like infinity.
        This is likely ok, because fields that could contain infinity, are [0, inf)
        and mask is -1.
        '''
        for i in INFINITY_KEYS:
            if i not in kwargs["settings"].keys():
                continue
            if kwargs["settings"][i] == float("inf"):
                kwargs["settings"][i] = INFINITY_MASK
            if kwargs["settings_default"][i] == float("inf"):
                kwargs["settings_default"][i] = INFINITY_MASK
        return super(TestSet, self).update(**kwargs)

    def save(self, **kwargs):
        '''
        Cast infinity to INFINITY_MASK, since databases don't like infinity.
        This is likely ok, because fields that could contain infinity, are [0, inf)
        and mask is -1.
        '''
        for i in INFINITY_KEYS:
            if getattr(self.settings, i, None) == float("inf"):
                setattr(self.settings, i, INFINITY_MASK)
            if getattr(self.settings_default, i, None) == float("inf"):
                setattr(self.settings_default, i, INFINITY_MASK)
        return super(TestSet, self).save(**kwargs)

    def __str__(self):
        return "TestSet {}".format(self.filename)

    @property
    def uploader(self):
        return self.run_initiator

    def get_filename(self, ending=".out"):
        if not ending or ending == ".out":
            return self.filename
        else:
            return self.filename.rsplit(".", 1)[0] + ending

    def raw(self, ftype=".out"):
        '''
        Get the raw data file.
        '''
        s = File.search()
        s = s.filter("term", testset_id=self.meta.id)
        s = s.filter("term", type=ftype.lstrip("."))
        try:
            contents = s.execute()[0].text
        except:
            contents = None

        return contents

    def gzip(self, ftype=".out"):
        data = self.raw(ftype=ftype)
        return gzip.compress(data.encode("utf-8"))

    def get_data(self):
        '''
        Get the data of the testrun
        '''
        all_instances = {}
        self.load_children()
        instances = self.children.to_dict().keys()
        for i in instances:
            all_instances[i] = self.children[i].to_dict()
            # seed instances with githash of parent testrun,
            # because in most cases compared files have the same filename
            all_instances[i][Key.GitHash] = self.git_hash
        return all_instances

    def json(self, ftype=".out"):
        '''
        Return the data contained in the TestSet object as JSON.
        '''
        if ftype == ".set":
            output = {}
            for k in list(self.settings):
                setting = getattr(self.settings, k)
                default = getattr(self.settings_default, k)

                if k in INFINITY_KEYS:
                    if setting == INFINITY_MASK:
                        setting = float("inf")
                    if default == INFINITY_MASK:
                        default = float("inf")

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
            raise NotImplemented()

    def csv(self, ftype=".out"):
        '''
        Return the data contained in the TestSet object as CSV.
        '''
        # TODO
        raise NotImplemented()

    def delete_all_associations(self):
        '''
        Delete all children(Result) and associated files(File)
        '''
        self.delete_all_children()
        self.delete_all_files()

    def delete_all_children(self):
        self.load_children()
        for c_name in self.children:
            c = self.children[c_name]
            c.delete()

    def delete_all_files(self):
        self.load_files()
        for ft in self.files:
            f = self.files[ft]
            f.delete()

    def load_children(self):
        '''
        Get all of the instance results associated with a TestSet.
        '''
        s = Result.search()
        # it's generally discouraged to return a large number of elements from a search query
        s = s.filter("term", _parent=self.meta.id)
        self.children = {}

        # this uses pagination/scroll
        for hit in s.scan():
            self.children[hit.instance_name] = hit

    def load_files(self):
        s = File.search()
        s = s.filter("term", testset_id=self.meta.id)

        self.files = {}
        # this uses pagination/scroll
        for hit in s.scan():
            self.files[hit.type] = hit

    def load_stats(self, subset=[]):
        '''
        Loads the statistics for a particular file. Accept a subset of instance names to
        compute statistics for.
        '''
        self.stats = {}
        if not hasattr(self, "children"):
            self.load_children()

        if subset:
            all_instances = [self.children[instance_name] for instance_name in subset]
        else:
            all_instances = self.children.to_dict().values()

        self.stats = compute_stat(all_instances)


date_handler = lambda obj: (  # noqa
    obj.isoformat()
    if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date)
    else None
)
