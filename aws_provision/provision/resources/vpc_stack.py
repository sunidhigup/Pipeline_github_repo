from aws_cdk import core, aws_ec2 as ec2
from aws_cdk.aws_ec2 import Vpc

import json


class VpcStack(core.Stack):

    def create_vpc(self, path):
        """
        Use existing Vpc or creates new one using config
        Args:
            path (str): path of config

        """
        config = get_vpc_config(path)


        
        # creating new vpc
        vpc_name = config['vpc']["vpc_name"]
        self.vpc = Vpc(
                self, vpc_name, cidr=config['vpc']['cidr'], nat_gateways=0,max_azs=config['vpc']['max_azs'],
                subnet_configuration=[ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PUBLIC,
                    name=config['vpc']['subnet_pub_name_1'],
                    cidr_mask=config['vpc']['cidr_pub_mask']
                ),
                  ec2.SubnetConfiguration(
                      subnet_type=ec2.SubnetType.PUBLIC,
                         name=config['vpc']['subnet_pub_name_2'],
                         cidr_mask=config['vpc']['cidr_pvt_mask']
                 )
                 ]

            )
        VpcStack.create_vpc_endpoints(self, path)


        return self.vpc
    
    # def createroutetable(self):
        
    #     table_ids = ec2.CfnRouteTable( self, "route_table_test",
    #             vpc_id=self.vpc.vpc_id)
    #     return table_ids
        
    def create_vpc_endpoints(self, path):
        vpc_config = get_vpc_config(path)
        self.vpc_endpoints = {}
        for vpc_endpoint_config in vpc_config['endpoints']:
            subnet_ids = []
            route_ids = []
            if vpc_endpoint_config['endpoint_type'] == "Interface":
                subnet_ids = [subnet.subnet_id for subnet in self.vpc.public_subnets]
            if vpc_endpoint_config['endpoint_type'] == "Gateway":
                route_ids = [subnet.route_table.route_table_id for subnet in self.vpc.public_subnets]
            
            # route_id = VpcStack.createroutetable(self)
            # route_ids.append(route_id.ref)
            self.vpc_endpoints[vpc_endpoint_config['service_name']] = ec2.CfnVPCEndpoint(
                self, vpc_endpoint_config['endpoint_type'] + vpc_endpoint_config['service_name'],
                vpc_id=self.vpc.vpc_id,
                vpc_endpoint_type=vpc_endpoint_config['endpoint_type'],
                service_name=vpc_endpoint_config['service_name'],
                subnet_ids=subnet_ids,
                route_table_ids=route_ids
            )


def get_vpc_config(path):
    """ Fetches config for vpc

    Returns:
        dict : config for vpc
    """
    #Reading config file
    with open(path) as f:
        roles_config = json.load(f)

    return roles_config
