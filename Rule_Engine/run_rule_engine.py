from Rule_Engine.Constant.constant import run_rule_engine_constant
from Rule_Engine.logging.cloudwatch.log_utils import write_logs
from Rule_Engine.rule_engine_jobs.rule_engine_processor import RuleEngineProcessor
from Rule_Engine.rule_engine_jobs.utils.rule_helper import get_job_details, argument_parser

if __name__ == "__main__":
    # Fetching input argument
    arg_dict = argument_parser()

    # Fetching job parameters from dynamodb metadata table
    parameters = get_job_details(arg_dict)

    obj = RuleEngineProcessor
    # Running rule engine
    obj.process(parameters)

    # Writing logs
    write_logs(run_rule_engine_constant.INFO, run_rule_engine_constant.INFO_RULE_ENGINE)
