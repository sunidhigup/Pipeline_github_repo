"""
Date Validation
---------------

Python script   :   date_validation.py
Version			:	1.0
Description     :   Module to validate different string date format values to standard date pattern
"""
from pyspark.sql.functions import expr
from pyspark.sql import functions as f
from Rule_Engine.rule_engine_jobs.constants.rule_engine_constants import JsonParamKeys, DateValidationParams
from collections import ChainMap


class DateValidation:
    """
        DataValidation class will be use to validate different string date format values
        to standard date pattern.
    """

    def __init__(self):
        self.default_date_value = DateValidationParams.DATE_DEFAULT_VALUE
        self.default_time_value = DateValidationParams.TIME_DEFAULT_VALUE
        self.date_default_format = DateValidationParams.DATE_DEFAULT_FORMAT
        self.time_default_format = DateValidationParams.TIME_DEFAULT_FORMAT
        self.date_output_format = DateValidationParams.DATE_OUTPUT_FORMAT

    def date_validation(self, col_name, field_values):
        """
        This method is use to generate sql expression & extract different rules from json
        which will be used in data validation.

        :param col_name: Name of the column which needs to be processed
        :param field_values: Dictionary containing json rules
        :return select expression
        """

        rule_list =""
        arg_list=""

        # Extracting field rules from field value dictionary
        if JsonParamKeys.FIELD_RULES in field_values:
            field_rules = field_values[JsonParamKeys.FIELD_RULES]
        else:
            field_rules = {}

        input_format = None

        for field in field_rules:
            if  JsonParamKeys.RULE_NAME in field:  
                rule_list=rule_list+field[JsonParamKeys.RULE_NAME]+JsonParamKeys.RULE_LIST_SEPERATOR_DATE 
            
            if JsonParamKeys.ARGS in field:
                data = dict(ChainMap(*field[JsonParamKeys.ARGS]))
                for keys in data:
                    arg_list=arg_list+str(data[keys])+JsonParamKeys.RULE_LIST_SEPERATOR_DATE    
                arg_list=arg_list[:-1]+JsonParamKeys.ARG_LIST_SEPERATOR 

        rule_list=rule_list[:-1]
        arg_list=arg_list[:-3]


        rule_name = ""

        if JsonParamKeys.RULE_NAME in field_rules:
            rule_name = field_rules[JsonParamKeys.RULE_NAME]

        # Extracting rules values from dataset rules
        if JsonParamKeys.ARGS in field_rules:
            if len(field_rules[JsonParamKeys.ARGS]) != 0:
                for args in field_rules[JsonParamKeys.ARGS]:
                    if JsonParamKeys.ARG_VALUE in args.keys():
                        input_format = args[JsonParamKeys.ARG_VALUE]
                    if JsonParamKeys.OUTPUT_FORMAT in args.keys():
                        self.date_output_format = args[JsonParamKeys.OUTPUT_FORMAT]



        select_expr = self.get_date_validation_result(col_name, input_format,rule_name,rule_list,arg_list)

        return select_expr

    def get_date_validation_result(self, col_name, input_format,rule_name,rule_list,arg_list):
        """
        This method is used to generate sql expression for validating date values.
        :param col_name: Name of the column which needs to be processed
        :param input_format: Date input format java
        :return select expression
        """

        select_expr = f.expr(
        "generic_udf_date(`" + col_name + "`, '" + col_name + "', '" + rule_list + "', '" +arg_list+ "') as `{}`".format(col_name))

        
        return select_expr
