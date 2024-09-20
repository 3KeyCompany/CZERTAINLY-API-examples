## This script includes API to retrieve Keycloak access token and import Identity Provider configuration 
import requests
import json

## URL of CZERTAINLY instance that we want to configure
api_url_base = "https://katka1.3key.company/"

## using username and password retrieve Keycloak admin access token (token is required for another APIs)
def getAuthenticationToken(username, password):
    api_url = api_url_base + "kc/realms/master/protocol/openid-connect/token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = 'username=' + username + '&password=' + password + '&grant_type=password&client_id=admin-cli'
    res = requests.post(api_url, headers=headers, data = payload)
    r_json = res.json()
    return(r_json)



## import Identity Provider configuration, for authorization provide admin access token 
def createIdentityProviderInstance(accessToken,IDPconfig):
    api_url = api_url_base + "kc/admin/realms/CZERTAINLY/identity-provider/instances"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {accessToken}'}
    res = requests.post(api_url, headers=headers, data = IDPconfig)
    print("Creating Identity Provider,..", res)
    return(res)


#################### main ####################################################################################

## provide admin username and password to authorize to keycloak and retrieve admin access token
username = "username"
password = "password"
accessToken = getAuthenticationToken(username, password)['access_token']


## specify Identity Provider configuration in JSON format
## To export Identity Provider configuration from another running KeyCloak we can:
    # 1. login to KeyCloak as admin
    # 2. Change Realm to CZERTAINLY !!!
    # 3. Go to Realm Settings in the Menu 
    # 4. At the right top click on Actions and choose Partially export
    # 5. In the obtained JSON file find the section Identity Provider and copy the required
    
## This is an example of SAML identity provider, configured at KeyCloak running at https://katka1.3key.company/kc/     

#################################################################################################################
config = {"postBindingLogout": "true",
        "singleLogoutServiceUrl": "https://winlab01.3key.company/adfs/ls/",
        "postBindingResponse": "true",
        "backchannelSupported": "false",
        "xmlSigKeyInfoKeyNameTransformer": "CERT_SUBJECT",
        "idpEntityId": "http://winlab01.3key.company/adfs/services/trust", 
        "loginHint": "false",
        "allowCreate": "true",
        "authnContextComparisonType": "exact",
        "syncMode": "IMPORT",
        "singleSignOnServiceUrl": "https://winlab01.3key.company/adfs/ls/",
        "wantAuthnRequestsSigned": "true",
        "allowedClockSkew": "30",
        "validateSignature": "false",
        "hideOnLoginPage": "false",
        "nameIDPolicyFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:WindowsDomainQualifiedName",
        "entityId": "https://katka1.3key.company/kc/realms/CZERTAINLY", 
        "signSpMetadata": "false",
        "wantAssertionsEncrypted": "false",
        "signatureAlgorithm": "RSA_SHA256",
        "sendClientIdOnLogout": "false",
        "wantAssertionsSigned": "false",
        "sendIdTokenOnLogout": "true",
        "postBindingAuthnRequest": "true",
        "forceAuthn": "false",
        "attributeConsumingServiceIndex": "0",
        "principalType": "Subject NameID"
      }
payload = json.dumps({
  "alias": "adfs-idp-alias", ## change this to specify identity provider alias, alias must be unique, without any spaces
  "displayName": "AD FS", ## change this to specify identity provider display name
  "providerId": "saml",
  "enabled": True,
  "updateProfileFirstLoginMode": "on",
  "trustEmail": False,
  "storeToken": False,
  "addReadTokenRoleOnCreate": False,
  "authenticateByDefault": False,
  "linkOnly": False,
  "config" : config})

#################################################################################################################

## import Identity Provider configuration
IDPconfig = payload
newIDP = createIdentityProviderInstance(accessToken, IDPconfig)