import os
import requests
import argparse

def login(email, password, orgId, realm):
    url = f"https://api.{realm}.signalfx.com/v2/session"
    headers = {"Content-Type": "application/json"}
    data = f'{{ "email": "{email}", "password": "{password}", "organizationId": "{orgId}" }}'
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get("accessToken")
    else:
        response.raise_for_status()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Login to SignalFx API and get access token.')
    parser.add_argument('--email', help='Your email address')
    parser.add_argument('--password', help='Your password')
    parser.add_argument('--orgId', help='Your organization ID')
    parser.add_argument('--realm', help='The realm of your SignalFx account')

    args = parser.parse_args()

    email = args.email or os.getenv('O11Y_EMAIL')
    password = args.password or os.getenv('O11Y_PASSWORD')
    orgId = args.orgId or os.getenv('O11Y_ORGID')
    realm = args.realm or os.getenv('O11Y_REALM')

    if not email or not password or not orgId or not realm:
        parser.error("All parameters must be provided either via command line arguments or environment variables.")

    try:
        access_token = login(email, password, orgId, realm)
        print(f"Access Token: {access_token}")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"An error occurred: {err}")
