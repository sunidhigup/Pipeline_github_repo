from data_processor.sql.join.join_mapper import JoinMapper


class JoinTable:

    def execute(self, params):
        """

        :param params:
        """
        #CDEP- Inside join_table execute step - JoinTable"
        JoinMapper.join(self, params)
