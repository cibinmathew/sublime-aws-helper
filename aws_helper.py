import os
import sys

import boto3
import sublime
import sublime_plugin
import yaml
import json
    """
    Usecase: if the selection matches a supported aws arn, the corresponding aws console url is opened.
    """
        arn= self.view.substr(sel)

import webbrowser
import re


class AwsHelperOpenArnInConsoleCommand(sublime_plugin.TextCommand):
    """
    Usecase: if the selection matches a supported aws arn, the corresponding aws console url is opened.
    """

    def run(self, edit):

        sel = self.view.sel()[0]
        arn= self.view.substr(sel)
        print(arn)
        # Define a dictionary of services with their ARN patterns and URL generation logic
        services = {
            "s3": {
                "pattern": r"^arn:aws:s3:::(?P<bucket_name>[a-zA-Z0-9.-_]+)$",
                "url": lambda match: "https://s3.console.aws.amazon.com/s3/buckets/{0}".format(match.group('bucket_name')),
            },
            "ecs": {
                "pattern": r"^arn:aws:ecs:(?P<region>[a-z0-9-]+):(?P<account_id>\d+):cluster/(?P<cluster_name>[a-zA-Z0-9-_]+)$",
                "url": lambda match: f"https://{match.group('region')}.console.aws.amazon.com/ecs/home?region={match.group('region')}#/clusters/{match.group('cluster_name')}",
            },
            "rds": {
                "pattern": r"^arn:aws:rds:(?P<region>[a-z0-9-]+):(?P<account_id>\d+):db:(?P<db_instance>[a-zA-Z0-9-_]+)$",
                "url": lambda match: f"https://{match.group('region')}.console.aws.amazon.com/rds/home?region={match.group('region')}#databases:id={match.group('db_instance')};is-cluster=false",
            },
        }

        # Iterate through services to find a match
        for service, config in services.items():
            print(config)
            match = re.match(config["pattern"], arn)
            if match:
                url = config["url"](match)
                # print(f"Opening {service.upper()} console for ARN: {arn}")
                webbrowser.open(url)
                return

        print("The provided ARN does not match any supported service patterns.")




class AwsHelperValidateIamCommand(sublime_plugin.TextCommand):

    def run(self, edit):

        self.title_length = 40

        client = boto3.client("accessanalyzer")
        selected_text = self.view.substr(self.view.sel()[0]).strip()

        print("Validating Policy...")
        self.view.set_status("AWS helper", "Validating Policy...")
        response = client.validate_policy(
            locale="EN",
            maxResults=123,
            policyDocument=selected_text,
            # policyType='IDENTITY_POLICY'|'RESOURCE_POLICY'|'SERVICE_CONTROL_POLICY',
            policyType="IDENTITY_POLICY",
            # validatePolicyResourceType='AWS::S3::Bucket'|'AWS::S3::AccessPoint'|'AWS::S3::MultiRegionAccessPoint'|'AWS::S3ObjectLambda::AccessPoint'|'AWS::IAM::AssumeRolePolicyDocument'
        )
        if response["findings"]:
            self.view.set_status("AWS helper", "Invalid IAM Policy")
            result = yaml.dump(response["findings"])
            self.create_new_tab(result, "Findings")
        else:
            # TODO clear after some time
            self.view.set_status("AWS helper", "Valid IAM Policy")

    def create_new_tab(self, text, title=""):
        # https://github.com/davidpeckham/sublime-filterlines/blob/master/filter.py
        results_view = self.view.window().new_file()
        title = (
            "%s..." % (title[: self.title_length])
            if len(title) > self.title_length
            else title
        )
        results_view.set_name("AWS helper: %s" % (title))
        results_view.set_scratch(True)
        results_view.settings().set("word_wrap", self.view.settings().get("word_wrap"))
        results_view.run_command(
            "append", {"characters": text, "force": True, "scroll_to_end": False}
        )
        results_view.set_syntax_file(self.view.settings().get("syntax"))
