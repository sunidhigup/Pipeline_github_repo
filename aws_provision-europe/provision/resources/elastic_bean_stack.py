from aws_cdk import core
from aws_cdk import aws_s3_assets
from aws_cdk import aws_elasticbeanstalk as elasticbeanstalk
import json
import os



class ElasticBeanstalk(core.Stack):
    """

    Args:
        core (aws.core.Stack): Stack class from aws
    """    
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

    def create_elastic_beanstalk(self, elastic_beanstalk_path):
        """

        :param elastic_beanstalk_path:
        """
        #Reading ebs config
        elastic_bean_config = ElasticBeanstalk.ebs_config(elastic_beanstalk_path)
        deploy_backend = elastic_bean_config["Deploy_backend"]

        #Deploying EBS
        if deploy_backend:
            elastic_bean = elastic_bean_config["Applications"]["Backend"]
            appname = elastic_bean["ApplicationName"]
            envname = elastic_bean["EnvironmentName"]
            s3_asset = elastic_bean["S3_Asset"]
            solname = elastic_bean["Solution_Stack_Name"]
        
        else:
            elastic_bean = elastic_bean_config["Applications"]["Frontend"]
            appname = elastic_bean["ApplicationName"]
            envname = elastic_bean["EnvironmentName"]
            s3_asset = elastic_bean["S3_Asset"]
            solname = elastic_bean["Solution_Stack_Name"]
            
            

        s3asset = ElasticBeanstalk.BeanstalkS3Stack(self, s3_asset)

        application = ElasticBeanstalk.createApplication(
            self, appname, s3asset)

        
        env = ElasticBeanstalk.createEnvironment(
            self, appname, envname, solname)
        
        


        


    def createApplication(self, appname, s3asset):
        """

        :param appname:
        :param s3asset:
        :return:
        """
        self.cfn_application = elasticbeanstalk.CfnApplication(self, "MyCfnApplication",
                                                          application_name=appname,
                                                          description="AWS Elastic Beanstalk Demo"
                                                          )

        self.app_version = elasticbeanstalk.CfnApplicationVersion(
            self,
            "application_version",
            application_name=appname,
            source_bundle=elasticbeanstalk.CfnApplicationVersion.SourceBundleProperty(
                s3_bucket=s3asset['s3bucket_name'],
                s3_key=s3asset['s3bucket_obj_key']
            )

        )
        return self.cfn_application

    def createEnvironment(self, application_name, environment_name, solution_stack_name):
        """

        :param application_name:
        :param environment_name:
        :param solution_stack_name:
        """
        

        version_label = self.app_version.ref
      
        beanstalk_env_config_template = elasticbeanstalk.CfnConfigurationTemplate(
            self,
            "Elastic-Beanstalk-Env-Config",
            application_name=application_name,
            solution_stack_name=solution_stack_name,
            option_settings=[
                elasticbeanstalk.CfnConfigurationTemplate.ConfigurationOptionSettingProperty(
                    namespace="aws:elasticbeanstalk:environment", option_name="EnvironmentType", value="SingleInstance"
                ),
                 
                elasticbeanstalk.CfnConfigurationTemplate.ConfigurationOptionSettingProperty(
                    namespace="aws:autoscaling:launchconfiguration", option_name="IamInstanceProfile", value="aws-elasticbeanstalk-ec2-role"
                ),
                elasticbeanstalk.CfnConfigurationTemplate.ConfigurationOptionSettingProperty(
                    namespace="aws:elasticbeanstalk:environment", option_name="ServiceRole", value="aws-elasticbeanstalk-service-role"
                )

            ]

        )
        
        beanstalk_env = elasticbeanstalk.CfnEnvironment(
            self,
            "Elastic-Beanstalk-Environment",
            application_name=application_name,
            environment_name=environment_name,
            solution_stack_name=solution_stack_name,
            version_label= version_label,
            option_settings=[
                elasticbeanstalk.CfnEnvironment.OptionSettingProperty(
                    namespace="aws:elasticbeanstalk:environment", option_name="EnvironmentType", value="SingleInstance"
                ),
                elasticbeanstalk.CfnEnvironment.OptionSettingProperty(
                    namespace="aws:autoscaling:launchconfiguration", option_name="IamInstanceProfile", value="aws-elasticbeanstalk-ec2-role"
                ),

                elasticbeanstalk.CfnEnvironment.OptionSettingProperty(
                    namespace="aws:elasticbeanstalk:environment", option_name="ServiceRole", value="aws-elasticbeanstalk-service-role"
                ),

            ]
        )
        self.app_version.add_depends_on(self.cfn_application)
        beanstalk_env.add_depends_on(self.cfn_application)
        beanstalk_env_config_template.add_depends_on(self.cfn_application)

        

    @staticmethod
    def ebs_config(path):
        """
            Fetches config for 
        Returns:
            dict : config for stepfunction
        """
        with open(path) as f:
            elasticbean_config = json.load(f)
        return elasticbean_config

    def BeanstalkS3Stack(self, s3_bean):
        """

        :param s3_bean:
        :param configbean:
        :return:
        """
        path=os.path.abspath(s3_bean)
        s3_bucket_asset = aws_s3_assets.Asset(
            self,
            "s3-asset",
            path=path

        )
       

        output_props = {}
        output_props['s3bucket_name'] = s3_bucket_asset.s3_bucket_name
        output_props['s3bucket_obj_key'] = s3_bucket_asset.s3_object_key
  
        return output_props
