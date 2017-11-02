INFINITY_KEYS = ("separating/flowcover/maxslackroot", "separating/flowcover/maxslack",
                 "heuristics/undercover/maxcoversizeconss")
INFINITY_MASK = -1
INFINITY = 1e+20
ZIPPED_SUFFIX = ".gz"
FILES_DIR = "files/"
STATIC_FILES_DIR = FILES_DIR + "static/"
ALL_SOLU = STATIC_FILES_DIR + "all.solu"
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
        }
NONE_DISPLAY = "--"
EXPORT_DATA_FORMATS = ("gzip", "json", "csv", "raw")
EXPORT_FILE_TYPES = (".out", ".set", ".err", ".meta")
ELASTICSEARCH_INDEX = "solver-results"

FORMAT_DATE = "%Y-%m-%d"
FORMAT_DATETIME_LONG = "%B %d, %Y %H:%M"
FORMAT_DATETIME_SHORT = "%d. %b %Y, %H:%M"
FORMAT_DATETIME = "%Y-%m-%d %H:%M:%S"
