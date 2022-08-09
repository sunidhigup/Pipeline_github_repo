from aws_cdk import core
from provision.provision_action.iam_role import IAmRole
import json

class JobIAmRole(core.Stack):
    """

    Args:
        core (core.aws.Stack): Stack class from aws
    """    
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

    def createAll(self, path):
        """
         Get roles config from json and created roles
            Args:
                path (str): path of config
        """        
        self.iam_roles = {}
        roles_config = JobIAmRole.iam_role_config(path)

        #Creating IAM Roles
        for role_name in roles_config:
            self.iam_roles[role_name] = IAmRole.create_role(self, role_name,path)
        
        return self.iam_roles

    @staticmethod
    def iam_role_config(path):
        """ Fetch config for iam roles

        Returns:
            dict : config of iam roles
        """        
        #Reading config file
        with open(path) as f:
            roles_config = json.load(f)
        
        return roles_config
