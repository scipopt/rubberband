INFINITY_KEYS = ("separating/flowcover/maxslackroot", "separating/flowcover/maxslack",
                 "heuristics/undercover/maxcoversizeconss")
INFINITY_MASK = -1
ZIPPED_SUFFIX = ".gz"
FILES_DIR = "files/"
STATIC_FILES_DIR = FILES_DIR + "static/"
ALL_SOLU = STATIC_FILES_DIR + "all.solu"
IPET_EVALUATIONS = {
        0: {"path": STATIC_FILES_DIR + "eval.xml", "name": "standard evaluation"},
        1: {"path": STATIC_FILES_DIR + "eval_seeds.xml", "name": "seeds evaluation"}
        }
NONE_DISPLAY = "--"
EXPORT_DATA_FORMATS = ("gzip", "json", "csv", "raw")
EXPORT_FILE_TYPES = (".out", ".set", ".err", ".meta")
ELASTICSEARCH_INDEX = "solver-results"
