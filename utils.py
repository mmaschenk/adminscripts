from botocore.credentials import create_credential_resolver
from botocore.credentials import SSOTokenLoader


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

def accessibleaccountsandroles(session):
    ssoclient = session.client('sso')
    accesstoken = getaccesstoken(session)

    li = ssoclient.list_accounts(accessToken=accesstoken);
    accounts = li['accountList']
    for account in accounts:
        rli = ssoclient.list_account_roles(accessToken=accesstoken, accountId=account['accountId'])        
        roles = rli['roleList']
        account['roles'] = roles
    return accounts

def allaccounts(session):
    orgs = session.client('organizations')
    la = orgs.list_accounts()
    accounts = la['Accounts']
    return accounts