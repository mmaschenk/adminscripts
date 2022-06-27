import boto3

from botocore.credentials import create_credential_resolver
from botocore.credentials import SSOTokenLoader

print("Here we go")


def getaccesstoken(session):
    """
    Retrieve the actual accesstoken from the cached sso connection. This assumes that the provided session is sso-authenticated and
    will use that session's startUrl to find the token (all configs that share this startUrl are accessible using this accesstoken)
    """
    coresession = session._session
    credentialprovider = create_credential_resolver(coresession).get_provider('sso')
    credentialprovider.load()
    authenticationconfig = credentialprovider._load_sso_config()
    tokenloader = SSOTokenLoader(cache=credentialprovider._token_cache)
    return tokenloader(authenticationconfig['sso_start_url'])
    

session = boto3.Session(profile_name='playground', region_name='eu-west-1')

print(session)
#boto3.setup_default_session(profile_name='playground')
s3 = session.resource('s3')

sts = session.client('sts')

print(sts.get_caller_identity())

ssoadminclient = session.client('sso-admin')

ssoclient = session.client('sso')


for bucket in s3.buckets.all():
    print(bucket.name)

accesstoken = getaccesstoken(session)
print(accesstoken)
print(type(accesstoken))

li = ssoclient.list_accounts(accessToken=accesstoken);

accounts = li['accountList']
#print (li['accountList'])

for account in accounts:
    print(account)

    rli = ssoclient.list_account_roles(accessToken=accesstoken, accountId=account['accountId'])
    roles = rli['roleList']
    #print(roles)

    for role in roles:
        print('\t',role)