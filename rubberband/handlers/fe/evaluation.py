from .base import BaseHandler
import pandas as pd


class EvaluationView(BaseHandler):

    def get(self, eval_id):
        # dummydata
        dataframe = pd.DataFrame(
                columns=['a', 'b', 'c'],
                index=[1, 2, 3],
                data=[[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        print(eval_id)
        print(self.get_argument("testruns"))

        htmlframe = dataframe.to_html(classes="stats-table table table-bordered")
        self.write(htmlframe)
