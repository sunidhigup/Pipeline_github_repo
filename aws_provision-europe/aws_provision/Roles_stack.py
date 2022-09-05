from aws_cdk import core
from constant.constant import STACKS_CONSTANTS
from provision.resources.iam_job_role import JobIAmRole



class Dep_Roles_Stack(core.Stack):
    """IAM Role creation Stack

    Args:
        core (aws.core.Stack): Stack class from aws
    """    
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        """init class for Roles creation stack

        Args:
            scope (core.Construct)
            id (str)
        """        
        
        env = kwargs[STACKS_CONSTANTS.ENV]
        super().__init__(scope, id,env=env)
        config = kwargs[STACKS_CONSTANTS.CONFIG]
        self.cfg=config

        #Fetching path for configs
 
        role_path= self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.IAM_CONFIG]
    


        #Creating resources
        roles = JobIAmRole.createAll(self,role_path)
        #return roles

