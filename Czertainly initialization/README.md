This set of scripts demonstrates an initial setup of CZERTAINLY access control and how to synchronize the list of CZERTAINLY user groups with user groups in LDAP.

## ldap.py

The purpose is to connect to the LDAP server and load a list of all dedicated user groups that we want to synchronize with CZERTAINLY.

This script includes a class `Ldap` used for connection to the LDAP server with user authentication. 

In case of successful authentication to LDAP we can search any object of type GROUP. 

The class `Ldap` includes three functions:
| Function | 	 Description |
| -------- |  ---------------|
|  init | Setting the LDAP URI and connecting to the LDAP server by a dedicated user|
| who_am_i | Get information about the authenticated user
| get_groups | From LDAP get all objects of type GROUP - specifically group name and email


## GroupsRolesInit.py

GroupsRolesInit.py includes functions of CZERTAINLY APIs used for Group, Ra Profile, and Roles management.



## main.py 
This script is used to synchronize data from LDAP and data in CZERTAINLY. 
The synchronization includes: 

- The script checks whether a new group appears in LDAP, and then the groups are added to CZERTAINLY.
- The script checks whether all emails in LDAP correspond to group emails in CZERTAINLY. In case of any changes in LDAP, the change will be reflected in CZERTAINLY.
- The script checks if there are any redundant groups in CZERTAINLY compared to LDAP. The redundant groups will be removed. 
