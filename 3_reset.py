import boto3
import json
import os
import requests
import argparse

def get_env_var(var_name):
    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"Environment variable {var_name} must be set")
    return value

def update_trust_policy(roleArn, current_external_id, default_external_id):
    session = boto3.Session()
    iam = session.client('iam')
    role_name = roleArn.split('/')[-1]

    response = iam.get_role(RoleName=role_name)
    trust_policy = response['Role']['AssumeRolePolicyDocument']

    print("Current Trust Policy:", json.dumps(trust_policy, indent=4))

    updated = False
    for statement in trust_policy['Statement']:
        if 'Condition' in statement and 'StringEquals' in statement['Condition']:
            if 'sts:ExternalId' in statement['Condition']['StringEquals']:
                if statement['Condition']['StringEquals']['sts:ExternalId'] == current_external_id:
                    statement['Condition']['StringEquals']['sts:ExternalId'] = default_external_id
                    updated = True

    if not updated:
        raise ValueError(f"ExternalId {current_external_id} not found in the current trust policy")

    print("Updated Trust Policy:", json.dumps(trust_policy, indent=4))

    iam.update_assume_role_policy(
        RoleName=role_name,
        PolicyDocument=json.dumps(trust_policy)
    )

    print(f"Updated the trust policy for role: {role_name}")

def login(email, password, org_id, realm):
    url = f"https://api.{realm}.signalfx.com/v2/session"
    headers = {"Content-Type": "application/json"}
    data = {
        "email": email,
        "password": password,
        "organizationId": org_id
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()
    return response.json().get("accessToken")

def delete_integration(realm, token, integration_id):
    url = f"https://api.{realm}.signalfx.com/v2/integration/{integration_id}"
    headers = {
        "Content-Type": "application/json",
        "X-SF-TOKEN": token
    }
    response = requests.delete(url, headers=headers)

    if response.status_code == 204:
        print("Integration deleted successfully.")
    else:
        print(f"Failed to delete integration. Status code: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Login to SignalFx API, create integration, and update IAM trust policy.')
    parser.add_argument('--email', help='Your email address')
    parser.add_argument('--password', help='Your password')
    parser.add_argument('--orgId', help='Your organization ID')
    parser.add_argument('--realm', help='The realm of your SignalFx account')
    parser.add_argument('--current_external_id', help='Current External ID to replace in the trust policy')
    parser.add_argument('--integration_id', help='The Integration ID of the AWS Integration to be deleted')
    parser.add_argument('--roleArn', help='IAM role ARN to update trust policy')
    parser.add_argument('--defaultExternalId', help='The Default External ID that will be set')


    args = parser.parse_args()

    email = args.email or get_env_var('O11Y_EMAIL')
    password = args.password or get_env_var('O11Y_PASSWORD')
    org_id = args.orgId or get_env_var('O11Y_ORGID')
    realm = args.realm or get_env_var('O11Y_REALM')
    current_external_id = args.current_external_id or get_env_var('EXTERNAL_ID')
    integration_id = args.integration_id or get_env_var('INTEGRATION_ID')
    roleArn = args.roleArn or get_env_var('ROLE_ARN')
    default_external_id = args.defaultExternalId or os.getenv('DEFAULT_EXTERNAL_ID')

    try:
        token = login(email, password, org_id, realm)
        delete_integration(realm, token, integration_id)
        update_trust_policy(roleArn, current_external_id, default_external_id)
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"An error occurred: {err}")
