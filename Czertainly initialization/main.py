from ldap import ldap_groups
from GroupsRolesInit import * 

czertainly_groups = []
for group in listGroup():
    czertainly_groups.append({"name": group['name'],"email": group['email']})

czertainly_group_names = [item['name'] for item in czertainly_groups]
czertainly_group_emails = [item['email'] for item in czertainly_groups]



## add ldap group, edit ldap group email 

for ldap_group in ldap_groups:
    group_name = ldap_group['name']
    group_email = ldap_group['email']

    if group_name in czertainly_group_names:
        czertainly_group_email = czertainly_group_emails[czertainly_group_names.index(group_name)]
        if group_email != czertainly_group_email:
            print("new email", group_email)
            editobject = editObject(group_name,group_email)
    else:
        print("new group", group_name)
        newobject = createObject (group_name, group_email)
    
## removing of redundant groups (the groups is in CZERTAINLY but not in LDAP)
ldap_groups_names = [item['name'] for item in ldap_groups]
     
for czertainly_group in [item['name'] for item in czertainly_groups]:
    if czertainly_group not in ldap_groups_names:
        print("group to remove", czertainly_group)
        deleteobject = deleteObject(czertainly_group)
     
     
     
## delete owner for all certificates      
deleteCertificateOwner(listCertificatesUuids())     