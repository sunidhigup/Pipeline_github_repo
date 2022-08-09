from data_processor.sql.join.multi_table_join_mapper import MultiTableJoinMapper


class JoinMultiTable:

    def execute(self, params):
        """

        :param params:
        """
        ##CDEP- Inside join_table execute step - MultiTableJoinMapper
        MultiTableJoinMapper.join(self, params)
