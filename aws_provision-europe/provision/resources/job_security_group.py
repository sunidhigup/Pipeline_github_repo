from aws_cdk import core,aws_ec2 as ec2
from provision.provision_action.security_groups import SecurityGroups
import json
from constant.constant import SECURITYGROUP

class JobSecurityGroup(core.Stack):
    """

    Args:
        core (aws.core.Stack): Stack class from aws
    """    
    def __init__(self, scope: core.Construct, id: str, vpc=None, **kwargs) -> None:
        """_summary_

        Args:
            scope (core.Construct): _description_
            id (str): _description_
            vpc (_type_, optional): _description_. Defaults to None.
        """        
        super().__init__(scope, id, **kwargs)


    def createAll(self, path):
        """
         Attaches existing security group if exists or creates new one
        """        

        security_groups_config = JobSecurityGroup.security_group_config(path)
        self.security_group_map = {}
        # try:
        #     #use existing group

        #     ecs_sg_cluster = ec2.SecurityGroup.from_security_group_id(self,SECURITYGROUP.ID ,
        #                                                    security_group_id=SECURITYGROUP.GROUP_ID)
         
        # except:
            #create new security group
        
        #Creating security groups
        for security_group_name in security_groups_config:
            
            self.security_group_map[security_group_name] = SecurityGroups.create_security_group(self,
                                                                                                    security_group_name,path)

        for security_group_name in security_groups_config:
               
            SecurityGroups.add_inbound_rules(self,security_group_name,self.security_group_map,path)
            SecurityGroups.add_outbound_rules(self,security_group_name,self.security_group_map,path)

    @staticmethod
    def security_group_config(path):
        """ Fetches config for security group

        Args:
            path (str): path of config

        Returns:
            dict: config for security group
        """        
        #Reading config file
        with open(path) as f:
            security_groups_config = json.load(f)
        return security_groups_config
