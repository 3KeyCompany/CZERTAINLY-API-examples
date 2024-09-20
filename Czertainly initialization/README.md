This set of scripts demonstrates an initial setup of CZERTAINLY access control and synchronizes the list of CZERTAINLY user groups with user groups in LDAP.


## LdapGroups.py

The purpose of this script is to connect to the LDAP server and retrieve a list of all user groups designated for synchronization with CZERTAINLY.

It includes a class `Ldap`, which handles the connection to the LDAP server and user authentication.

Upon successful authentication, the script allows searching for any objects of type `GROUP`. 

The class `Ldap` includes three functions:
| Function | 	 Description |
| -------- |  ---------------|
|  init | Setting the LDAP URI and connecting to the LDAP server by a dedicated user|
| who_am_i | Get information about the authenticated user
| get_groups | From LDAP get all objects of type GROUP - specifically group name and email


## GroupsRolesInit.py

This scripts includes API for working with CZERTAINLY - roles, groups, RA Profile and Authorities management.

Both **Initialization.py** and **DatabaseSync.py** scripts include references to **GroupsRolesInit.py**.

## Initialization.py 

This script implements a basic CZERTAINLY configuration including approving connectors, creating roles with specifiv permission, groups, RA profile and Authorirites. 

## DatabaseSync.py

This script is used to synchronize data from LDAP and data in CZERTAINLY. 
The synchronization includes: 

- The script checks whether a new group appears in LDAP, and then the groups are added to CZERTAINLY.
- The script checks whether all emails in LDAP correspond to group emails in CZERTAINLY. In case of any changes in LDAP, the change will be reflected in CZERTAINLY.
- The script checks if there are any redundant groups in CZERTAINLY compared to LDAP. The redundant groups will be removed. 

## identityProvider.py

This script includes API to retrieve Keycloak access token and import Identity Provider configuration. 

The function **getAuthenticationToken** gets username and password retrieve Keycloak admin access token.
The function **createIdentityProviderInstance** imports Identity Provider configuration, for authorization admin access token is provided.
