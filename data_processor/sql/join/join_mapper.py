import datetime

from data_processor.constants import Constants
from data_processor.logging.cloudwatch.log_utils import write_logs
from data_processor.utils.actions import Actions
from data_processor.utils.storage_level import StorageLevel

from data_processor.sql.constant.constants import mapper_constants
class JoinMapper:
    """

    """
    def __init__(self):
        pass

    def join(self, params):
        """

        :param params:
        :return:
        """
        write_logs("Info", "CDEP- Inside join_mapper.join()", params)
        spark_session = params.spark

        params.job_dict[mapper_constants.BATCH_ID] = params.batch_id + params.step_number + params.step_name + str(
            datetime.datetime.now())
        params.job_dict[mapper_constants.STEP_NUMBER] = params.step_number
        params.job_dict[mapper_constants.STEP_NAME] = params.step_name
        params.job_dict[mapper_constants.START_TIME] = str(datetime.datetime.now())
        params.job_dict[mapper_constants.STATUS] = mapper_constants.STATUS_RUNNING

        job_status_table = Constants.job_step_status_table
        params.dynamoDb.Table(job_status_table).put_item(Item=params.job_dict)

        # Design a loop approach -- Use a dict or struct
        join_dict = {Constants.JOIN_TYPE: params.step_config[Constants.JOIN_PARAMS][Constants.JOIN_TYPE],
                     Constants.JOIN_CONDITION: params.step_config[Constants.JOIN_PARAMS][Constants.JOIN_CONDITION],
                     Constants.JOIN_TEMP_VIEW: params.step_config[Constants.JOIN_PARAMS][Constants.JOIN_TEMP_VIEW],
                     Constants.JOIN_SELECT_COLS: params.step_config[Constants.JOIN_PARAMS][Constants.JOIN_SELECT_COLS],
                     Constants.JOIN_FILTER: params.step_config[Constants.JOIN_PARAMS][Constants.JOIN_FILTER],
                     Constants.JOIN_TABLE_1_TEMP_VIEW:
                         params.step_config[Constants.JOIN_PARAMS][Constants.JOIN_TABLE_1][
                             Constants.JOIN_TABLE_1_TEMP_VIEW],
                     Constants.JOIN_TABLE_1_COLS: params.step_config[Constants.JOIN_PARAMS][Constants.JOIN_TABLE_1][
                         Constants.JOIN_TABLE_1_COLS],
                     Constants.JOIN_TABLE_1_FILTER: params.step_config[Constants.JOIN_PARAMS][Constants.JOIN_TABLE_1][
                         Constants.JOIN_TABLE_1_FILTER], Constants.JOIN_TABLE_2_TEMP_VIEW:
                         params.step_config[Constants.JOIN_PARAMS][Constants.JOIN_TABLE_2][
                             Constants.JOIN_TABLE_2_TEMP_VIEW],
                     Constants.JOIN_TABLE_2_COLS: params.step_config[Constants.JOIN_PARAMS][Constants.JOIN_TABLE_2][
                         Constants.JOIN_TABLE_2_COLS],
                     Constants.JOIN_TABLE_2_FILTER: params.step_config[Constants.JOIN_PARAMS][Constants.JOIN_TABLE_2][
                         Constants.JOIN_TABLE_2_FILTER],
                     Constants.JOIN_ACTION: params.step_config[Constants.JOIN_PARAMS][
                         Constants.JOIN_ACTION],
                     Constants.JOIN_PERSIST: params.step_config[Constants.JOIN_PARAMS][Constants.JOIN_PERSIST],
                     Constants.JOIN_PERSIST_TYPE: params.step_config[Constants.JOIN_PARAMS][
                         Constants.JOIN_PERSIST_TYPE]}
        write_logs(mapper_constants.INFO, "CDEP- Join Type : " + join_dict.get(Constants.JOIN_TYPE, ''), params)
        write_logs(mapper_constants.INFO, "CDEP- Join Condition : " + join_dict.get(Constants.JOIN_TEMP_VIEW, ''), params)
        write_logs(mapper_constants.INFO, "CDEP- df : " + join_dict.get(Constants.JOIN_TEMP_VIEW, ''), params)
        write_logs(mapper_constants.INFO, "CDEP- Join cols : " + join_dict.get(Constants.JOIN_SELECT_COLS, ''), params)
        write_logs(mapper_constants.INFO, "CDEP- Join filter : " + join_dict.get(Constants.JOIN_FILTER, ''))
        write_logs(mapper_constants.INFO, "CDEP- Table 1 : " + join_dict.get(Constants.JOIN_TABLE_1_TEMP_VIEW, ''), params)
        write_logs(mapper_constants.INFO, "CDEP- Table 1 filter : " + join_dict.get(Constants.JOIN_TABLE_1_COLS, ''), params)
        write_logs(mapper_constants.INFO, "CDEP- Table 1 cols : " + join_dict.get(Constants.JOIN_TABLE_1_FILTER, ''), params)
        write_logs(mapper_constants.INFO, "CDEP- Table 2 : " + join_dict.get(Constants.JOIN_TABLE_2_TEMP_VIEW, ''), params)
        write_logs(mapper_constants.INFO, "CDEP- Table 2 cols : " + join_dict.get(Constants.JOIN_TABLE_2_COLS, ''), params)
        write_logs(mapper_constants.INFO, "CDEP- Table 2 filter : " + join_dict.get(Constants.JOIN_TABLE_2_FILTER, ''), params)

        if join_dict.get(Constants.JOIN_TABLE_1_FILTER, '').strip() != '':
            write_logs(mapper_constants.INFO, "Table 1 Filter present...", params)
            tble1 = "SELECT {} FROM {} WHERE {}".format(join_dict.get(Constants.JOIN_TABLE_1_COLS, ''),
                                                        join_dict.get(Constants.JOIN_TABLE_1_TEMP_VIEW, ''),
                                                        join_dict.get(Constants.JOIN_TABLE_1_FILTER, ''))
        else:
            tble1 = "SELECT {} FROM {}".format(join_dict.get(Constants.JOIN_TABLE_1_COLS, ''),
                                               join_dict.get(Constants.JOIN_TABLE_1_TEMP_VIEW, ''))

        if join_dict.get(Constants.JOIN_TABLE_2_FILTER, '').strip() != '':
            write_logs(mapper_constants.INFO, "Table 2 Filter present...", params)
            tble2 = "SELECT {} FROM {} WHERE {}".format(join_dict.get(Constants.JOIN_TABLE_2_COLS, ''),
                                                        join_dict.get(Constants.JOIN_TABLE_2_TEMP_VIEW, '')
                                                        , join_dict.get(Constants.JOIN_TABLE_2_FILTER, ''))
        else:
            tble2 = "SELECT {} FROM {}".format(join_dict.get(Constants.JOIN_TABLE_2_COLS, '')
                                               , join_dict.get(Constants.JOIN_TABLE_2_TEMP_VIEW, ''))

        if join_dict.get(Constants.JOIN_FILTER, '').strip() != '':
            write_logs(mapper_constants.INFO, "Join Filter present...", params)
            query = "SELECT {} FROM ( {} ) {} {} JOIN ( {} ) {} ON {} WHERE {}" \
                .format(join_dict.get(Constants.JOIN_SELECT_COLS, ''),
                        tble1, join_dict.get(Constants.JOIN_TABLE_1_TEMP_VIEW, ''),
                        join_dict.get(Constants.JOIN_TYPE, ''),
                        tble2, join_dict.get(Constants.JOIN_TABLE_2_TEMP_VIEW, ''),
                        join_dict.get(Constants.JOIN_CONDITION, ''),
                        join_dict.get(Constants.JOIN_FILTER, ''))
        else:
            query = "SELECT {} FROM ( {} ) {} {} JOIN ( {} ) {} ON {}" \
                .format(join_dict.get(Constants.JOIN_SELECT_COLS, ''),
                        tble1, join_dict.get(Constants.JOIN_TABLE_1_TEMP_VIEW, ''),
                        join_dict.get(Constants.JOIN_TYPE, ''),
                        tble2, join_dict.get(Constants.JOIN_TABLE_2_TEMP_VIEW, ''),
                        join_dict.get(Constants.JOIN_CONDITION, ''))

        write_logs(mapper_constants.INFO, "CDEP- tbl1 query : ".format(tble1), params)
        write_logs(mapper_constants.INFO, "CDEP- tbl2 query : ".format(tble2), params)
        write_logs(mapper_constants.INFO, "CDEP- join query : ".format(query), params)

        write_logs(mapper_constants.INFO, "CDEP- List of Tables....", params)
        spark_session.sql("show tables").where("isTemporary = true").show()
        write_logs(mapper_constants.INFO, "CDEP- Executing query....", params)
        df = spark_session.sql(query)
        df.createOrReplaceTempView(join_dict.get(Constants.JOIN_TEMP_VIEW, ''))

        if join_dict.get(Constants.JOIN_PERSIST, '') == "True":
            write_logs(mapper_constants.INFO,
                       "Persisting DF with persist type {}".format(join_dict.get(Constants.JOIN_PERSIST_TYPE, '')),
                       params)
            level = StorageLevel.getStorageLevel(self, join_dict.get(Constants.JOIN_PERSIST_TYPE, ''))
            df.persist(level)

        if join_dict.get(Constants.JOIN_ACTION, '').strip() != "":
            write_logs(mapper_constants.INFO, "Executing Action : {}".format(join_dict.get(Constants.JOIN_ACTION, '')), params)
            Actions.getAction(self, join_dict.get(Constants.JOIN_ACTION, ''), df)

        params.job_dict[mapper_constants.END_TIME] = str(datetime.datetime.now())
        params.job_dict[mapper_constants.STATUS] = mapper_constants.STATUS_COMPLETED

        params.dynamoDb.Table(job_status_table).put_item(Item=params.job_dict)

        return df
