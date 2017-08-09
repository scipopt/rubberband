from .base import BaseHandler
from rubberband.models import TestSet


class CompareView(BaseHandler):
    def get(self):
        base_id = self.get_argument("base", None)

        base = TestSet.get(id=base_id)
        if base.git_commit_timestamp:
            date_limit = base.git_commit_timestamp.isoformat()
        else:
            date_limit = base.index_timestamp.isoformat()

        older_choices = TestSet.search()\
            .filter("term", test_set=base.test_set)\
            .filter("term", mode=base.mode)\
            .filter("range", git_commit_timestamp={'lt': date_limit})\
            .sort({"git_commit_timestamp": {"order": "desc"}})[:10]

        newer_choices = TestSet.search()\
            .filter("term", test_set=base.test_set)\
            .filter("term", mode=base.mode)\
            .filter("range", git_commit_timestamp={'gt': date_limit})\
            .sort({"git_commit_timestamp": {"order": "asc"}})[:10]

        same_commit = TestSet.search()\
            .filter("term", test_set=base.test_set)\
            .filter("term", mode=base.mode)\
            .filter("term", git_hash=base.git_hash)

        choices = {}
        choices["older"] = older_choices.execute()
        choices["newer"] = newer_choices.execute()
        choices["same"] = same_commit.execute()

        self.render("compare.html", page_title="Compare", base=base,
                    choices=choices)

    def post(self):
        # compares contains the meta ids (the hashes?) of all but one comparison TestSet
        compares = list(self.request.arguments.keys())
        # base identifies via meta id (via hash?) one of the comparison TestSet
        base = self.get_argument("base", None)
        if base:
            compares.remove("base")
            if base in compares:
                compares.remove(base)
        else:
            base = compares.pop(0)

        cmp_string = ",".join(compares)
        next_url = "{}/result/{}?compare={}".format(self.application.base_url, base, cmp_string)
        self.redirect(next_url)
