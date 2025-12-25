"""Methods for importing a TestSet from logfiles."""

import os
import json
import logging
import traceback
import dateutil.parser
from elasticsearch import TransportError
from datetime import datetime

from ipet import Experiment, Key
from ipet.misc import loader
from tornado.options import options

# package imports
from rubberband.models import TestSet, Result, File, Settings
from rubberband.constants import ADD_READERS, FORMAT_DATETIME, SOLU_DIR
from rubberband.utils import gitlab as gl
from .stats import ImportStats
from .hasher import generate_sha256_hash

REQUIRED_FILES = set([".out"])
OPTIONAL_FILES = set([".solu", ".err", ".set", ".meta"])
ALL_SOLU = (
    SOLU_DIR + "instancedb.sqlite3"
    if os.path.isfile(SOLU_DIR + "instancedb.sqlite3")
    else SOLU_DIR + "allpublic.solu"
)


class Importer(object):
    """Organize and process retrieved files."""

    def __init__(self, user):
        """
        Create a Importer object for a user.

        Parameters
        ----------
        user : str
            current user
        """
        if not user:
            raise Exception("Missing user when initializing client.")

        self.current_user = user
        self.logger = logging.getLogger(__name__)
        self.logger.info(
            "{} opened a connection to Elasticsearch with the {}".format(
                self.current_user, type(self).__name__
            )
        )
        self.tags = []

    def reimport_files(self, paths, testset):
        """
        Reimport file bundle.

        Parameters
        ----------
        paths : dict str
            dictionary of filenames
        testset : TestSet
            already existing TestSet in Rubberband
        """
        self.importstats = ImportStats("results", "")
        self.remove_files = True
        try:
            self.parse_file_bundle(paths, initial=False, testset=testset)
        except Exception:
            self.importstats.status = "fail"
            traceback.print_exc()

        return self.importstats

    def process_files(self, paths, tags=[], remove=True, expirationdate=None):
        """
        Process filebundle and import to rubberband.

        Parameters
        ----------
        paths : list str
            list of filenames
        tags : list
            tags to add to TestSet (default [])
        remove : bool
            remove raw uploaded files from server (default True)
        expirationdate : str in date form
            Date after which data can be purged from elasticsearch (default: None)
        """
        # This gets called by both the apiupload and the webupload
        total_files = len(paths)
        basename = ""
        if total_files > 0:
            basename = os.path.basename(paths[0])
        self.importstats = ImportStats("results", basename=basename)
        self.tags = tags
        self.remove_files = remove
        self.logger.info("Found {} files. Beginning to parse.".format(total_files))
        try:
            # parsing all locally saved files
            self.parse_file_bundle(paths, expirationdate=expirationdate)
        except Exception:
            self.importstats.status = "fail"
            traceback.print_exc()

        return self.importstats

    def parse_file_bundle(
        self, bundle, expirationdate=None, initial=True, testset=None
    ):
        """
        Internal method that parses a single file bundle.

        The bundle is a tuple of strings (paths).
        A bundle should contain the following files: .out (.solu, .err, .set, .meta)

        Parameters
        ----------
        bundle : list str
            list of filenames
        expirationdate : str in date form
            Date after which data can be purged from elasticsearch (default: None)
        initial : bool
            indicate if the testset is parsed the first time or already exists (default: None)
        testset : TestSet
            TestSet if already existing (default: None)
        """
        # validate and organize files (make sure they exist and are readable)
        self.files = self.validate_and_organize_files(bundle)

        # generate file hash
        self.file_id = generate_sha256_hash(self.files[".out"])

        # initial is true on upload, on reimport it is false
        if initial:
            # check if already existing
            found = self.file_lookup()
            if found:
                self.importstats.status = "found"
                self.importstats.setUrl("/result/{}".format(found.meta.id))
                msg = (
                    "File was previously uploaded by {} on {}. Upload aborted.".format(
                        found.get_uploader, found.index_timestamp
                    )
                )
                self._log_info(msg)
                return

        # parse files with ipet
        ipettestrun = self.get_data_from_ipet()
        # data is the 'data' DataFrame from ipet.TestRun
        data = json.loads(ipettestrun.data.to_json())

        # get the scipparameters (from settings file) and their defaults from ipet
        settings = ipettestrun.getParameterData()

        # organize data into file_data and results
        # get data from getter of testrun.metadatadict
        md = ipettestrun.getMetaData()
        # only keep the metadata that is the same for all instances
        md = drop_different(dictionary=md, data=data)

        # collect data from testrun as a whole
        file_data = self.get_file_data(
            data, settings=settings, expirationdate=expirationdate, metadata=md
        )

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
        """
        Denormalize IPET data.

        Parameters
        ----------
        data : dict dict
            Data from IPET

        Returns
        -------
        dict dict
            modified data
        """
        results = {}
        instances = data["Solver"].keys()

        for i in instances:
            results[i] = {"instance_name": data[Key.ProblemName][i], "instance_id": i}

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
        """
        Keep track of import failures.

        Parameters
        ----------
        message : str
            Message to log.
        """
        self.logger.error(message)
        if not hasattr(self, "files"):
            self.importstats.logMessage("_", message)
        else:
            self.importstats.logMessage(self.files[".out"], message)
        self.importstats.fail += 1

    def _log_info(self, message):
        """
        Keep track of import events.

        Parameters
        ----------
        message : str
            Message to log.
        """
        self.logger.info(message)
        self.importstats.logMessage(self.files[".out"], message)

    def get_file_data(self, data, settings=None, expirationdate=None, metadata={}):
        """
        Get data about file.

        Parameters
        ----------
        data : dict
            Data in json format from ipet
        settings
            Settings parameterdata dictionary from ipet (default: None)
        expirationdate : str in date form
            Date after which data can be purged from elasticsearch (default: None)
        metadata
            Metadata dictionary from IPET (default: {})
        """
        # settings is a tuple
        file_data = {
            "id": self.file_id,
            "filename": os.path.basename(self.files[".out"]),
            "metadata": metadata,
            "tags": self.tags,
            "index_timestamp": datetime.now(),
        }

        if expirationdate is not None:
            file_data["expirationdate"] = expirationdate

        ipetkeymapping = {
            "solver": Key.Solver,
            "solver_version": Key.Version,
            "time_limit": Key.TimeLimit,
            "lp_solver": "LPSolver",
            "lp_solver_version": "LPSolverVersion",
            "lp_solver_githash": "SpxGitHash",
            "mode": "mode",
            "git_hash": "GitHash",
        }
        for key, ipetkey in ipetkeymapping.items():
            file_data[key] = self.most_frequent_value(data, ipetkey)

        # get some info via ipet metadata...
        metamapping = {
            "test_set": "TstName",
            "settings_short_name": "Settings",
            "seed": "Seed",
            "permutation": "Permutation",
            "run_environment": "Queue",
            "opt_flag": "OptFlag",
            "os": "OperatingSystem",
            "time_factor": "TimeFactor",
        }
        # by this time we dropped all metadata that is not equal or empty for all data rows
        for key, tag in metamapping.items():
            if tag in metadata.keys():
                file_data[key] = metadata[tag]
        # it can be an old file if there is no meta file. then try to read info from filename
        if self.files[".meta"] is None:
            # this might be empty, also this is very bad practice. we keep it for historical data.
            file_data.update(self.parse_info_from_filename(self.files))

        if options.gitlab_url:
            file_data["run_initiator"] = gl.get_username(self.current_user)
        else:
            file_data["run_initiator"] = self.current_user

        if settings:
            file_data["settings"] = settings[0]
            file_data["settings_default"] = settings[1]

        # get git data if it is available
        if "GitHash" in data and data["GitHash"]:
            git_hash = file_data["git_hash"]
            file_data["git_hash_dirty"] = git_hash.endswith("-dirty")
            if file_data["git_hash_dirty"]:
                git_hash = git_hash.rstrip("-dirty")

            project_id_key = options.gitlab_project_ids.get(file_data["solver"].lower())
            if not project_id_key:
                msg = "No project id specified for {}. Skipping commit lookup.".format(
                    file_data["solver"].lower()
                )
                self._log_info(msg)
            elif options.gitlab_url:
                try:
                    commit = gl.get_commit_data(project_id_key, git_hash)

                    file_data["git_hash"] = commit.id
                    # user the author timestamp
                    file_data["git_commit_timestamp"] = dateutil.parser.parse(
                        commit.authored_date
                    )
                    file_data["git_commit_author"] = gl.get_username(
                        commit.author_email
                    )
                except Exception:
                    msg = "Couldn't find commit {} in Gitlab. Aborting...".format(
                        git_hash
                    )
                    self._log_failure(msg)

        return file_data

    def parse_info_from_filename(self, files):
        """
        Parse information from filename.

        Parameters
        ----------
        files : dict
            Files to parse from. Should contain ".out".

        Returns
        -------
            dict of information about build options.
        """
        filename = os.path.basename(self.files[".out"])
        rogue_string = ".zib.de"
        file_path_clean = filename.replace(rogue_string, "")
        fnparts = file_path_clean.split(".")
        if len(fnparts) != 8:
            return {}

        info = {
            "test_set": fnparts[1],  # short, bug, etc,
            "settings_short_name": fnparts[-2],
            "run_environment": fnparts[-3],
            "opt_flag": fnparts[-5],
            "architecture": fnparts[-7],
            "os": fnparts[-8],
        }
        return info

    def validate_and_organize_files(self, list_of_files):
        """
        Ensure files are of the correct type and readable.

        Parameters
        ----------
        list_of_files : list
            List of filenames.

        Returns
        -------
            dict str of filenames that are correct and readable.
        """
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
                msg = "File type {} is unsupported. Ignoring this file ({}). Supported files: {}".format(
                    file_extension, filename, ", ".join(all_file_ext)
                )
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

    def save_structured_data(self, file_level_data, results, testset=None):
        """
        Save TestSet and Result model instances in Elasticsearch.

        Parameters
        ----------
        file_level_data : dict
            Data about TestSet (the whole TestRun)
        results : list
            Data of individual instances
        testset : TestSet
            (default: None)
        """
        try:
            settings = file_level_data.pop("settings")
            settings_default = file_level_data.pop("settings_default")
            if testset is None:
                file_level_data["upload_timestamp"] = file_level_data["index_timestamp"]
                file_level_data["uploader"] = file_level_data["run_initiator"]
                f = TestSet(**file_level_data)
                f.save()

                settings = Settings(**settings, testset_id=f.meta.id)
                settings.save()

                default_settings = Settings(**settings_default, testset_id=f.meta.id)
                default_settings.save()

                f.update(
                    settings_id=settings.meta.id,
                    default_settings_id=default_settings.meta.id,
                )

            else:
                f = testset
                if f.upload_timestamp is None:
                    file_level_data["upload_timestamp"] = f.index_timestamp
                if f.uploader is None:
                    file_level_data["uploader"] = f.run_initiator
                f.update(**file_level_data)

                settings = Settings(**settings, testset_id=f.meta.id)
                settings.save()

                default_settings = Settings(**settings_default, testset_id=f.meta.id)
                default_settings.save()

                f.update(
                    settings_id=settings.meta.id,
                    default_settings_id=default_settings.meta.id,
                )

            self.testset_meta_id = f.meta.id  # save this for backup step
            result_ids = []
            for r in results:
                r["testset_id"] = f.meta.id
                # TODO move this to constructor of Result model?
                for key in ["Datetime_Start", "Datetime_End"]:
                    try:
                        timestamp = int(r[key])
                        timestr = datetime.fromtimestamp(timestamp).strftime(
                            FORMAT_DATETIME
                        )
                        r[key] = timestr
                    except (KeyError, TypeError):
                        pass
                res = Result(**r)
                res.save()
                result_ids.append(res.meta.id)

            f.update(result_ids=result_ids)
        except Exception as e:
            # database error
            msg = "Some kind of database error."
            self._log_failure(msg)
            self._log_failure(e)
            raise

        msg = "Data for file {} was successfully imported and archived".format(
            self.files[".out"]
        )
        self.logger.info(msg)
        self.importstats.status = "success"
        self.importstats.setUrl("/result/{}".format(self.testset_meta_id))

    def backup_files(self):
        """Save all file contents in Elasticsearch."""
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
                except TransportError as e:
                    msg = (
                        "Couldn't create file in Elasticsearch. Check the logs for more info."
                        " Aborting..."
                    )
                    self._log_failure(msg)
                    self._log_failure(e.args)
                    raise

        self._log_info(
            "{} file bundle backed up in Elasticsearch.".format(self.files[".out"])
        )

    def get_data_from_ipet(self):
        """
        Import data from IPET.

        Create ipet.experiment, add files and execute ipet.collectData.

        Returns
        -------
        ipet.testrun object
        """
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

            path = ADD_READERS
            if os.path.isfile(path):
                for r in loader.loadAdditionalReaders([path]):
                    c.readermanager.registerReader(r)
                    self.logger.info("Added additional reader: " + r.getName())

            for solver in loader.loadAdditionalSolvers():
                c.readermanager.addSolver(solver)
                self.logger.info("Added additional solver: " + solver.getName())

            c.collectData()

        except Exception:
            traceback.print_exc()
            msg = "Some kind of ipet error. Aborting..."
            self._log_failure(msg)
            raise

        testruns = c.getTestRuns()
        if len(testruns) != 1:
            msg = "Unexpected number of testruns. Expected 1, got: {}".format(
                len(testruns)
            )
            self._log_failure(msg)
            raise Exception(msg)

        return testruns[0]

    def file_lookup(self):
        """
        Use the file_id (sha256 hash) to determine if a file is already existing in elasticsearch.

        Return None if not found.
        """
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
            raise Exception("file_id not yet set. Lookup failed.")

    def most_frequent_value(self, data, key, throwex=False):
        """
        Find most frequent value in data[key].

        Parameters
        ----------
        data : dict
            dictionary containing lists of values.
        key : key
            key to search for

        Returns
        -------
        value
        """
        if key not in data.keys():
            if throwex:
                msg = "Missing key {} in data.".format("key")
                self._log_failure(msg)
                raise Exception(msg)
            else:
                return None

        d = data[key]
        count = {}
        for v in d.values():
            count[v] = count.get(v, 0) + 1
        try:
            count.pop(None)
        except KeyError:
            pass
        try:
            count.pop("nan")
        except KeyError:
            pass
        return max(count, key=count.get)


def _determine_type(inst):
    """
    Determine the problem type of a given Result.

    This code was adapted from check/check.awk
    Possible return values: MIQCP, MINLP, QCP, NLP, CIP, LP, BP, IP MBP, MIP

    Parameters
    ----------
    inst : Result
        Result instance to determine type for.

    Returns
    -------
    str
    """
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
    linear_constraints += inst.get("Constraints_Number_logicor") or 0
    linear_constraints += inst.get("Constraints_Number_knapsack") or 0
    linear_constraints += inst.get("Constraints_Number_setppc") or 0
    linear_constraints += inst.get("Constraints_Number_varbound") or 0
    quadratic_constraints = inst.get("Constraints_Number_quadratic") or 0
    quadratic_constraints += inst.get("Constraints_Number_soc") or 0
    nonlinear_constraints = inst.get("Constraints_Number_nonlinear") or 0
    nonlinear_constraints += inst.get("Constraints_Number_abspower") or 0
    nonlinear_constraints += inst.get("Constraints_Number_bivariate") or 0

    if linear_constraints < constraints:
        linear_and_quadratic_constraints = linear_constraints + quadratic_constraints

        if linear_and_quadratic_constraints == constraints:
            if binary_variables == 0 and integer_variables == 0:
                return "QCP"
            else:
                return "MIQCP"

        elif linear_and_quadratic_constraints + nonlinear_constraints == constraints:
            if binary_variables == 0 and integer_variables == 0:
                return "NLP"
            else:
                return "MINLP"

        else:
            return "CIP"

    elif binary_variables == 0 and integer_variables == 0:
        return "LP"

    elif continuous_variables == 0:
        if integer_variables == 0 and implicit_variables == 0:
            return "BP"
        else:
            return "IP"

    elif integer_variables == 0:
        return "MBP"

    else:
        return "MIP"


def drop_different(dictionary, data):
    """Drop from dictionary the fields that are not constant in the data.

    Parameters
    ----------
    dictionary : dict
    data : pandas.DataFrame

    Returns
    -------
    dict
    """
    keep = {}
    for k, v in dictionary.items():
        val = None
        different = False
        for el in set(data[k].values()):
            if el not in [val, None, ""]:
                if val is None:
                    val = el
                else:
                    different = True
                    break
        if not different:
            keep[k] = v
    return keep


def bundle_files(paths):
    """Take a bundle of files and split them by basename."""
    bundles = []
    for basename in [
        os.path.splitext(path)[0]
        for path in paths
        if os.path.splitext(path)[1] == ".out"
    ]:
        bundles.append(
            tuple([path for path in paths if os.path.splitext(path)[0] == basename])
        )
    for f in paths:
        if os.path.splitext(f)[1] == ".solu":
            for bundle in bundles:
                if f not in bundle:
                    bundle.append(f)
    if bundles != []:
        return bundles
    else:
        return [[]]
