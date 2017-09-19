INFINITY_KEYS = ("separating/flowcover/maxslackroot", "separating/flowcover/maxslack",
                 "heuristics/undercover/maxcoversizeconss")
INFINITY_MASK = -1
ZIPPED_SUFFIX = ".gz"
FILES_DIR = "files/"
STATIC_FILES_DIR = FILES_DIR + "static/"
ALL_SOLU = STATIC_FILES_DIR + "all.solu"
IPET_EVALUATIONS = [STATIC_FILES_DIR + i for i in ["eval.xml"]]
NONE_DISPLAY = "--"
EXPORT_DATA_FORMATS = ("gzip", "json", "csv", "raw")
EXPORT_FILE_TYPES = (".out", ".set", ".err", ".meta")
ELASTICSEARCH_INDEX = "solver-results"
