import os
import json
import logging
import dateutil.parser
from datetime import datetime
import traceback
from gitlab.exceptions import GitlabGetError

from ipet import Experiment, Key
from ipet.misc import loader
from tornado.options import options

# package imports
from rubberband.models import TestSet, Result, File
from rubberband.constants import ALL_SOLU, ADD_READERS, FORMAT_DATETIME
from rubberband.utils import gitlab as gl
from .stats import ImportStats
from .hasher import generate_sha256_hash

REQUIRED_FILES = set([".out"])
OPTIONAL_FILES = set([".solu", ".err", ".set", ".meta"])


class ResultClient(object):
    '''
    Upload and retrieve result files.
    '''

    def __init__(self, user):
        if not user:
            raise Exception("Missing user when initiliazing client.")

        self.current_user = user
        # here, usually __name__ is "ResultClient" opposed to "__main__"
        self.logger = logging.getLogger(__name__)
        self.logger.info("{} opened a connection to elasticsearch with the {}"
                         .format(self.current_user, type(self).__name__))
        self.tags = []

    def reimport_files(self, paths, testset):
        '''
        Reimport file bundle
        '''
        self.metadata = ImportStats("results")
        self.remove_files = True
        try:
            self.parse_file_bundle(paths, initial=False, testset=testset)
        except:
            self.metadata.status = "fail"
            traceback.print_exc()

        return self.metadata

    def process_files(self, paths, tags=[], remove=True, expirationdate=None):
        '''
        Process files, one at a time. Accepts a list.
        '''
        # TODO: maybe check for reasonable expdate?
        # This gets called by both the apiupload and the webupload
        self.metadata = ImportStats("results")
        total_files = len(paths)
        self.tags = tags
        self.remove_files = remove
        self.logger.info("Found {} files. Beginning to parse.".format(total_files))
        try:
            # parsing all locally saved files
            self.parse_file_bundle(paths, expirationdate=expirationdate)
        except:
            self.metadata.status = "fail"
            traceback.print_exc()

        return self.metadata

    def parse_file_bundle(self, bundle, expirationdate=None, initial=True, testset=None):
        '''
        Internal method that parses a single file bundle. The bundle is a tuple of strings (paths).

        A bundle should contain the following files:
            *.out

        Optionally, the bundle could also contain a .set, .meta, .err and .solu file.
        '''
        # validate and organize files
        self.files = self.validate_and_organize_files(bundle)

        # generate file hash
        self.file_id = generate_sha256_hash(self.files[".out"])

        if initial:
            # check if already existing
            found = self.file_lookup()
            if found:
                self.metadata.status = "found"
                self.metadata.setUrl("/result/{}".format(found.meta.id))
                msg = "File was previously uploaded by {} on {}. Upload aborted."\
                      .format(found.uploader, found.index_timestamp)
                self._log_info(msg)
                return

        # parse files with ipet
        # manageable is the ipet.TestRun
        manageable = self.get_data_from_ipet()
        # data is the 'data' DataFrame from ipet.TestRun
        data = json.loads(manageable.data.to_json())
        # get the scipparameters and the defaultparameters from ipet
        settings = manageable.getParameterData()

        # organize data into file_data and results
        # get data from testrun.metadatadict
        md = manageable.getMetaData()
        # collect data from testrun as a whole
        file_data = self.get_file_data(data, settings=settings, expirationdate=expirationdate,
                metadata=md)

        results = self.get_results_data(data)

        # save the structured data in elasticsearch
        self.save_structured_data(file_data, results, testset=testset)
        if initial:
            self.backup_files()

        # clean up filesystem if remove flag set
        if self.remove_files:
            for t, f in self.files.items():
                if f and not f == ALL_SOLU:
                    os.remove(f)

        self._log_info("Finished!")

    def get_results_data(self, data):
        '''
        Denormalize ipet data
        '''

        results = {}
        instances = data["SolvingTime"].keys()

        for i in instances:
            results[i] = {
                    "instance_name": data[Key.ProblemName][i],
                    "instance_id": i
                    }

        for k, v in data.items():
            for instance, metric in v.items():
                k = k.replace(".", "_")
                results[instance][k] = metric

        # extra: determine type of instance and number of iterations
        for k, v in results.items():
            results[k]["instance_type"] = _determine_type(v)
            iteration_values = [
                results[k].get("LP_Iterations_barrierLP"),
                results[k].get("LP_Iterations_dualLP"),
                results[k].get("LP_Iterations_primalLP"),
            ]

            if None in set(iteration_values):
                results[k]["Iterations"] = None
            else:
                results[k]["Iterations"] = sum(iteration_values)

        return results.values()

    def _log_failure(self, message):
        '''
        Keep track of import failures
        '''
        self.logger.error(message)
        if not hasattr(self, "files"):
            self.metadata.logMessage("_", message)
        else:
            self.metadata.logMessage(self.files[".out"], message)
        self.metadata.fail += 1

    def _log_info(self, message):
        '''
        Keep track of import failures
        '''
        self.logger.info(message)
        self.metadata.logMessage(self.files[".out"], message)

    def get_file_data(self, data, settings=None, expirationdate=None, metadata={}):
        # settings is a tuple
        # data is 'data' DataFrame from ipet.TestRun
        # for scip these data is available
        file_keys = set([Key.TimeLimit, Key.Version, "LPSolver", "GitHash", Key.Solver, "mode"])
        # TODO once the ipet is up to date, use this and update the rest
        # file_keys = set([Key.TimeLimit, Key.Version, Key.LPSolver, Key.GitHash,
        if "LPSolver" in data:
            # assume that a testrun is all run with the same lpsolver
            for v in list(data["LPSolver"].values()):
                if v != "nan":
                    break
            lp_solver_name, lp_solver_version = v.split(" ")
        else:
            lp_solver_name = None
            lp_solver_version = None

        vs = {}
        for i in ["mode", Key.TimeLimit]:
            if i in data:
                vs[i] = list(data[i].values())[0]

        filename = os.path.basename(self.files[".out"])

        file_data = {
            "filename": filename,
            "solver": list(data[Key.Solver].values())[0],
            "solver_version": list(data[Key.Version].values())[0],
            "mode": vs.get("mode"),
            "time_limit": vs.get(Key.TimeLimit),
            "lp_solver": lp_solver_name,
            "lp_solver_version": lp_solver_version,
            "tags": self.tags,
            "index_timestamp": datetime.now(),
            "metadata": metadata
        }
        if expirationdate is not None:
            file_data["expirationdate"] = expirationdate

        # read the following from metadata, which is added to each problem after parsing
        # assume that a testrun is run on all instances with the same test_set, environment,
        # settings, opt_flag, architecture, os (etc.)

        # get these via ipet metadata...
        # TODO are these correct?
        if self.files[".meta"] is not None:
            mapping = {
                    "test_set": "TstName",
                    "settings_short_name": "Settings",
                    "seed": "Seed",
                    "permutation": "Permutation",
                    "run_environment": "Queue",
                    "opt_flag": "OptFlag",
                    "os": "OperatingSystem"
                    }

            for key, tag in mapping.items():
                try:
                    file_data[key] = metadata[tag]
                except:
                    pass
        else:
            file_data.update(self.parse_info_from_filename(self.files))

        if options.gitlab_url:
            file_data["run_initiator"] = gl.get_username(self.current_user)
        else:
            file_data["run_initiator"] = self.current_user

        if settings:
            file_data["settings"] = settings[0]
            file_data["settings_default"] = settings[1]

        # get data from git if it's available
        if "GitHash" in data and data["GitHash"]:
            git_hash = list(data["GitHash"].values())[0]

            if git_hash.endswith("-dirty"):
                file_data["git_hash_dirty"] = True
                git_hash = git_hash.rstrip("-dirty")
            else:
                file_data["git_hash_dirty"] = False

            project_id_key = options.gitlab_project_ids.get(file_data["solver"].lower())
            if not project_id_key:
                file_data["git_hash"] = git_hash
                msg = "No project id specified for {}. Skipping commit lookup."\
                    .format(file_data["solver"].lower())
                self._log_info(msg)
            else:
                try:
                    commit = gl.get_commit_data(project_id_key, git_hash)
                    file_data["git_hash"] = commit.id
                    # user the author timestamp
                    file_data["git_commit_timestamp"] = dateutil.parser.parse(commit.authored_date)
                    file_data["git_commit_author"] = gl.get_username(commit.author_name)
                except GitlabGetError:
                    msg = "Couldn't find commit {} in Gitlab. Aborting...".format(git_hash)
                    self._log_failure(msg)
                    raise

        for k in file_keys:
            data.pop(k, None)

        file_data["id"] = self.file_id

        return file_data

    def parse_info_from_filename(self, files):
        filename = os.path.basename(self.files[".out"])
        rogue_string = ".zib.de"
        file_path_clean = filename.replace(rogue_string, "")
        fnparts = file_path_clean.split(".")
        info = {
                "test_set": fnparts[1],  # short, bug, etc,
                "settings_short_name": fnparts[-2],
                "run_environment": fnparts[-3],
                "opt_flag": fnparts[-5],
                "architecture": fnparts[-7],
                "os": fnparts[-8]}
        return info

    def validate_and_organize_files(self, list_of_files):
        '''
        Ensure files are of the correct type and readable.
        '''
        required_files = {key: None for key in REQUIRED_FILES}
        optional_files = {key: None for key in OPTIONAL_FILES}

        all_file_ext = REQUIRED_FILES.union(OPTIONAL_FILES)

        for f in list_of_files:
            if os.path.islink(f):
                msg = "Cannot parse results from a symlink. Please input an absolute path."
                self._log_failure(msg)
                raise Exception(msg)

            if os.path.isdir(f):
                msg = "Cannot parse results from a directory. Please input a file path."
                self._log_failure(msg)
                raise Exception(msg)

            filename, file_extension = os.path.splitext(f)
            if file_extension not in all_file_ext:
                msg = "File type {} is unsupported. Ignoring this file. Supported files: {}"\
                        .format(file_extension, ", ".join(all_file_ext))
                self._log_failure(msg)

            for r in required_files:
                if f.endswith(r):
                    if not os.path.exists(f):
                        msg = "Cannot parse results from a file that doesn't exist."
                        self._log_failure(msg)
                        raise Exception(msg)
                    required_files[r] = f
                    break

            for o in optional_files:
                if f.endswith(o) and os.path.exists(f):
                    optional_files[o] = f
                    break

        missing = [k for k, v in required_files.items() if v is None]

        if missing:
            msg = "Missing required files: {}".format(", ".join(missing))
            self._log_failure(msg)
            raise Exception(msg)

        self.logger.info("Parsing {}.".format(required_files[".out"]))
        required_files.update(optional_files)

        return required_files

    def save_structured_data(self, file_level_data, instance_level_data, testset=None):
        '''
        Save TestSet and Result model instances in Elasticsearch.
        '''
        try:
            # save parent
            if testset is None:
                file_level_data["upload_timestamp"] = file_level_data["index_timestamp"]
                file_level_data["uploader"] = file_level_data["run_initiator"]
                f = TestSet(**file_level_data)
                f.save()
            else:
                f = testset
                if f.upload_timestamp is None:
                    file_level_data["upload_timestamp"] = f.index_timestamp
                    file_level_data["uploader"] = f.run_initiator
                f.update(**file_level_data)
            self.testset_meta_id = f.meta.id  # save this for backup step
            # save children
            for r in instance_level_data:
                r["_parent"] = f.meta.id
                # TODO move this to constructor of Result model?
                for key in ["Datetime_Start", "Datetime_End"]:
                    try:
                        timestamp = int(r[key])
                        timestr = datetime.fromtimestamp(timestamp).strftime(FORMAT_DATETIME)
                        r[key] = timestr
                    except:
                        pass
                res = Result(**r)
                res.save()
        except:
            # database error
            msg = "Some kind of database error."
            self._log_failure(msg)
            raise

        msg = "Data for file {} was successfully imported and archived".format(self.files[".out"])
        self.logger.info(msg)
        self.metadata.status = "success"
        self.metadata.setUrl("/result/{}".format(self.testset_meta_id))

    def backup_files(self):
        '''
        Save all of the file contents in Elasticsearch.
        '''
        # remove solu file from checkin
        self.files.pop(".solu")
        for ftype, f in self.files.items():
            if not f:  # no file specified
                continue

            basename = os.path.basename(f)
            data = {
                "type": ftype.lstrip("."),
                "filename": basename,
                "hash": generate_sha256_hash(f),
                "testset_id": self.testset_meta_id,
            }
            with open(f) as f_in:
                self._log_info("Backing up {} in Elasticsearch".format(f))

                data["text"] = f_in.read()
                try:
                    fobj = File(**data)
                    fobj.save()
                except:
                    msg = "Couldn't create file in Elasticsearch. Check the logs for more info."\
                          " Aborting..."
                    self._log_failure(msg)
                    raise

        self._log_info("{} file bundle backed up in Elasticsearch.".format(self.files[".out"]))

    def get_data_from_ipet(self):
        try:
            c = Experiment()

            # Metafiles will be loaded automatically if they are placed next to outfiles
            c.addOutputFile(self.files[".out"])

            if self.files[".err"] is not None:
                c.addOutputFile(self.files[".err"])

            if self.files[".set"] is not None:
                c.addOutputFile(self.files[".set"])

            if self.files[".solu"] is None:
                msg = "No solu file found."
                path = ALL_SOLU
                if os.path.isfile(path):
                    msg = "Adding SoluFile."
                    self.files[".solu"] = path
            else:
                msg = "Adding SoluFile."

            self.logger.info(msg)
            if self.files[".solu"] is not None:
                c.addSoluFile(self.files[".solu"])

            msg = "No reader file found."
            path = ADD_READERS
            if os.path.isfile(path):
                msg = "Adding additional readers."
                for r in loader.loadAdditionalReaders([path]):
                    c.readermanager.registerReader(r)

            self.logger.info(msg)

            c.collectData()

        except:
            msg = "Some kind of ipet error. Aborting..."
            self._log_failure(msg)
            raise

        testruns = c.getTestRuns()
        if len(testruns) != 1:
            msg = "Unexpected number of testruns. Expected 1, got: {}".format(len(testruns))
            self._log_failure(msg)
            raise Exception(msg)

        return testruns[0]

    def file_lookup(self):
        '''
        Uses the file_id (sha256 hash) to determine if a file is already existing in elasticsearch.

        Return None if not found.
        '''
        # this should not happen
        if hasattr(self, "testset_meta_id"):
            f = TestSet.get(id=self.testset_meta_id)
            return f

        elif self.file_id:
            s = TestSet.search()
            s = s.filter("term", id=self.file_id)
            found = list(s.execute())
            if len(found) >= 1:
                return found[0]
            return None

        # this should not happen
        else:
            raise Exception('file_id not yet set. Lookup failed.')


def _determine_type(inst):
    '''
    Determine the problem type. This code was adapted from check/check.awk
    Possible return values: MIQCP, MINLP, QCP, NLP, CIP, LP, BP, IP MBP, MIP
    '''
    initvariables = inst.get("OriginalProblem_Vars") or 0

    # the original problem had no variables, so parsing probably went wrong
    if initvariables == 0:
        return None

    binary_variables = inst.get("PresolvedProblem_BinVars") or 0
    integer_variables = inst.get("PresolvedProblem_IntVars") or 0
    continuous_variables = inst.get("PresolvedProblem_ContVars") or 0
    implicit_variables = inst.get("PresolvedProblem_ImplVars") or 0
    constraints = inst.get("PresolvedProblem_InitialNCons") or 0
    linear_constraints = inst.get("Constraints_Number_linear") or 0
    linear_constraints += (inst.get("Constraints_Number_logicor") or 0)
    linear_constraints += (inst.get("Constraints_Number_knapsack") or 0)
    linear_constraints += (inst.get("Constraints_Number_setppc") or 0)
    linear_constraints += (inst.get("Constraints_Number_varbound") or 0)
    quadratic_constraints = inst.get("Constraints_Number_quadratic") or 0
    quadratic_constraints += (inst.get("Constraints_Number_soc") or 0)
    nonlinear_constraints = inst.get("Constraints_Number_nonlinear") or 0
    nonlinear_constraints += (inst.get("Constraints_Number_abspower") or 0)
    nonlinear_constraints += (inst.get("Constraints_Number_bivariate") or 0)

    if (linear_constraints < constraints):

        linear_and_quadratic_constraints = linear_constraints + quadratic_constraints

        if (linear_and_quadratic_constraints == constraints):
            if (binary_variables == 0 and integer_variables == 0): return "QCP"
            else: return "MIQCP"

        elif (linear_and_quadratic_constraints + nonlinear_constraints == constraints):
            if (binary_variables == 0 and integer_variables == 0): return "NLP"
            else: return "MINLP"

        else: return "CIP"

    elif (binary_variables == 0 and integer_variables == 0): return "LP"

    elif (continuous_variables == 0):
        if (integer_variables == 0 and implicit_variables == 0): return "BP"
        else: return "IP"

    elif (integer_variables == 0): return "MBP"

    else: return "MIP"
