#!/usr/bin/env python

import boto3
from botocore.config import Config
from ansible.errors import AnsibleError

from ansible.plugins.lookup import LookupBase

class VenaLookupBase(LookupBase):
    def __init__(self, **kwargs):
        super(VenaLookupBase, self).__init__(**kwargs)

    def get_client(self, service, region=None, keys=None):
        kwargs = {
            "config" : Config(retries = {"max_attempts" : 100})
        }
        if keys:
            if len(keys) != 2:
                raise AnsibleError("when providing keys, must provide both access key and secret key")
            kwargs["aws_access_key_id"] = keys[0]
            kwargs["aws_secret_access_key"] = keys[1]

        return boto3.client(service, region, **kwargs)

    def get_value(self, obj, path):
        """
        if path = a.b.c.d, return obj[a][b][c][d]
        """

        expected_key_type = None
        if type(obj) == dict:
            expected_key_type = str
        elif type(obj) == list:
            expected_key_type = int
        else:
            raise ValueError("obj must be a dict or list")

        #either [a] or [a, b.c.d.g]
        parts = path.split(".", 1)
        key = parts[0]
        if expected_key_type == int:
            key = int(key)

        if len(parts) == 1:
            return obj[key]
        else:
            return self.get_value(obj[key], parts[1])

    def assert_length(self, l, name, expected=1):
        if len(l) != expected:
            raise AnsibleError("Wrong number of {}. Expected {}, found {}".format(
                name, expected, len(l)))
