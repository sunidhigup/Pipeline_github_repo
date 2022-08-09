from Rule_Engine.rule_engine_jobs.rule_engine_processor import RuleEngineProcessor
from data_processor.steps.constant.constants import rule_engine_constants

class RuleEngine:

    def execute(self, params):

        parameters = params.step_config.get(rule_engine_constants.PARAMS)
        spark_session = params.spark
        isRuleEngine = params.step_config.get(rule_engine_constants.METHOD_NAME)
        if isRuleEngine == rule_engine_constants.RULE_ENGINE:
            parameters[rule_engine_constants.PARAMETER_ISRULENGINE] = True
            parameters[rule_engine_constants.SPARK_SESSION] = spark_session

        db_name = parameters.get(rule_engine_constants.DB_NAME)
        df_name = parameters.get(rule_engine_constants.DF)

        if db_name != "":
            spark_session.sql(f"use `{db_name}`")

        # df1 = spark_session.read.csv("s3://dep-develop/Pepsi/DEP_Finance/disp/Rule_engine/Input/disp.csv",header = True)
        # df1.createOrReplaceTempView("temp")

        statement = "select * from {}".format(df_name)

        # statement = step_param.spark.sql("select * from {}".format(df_name))
        # statement = f"SELECT * FROM {df_name}}"

        df = spark_session.sql(statement)

        RuleEngineProcessor.process(parameters, df)
