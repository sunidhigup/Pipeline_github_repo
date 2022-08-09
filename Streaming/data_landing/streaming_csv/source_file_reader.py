import csv


class SourceData:
    """

    """
    def __init__(self, source_path):
        self.source_path = source_path

    def read_data(self):
        """

        :return:
        """
        #opening file
        file = open(self.source_path, 'r', encoding="utf8")
        self.reader=csv.DictReader(file)
        return self.reader

    @classmethod
    def chunkit(cls, l, n):
        """

        :param l:
        :param n:
        """
        for i in range(0, len(l), n):
            yield l[i:i + n]