"""Define constants used by rubberband."""

INFINITY_KEYS = ("separating/flowcover/maxslackroot", "separating/flowcover/maxslack",
                 "heuristics/undercover/maxcoversizeconss", "solvingphases/optimalvalue",
                 "misc/referencevalue")
INFINITY_MASK = -1
INFINITY_FLOAT = float('inf')
INFINITY_DISPLAY = 1e+20
FILE_INDEX = 'file'
RESULT_INDEX = 'result'
TESTSET_INDEX = 'testset'
SETTINGS_INDEX = 'settings'
ZIPPED_SUFFIX = ".gz"
FILES_DIR = "files/"
ALL_SOLU = FILES_DIR + "instancedata/database/instancedb.sqlite3"
STATIC_FILES_DIR = FILES_DIR + "static/"
ADD_READERS = STATIC_FILES_DIR + "additional_readers.xml"
IPET_EVALUATIONS = {
        0: {"path": STATIC_FILES_DIR + "eval_singleruns_exclude.xml",
            "name": "single runs - exclude fails & aborts (standard)"},
        1: {"path": STATIC_FILES_DIR + "eval_singleruns_include.xml",
            "name": "single runs - include fails & aborts (standard)"},
        2: {"path": STATIC_FILES_DIR + "eval_singleruns_punish.xml",
            "name": "single runs - punish fails & aborts (standard)"},
        3: {"path": STATIC_FILES_DIR + "eval_groupgithash_exclude.xml",
            "name": "group by githash - exclude fails & aborts"},
        4: {"path": STATIC_FILES_DIR + "eval_groupsettings_exclude.xml",
            "name": "group by settings - exclude fails & aborts"},
        5: {"path": STATIC_FILES_DIR + "eval_grouplpsolver_exclude.xml",
            "name": "group by LP solver - exclude fails & aborts"},
        6: {"path": STATIC_FILES_DIR + "eval_groupsettings_exclude_detailed.xml",
            "name": "detailed view - group settings, exclude"},
        7: {"path": STATIC_FILES_DIR + "eval_groupsettings_include_detailed.xml",
            "name": "detailed view - group settings, include"},
        8: {"path": STATIC_FILES_DIR + "eval_groupgithash_exclude_detailed.xml",
            "name": "detailed view - group githash, exclude"},
        9: {"path": STATIC_FILES_DIR + "evaluation-pure.xml",
            "name": "pure evaluation for sap"},
        10: {"path": STATIC_FILES_DIR + "evaluation-deco.xml",
            "name": "deco evaluation for sap"},
        11: {"path": STATIC_FILES_DIR + "evalclusterbench_queue.xml",
            "name": "clusterbenchmark queues"},
        12: {"path": STATIC_FILES_DIR + "evalclusterbench_queuenode.xml",
            "name": "clusterbenchmark queuenodes"},
        13: {"path": STATIC_FILES_DIR + "papilo_evaluation.xml",
            "name": "evaluation papilo"},
        14: {"path": STATIC_FILES_DIR + "papilo_evaluation_solver_specific.xml",
            "name": "evaluation papilo solver specific"},
        15: {"path": STATIC_FILES_DIR + "papilo_evaluation_groupsettings.xml",
            "name": "evaluation papilo group settings"},
        }
# date sorting works only with the empty NONE_DISPLAY at the moment
NONE_DISPLAY = ""
EXPORT_DATA_FORMATS = ("gzip", "json", "csv", "raw")
EXPORT_FILE_TYPES = (".out", ".set", ".err", ".meta")

FORMAT_DATE = "%Y-%m-%d"
FORMAT_DATETIME_LONG = "%d. %b %Y, %H:%M"
FORMAT_DATETIME_SHORT = "%d. %b %y"
FORMAT_DATETIME = "%Y-%m-%d %H:%M:%S"
