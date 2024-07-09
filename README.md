# Splunk O11Y API Session Auth

## Introduction

Some example scripts that show how to use session auth to run Admin Level API commands with Splunk Observability Cloud

This example use case is based on the creation of an AWS Integration which is a three step process:

1. Create the Integration
2. Create or Update the Trust Relationship Policy in AWS (this example updates an existing policy)
3. Activate the integration created in step 1

## The Scripts

### 0_login_script.py

Simple script to test the session auth mechanism, will return a fresh token every time it is run

```cmd
python3 0_login_script.py
```

### 1_create_aws_integration_and_update_iam.py

This scripts creates the AWS Integration in Splunk O11Y Cloud, and updates the existing Trust Relationship Policy in the role specified by the ARN, replacing the 'DEFAULT_EXTERNAL_ID' with the new one generated

```cmd
python3 1_create_aws_integration_and_update_iam.py
```

### 2_update_aws_integration.py

This script updates the AWS Integration created by the 1st script

```cmd
python3 2_update_aws_integration.py
```

### Clean Up

The optional clean up script resets the Trust Relationship Policy and deletes the AWS Integration from Splunk O11Y Cloud

```cmd
python3 3_reset.py
```

## Env Vars

The following env variables can be exported

export O11Y_EMAIL=your e-mail

export O11Y_PASSWORD=your password

export O11Y_ORGID=your org id

export O11Y_REALM=your realm

export INTEGRATION_NAME=your integration name

export TOKEN_NAME=your token name

export REGIONS="eu-west-1,eu-west-3"

export SFX_AWS_ACCNT_ARN="arn:aws:iam::214014584948:root"

export ROLE_ARN=arn of your existing role

export DEFAULT_EXTERNAL_ID=ID in your existing role e.g. CHANGE_ME

## Run Time Vars

Alternatively you can pass in parameters at run time

```cmd
python3 0_login_script.py --email your_email@example.com --password your_password --orgId your_organization_id --realm your_realm
```

```cmd
python3 1_create_aws_integration_and_update_iam.py --email your_email@example.com --password your_password --orgId your_organization_id --realm your_realm --name "your_integraion_name" --namedToken "your_sfx_token_name" --regions "region-name-1" "region-name-2" --sfxAwsAccountArn "arn:aws:iam::214014584948:root" --aws_access_key_id your_aws_access_key_id --aws_secret_access_key your_aws_secret_access_key --roleArn "your_role_arn" --defaultExternalId "CHANGE_ME"
```

```cmd
python3 2_update_aws_integration.py --email your_email@example.com --password your_password --orgId your_organization_id --realm your_realm --name "API_Demo" --namedToken "your_sfx_token_name" --regions "eu-west-1" "eu-west-3" --sfxAwsAccountArn "arn:aws:iam::214014584948:root" --aws_access_key_id your_aws_access_key_id --aws_secret_access_key your_aws_secret_access_key --roleArn "your_role_arn"
```

```cmd
python3 3_reset.py --email your_email@example.com --password your_password --orgId your_organization_id --realm your_realm --roleArn "your_role_arn" --defaultExternalId "CHANGE_ME"
```