
import os
import requests
import json
import argparse

def login(email, password, orgId, realm):
    url = f"https://api.{realm}.signalfx.com/v2/session"
    headers = {"Content-Type": "application/json"}
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

def update_integration(realm, token, integration_id, name, namedToken, regions, sfxAwsAccountArn, new_external_id, roleArn):
    url = f"https://api.{realm}.signalfx.com/v2/integration/{integration_id}"
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
        "roleArn": roleArn,
        "sfxAwsAccountArn": sfxAwsAccountArn,
        "externalId": new_external_id
    }
    
    # Debugging: Print the request details
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    response = requests.put(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()
        
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
    parser.add_argument('--new_external_id', help='New External ID')
    parser.add_argument('--integration_id', help='Integration ID')

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
    
    new_external_id = args.new_external_id or os.getenv('EXTERNAL_ID')
    integration_id = args.integration_id or os.getenv('INTEGRATION_ID')
    
    try:
        # Login to SignalFx
        access_token = login(email, password, orgId, realm)
        
        if new_external_id and integration_id:
            
            # Debugging: Print the values
            print(f"realm: {realm}")
            print(f"access_token: {access_token}")
            print(f"integration_id: {integration_id}")
            print(f"name: {name}")
            print(f"namedToken: {namedToken}")
            print(f"regions: {regions}")
            print(f"sfxAwsAccountArn: {sfxAwsAccountArn}")
            print(f"new_external_id: {new_external_id}")
            print(f"roleArn: {roleArn}")
            
            # Update the integration with the new external ID
            updated_integration_response = update_integration(
                realm, access_token, integration_id, name, namedToken, regions, sfxAwsAccountArn, new_external_id, roleArn
            )
            print(f"Updated Integration Response: {json.dumps(updated_integration_response, indent=2)}")
        else:
            raise ValueError("Error: Missing externalId or id in the response.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")