import json

import aws_cdk.aws_secretsmanager as secretsmanager
from aws_cdk import aws_iam as iam


def create_secret_manager(self, path):
    """
     Creates new secret
    """

    # fetches config
    config = secret_config(path)

    # created iam service role
    role = iam.Role(
        self,
        config["service_role"]["name"],
        assumed_by=iam.ServicePrincipal(config["service_role"]["assumed_by"]),
        managed_policies=[
            iam.ManagedPolicy.from_aws_managed_policy_name(
                config["service_role"]["policy"]
            )
        ]
        #    inline_policies=[read_scripts_document],
    )

    # Default secret
    secret = secretsmanager.Secret(self, config["logical_id"])
    secret.grant_read(role)

    iam.User(self, "User",
             password=secret.secret_value
             )

    # Templated secret
    templated_secret = secretsmanager.Secret(self, "TemplatedSecret",
                                             generate_secret_string=secretsmanager.SecretStringGenerator(
                                                 secret_string_template=json.dumps({"username": config["user"]}),
                                                 generate_string_key=config["password"]
                                             )
                                             )

    iam.User(self, "OtherUser",
             user_name=templated_secret.secret_value_from_json("username").to_string(),
             password=templated_secret.secret_value_from_json("password")
             )


def secret_config(path):
    """Fetches config for secret manager
    Args:
            path (str): path of config

    Returns:
        dict: config for secret manager
    """
    #Reading config file
    with open(path) as f:
        secret_config = json.load(f)
    return secret_config
