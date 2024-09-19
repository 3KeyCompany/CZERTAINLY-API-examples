## This script implements a basic CZERTAINLY configuration including creating roles, groups, RA profile, Authorirites. 

from GroupsRolesInit import * 


## approve connectors
connectors = ["Common-Credential-Connector", "HashiCorp-Vault-Connector"] ## specify which connectors should be approve 
enableConnectors(connectors)

## Create Vault Authority
connectorVaultUuid = getConnectorUuid("HashiCorp-Vault-Connector") 
vaultAuthorityname = "API Vault CA" # specify Vault Authority name 
vaultURL = "https://katka2.3key.company:443" #specify url of Vault server
roleID = "37eb08f0-7534-6257-e748-8aa7af1fae83" # specify role ID for authorization (part of Vault app role )
roleSecret = "7c3b1d39-7e53-7e6e-4146-ee44a38e1887" # specify role Secret (part of Vault app role)

newVaultAuthority = createVaultAuthority(vaultAuthorityname, vaultURL, roleID, roleSecret, connectorVaultUuid)
authorityUuid = newVaultAuthority['uuid']


## Create Vault RA Profile ###############
vaultRaProfilename = "API Vault first" # specify Vault Authority name 
pkiEngine = "pki"  # enter pki engine name (from Vault server)
vaultRole = "first" # enter vault role (from Vault server)

newVaultRAProfile = createVaultRAProfile(vaultRaProfilename, authorityUuid, pkiEngine, vaultRole)
raProfileUuid = newVaultRAProfile['uuid']


# get Authority name
authorityDetail = getAuthorityDetail(authorityUuid) 
authorityName = authorityDetail['name']

# get RA profile name 
raProfileDetail = getRaProfileDetail (authorityUuid, raProfileUuid)
raProfileName = raProfileDetail['name']


## Create first role 
roleName = "RB" # specify name of a new role
role  = createRole(roleName)
roleUuid = role["uuid"]

resourceAuthorityUuid = getResourceUuid("authorities")
resourceRAProfileUuid = getResourceUuid("raProfiles")

## Give the role required permissions
editedRole = addRolesRBPermissions (roleUuid)
editedRole = addRolesRAProfiles(roleUuid, resourceRAProfileUuid, raProfileUuid, raProfileName)
editedRole = addRolesAuthorities(roleUuid, resourceAuthorityUuid, authorityUuid, authorityName)

## Create a Group (with the same name as for Role) 
groupName = roleName
groupEmail = "email@example.com" # enter the group email
createGroup (groupName, groupEmail)

## create ACME profile 
acmeProfileName = "APIACME"  ## specify name for ACME profile, cannot contain any spaces 
newAcmeProfile = createAcmeProfile(acmeProfileName)
acmeProfileUuid = newAcmeProfile["uuid"]

# activate ACME profile
activateAcmeProfile(acmeProfileUuid)

# activate ACME for RA Profile
activateAcmeforRaProfile(authorityUuid, raProfileUuid, acmeProfileUuid)


# # Create MS Authority

# create cerdentials
credentialConnectorUuid = getConnectorUuid("Common-Credential-Connector")

msCredentialsName = "API ms adcs" # specify name of the credentials
username = "czertainly-unpriv" # enter username of the given Windows user 
password = "password" # enter password of the given Windows user 

msCredentials = createBasicCredentials(msCredentialsName, username, password, credentialConnectorUuid)


# Create MS Authority instance 

pyadcsConnectorUuid = getConnectorUuid("PyADCS-Connector")

msAdcsName = "API MS ADCS" ## specify name of MS ADCS authority
msAdcsCredentialsUuid = msCredentials["uuid"]
https = True
msAdcsURL = "winlab01.3key.company" ## enter URL of Windows server with running MS ADCS 

msAuthority = createMsAuthority(msAdcsName, msAdcsURL, msAdcsCredentialsUuid, pyadcsConnectorUuid)