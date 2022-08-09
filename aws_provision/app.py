#!/usr/bin/env python3

from aws_cdk import core
# from aws_provision.Orchestration_stack import Dep_orchestration_Stack
# from aws_provision.Roles_stack import Dep_Roles_Stack
from aws_provision.Database_stack import Dep_DB_Stack
from aws_provision.S3_stack import S3_Stack
# from aws_provision.aws_provision_stack import AwsProvisionStack
from aws_provision.Infra_stack import Dep_infra_Stack

app = core.App()

env_qa_us = core.Environment(account=app.node.try_get_context('qa')['account'],
                             region=app.node.try_get_context('qa')['region'])
env_dev_us = core.Environment(account=app.node.try_get_context('dev')['account'],
                              region=app.node.try_get_context('dev')['region'])

#Dep_Roles_Stack(app, "dep-roles", env=env_dev_us, config="dev")
#Dep_orchestration_Stack(app, "dep-orchestration", env=env_dev_us, config="dev")

#Making stack for db, S3, Infra

Dep_DB_Stack(app, "dep-db-qa", env=env_dev_us, config="dev")
Dep_infra_Stack(app, "dep-infra-qa", env=env_dev_us, config="dev")
S3_Stack(app, "dep-s3-qa", env=env_dev_us, config="dev")

app.synth()
