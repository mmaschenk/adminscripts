from botocore.credentials import create_credential_resolver
from botocore.credentials import SSOTokenLoader

import sys
import os
import copy

profile = os.getenv("AWS_PROFILE", "masterpayer-readonly")
region = os.getenv("AWS_REGION", "eu-west-1")

class SimpleCache(object):
    def __init__(self, retriever) -> None:
        self.retrievlambda = retriever
        self.cache = {}

    def get(self, key):
        if key not in self.cache:
            self.cache[key] = self.retrievlambda(key)
        return self.cache[key]

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

def getinstanceandidstore(session):
    ssoadmin = session.client('sso-admin')
    li = ssoadmin.list_instances()

    return li['Instances'][0]['InstanceArn'], li['Instances'][0]['IdentityStoreId']

def analyzeaccount(session, account, usercache, groupcache, permissioncache, policycache):
    idstore = session.client('identitystore')
    ssoadmin = session.client('sso-admin')
    li = ssoadmin.list_instances()
    instancearn = li['Instances'][0]['InstanceArn']
    idstoreid = li['Instances'][0]['IdentityStoreId']

    ps = ssoadmin.list_permission_sets_provisioned_to_account(InstanceArn=instancearn, AccountId=account['Id'])

    account['permissions'] = {}
    for permission in ps['PermissionSets']:
        psinfo = copy.copy(permissioncache.get(permission))
        account['permissions'][psinfo['Name']] = psinfo
        policies = policycache.get(permission)
        psinfo['policies'] = policies
        psinfo['users'] = []
        psinfo['groups'] = []
        psinfo['unknownassignment'] = []
        aa = ssoadmin.list_account_assignments(
            InstanceArn=instancearn, 
            AccountId=account['Id'],
            PermissionSetArn=permission)
        for assignment in aa['AccountAssignments']:
            if assignment['PrincipalType'] == 'USER':
                userinfo = usercache.get(assignment['PrincipalId'])
                psinfo['users'].append(userinfo)
            elif assignment['PrincipalType'] == 'GROUP':
                groupinfo = groupcache.get(assignment['PrincipalId'])
                psinfo['groups'].append(groupinfo)
            else:
                psinfo['unknownassignment'].append(assignment)
    return account

def analyzeaccounts(session, silent=False, maxentries=-1):
    idstore = session.client('identitystore')
    all_accounts = sorted(allaccounts(session), key=lambda x: x['Name'].lower())
    ssoadmin = session.client('sso-admin')

    instancearn, idstoreid = getinstanceandidstore(session)

    userlookup = lambda userid: idstore.describe_user(IdentityStoreId=idstoreid, UserId=userid)
    grouplookup = lambda groupid: idstore.describe_group(IdentityStoreId=idstoreid, GroupId=groupid)
    permissionlookup = lambda permission: ssoadmin.describe_permission_set(InstanceArn=instancearn, PermissionSetArn=permission)['PermissionSet']
    policylookup = lambda permission: ssoadmin.list_managed_policies_in_permission_set(InstanceArn=instancearn, PermissionSetArn=permission)['AttachedManagedPolicies']
    usercache = SimpleCache(userlookup)
    groupcache = SimpleCache(grouplookup)
    permissioncache = SimpleCache(permissionlookup)
    policycache = SimpleCache(policylookup)
    accountdata = []

    i = 0 ;
    for account in all_accounts:
        if not silent:
            print(f"\r{i}/{len(all_accounts)}", end='', flush=True, file=sys.stderr)
        acdata = analyzeaccount(session, account, usercache=usercache, groupcache=groupcache, permissioncache=permissioncache, policycache=policycache)
        accountdata.append(acdata)
        i += 1
        if i == maxentries:
            break

    print(f"\r\033[K", flush=True, file=sys.stderr)
    return accountdata

if __name__ == "__main__":
    print(f"Please don't run this module directly", file=sys.stderr)
    