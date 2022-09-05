import setuptools
import json


with open("README.md") as fp:
    long_description = fp.read()

with open("version.json") as fp:
    version = json.load(fp)


setuptools.setup(
    name="aws_provision",
    version=version["setup"],

    description="An empty CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "aws_provision"},
    packages=setuptools.find_packages(where="aws_provision"),

    install_requires=[
        
        version["aws_cdk"],
        "aws-cdk.aws_elasticbeanstalk==1.109.0",
        "aws-cdk.aws_lambda==1.109.0",
        "aws-cdk.aws_stepfunctions_tasks==1.109.0",
        "aws-cdk.aws_stepfunctions==1.109.0",
        "aws-cdk.aws_emr==1.109.0",
        "aws-cdk.aws_lambda_event_sources==1.109.0"
        ],

    python_requires=version["python"],

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
