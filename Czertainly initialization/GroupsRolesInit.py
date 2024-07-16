# importing libraries
import requests
import json


headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
cert_file = "admin-czertainly-lab09.crt"
key_file = "admin-czertainly-lab09.key"
api_url_base = "https://czertainly.3key.company"


## init Authority and RA profile attributes - Authority and RA profile for issuing client certificates 
initAuthorityUuid = "29ff8e25-7529-4f72-b16f-61ea61e10508"
# initAuthorityUuid = None
initAuthorityName = "MS ADCS https"
initRAProfileUuid = "5c358df9-f421-4970-91ed-782f88d5dcd8"
initRAProfileName = "client-certificate"


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

# Assign attributes to Role ---------------------

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


# def addRolesAuthorities(roleUuid, AuthoritiesUuid):
#     api_url = "https://demo.czertainly.online/api/v1/roles"
#     headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
#     authoritiesObjects = {"uuid": "ce66c2fe-37c3-4bbe-9fbc-c20102ec5108", "name": "lab02-ADCS-https",  "allow": ["detail","list"]}
#     # authoritiesObjects = [{"uuid": "d1976e01-712b-4816-a120-8dd5c3f464a8", "name": "ejbca.3key.company",  "allow": ["detail","list"]}]

#     # RAProfilesObjects = [{"uuid": "d1fac75d-0c58-4331-ac40-944a76b73029","name": "RB-Team2", "allow": ["detail","list"]}]
#     # authorities = {"name": "authorities",  "allowAllActions": False, "actions": [], "objects": authoritiesObjects}
#     # RAProfiles = {"name": "raProfiles",  "allowAllActions": False, "actions": [], "objects": RAProfilesObjects}
#     certificates = {"name": "certificates","allowAllActions": True, "actions": [],"objects": []}
#     resources = [authoritiesObjects]
   
#     data = {"allowAllResources": False, "resources": resources}
#     res = requests.post(api_url + "/" + roleUuid + "/permissions/" + AuthoritiesUuid + "/objects" , headers=headers, cert=(cert_file, key_file), json = data)
#     r_json = res.json()
#     return(r_json)


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

    


