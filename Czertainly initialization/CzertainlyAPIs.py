## This scripts includes API for working with CZERTAINLY - roles, groups management and RA Profile, Authorities management 

# importing libraries
import requests
import json
import uuid


headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

################ Authorization ############################################
cert_file = "client1.crt" # Specify certificates for CZERTAINLY authentication
key_file = "client1.key"

api_url_base = "https://katka4.3key.company/" # Specify CZERTAINLY URL

# cert_file = "admin-czertainly-lab09.crt"
# key_file = "admin-czertainly-lab09.key"
# api_url_base = "https://katka1.3key.company/"


################ Connectors ############################################
def listConnectors():
    api_url = api_url_base + "/api/v1/connectors"
    res = requests.get(api_url, headers=headers, cert=(cert_file, key_file))
    r_json = res.json()
    return(r_json)

def getConnectorUuid(connectorName):
    for connector in listConnectors():
        if connectorName == connector["name"]:
            return(connector["uuid"])

def approveConnector(connectorUuid):
    api_url = api_url_base + "/api/v1/connectors/" + connectorUuid + "/approve"
    res = requests.put(api_url, headers=headers, cert=(cert_file, key_file))
    return(res)

def enableConnectors(listOfConnectorsToApprove):
    for connector in listConnectors():
        if connector["name"] in listOfConnectorsToApprove:
            res = approveConnector(connector["uuid"])
            print("Approving Connector ", connector["name"], res)
              


################ Roles ################################################
# List Roles
def listRoles():
    api_url = api_url_base + "/api/v1/roles"
    res = requests.get(api_url , headers=headers, cert=(cert_file, key_file))
    r_json = res.json()
    return(r_json)

# Create Role
def createRole(name):
    api_url = api_url_base + "/api/v1/roles"
    data = { "name": name}
    res = requests.post(api_url, headers=headers, cert=(cert_file, key_file), json = data)
    r_json = res.json()
    print("Creating Role...", res)
    return(r_json)


# Delete Role
def deleteRole(uuid):
    api_url = api_url_base + "/api/v1/roles"
    res = requests.delete(api_url + "/" + uuid, headers=headers, cert=(cert_file, key_file))
    return(res)

############### Roles Permissions ##########################################

# Get Role Permissions
def getRolePermissions(uuid):
    api_url = api_url_base + "/api/v1/roles"
    res = requests.get(api_url + "/" + uuid + "/permissions", headers=headers, cert=(cert_file, key_file))
    r_json = res.json()
    return(r_json)


# Add working with certificate to Role permissions

def addRolesCertificates(uuid): # add permissions to work with certificates
    api_url = api_url_base + "/api/v1/roles"
    certificates = {"name": "certificates","allowAllActions": True, "actions": [],"objects": []}
    resources = [certificates]
    data = {"allowAllResources": False, "resources": resources}
    res = requests.post(api_url + "/" + uuid + "/permissions", headers=headers, cert=(cert_file, key_file), json = data)
    r_json = res.json()
    return(r_json)



# Add initialized role permissions including:
## working with certificates
## working with acme 
## working with ra profiles
## working with authorities

## Note: Most of permissions are read and list only. These permissions allow basic CZERTAINLY functions for CZERTAINLY users (not CZERTAINLY admins).

def addRolesRBPermissions(uuid):
    api_url = api_url_base + "/api/v1/roles"
    certificates = {"name": "certificates","allowAllActions": True, "actions": [],"objects": []}
    locations = {"name": "locations","allowAllActions": False, "actions": ["detail","list"],"objects": []}
    acmeAccounts = {"name": "acmeAccounts","allowAllActions": False, "actions": ["detail","list"],"objects": []}
    acmeProfiles = {"name": "acmeProfiles","allowAllActions": False, "actions": ["detail","list"],"objects": []}
    approvalProfiles = {"name": "approvalProfiles","allowAllActions": False, "actions": ["detail","list"],"objects": []}
    authorities = {"name": "authorities","allowAllActions": False, "actions": ["list"],"objects": []}
    attributes = {"name": "attributes","allowAllActions": False, "actions": ["detail","list", "members"],"objects": []}
    connectors = {"name": "connectors","allowAllActions": False, "actions": ["detail","list"],"objects": []}
    discoveries = {"name": "discoveries","allowAllActions": False, "actions": ["detail","list"],"objects": []}
    groups = {"name": "groups","allowAllActions": False, "actions": ["detail","list","members"],"objects": []}
    raProfiles = {"name": "raProfiles","allowAllActions": False, "actions": ["list"],"objects": []}
    roles = {"name": "roles","allowAllActions": False, "actions": ["detail","list"],"objects": []}
    triggers = {"name": "triggers","allowAllActions": False, "actions": ["detail","list"],"objects": []}
    users = {"name": "users","allowAllActions": False, "actions": ["detail","list"],"objects": []}
    complianceProfiles = {"name": "complianceProfiles","allowAllActions": False, "actions": ["detail","list"],"objects": []}
    credentials  = {"name": "credentials","allowAllActions": False, "actions": ["detail","list"],"objects": []}
    discoveries = {"name": "discoveries","allowAllActions": True, "actions": [],"objects": []}
    roles = {"name": "roles","allowAllActions": False, "actions": ["list"],"objects": []}
    triggers = {"name": "triggers","allowAllActions": False, "actions": ["detail","list"],"objects": []}
        
    resources = [certificates, locations, acmeAccounts,acmeProfiles,approvalProfiles,authorities,attributes,connectors,complianceProfiles,credentials,discoveries,groups,raProfiles,roles,triggers,users]
    data = {"allowAllResources": False, "resources": resources}
    res = requests.post(api_url + "/" + uuid + "/permissions", headers=headers, cert=(cert_file, key_file), json = data)
    r_json = res.json()
    print("Adding roles permissions...", res)
    return(r_json)


## Add new authority and RA Profiles to Role permissions

def addRolesRAProfiles(roleUuid, resourceRAProfileUuid, RAProfileUuid, RAProfileName):
    api_url = api_url_base + "/api/v1/roles"
    data = [{"uuid": RAProfileUuid, "name": RAProfileName, "allow": ["list", "detail"]}]
    api_url = api_url + "/" + roleUuid + "/permissions/" + resourceRAProfileUuid + "/objects" 
    res = requests.post(api_url , headers=headers, cert=(cert_file, key_file), json = data)
    print("Adding RA Profiles permissions...", res)
    return(res)


def addRolesAuthorities(roleUuid, resourceAuthorityUuid, authorityUuid, authorityName):
    api_url = api_url_base + "/api/v1/roles"
    data = [{"uuid": authorityUuid, "name": authorityName, "allow": ["list", "detail", "members"]}]
    api_url = api_url + "/" + roleUuid + "/permissions/" + resourceAuthorityUuid + "/objects" 
    res = requests.post(api_url , headers=headers, cert=(cert_file, key_file), json = data)
    print("Adding Authorities permissions...", res)
    return(res)



############ Create Authority #####################################################

# Create HashiCorp Vault CA

def createVaultAuthority(name , vaultURL, roleID, roleSecret, connectorUUid):
    authorityValue = [{"data": vaultURL}]
    authority_url = {"uuid": "8a68156a-d1f5-4322-b2a5-26e872a6fc0e", "name": "authority_url", "label": "Vault URL", "type": "data", "contentType": "string", "content": authorityValue}
    roleIdValue = [{"data": roleID}]
    role_id = { "uuid": "97a46e73-bf7d-421d-ae5a-2d0f453eb300","name": "role_id", "label": "Role ID", "type": "data", "contentType": "string", "content": roleIdValue}
    credentialsTypeValue =  [{"reference": "AppRole","data": "approle"}]
    credentials_type = {"uuid": "85197836-2ceb-4e77-b14e-53d2e9761cfc","name": "credentials_type","label": "Authentication method","type": "data", "contentType": "string","content": credentialsTypeValue}
    roleSecretValue = [{"data": roleSecret}]
    role_secret = { "uuid": "60daa99e-5b08-4f36-8f51-d136ecba74e9","name": "role_secret","label": "Role Secret","type": "data","contentType": "string","content": roleSecretValue}
    attributes = [authority_url, role_id, credentials_type, role_secret]
    kind = "HVault"
    data = { "name": name, "attributes": attributes, "connectorUuid": connectorUUid,"kind": kind}
    api_url = api_url_base + "/api/v1/authorities"
    res = requests.post(api_url, headers=headers, cert=(cert_file, key_file), json = data)
    r_json = res.json()
    print("Creating Vault Authority...",res)
    return(r_json)  

# Create MS ADCS Authority

def createMsAuthority(name , msAdcsURL,  credentialsUuid, connectorUUid):
    authority_winrm_port_Value = [{"data": 5986}]
    authority_winrm_port = {"uuid": "079f9f93-adc0-48bd-96f1-095991295cb9", "name": "authority_winrm_port", "label": "WinRM Port", "type": "data", "contentType": "integer", "content": authority_winrm_port_Value}
    
    authority_use_https_Value = [{"data": True}]
    authority_use_https = { "uuid": "645d3690-b460-43e7-94c9-9374cf5f14b3","name": "authority_use_https", "label": "Use HTTPS", "type": "data", "contentType": "boolean", "content": authority_use_https_Value}
    
    authority_credential_type_Value =  [{"reference": "Basic","data": "Basic"}]
    authority_credential_type = {"uuid": "e05beb6a-90fe-4f85-bd9f-2394d70a0a29","name": "authority_credential_type","label": "Credential Type","type": "data", "contentType": "string","content": authority_credential_type_Value}
    
    authority_credential_Value = [{"data": {"uuid": credentialsUuid}}]
    authority_credential = { "uuid": "93d77f65-d9c4-497c-bdee-f3330eb0f209","name": "authority_credential","label": "Credential","type": "data","contentType": "credential","content": authority_credential_Value}
    
    authority_winrm_transport_Value = [{ "reference": "CredSSP", "data": "credssp"}]
    authority_winrm_transport = { "uuid": "06cf66eb-5c1e-4edf-8308-617565a5d6b4","name": "authority_winrm_transport", "label": "WinRM Transport", "type": "data", "contentType": "string", "content": authority_winrm_transport_Value}
    
    authority_server_address_Value = [{ "data": msAdcsURL}]
    authority_server_address = { "uuid": "f2ee713a-c7cf-4b27-ae91-a84606b4877a","name": "authority_server_address", "label": "ADCS server address", "type": "data", "contentType": "string", "content": authority_server_address_Value}

    attributes = [authority_winrm_port, authority_use_https, authority_credential_type, authority_credential, authority_winrm_transport, authority_server_address]
    kind = "PyADCS-WinRM"
    data = { "name": name, "attributes": attributes, "connectorUuid": connectorUUid,"kind": kind}
    api_url = api_url_base + "/api/v1/authorities"
    res = requests.post(api_url, headers=headers, cert=(cert_file, key_file), json = data)
    r_json = res.json()
    print("Creating MS ADCS Authority...",res)
    return(r_json)  


      
      
############### Create RA Profile ############################################
## create RA profile for HashiCorp Vault CA 

def createVaultRAProfile(name, authorityUuid, pkiEngine, vaultRole):
    authorityInstanceUuid = authorityUuid
    raProfileRoleValue = [{"reference": vaultRole,"data": vaultRole}]
    ra_profile_role = {"uuid": "389dfa3c-cf45-458e-bca4-507d11b2858c","name": "ra_profile_role", "label": "Role", "type": "data", "contentType": "string", "content": raProfileRoleValue}
    raProfileEngineValue = [{ "reference": pkiEngine, "data": { "engineName": pkiEngine}}]
    ra_profile_engine = {"uuid": "e7817459-41cf-40d4-ad3d-9808ef14cad7","name": "ra_profile_engine", "label": "PKI secret engine", "type": "data", "contentType": "object", "content": raProfileEngineValue}
    raProfileAuthorityValue = [{ "data": "Vault CA"}]
    ra_profile_authority = {"uuid": "5af5693a-74bf-4ec4-b101-44ce35d8455b","name": "ra_profile_authority","label": "Authority UUID","type": "data","contentType": "string","content": raProfileAuthorityValue}
    attributes = [ra_profile_role, ra_profile_engine, ra_profile_authority]
    data = { "name": name, "authorityInstanceUuid": authorityInstanceUuid, "attributes": attributes, "enabled" : True}
    api_url = api_url_base + "/api/v1/authorities/" + authorityUuid + "/raProfiles"
    res = requests.post(api_url, headers=headers, cert=(cert_file, key_file), json = data)
    r_json = res.json()
    print("Creating Vault RA profile...",res)
    return(r_json)  
   

########################### Groups ##############################

# List Group

def listGroup():
    
    api_url = api_url_base + "/api/v1/groups"
    res = requests.get(api_url, headers=headers, cert=(cert_file, key_file))
    r_json = res.json()
    return(r_json)

# Create Group (with email)
def createGroup(name, email):
    api_url = api_url_base + "/api/v1/groups"
    data = { "name": name, "email": email}
    res = requests.post(api_url, headers=headers, cert=(cert_file, key_file), json = data)
    r_json = res.json()
    print("Creating Group...",res)
    return(r_json)

# Delete Group
def deleteGroup(uuid):
    api_url = api_url_base + "/api/v1/groups"
    res = requests.delete(api_url + "/" + uuid, headers=headers, cert=(cert_file, key_file))
    return(res)


# Update Group - jiny email
def editGroup(name, email, uuid):
    api_url = api_url_base + "/api/v1/groups"
    data = { "name": name, "email": email}
    res = requests.put(api_url + "/" + uuid, headers=headers, cert=(cert_file, key_file), json = data)
    r_json = res.json()
    return(r_json)


############### Create, Edit, Delete object (role, group) ############################

## Note: these APIs are used in DatabaseSync.py script

# based on name and email create group and role
def createObject(name, email):
    role  = createRole(name)
    uuid = role["uuid"]
    addRolesCertificates (uuid)
    createGroup (name, email)


# based on group name edit group email
def editObject(name, email):
    allgroups = listGroup()
    for group in allgroups:
      if  group["name"] == name:
        uuid = 	group["uuid"]
        editGroup(name, email, uuid)


# based on name delete group and role
def deleteObject(name):
    allgroups = listGroup()
    for group in allgroups:
        if group["name"] == name:
            groupuuid = group["uuid"]
    allroles = listRoles()
    for role in allroles:
        if role["name"] == name:
            roleuuid = role["uuid"]
    deleteGroup(groupuuid)        
    deleteRole(roleuuid)



# Delete certificate owner - the change will be applied to all certificates in the inventory

# List all certificates UUIDs
def listCertificatesUuids():
    api_url = api_url_base + "/api/v1/certificates"
    res = requests.post(api_url , headers=headers, cert=(cert_file, key_file),json = {"itemsPerPage": 100, "pageNumber": 1}) ## only first 100 certiifcates will be listed!!!!!!
    r_json = res.json()
    uuids = [cert['uuid'] for cert in r_json['certificates']]
    return(uuids)



def deleteCertificateOwner(certUuids):
    api_url =  api_url_base + "/api/v1/certificates"
    data = { "ownerUuid": "", "certificateUuids": certUuids}
    res = requests.patch(api_url , headers=headers, cert=(cert_file, key_file), json = data)
    return(res)

    

################## Resources, Objects ##################### 

def getResources(): # Get list of resources (acmeAcocounts, authorites, raprofiles) with their permissions (detail, list, delete ,...)
    api_url = api_url_base + "api/v1/auth/resources"
    res = requests.get(api_url, headers=headers, cert=(cert_file, key_file))
    r_json = res.json()
    return(r_json)

def getObjectOfResources(): # Get objects (ejbca, msadcs,..) of the resources (authority) 
    api_url = api_url_base + "api/v1/auth/resources/authorities/objects"
    res = requests.get(api_url, headers=headers, cert=(cert_file, key_file))
    r_json = res.json()
    return(r_json)

def getResourceUuid(resource): # Get Uuid of the resources (authority) 
    for rsc in getResources():
        if rsc["name"] == resource:
            return (rsc["uuid"])
    
    api_url = api_url_base + "api/v1/auth/resources/authorities/objects"
    res = requests.get(api_url, headers=headers, cert=(cert_file, key_file))
    r_json = res.json()
    return(r_json)

################# Credentials #################################

def createBasicCredentials (name, username, password, connectorUUid ):
    api_url = api_url_base + "api/v1/credentials"
    usernameValue = [{ "data": username}]
    usernameAttribute = {"uuid": "fe2d6d35-fb3d-4ea0-9f0b-7e39be93beeb","name": "username","label": "Username","type": "data","contentType": "string","content": usernameValue}
    passwordValue = [{ "data": password}]
    passwordAttribute = {"uuid": "04506d45-c865-4ddc-b6fc-117ee5d5c8e7","name": "password","label": "Password","type": "data","contentType": "secret","content": passwordValue}
    attributes = [usernameAttribute, passwordAttribute]
    data = { "name": name, "kind": "Basic", "attributes": attributes, "connectorUuid": connectorUUid}
    res = requests.post(api_url, headers=headers, cert=(cert_file, key_file), json = data)
    print("Creating Basic Credentials...",res)
    r_json = res.json()
    return(r_json)
    


################# RA profile, Authority details ###############

def getRaProfileDetail(authorityUuid, raProfileUuid): 
    api_url = api_url_base + "api/v1/authorities/" + authorityUuid + "/raProfiles/" + raProfileUuid
    res = requests.get(api_url, headers=headers, cert=(cert_file, key_file))
    r_json = res.json()
    return(r_json)


def getAuthorityDetail(authorityUuid): 
    api_url = api_url_base + "api/v1/authorities/" + authorityUuid
    res = requests.get(api_url, headers=headers, cert=(cert_file, key_file))
    r_json = res.json()
    return(r_json)


def activateAcmeforRaProfile (authorityUuid, raProfileUuid, acmeProfileUuid):
    api_url = api_url_base + "api/v1/authorities/" + authorityUuid + "/raProfiles/" + raProfileUuid + "/protocols/acme/activate/" + acmeProfileUuid
    data = { "issueCertificateAttributes": [], "revokeCertificateAttributes": []}
    res = requests.patch(api_url , headers=headers, cert=(cert_file, key_file), json = data)
    print("Activating ACME for RA profile...",res)
    return(res)

################### ACME Profile ##################################

def createAcmeProfile(name):
    api_url = api_url_base + "api/v1/acmeProfiles"
    data = { "name": name,  "enabled": True}
    res = requests.post(api_url, headers=headers, cert=(cert_file, key_file), json = data)
    print("Creating ACME Profile...",res)
    r_json = res.json()
    return(r_json)

def activateAcmeProfile(acmeProfileUuid):
    api_url = api_url_base + "api/v1/acmeProfiles/" + acmeProfileUuid + "/enable"
    res = requests.patch(api_url, headers=headers, cert=(cert_file, key_file))
    print("Activating ACME profile...",res)
    return(res)


