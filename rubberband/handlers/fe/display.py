from .base import BaseHandler
from rubberband.constants import IPET_EVALUATIONS


class DisplayView(BaseHandler):

    # displays a file, api backend
    def get(self, mode, id):
        # display evalfile
        if mode == "eval":
            ipeteval = IPET_EVALUATIONS[int(id)]
            ipeteval_file = ipeteval["path"]
            out = ""

            # get file contents
            with open(ipeteval_file, "r") as f:
                for nr, line in enumerate(f):
                    out = out + line

            # replace < > & "
            out = out.replace("&", "&amp;").replace("<", "&lt;")
            out = out.replace(">", "&gt;").replace('"', "&quot;")

            # send answer
            self.write(out)

        else:
            self.write_error(400, msg="Error, file doesn't exist.")
