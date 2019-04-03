"""Define constants used by rubberband."""

INFINITY_KEYS = ("separating/flowcover/maxslackroot", "separating/flowcover/maxslack",
                 "heuristics/undercover/maxcoversizeconss")
INFINITY_MASK = -1
INFINITY = 1e+20
INFINITY_FLOAT = float('inf')
INFINITY_DISPLAY = 1e+20
ZIPPED_SUFFIX = ".gz"
FILES_DIR = "files/"
STATIC_FILES_DIR = FILES_DIR + "static/"
# ALL_SOLU = "instancedata/database/instancedb.sqlite3"
ALL_SOLU = STATIC_FILES_DIR + "all.solu"
ADD_READERS = STATIC_FILES_DIR + "additional_readers.xml"
IPET_EVALUATIONS = {
        0: {"path": STATIC_FILES_DIR + "eval_1.xml",
            "name": "evaluation 1"},
        1: {"path": STATIC_FILES_DIR + "eval_2.xml",
            "name": "evaluation 2"},
        }
NONE_DISPLAY = ""
EXPORT_DATA_FORMATS = ("gzip", "json", "csv", "raw")
EXPORT_FILE_TYPES = (".out", ".set", ".err", ".meta")
ELASTICSEARCH_INDEX = "rubberband-results"

FORMAT_DATE = "%Y-%m-%d"
FORMAT_DATETIME_LONG = "%d. %b %Y, %H:%M"
FORMAT_DATETIME_SHORT = "%d. %b %y"
FORMAT_DATETIME = "%Y-%m-%d %H:%M:%S"

DT_STYLE = "std"  # datatables style 'bs4' or 'std'
