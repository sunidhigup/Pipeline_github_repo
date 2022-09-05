from aws_cdk import (aws_stepfunctions as sfn, aws_stepfunctions_tasks as sfn_tasks, core)
import json

class StepFunction(core.Stack):
    """

    """
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

    def create_step_function(self, state_machine_name, definition,step_role):
        """ Creates stepfunction using definitions

        Args:
            state_machine_name (str): name of stepfunction
            definition : definition of stepfunction
            role : iam role for stepfunction

        Returns:
            StepFunction: newly created stepfunction
        """        
        step_def=json.dumps(definition)
        step_function = sfn.CfnStateMachine(
            self, state_machine_name,
            definition_string=step_def,
            state_machine_name=state_machine_name,
            role_arn=step_role
        )
        return step_function
