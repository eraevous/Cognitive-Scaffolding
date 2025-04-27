"""
Module: core_lib.storage.aws_clients 

- @ai-path: core_lib.storage.aws_clients 
- @ai-source-file: combined_storage.py 
- @ai-module: aws_clients 
- @ai-role: aws_client_provider 
- @ai-entrypoint: get_s3_client(), get_lambda_client() 
- @ai-intent: "Provide reusable, profile-aware boto3 clients for AWS service access."

🔍 Summary:
Provides factory functions to initialize `boto3` clients for AWS services (S3 and Lambda). These functions support injecting AWS CLI profiles (for development environments) and regions (default: "us-east-1"). Used across modules for consistent and testable cloud access.

📦 Inputs:
- profile (Optional[str]): AWS CLI profile name (default: None)
- region (str): AWS region name (default: "us-east-1")

📤 Outputs:
- boto3.client: Configured boto3 client instance (S3 or Lambda)

🔗 Related Modules:
- s3_utils.py → uses get_s3_client for upload/download
- lambda_summary.py → uses get_lambda_client for LLM summarization

🧠 For AI Agents:
- @ai-dependencies: boto3
- @ai-calls: boto3.Session().client()
- @ai-uses: profile, region, Session
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
- @notes: 
"""


import boto3
from typing import Optional


def get_s3_client(profile: Optional[str] = None, region: str = "us-east-1") -> boto3.client:
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


def get_lambda_client(profile: Optional[str] = None, region: str = "us-east-1") -> boto3.client:
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