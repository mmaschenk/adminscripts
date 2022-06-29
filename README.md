# Installation

It is recommended to do this install in a virtual environment:

```
% mkdir .venv
% virtualenv .venv
% . .venv/bin/activate
```

Install dependencies:

```
% pip -r requirements.txt
```

# Usage

The scripts build connections based on two environment variables:

### AWS_PROFILE
This holds the value of the configured aws cli profile for accessing your environment. If not defined it defaults to `masterpayer-readonly`

### AWS_REGION
This holds the value of the region your connection will point to. If not defined it defaults to `eu-west-1`

The following scripts are provided:

## accountaccess.py

This script provides an overview of all accounts in your organizations, and lists wether these
accounts are accessible through the current sso session. 
The script only works when your current session (`AWS_PROFILE`) is actually an sso based connection.

## accountanayzer.py

The script lists for all accounts in your organizations what permission sets are in place and
which user and/or groups have access. Please not that groups are not expanded to users in 
these groups as there is no AWS-published api available for listing members of groups :-(
