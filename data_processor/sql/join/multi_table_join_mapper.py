import datetime

from data_processor.constants import Constants
from data_processor.logging.cloudwatch.log_utils import write_logs
from data_processor.utils.actions import Actions
from data_processor.utils.storage_level import StorageLevel
from data_processor.sql.constant.constants import mapper_constants


class MultiTableJoinMapper:
    """

    """
    def __init__(self):
        pass

    def join(self, params):
        """

        :param params:
        :return:
        """
        write_logs(mapper_constants.INFO, mapper_constants.INFO_STATEMENT, params)
        spark_session = params.spark

        params.job_dict[mapper_constants.BATCH_ID] = "{}{}{}".format(params.batch_id, params.step_number, params.step_name)
        params.job_dict[mapper_constants.STEP_NUMBER] = params.step_number
        params.job_dict[mapper_constants.STEP_NAME] = params.step_name
        params.job_dict[mapper_constants.START_TIME] = str(datetime.datetime.now())
        params.job_dict[mapper_constants.STATUS] = mapper_constants.STATUS_RUNNING
        
        job_status_table = Constants.job_step_status_table
        params.dynamoDb.Table(job_status_table).put_item(Item=params.job_dict)


        join_dict = {Constants.JOIN_CONDITION: params.step_config[Constants.JOIN_PARAMS][Constants.JOIN_CONDITION],
                     Constants.JOIN_TEMP_VIEW: params.step_config[Constants.JOIN_PARAMS][Constants.JOIN_TEMP_VIEW],
                     Constants.JOIN_SELECT_COLS: params.step_config[Constants.JOIN_PARAMS][Constants.JOIN_SELECT_COLS],
                     Constants.JOIN_FILTER: params.step_config[Constants.JOIN_PARAMS][Constants.JOIN_FILTER],
                     Constants.MULTI_JOIN_TABLES:
                         params.step_config[Constants.JOIN_PARAMS][Constants.MULTI_JOIN_TABLES],
                     Constants.MULTI_JOIN_TYPES: params.step_config[Constants.JOIN_PARAMS][Constants.MULTI_JOIN_TYPES],
                     Constants.JOIN_ACTION: params.step_config[Constants.JOIN_PARAMS][
                         Constants.JOIN_ACTION],
                     Constants.JOIN_PERSIST: params.step_config[Constants.JOIN_PARAMS][Constants.JOIN_PERSIST],
                     Constants.JOIN_PERSIST_TYPE: params.step_config[Constants.JOIN_PARAMS][
                         Constants.JOIN_PERSIST_TYPE]}

        join_condition = ''

        write_logs(mapper_constants.INFO, "Type of join_dict.get(Constants.MULTI_JOIN_TABLES).values()) - {}".format(
            type(join_dict.get(Constants.MULTI_JOIN_TABLES).values())), params)

        tables = list(join_dict.get(Constants.MULTI_JOIN_TABLES).values())[:-1]
        last_table = list(join_dict.get(Constants.MULTI_JOIN_TABLES).values())[-1:][0]

        joins = list(join_dict.get(Constants.MULTI_JOIN_TYPES).values())

        for table, join in zip(tables, joins):
            join_condition += " {} {} JOIN".format(table, join)

        join_condition += " {}".format(last_table)

        write_logs(mapper_constants.INFO, "Join Condition - {}".format(join_condition), params)

        if join_dict.get(Constants.MULTI_JOIN_FILTER, '').strip() != '':
            query = "SELECT {} FROM {} ON {} WHERE {}" \
                .format(join_dict.get(Constants.MULTI_JOIN_SELECT_COLS), join_condition,
                        join_dict.get(Constants.MULTI_JOIN_CONDITION), join_dict.get(Constants.MULTI_JOIN_FILTER))
        else:
            query = "SELECT {} FROM {} ON {} " \
                .format(join_dict.get(Constants.MULTI_JOIN_SELECT_COLS), join_condition,
                        join_dict.get(Constants.MULTI_JOIN_CONDITION))

        write_logs(mapper_constants.INFO, "Query - {}".format(query), params)

        write_logs(mapper_constants.INFO, "CDEP- Executing query in multi table join mapper....", params)
        df = spark_session.sql(query)
        df.createOrReplaceTempView(join_dict.get(Constants.JOIN_TEMP_VIEW, ''))

        if join_dict.get(Constants.JOIN_PERSIST, '') == "True":
            write_logs(mapper_constants.INFO,
                       "Persisting DF with persist type {}".format(join_dict.get(Constants.JOIN_PERSIST_TYPE, '')), params)
            level = StorageLevel.getStorageLevel(self, join_dict.get(Constants.JOIN_PERSIST_TYPE, ''))
            df.persist(level)

        if join_dict.get(Constants.JOIN_ACTION, '').strip() != "":
            write_logs(mapper_constants.INFO, "Executing Action : {}".format(join_dict.get(Constants.JOIN_ACTION, '')), params)
            Actions.getAction(self, join_dict.get(Constants.JOIN_ACTION, ''), df)

        params.job_dict[mapper_constants.END_TIME] = str(datetime.datetime.now())
        params.job_dict[mapper_constants.STATUS] = mapper_constants.STATUS_COMPLETED
        params.dynamoDb.Table(job_status_table).put_item(Item=params.job_dict)

        return df
