import boto3

import utils

session = boto3.Session(profile_name='masterpayer-readonly', region_name='eu-west-1')

print(session)
s3 = session.resource('s3')
sts = session.client('sts')

print(sts.get_caller_identity())

ssoadminclient = session.client('sso-admin')
ssoclient = session.client('sso')

for bucket in s3.buckets.all():
    print(bucket.name)

def showaccessibleaccountsandroles():

    accounts = utils.accessibleaccountsandroles(session)
    for account in accounts:
        print(f"{account['accountName']:40} {account['accountId']} {account['emailAddress']}")
        roles = account['roles']
        for role in roles:
            print(f"\t {role['roleName']}")

def showallaccounts(session):
    accounts = utils.allaccounts(session)
    for account in accounts:
        print(f"{account['Name']:40} {account['Id']} {account['Status']} {account['JoinedMethod']} {account['Email']}")


def main():
    showaccessibleaccountsandroles()
    showallaccounts(session)
    

if __name__ == "__main__":
    main()