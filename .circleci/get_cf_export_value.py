"""
Because us-east-1 is really the only place that AWS works properly.

This shouldn't be a thing. But, it is a thing.

Our main stack is in `eu-west-2` and the CloudFront
distribution is "global", meaning a very specific part of the US.

However, when we want to attach a lambda@edge function
to the "global" resource for our `eu-west-2` deployment, the lambda
function itself needs to be in...you guessed it, a very specific part
of the US.

Fine, but we also need a way to share the version ARN of that function
with the CloudFront distribution. The right way to do this is via the
CloudFormation Exports system, however they don't work across regions.

This means that either Lambda@Edge only really works if you deploy to
a very specific part of the US, or if you hack some script together like
the below.

"""

import sys

import boto3


def get_export_value(export_name):
    cf_client = boto3.client("cloudformation", region_name="us-east-1")
    for export in cf_client.list_exports()["Exports"]:
        if export["Name"] == export_name:
            return export["Value"]
    raise ValueError(f"Export {export_name} not found")


if __name__ == "__main__":
    export_name = sys.argv[1]
    print(get_export_value(export_name))
