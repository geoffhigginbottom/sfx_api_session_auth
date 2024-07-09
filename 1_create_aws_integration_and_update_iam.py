import os
import requests
import argparse
import json
import boto3

def login(email, password, orgId, realm):
    url = f"https://api.{realm}.signalfx.com/v2/session"
    headers = { "Content-Type": "application/json" }
    data = {
        "email": email,
        "password": password,
        "organizationId": orgId
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json().get("accessToken")
    else:
        response.raise_for_status()

def create_integration(realm, token, name, namedToken, regions, sfxAwsAccountArn):
    url = f"https://api.{realm}.signalfx.com/v2/integration"
    headers = {
        "Content-Type": "application/json",
        "X-SF-TOKEN": token
    }
    data = {
        "authMethod": "ExternalId",
        "type": "AWSCloudWatch",
        "enableAwsUsage": True,
        "enabled": True,
        "importCloudWatch": True,
        "metadataPollRate": 60000,
        "name": name,
        "namedToken": namedToken,
        "pollRate": 60000,
        "regions": regions,
        "sfxAwsAccountArn": sfxAwsAccountArn
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def update_iam_trust_policy(role_arn, old_external_id, new_external_id):
    session = boto3.Session()
    iam = session.client('iam')
    role_name = role_arn.split('/')[-1]

    response = iam.get_role(RoleName=role_name)
    trust_policy = response['Role']['AssumeRolePolicyDocument']

    print("Current Trust Policy:", json.dumps(trust_policy, indent=4))

    updated = False
    for statement in trust_policy['Statement']:
        if 'Condition' in statement and 'StringEquals' in statement['Condition']:
            if 'sts:ExternalId' in statement['Condition']['StringEquals']:
                if statement['Condition']['StringEquals']['sts:ExternalId'] == old_external_id:
                    statement['Condition']['StringEquals']['sts:ExternalId'] = new_external_id
                    updated = True

    if not updated:
        raise ValueError(f"ExternalId {old_external_id} not found in the current trust policy")

    print("Updated Trust Policy:", json.dumps(trust_policy, indent=4))

    iam.update_assume_role_policy(
        RoleName=role_name,
        PolicyDocument=json.dumps(trust_policy)
    )

    print(f"Updated the trust policy for role: {role_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Login to SignalFx API, create integration, and update IAM trust policy.')
    parser.add_argument('--email', help='Your email address')
    parser.add_argument('--password', help='Your password')
    parser.add_argument('--orgId', help='Your organization ID')
    parser.add_argument('--realm', help='The realm of your SignalFx account')
    parser.add_argument('--name', help='Name for the integration')
    parser.add_argument('--namedToken', help='Named token for the integration')
    parser.add_argument('--regions', nargs='+', help='Regions for the integration')
    parser.add_argument('--sfxAwsAccountArn', help='SignalFx AWS account ARN')
    parser.add_argument('--roleArn', help='IAM role ARN to update trust policy')
    parser.add_argument('--defaultExternalId', help='Default External ID to replace in the trust policy')

    args = parser.parse_args()

    email = args.email or os.getenv('O11Y_EMAIL')
    password = args.password or os.getenv('O11Y_PASSWORD')
    orgId = args.orgId or os.getenv('O11Y_ORGID')
    realm = args.realm or os.getenv('O11Y_REALM')
    name = args.name or os.getenv('INTEGRATION_NAME')
    namedToken = args.namedToken or os.getenv('TOKEN_NAME')
    regions = args.regions or (os.getenv('REGIONS').split(',') if os.getenv('REGIONS') else None)
    sfxAwsAccountArn = args.sfxAwsAccountArn or os.getenv('SFX_AWS_ACCNT_ARN')
    roleArn = args.roleArn or os.getenv('ROLE_ARN')
    defaultExternalId = args.defaultExternalId or os.getenv('DEFAULT_EXTERNAL_ID')

    if not (email and password and orgId and realm and name and namedToken and regions and sfxAwsAccountArn and roleArn and defaultExternalId):
        raise ValueError("All parameters (either as arguments or environment variables) must be provided.")

    try:
        access_token = login(email, password, orgId, realm)
        integration_response = create_integration(
            realm, access_token, name, namedToken, regions, sfxAwsAccountArn
        )
        print(f"Integration Response: {json.dumps(integration_response, indent=2)}")

        new_external_id = integration_response.get("externalId")
        integration_id = integration_response.get("id")

        if new_external_id and integration_id:
            update_iam_trust_policy(roleArn, defaultExternalId, new_external_id)
        else:
            raise ValueError("Error: Missing externalId or id in the response.")
    
        if new_external_id and integration_id:
            with open('env_vars.sh', 'w') as env_file:
                env_file.write(f'export EXTERNAL_ID={new_external_id}\n')
                env_file.write(f'export INTEGRATION_ID={integration_id}\n')
            print(f"NEW_EXTERNAL_ID set to: {new_external_id}")
            print(f"INTEGRATION_ID set to: {integration_id}")
            print(f"Environment variables written to env_vars.sh")
        else:
            print("Error: Missing externalId or id in the response.")
        
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"An error occurred: {err}")
