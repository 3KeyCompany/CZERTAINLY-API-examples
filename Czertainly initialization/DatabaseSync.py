## This script implements a synchronization between LDAP and CZERTAINLY database - specifically CZERTAINLY groups and roles regarding to data in LDAP  

from LdapGroups import ldap_groups
from GroupsRolesInit import * 

## reading existing groups in CZERTAINLY
czertainly_groups = []
for group in listGroup():
    czertainly_groups.append({"name": group['name'],"email": group['email']})

czertainly_group_names = [item['name'] for item in czertainly_groups]
czertainly_group_emails = [item['email'] for item in czertainly_groups]



## synchronization between LDAP and CZERTAINLY database
# if a new group appears in LDAP then the group is added to CZERTAINLY. 
# if a group email has been changed in LDAP then the group email is edited in CZERTAINLY
# if some group has been deleted from LDAP then the group is deleted CZERTAINLY


for ldap_group in ldap_groups:
    group_name = ldap_group['name']
    group_email = ldap_group['email']

    if group_name in czertainly_group_names:
        czertainly_group_email = czertainly_group_emails[czertainly_group_names.index(group_name)]
        if group_email != czertainly_group_email: ## LDAP contains different (new) email
            print("new email", group_email)
            editobject = editObject(group_name,group_email)
    else:
        print("new group", group_name)  ## LDAP contains a new groups
        newobject = createObject (group_name, group_email)
    
## removing of redundant groups (the groups are in CZERTAINLY but not in LDAP)
ldap_groups_names = [item['name'] for item in ldap_groups]
     
for czertainly_group in [item['name'] for item in czertainly_groups]:
    if czertainly_group not in ldap_groups_names:
        print("group to remove", czertainly_group)
        deleteobject = deleteObject(czertainly_group)
     
      
## delete owner for all certificates      
deleteCertificateOwner(listCertificatesUuids())     