"""Administrator-only setup: AWS_PROFILE=redya-admin python3 deploy/provision.py."""
import json
from pathlib import Path
import boto3
from botocore.exceptions import ClientError

CONFIG = json.loads((Path(__file__).parent / 'config.json').read_text())


def provision():
    c = CONFIG
    session = boto3.Session(region_name=c['region'])
    assert session.client('sts').get_caller_identity()['Account'] == c['account']
    s3, iam, ssm = (session.client(service) for service in ('s3', 'iam', 'ssm'))
    bucket = c['bucket']
    try:
        s3.head_bucket(Bucket=bucket, ExpectedBucketOwner=c['account'])
    except ClientError as error:
        if error.response['Error']['Code'] not in {'404', 'NoSuchBucket'}:
            raise
        s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={'LocationConstraint': c['region']})
    s3.put_public_access_block(Bucket=bucket, PublicAccessBlockConfiguration={name: True for name in ('BlockPublicAcls', 'IgnorePublicAcls', 'BlockPublicPolicy', 'RestrictPublicBuckets')})
    s3.put_bucket_encryption(Bucket=bucket, ServerSideEncryptionConfiguration={'Rules': [{'ApplyServerSideEncryptionByDefault': {'SSEAlgorithm': 'AES256'}}]})
    s3.put_bucket_versioning(Bucket=bucket, VersioningConfiguration={'Status': 'Enabled'})
    s3.put_bucket_lifecycle_configuration(Bucket=bucket, LifecycleConfiguration={'Rules': [{'ID': 'ExpireDeploymentArtifacts', 'Status': 'Enabled', 'Filter': {'Prefix': 'releases/'}, 'Expiration': {'Days': 30}, 'NoncurrentVersionExpiration': {'NoncurrentDays': 7}, 'AbortIncompleteMultipartUpload': {'DaysAfterInitiation': 1}}]})
    s3.put_bucket_policy(Bucket=bucket, Policy=json.dumps({'Version': '2012-10-17', 'Statement': [{'Sid': 'DenyInsecureTransport', 'Effect': 'Deny', 'Principal': '*', 'Action': 's3:*', 'Resource': [f'arn:aws:s3:::{bucket}', f'arn:aws:s3:::{bucket}/*'], 'Condition': {'Bool': {'aws:SecureTransport': 'false'}}}]}))
    trust = {'Version': '2012-10-17', 'Statement': [{'Effect': 'Allow', 'Principal': {'Federated': f"arn:aws:iam::{c['account']}:oidc-provider/token.actions.githubusercontent.com"}, 'Action': 'sts:AssumeRoleWithWebIdentity', 'Condition': {'StringEquals': {'token.actions.githubusercontent.com:aud': 'sts.amazonaws.com', 'token.actions.githubusercontent.com:sub': c['oidc_subject']}}}]}
    try:
        iam.get_role(RoleName=c['role'])
    except iam.exceptions.NoSuchEntityException:
        iam.create_role(RoleName=c['role'], AssumeRolePolicyDocument=json.dumps(trust), Description='EJI main branch static site deployment only', MaxSessionDuration=3600)
    else:
        iam.update_assume_role_policy(RoleName=c['role'], PolicyDocument=json.dumps(trust))
    object_arn = f'arn:aws:s3:::{bucket}/releases/*'
    policy = {'Version': '2012-10-17', 'Statement': [
        {'Sid': 'DeploymentArtifactsOnly', 'Effect': 'Allow', 'Action': ['s3:PutObject', 's3:GetObject'], 'Resource': object_arn},
        {'Sid': 'FixedProductionReceiverOnly', 'Effect': 'Allow', 'Action': 'ssm:SendCommand', 'Resource': [f"arn:aws:ssm:{c['region']}:{c['account']}:document/{c['document']}", f"arn:aws:ec2:{c['region']}:{c['account']}:instance/{c['instance']}"]},
        {'Sid': 'ReadCommandResult', 'Effect': 'Allow', 'Action': 'ssm:GetCommandInvocation', 'Resource': '*'},
    ]}
    iam.put_role_policy(RoleName=c['role'], PolicyName='EJIStaticProductionDeploy', PolicyDocument=json.dumps(policy))
    iam.put_role_policy(RoleName=c['host_role'], PolicyName='EJIReadDeploymentArtifacts', PolicyDocument=json.dumps({'Version': '2012-10-17', 'Statement': [{'Effect': 'Allow', 'Action': 's3:GetObject', 'Resource': object_arn}]}))
    document = {
        'schemaVersion': '2.2', 'description': 'Deploy verified EJI static assets through the installed fixed receiver',
        'parameters': {name: {'type': 'String', 'interpolationType': 'ENV_VAR', 'allowedPattern': pattern} for name, pattern in [('Revision', '^[0-9a-f]{40}$'), ('Digest', '^[0-9a-f]{64}$')]},
        'mainSteps': [{'action': 'aws:runShellScript', 'name': 'DeployVerifiedStaticSite', 'precondition': {'StringEquals': ['platformType', 'Linux']}, 'inputs': {'timeoutSeconds': '180', 'runCommand': ['set -eu', 'python3 /opt/electrajaringan/deploy/receive.py "$SSM_Revision" "$SSM_Digest"']}}],
    }
    content = json.dumps(document)
    try:
        ssm.get_document(Name=c['document'], DocumentVersion='$DEFAULT')
    except ssm.exceptions.InvalidDocument:
        ssm.create_document(Name=c['document'], Content=content, DocumentType='Command', DocumentFormat='JSON')
    else:
        try:
            updated = ssm.update_document(Name=c['document'], Content=content, DocumentVersion='$LATEST', DocumentFormat='JSON')
            ssm.update_document_default_version(Name=c['document'], DocumentVersion=updated['DocumentDescription']['DocumentVersion'])
        except ssm.exceptions.DuplicateDocumentContent:
            pass
    print(json.dumps({'bucket': bucket, 'role': c['role'], 'document': c['document'], 'oidc_subject': c['oidc_subject']}, indent=2))


if __name__ == '__main__':
    provision()
