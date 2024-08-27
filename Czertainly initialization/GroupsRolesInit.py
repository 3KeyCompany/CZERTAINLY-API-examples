# importing libraries
import requests
import json


headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
cert_file = "admin-czertainly-lab09.crt"
key_file = "admin-czertainly-lab09.key"
api_url_base = "https://katka1.3key.company/"


## init Authority and RA profile attributes - Authority and RA profile for issuing client certificates 
initAuthorityUuid = "8cfa857e-5d5f-4966-9bea-189477f3193a"
# initAuthorityUuid = None
initAuthorityName = "Vault CA"
initRAProfileUuid = "be8aa70c-5914-4ac2-8a3f-9be19132bee9"
initRAProfileName = "Vault profile first"

# RAProfileUuid = "be8aa70c-5914-4ac2-8a3f-9be19132bee9"
# RAProfileName = "Vault profile first"
# authorityUuid = "8cfa857e-5d5f-4966-9bea-189477f3193a"
# authorityName = "Vault CA"


# Function to get data from API
def get_RA_profiles():
    api_url = api_url_base + "/api/v1/raProfiles"
    res = requests.get(api_url, headers=headers, cert=(cert_file, key_file))
    r_json = res.json()
    return(r_json)


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
    return(r_json)



# Delete Role
def deleteRole(uuid):
    api_url = api_url_base + "/api/v1/roles"
    res = requests.delete(api_url + "/" + uuid, headers=headers, cert=(cert_file, key_file))
    return(res)

# Assign Permissions to Role ---------------------

# Get Role Permissions
def getRolePermissions(uuid):
    api_url = api_url_base + "/api/v1/roles"
    res = requests.get(api_url + "/" + uuid + "/permissions", headers=headers, cert=(cert_file, key_file))
    r_json = res.json()
    return(r_json)


## Add new authority and RA Profiles to Role (ted to nepotrebujeme)

def addRolesRAProfiles(roleUuid, resourcesUuid, RAProfileUuid, RAProfileName):
    api_url = api_url_base + "/api/v1/roles"
    data = {"uuid": RAProfileUuid, "name": RAProfileName, "allow": ["list", "detail"]}
    api_url = api_url + "/" + roleUuid + "/permissions/" + resourcesUuid + "/objects/" + RAProfileUuid
    res = requests.put(api_url , headers=headers, cert=(cert_file, key_file), json = data)
    return(res)



def addRolesAuthorities(roleUuid, resourcesUuid, authorityUuid, authorityName):
    api_url = api_url_base + "/api/v1/roles"
    data = {"uuid": authorityUuid, "name": authorityName, "allow": ["list", "detail"]}
    api_url = api_url + "/" + roleUuid + "/permissions/" + resourcesUuid + "/objects/" + authorityUuid
    res = requests.put(api_url , headers=headers, cert=(cert_file, key_file), json = data)
    return(res)





# -------------------------------------------------------------------------------------------------


# Add permissions to Role - zakladni nastaveni roli pro koncove uzivatele
## pristup k certifikatum, (pristup k vlastni grupe)

def addRolesCertificates(uuid): # add permissions to work with certificates
    api_url = api_url_base + "/api/v1/roles"
    certificates = {"name": "certificates","allowAllActions": True, "actions": [],"objects": []}
    resources = [certificates]
    data = {"allowAllResources": False, "resources": resources}
    res = requests.post(api_url + "/" + uuid + "/permissions", headers=headers, cert=(cert_file, key_file), json = data)
    r_json = res.json()
    return(r_json)


## RB intit configuration - rb_group_1 - intit users can do all operations with certificates and can initialize discovery (both for specific HashiCorp Vault CA)
## pridat do authorities 



def addRolesRBPermissions(uuid): # add permissions to work with certificates
    api_url = api_url_base + "/api/v1/roles"
    certificates = {"name": "certificates","allowAllActions": True, "actions": [],"objects": []}
    locations = {"name": "locations","allowAllActions": True, "actions": ["detail","list"],"objects": []}
    acmeAccounts = {"name": "acmeAccounts","allowAllActions": False, "actions": ["detail","list"],"objects": []}
    acmeProfiles = {"name": "acmeProfiles","allowAllActions": False, "actions": ["detail","list"],"objects": []}
    authorities = {"name": "authorities","allowAllActions": False, "actions": ["detail","list"],"objects": []}
    connectors = {"name": "connectors","allowAllActions": False, "actions": ["detail","list"],"objects": []}
    discoveries = {"name": "discoveries","allowAllActions": False, "actions": ["detail","list"],"objects": []}
    groups = {"name": "groups","allowAllActions": False, "actions": ["detail","list"],"objects": []}
    raProfiles = {"name": "raProfiles","allowAllActions": False, "actions": ["detail","list"],"objects": []}
    roles = {"name": "roles","allowAllActions": False, "actions": ["detail","list"],"objects": []}
    triggers = {"name": "triggers","allowAllActions": False, "actions": ["detail","list"],"objects": []}
    users = {"name": "users","allowAllActions": False, "actions": ["detail","list"],"objects": []}
    
    
    resources = [certificates, locations, acmeAccounts,acmeProfiles,authorities,connectors,discoveries,groups,raProfiles,roles,triggers,users]
    data = {"allowAllResources": False, "resources": resources}
    res = requests.post(api_url + "/" + uuid + "/permissions", headers=headers, cert=(cert_file, key_file), json = data)
    r_json = res.json()
    return(r_json)


RAProfileUuid = "be8aa70c-5914-4ac2-8a3f-9be19132bee9"
RAProfileName = "Vault profile first"
authorityUuid = "8cfa857e-5d5f-4966-9bea-189477f3193a"
authorityName = "Vault CA"
resourceAuthorityUuid = "b8e2bda3-c791-4641-bc0d-8a68315692cc"
resourceRAProfileUuid = "0d504c55-b76f-4259-a051-9d8b853dfa33"


## Add new authority and RA Profiles to Role (ted to nepotrebujeme)

def addRolesRAProfiles(roleUuid, resourceRAProfileUuid, RAProfileUuid, RAProfileName):
    api_url = api_url_base + "/api/v1/roles"
    data = [{"uuid": RAProfileUuid, "name": RAProfileName, "allow": ["list", "detail", "delete"]}]
    api_url = api_url + "/" + roleUuid + "/permissions/" + resourceRAProfileUuid + "/objects" 
    res = requests.post(api_url , headers=headers, cert=(cert_file, key_file), json = data)
    return(res)



def addRolesAuthorities(roleUuid, resourceAuthorityUuid, authorityUuid, authorityName):
    api_url = api_url_base + "/api/v1/roles"
    data = [{"uuid": authorityUuid, "name": authorityName, "allow": ["list", "detail", "delete"]}]
    api_url = api_url + "/" + roleUuid + "/permissions/" + resourceAuthorityUuid + "/objects" 
    res = requests.post(api_url , headers=headers, cert=(cert_file, key_file), json = data)
    return(res)



# def addRolesRBAuthorities(roleUuid):
#     api_url = api_url_base + "/api/v1/roles"
#     authoritiesObjects = [{"uuid": authorityuUid, "name": authorityName,  "allow": ["detail","list"]}]
#     RAProfilesObjects = [{"uuid": RAProifleUuid ,"name": authorityName , "allow": ["detail","list"]}]
    
#     authorities = {"name": "authorities",  "allowAllActions": False, "actions": [], "objects": authoritiesObjects}
#     RAProfiles = {"name": "raProfiles",  "allowAllActions": False, "actions": [], "objects": RAProfilesObjects}
#     certificates = {"name": "certificates","allowAllActions": True, "actions": [],"objects": []}
#     resources = [authorities]
   
#     data = {"allowAllResources": False, "resources": resources}
#     res = requests.post(api_url + "/" + roleUuid + "/permissions/" + resourceAuthorityUuid + "/objects" , headers=headers, cert=(cert_file, key_file), json = data)
#     r_json = res.json()
#     return(r_json)

## Create Autohority

# def createAuthority(type, name):
#     if type == "vault":
#       name  = "name"
#       connectorUuid="c6d0352a-346d-4f6b-bc41-9a113eab97a5"
#       kind="HVault"
      


#----------------------------------------------------------------------------------

# List Group

def listGroup():
    api_url = api_url_base + "/api/v1/groups"
    res = requests.get(api_url, headers=headers, cert=(cert_file, key_file))
    r_json = res.json()
    return(r_json)

# Create Group (s emailem)
def createGroup(name, email):
    api_url = api_url_base + "/api/v1/groups"
    data = { "name": name, "email": email}
    res = requests.post(api_url, headers=headers, cert=(cert_file, key_file), json = data)
    r_json = res.json()
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



# Create object (new role, new group)

# based on name and email create group and role
def createObject(name, email):
    role  = createRole(name)
    uuid = role["uuid"]
    addRolesCertificates (uuid)
    if (initAuthorityUuid and initRAProfileUuid != None):
        resourcesAuthorityUuid = "b8e2bda3-c791-4641-bc0d-8a68315692cc"
        resourcesRAProfileUuid = "0d504c55-b76f-4259-a051-9d8b853dfa33"
        addRolesAuthorities(uuid, resourcesAuthorityUuid, initAuthorityUuid, initAuthorityName)
        addRolesRAProfiles (uuid, resourcesRAProfileUuid, initRAProfileUuid, initRAProfileName)
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

    

################## RB init configuration ##################### 

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


# a = getResources()
# print (a)

# b = getObjectOfResources()
# print (b)

## main



role  = createRole("RB")
print("role", role)
roleUuid = role["uuid"]

RAProfileUuid = "be8aa70c-5914-4ac2-8a3f-9be19132bee9"
RAProfileName = "Vault profile first"
authorityUuid = "8cfa857e-5d5f-4966-9bea-189477f3193a"
authorityName = "Vault CA"
resourceAuthorityUuid = "b8e2bda3-c791-4641-bc0d-8a68315692cc"
resourceRAProfileUuid = "0d504c55-b76f-4259-a051-9d8b853dfa33"

editedRole = addRolesRBPermissions (roleUuid)
editedRole = addRolesRAProfiles(roleUuid, resourceRAProfileUuid, RAProfileUuid, RAProfileName)
editedRole = addRolesAuthorities(roleUuid, resourceAuthorityUuid, authorityUuid, authorityName)


