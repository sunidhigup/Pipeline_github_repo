from pyspark.sql import functions as f
from Rule_Engine.rule_engine_jobs.constants.rule_engine_constants import JsonParamKeys, NumericValidationParams, CharacterConstants
from collections import ChainMap

class NumericValidation:
    """
        NumericValidation class will be use to validate different numeric & int
        values.
    """

    def numeric_validation(self, col_name, field_values=None):
        """
            This method will generate sql expression & extract different rules from json
            which will be used in numeric validation.
            :param col_name: Name of the column which needs to be processed
            :param field_values: Dictionary containing json rules
            :return select expression
        """

        # Extracting field rules from field value dictionary
        if field_values is None:
            field_values = {}

        rule_list =""
        arg_list=""


        if JsonParamKeys.FIELD_RULES in field_values:
            field_rules = field_values[JsonParamKeys.FIELD_RULES]
        else:
            field_rules = {}


        for field in field_rules:
            if  JsonParamKeys.RULE_NAME in field:  
                rule_list=rule_list+field[JsonParamKeys.RULE_NAME]+JsonParamKeys.RULE_LIST_SEPERATOR 
            
            if JsonParamKeys.ARGS in field:
                data = dict(ChainMap(*field[JsonParamKeys.ARGS]))
                for keys in data:
                    arg_list=arg_list+str(data[keys])+JsonParamKeys.RULE_LIST_SEPERATOR    
                arg_list=arg_list[:-1]+JsonParamKeys.ARG_LIST_SEPERATOR 

        rule_list=rule_list[:-1]
        arg_list=arg_list[:-3]


        # Extracting default value from schema dictionary
        default_value = '0'

        # if JsonParamKeys.DEFAULT_DECIMAL_VALUE in field_values[JsonParamKeys.FIELD_RULES][0]:
        if JsonParamKeys.DEFAULT_DECIMAL_VALUE in field_rules:
            default_value = field_values[JsonParamKeys.FIELD_RULES][0][JsonParamKeys.DEFAULT_DECIMAL_VALUE]

        # Extracting field type from schema dictionary
        field_type = ""
        if JsonParamKeys.TYPE_ATTR in field_values:
            field_type = field_values[JsonParamKeys.TYPE_ATTR]

        # Setting decimal separator as dot
        decimal_sep = CharacterConstants.DOT

        int_type_list = NumericValidationParams.INT_TYPE_LIST
        scale = 0
        rule_name = ""

        # for field in field_rules:
        if JsonParamKeys.RULE_NAME in field_rules:
            rule_name = field_rules[JsonParamKeys.RULE_NAME]

        if JsonParamKeys.ARGS in field_rules:
            if len(field_rules[JsonParamKeys.ARGS]) != 0:
                for args in field_rules[JsonParamKeys.ARGS]:

                    if JsonParamKeys.DEFAULT_DECIMAL_VALUE in args.keys():
                        default_value = args[JsonParamKeys.DEFAULT_DECIMAL_VALUE]

         

        select_expr = self.get_numeric_validation_result(col_name, default_value, scale, field_type,
                                                         decimal_sep, int_type_list,rule_list,arg_list)

        
        return select_expr

    @staticmethod
    def get_numeric_validation_result(col_name, default_value, scale, field_type, decimal_sep,
                                      int_type_list,rule_list,arg_list):

        """
        This method is used to generate sql expression for numeric validation.
        :param decimal_sep:
        :param col_name: Name of the column which needs to be processed
        :param default_value: Numeric default value
        :param scale: Scale which needs to be set to numeric value
        :param field_type: Type of numeric field
        :param int_type_list: Comma separated string containing int & bigint
        :return select expression
        """        
    

        select_expr = f.expr(
        "generic_Udf(`" + col_name + "`, '" + col_name + "', '" + rule_list + "', '" +arg_list+ "') as `{}`".format(col_name))

        return select_expr
