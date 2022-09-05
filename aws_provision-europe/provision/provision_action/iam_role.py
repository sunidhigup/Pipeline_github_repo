from aws_cdk import aws_iam as _iam
import json

class IAmRole:

    def create_role(self, role_name:str,path:str) :
        """ creates iam roles

        Args:
            role_name (str): name of role
            path(str): path of config

        Returns:
            role: returns the role created
        """        
        

        role_config = IAmRole.get_role_config(role_name,path)
        # actions = role_config['custom']['action']
        # resources = role_config['custom']['resources']
        managed_policies = IAmRole.get_managed_policy(role_config['standard'])
        service_principal = role_config['service-principal']

        iam_role = _iam.Role(self, role_name, role_name=role_name,
                                assumed_by=_iam.ServicePrincipal(service_principal),
                                managed_policies=managed_policies)
        
        # policy_statements = _iam.PolicyStatement(
        #     effect=_iam.Effect.ALLOW,
        #     resources=resources,
        #     actions=actions
        # )

        # iam_role.add_to_policy(policy_statements)
        return iam_role

    @staticmethod
    def get_role_config(role_name:str,path) -> dict :
        """ Fetch config for iam roles

        Args:
            role_name (str): name of role policy

        Returns:
            dict: config for roles
        """        
        with open(path) as f :
            roles_config = json.load(f)
        
        return roles_config[role_name]

    @staticmethod
    def get_managed_policy(managed_polices_config:str):
        """ Fetch managed policy

        Args:
            managed_polices_config (str): name of policy

        Returns:
            List : list of managed policy
        """        
        managed_polices_list = []
        for managed_policy_name in managed_polices_config:
            managed_polices_list.append(_iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name))

        return managed_polices_list

