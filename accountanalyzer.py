
import boto3
import utils

def main():
    session = boto3.Session(profile_name='masterpayer', region_name='eu-west-1')

    data = utils.analyzeaccounts(session)

    for account in data:
        print(f"Account: {account['Name']} {account['Id']} ({account['Email']})")
        
        for permission in account['permissions'].keys():
            psinfo = account['permissions'][permission]
            print(f"  Permission: {psinfo['Name']} ({psinfo.get('Description','')})")

            print(f"    Policies: {','.join([p['Name'] for p in account['permissions'][permission]['policies']])}")
            if account['permissions'][permission]['users']:
                print(f"    Users: {','.join([u['UserName'] for u in account['permissions'][permission]['users']])}")
            if account['permissions'][permission]['groups']:
                print(f"    Groups: {','.join([g['DisplayName'] for g in account['permissions'][permission]['groups']])}")

        print()

if __name__ == "__main__":
    main()