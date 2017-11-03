from rubberband.models import TestSet


def search(query):
    s = TestSet.search()

    if "tags" in query:
        tags = query["tags"]
        tags = tags.split(",")
        tags = list(map(str.strip, tags))
        s = s.filter("terms", tags=tags)
        del(query["tags"])

    # return 100 items unless a limit is explicitly set
    limit = query.pop("limit", None) or 100
    limit = int(limit)

    for field, value in query.items():
        filter_dict = {field: value}
        s = s.filter("term", **filter_dict)

    return s.sort("-index_timestamp")[:limit].execute()
