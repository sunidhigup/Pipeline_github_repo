import pyspark


class Actions:

    def getAction(self, action_type, df):
        """

        :param action_type:
        :param df:
        """
        action = {
            "show": df.show(truncate=False),
            "count": df.count,
        }
