from aws_cdk import aws_ec2 as ec2
from aws_cdk.aws_ec2 import  CfnSecurityGroup,  CfnSecurityGroupIngress,CfnSecurityGroupEgress
import json

class SecurityGroups:

    def create_security_group(self, security_group_name:str,path:str):
        """ creates security group

        Args:
            security_group_name (str): name of group
            path(str): path to config

        Returns:
            SecurityGroup : newly created security groups
        """        
        security_group_config = SecurityGroups.get_security_group_config(security_group_name,path)
        return CfnSecurityGroup(
            self, security_group_name, #vpc_id=self.vpc.vpc_id,
            group_description=security_group_config['group_description'], group_name=security_group_name
        )

    def add_inbound_rules(self, security_group_name : str, source_security_group_map: dict,path):
        """
        creates inbound rule for groups

        Args:
            security_group_name (str): name of security group
            source_security_group_map (dict): security groups in key value pair
        """        
        security_group_config = SecurityGroups.get_security_group_config(security_group_name,path)

        for inbound_rule in security_group_config['Inbound']:
            CfnSecurityGroupIngress(self, inbound_rule['id'], ip_protocol=inbound_rule['ip_protocol'],
                                    source_security_group_id=source_security_group_map[
                                        inbound_rule['source_security_group_name']].attr_group_id,
                                    from_port=inbound_rule['from_port'], to_port=inbound_rule['to_port'],
                                    group_id=source_security_group_map[security_group_name].attr_group_id)

    def add_outbound_rules(self, security_group_name:str, source_security_group_map:dict,path):
        """
        creates outbound rule for groups

        Args:
            security_group_name (str): name of security group
            source_security_group_map (dict): security groups in key value pair
        """ 
        security_group_config = SecurityGroups.get_security_group_config(security_group_name,path)
        for outbound_rule in security_group_config['Outbound']:
            outbound_rule_generic_config = {}
            if 'source_security_group_name' in outbound_rule:
                outbound_rule_generic_config['destination_security_group_id']=source_security_group_map[outbound_rule['source_security_group_name']].attr_group_id
            # if 'destination_prefix_list_name' in outbound_rule:
            #     outbound_rule_generic_config['destination_prefix_list_id'] = self.prefix_list_map[outbound_rule['destination_prefix_list_name']].attr_prefix_list_id
           
            CfnSecurityGroupEgress(self,outbound_rule['id'],ip_protocol=outbound_rule['ip_protocol'],
                                   from_port=outbound_rule['from_port'],to_port=outbound_rule['to_port'],
                                   group_id=source_security_group_map[security_group_name].attr_group_id,
                                    **outbound_rule_generic_config
                                   )


    @staticmethod
    def get_security_group_config(security_group_name,path):
        """ Fetches config for security group

        Returns:
            dict: config for security group
        """  
        with open(path) as f:
            security_groups_config = json.load(f)
        return security_groups_config[security_group_name]
