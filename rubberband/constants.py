INFINITY_KEYS = ("separating/flowcover/maxslackroot", "separating/flowcover/maxslack",
                 "heuristics/undercover/maxcoversizeconss")
INFINITY_MASK = -1
ZIPPED_SUFFIX = ".gz"
FILES_DIR = "files/"
STATIC_FILES_DIR = FILES_DIR + "static/"
ALL_SOLU = STATIC_FILES_DIR + "all.solu"
IPET_EVALUATIONS = {
        0: {"path": STATIC_FILES_DIR + "eval1.xml", "name": "evaluation1"},
        1: {"path": STATIC_FILES_DIR + "eval2.xml", "name": "evaluation2"},
        2: {"path": STATIC_FILES_DIR + "eval3.xml", "name": "evaluation3"},
        3: {"path": STATIC_FILES_DIR + "eval4.xml", "name": "evaluation4"},
        4: {"path": STATIC_FILES_DIR + "eval5.xml", "name": "evaluation5"},
        5: {"path": STATIC_FILES_DIR + "eval6.xml", "name": "evaluation6"},
        6: {"path": STATIC_FILES_DIR + "eval1.xml", "name": "evaluation7"},
        7: {"path": STATIC_FILES_DIR + "eval2.xml", "name": "evaluation8"},
        8: {"path": STATIC_FILES_DIR + "eval3.xml", "name": "evaluation9"},
        9: {"path": STATIC_FILES_DIR + "eval4.xml", "name": "evaluation10"}
        }
NONE_DISPLAY = "--"
EXPORT_DATA_FORMATS = ("gzip", "json", "csv", "raw")
EXPORT_FILE_TYPES = (".out", ".set", ".err", ".meta")
ELASTICSEARCH_INDEX = "solver-results"

FORMAT_DATE = "%Y-%m-%d"
FORMAT_DATETIME_LONG = "%B %d, %Y %H:%M"
FORMAT_DATETIME_SHORT = FORMAT_DATE + " %H:%M"
FORMAT_DATETIME = "%Y-%m-%d %H:%M:%S"
