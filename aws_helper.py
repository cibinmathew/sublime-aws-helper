import os
import sys

import boto3
import sublime
import sublime_plugin
import yaml
import json


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
