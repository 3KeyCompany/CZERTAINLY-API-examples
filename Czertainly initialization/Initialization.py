## This script implements a basic CZERTAINLY configuration including approving connectors, creating roles with specifiv permission, groups, RA profile and Authorirites. 

##### Authorization ###################################

# Provide the authorization information in Authorization.py file.

######## Configuration ################################
#In this section, provide your configuration parameters, including the names of new objects, URLs, and other required attributes from the external system.

## Approve connectors
connectors = ["Common-Credential-Connector", "HashiCorp-Vault-Connector","PyADCS-Connector"] ## specify which connectors should be approve 

## Vault authority 
vaultAuthorityname = "API-Vault-CA" # specify Vault Authority name 
vaultURL = "https://katka2.3key.company:443" #specify url of Vault server
roleID = "37eb08f0-7534-6257-e748-8aa7af1fae83" # specify role ID for authorization (part of Vault app role )
roleSecret = "7c3b1d39-7e53-7e6e-4146-ee44a38e1887" # specify role Secret (part of Vault app role)

## Vault RA Profile ###############
vaultRaProfilename = "API-Vault-first" # specify Vault Authority name 
pkiEngine = "pki"  # enter pki engine name (from Vault server)
vaultRole = "first" # enter vault role (from Vault server)

## New role 
roleName = "API-role" # specify name of a new role

## New Group 
groupName = roleName ## the group be identical to Role name, you can change it
groupEmail = "email@example.com" # enter the group email


## ACME profile 
acmeProfileName = "API-ACME"  ## specify name for ACME profile, cannot contain any spaces 

##MS ADCS Authority

# cerdentials
msCredentialsName = "API-ms-adcs" # specify name of the credentials
username = "czertainly-unpriv" # enter username of the given Windows user 
password = "password" # enter password of the given Windows user 

# MS Authority instance 
msAdcsName = "API-MS-ADCS" ## specify name of MS ADCS authority
msAdcsURL = "winlab01.3key.company" ## enter URL of Windows server with running MS ADCS 

### Important Note: the certificate of CA (MS ADCS certification authority) issuing  the server certificate for winrm must be added in values.yaml in the trusted-certificate section 



# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# This part of script includes calling functions implemented in CzertainlyAPIs.py. Please do not make any changes here.

from CzertainlyAPIs import * 

## approve connectors
enableConnectors(connectors)

## Create Vault Authority
connectorVaultUuid = getConnectorUuid("HashiCorp-Vault-Connector") 
callback = VaultCallback(connectorVaultUuid)

newVaultAuthority = createVaultAuthority(vaultAuthorityname, vaultURL, roleID, roleSecret, connectorVaultUuid)
authorityUuid = newVaultAuthority['uuid']


## Create Vault RA Profile
newVaultRAProfile = createVaultRAProfile(vaultRaProfilename, authorityUuid, pkiEngine, vaultRole)
raProfileUuid = newVaultRAProfile['uuid']


# get Authority name
authorityDetail = getAuthorityDetail(authorityUuid) 
authorityName = authorityDetail['name']

# get RA profile name 
raProfileDetail = getRaProfileDetail (authorityUuid, raProfileUuid)
raProfileName = raProfileDetail['name']


## Create the first role 
role  = createRole(roleName)
roleUuid = role["uuid"]

resourceAuthorityUuid = getResourceUuid("authorities")
resourceRAProfileUuid = getResourceUuid("raProfiles")

## Give the role required permissions
editedRole = addRolesRBPermissions (roleUuid)
editedRole = addRolesRAProfiles(roleUuid, resourceRAProfileUuid, raProfileUuid, raProfileName)
editedRole = addRolesAuthorities(roleUuid, resourceAuthorityUuid, authorityUuid, authorityName)

## Create a Group (with the same name as for Role) 
createGroup (groupName, groupEmail)

## create ACME profile 
newAcmeProfile = createAcmeProfile(acmeProfileName)
acmeProfileUuid = newAcmeProfile["uuid"]

# activate ACME profile
activateAcmeProfile(acmeProfileUuid)

# activate ACME for RA Profile

activateAcmeforRaProfile(authorityUuid, raProfileUuid, acmeProfileUuid)


# Create MS Authority

# create cerdentials
credentialConnectorUuid = getConnectorUuid("Common-Credential-Connector")
msCredentials = createBasicCredentials(msCredentialsName, username, password, credentialConnectorUuid)

## Create MS Authority instance 
pyadcsConnectorUuid = getConnectorUuid("PyADCS-Connector")
msAdcsCredentialsUuid = msCredentials["uuid"]
https = True

msAuthority = createMsAuthority(msAdcsName, msAdcsURL, msAdcsCredentialsUuid, pyadcsConnectorUuid)