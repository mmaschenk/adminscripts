
"""
This script lists the accessibility of all accounts in all organizations by the account that is currently logged in.
The currently logged in user needs to have read access to ogranizational accounts.
It is assumed the currently logged in user has logged in through sso.
"""

import boto3
import utils

def main():
    session = boto3.Session(profile_name='masterpayer-readonly', region_name='eu-west-1')
    xs_accounts = utils.accessibleaccountsandroles(session)
    all_accounts = sorted(utils.allaccounts(session), key=lambda x: x['Name'].lower())

    xs = { account['accountId'] : account for account in xs_accounts }

    for account in all_accounts:
        if account['Id'] in xs:
            xsmessage = f"acessible through: {','.join([ role['roleName'] for role in xs[account['Id']]['roles'] ])}"
        else:
            xsmessage = 'INACCESSIBLE'
        print(f"{account['Name']:40} {account['Id']} {xsmessage}")

if __name__ == "__main__":
    main()