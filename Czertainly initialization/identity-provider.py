import requests
import json

headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

api_url_base = "https://katka1.3key.company/"

def createAuthenticationToken(username, password):
    api_url = api_url_base + "kc/realms/master/protocol/openid-connect/token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = 'username=' + username + '&password=' + password + '&grant_type=password&client_id=admin-cli'
    res = requests.post(api_url, headers=headers, data = payload)
    print(res)
    r_json = res.json()
    return(r_json)


username = "admin"
password = "admin"
accessToken = createAuthenticationToken(username, password)['access_token']
print(accessToken)


def createIdentityProviderInstance(accessToken):
    api_url = api_url_base + "kc/admin/realms/CZERTAINLY/identity-provider/instances"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {accessToken}'}
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
      "alias": "adfs-idp-alias-6",
      "displayName": "AD FS 6",
      "providerId": "saml",
      "enabled": True,
      "updateProfileFirstLoginMode": "on",
      "trustEmail": False,
      "storeToken": False,
      "addReadTokenRoleOnCreate": False,
      "authenticateByDefault": False,
      "linkOnly": False,
      "config" : config})
    res = requests.post(api_url, headers=headers, data = payload)
    print(res)
    return(res)

newIDP = createIdentityProviderInstance(accessToken)
print(newIDP)
