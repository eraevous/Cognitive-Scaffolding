"""
📦 Module: core_lib.storage.aws_clients
- @ai-path: core_lib.storage.aws_clients
- @ai-source-file: combined_storage.py
- @ai-role: AWS Client Provider
- @ai-intent: "Provide reusable, profile-aware boto3 clients for AWS service access."

🔍 Module Summary:
This module defines simple factory functions to initialize `boto3` clients for AWS services like S3 and Lambda. 
Clients can be configured with optional AWS profiles (e.g., for local dev) and target regions (default "us-east-1"), 
supporting flexibility across deployment environments.

🗂️ Contents:

| Name              | Type     | Purpose                               |
|:------------------|:---------|:--------------------------------------|
| get_s3_client      | Function | Create a boto3 client for Amazon S3.  |
| get_lambda_client  | Function | Create a boto3 client for AWS Lambda. |

🧠 For AI Agents:
- @ai-dependencies: boto3
- @ai-uses: Session, client
- @ai-tags: boto3, aws, cloud, s3, lambda

⚙️ Meta:
- @ai-version: 0.2.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Add reusable AWS session client functions
- @change-summary: Initialize boto3 clients with optional profile and region support
- @notes: ""

👤 Human Overview:
    - Context: Used when consistent, optionally profile-scoped AWS clients are needed across modules.
    - Change Caution: Ensure AWS credentials and profile configurations are managed securely.
    - Future Hints: Extend to support additional AWS services if needed (e.g., DynamoDB, SNS).
"""


from typing import Optional

import boto3


def get_s3_client(
    profile: Optional[str] = None, region: str = "us-east-1"
) -> boto3.client:
    """
    Create and return a boto3 S3 client.

    Args:
        profile (str, optional): AWS CLI profile name
        region (str): AWS region

    Returns:
        boto3.client: Initialized S3 client
    """
    if profile:
        session = boto3.Session(profile_name=profile, region_name=region)
    else:
        session = boto3.Session(region_name=region)

    return session.client("s3")


def get_lambda_client(
    profile: Optional[str] = None, region: str = "us-east-1"
) -> boto3.client:
    """
    Create and return a boto3 Lambda client.

    Args:
        profile (str, optional): AWS CLI profile name
        region (str): AWS region

    Returns:
        boto3.client: Initialized Lambda client
    """
    if profile:
        session = boto3.Session(profile_name=profile, region_name=region)
    else:
        session = boto3.Session(region_name=region)

    return session.client("lambda")
