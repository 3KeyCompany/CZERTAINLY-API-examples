import ldap3

# source
# https://gist.github.com/anilpai/01f1bda55d0d2fe0efa45cd668c00fc6


class Ldap:
    def __init__(self, server_uri, ldap_user, ldap_password):
        self.server = ldap3.Server(server_uri, get_info=ldap3.ALL)
        self.conn = ldap3.Connection(self.server, user=ldap_user, password=ldap_password, auto_bind=True)
        print(self.conn)
    def who_am_i(self):
        return self.conn.extend.standard.who_am_i()
    
    
    def get_groups(self):
        self.conn.search('ou=Groups,dc=winlab,dc=3key,dc=company', '(objectclass=group)', attributes=[ 'cn','objectclass','mail'])
        return self.conn.entries
    
    def get_members(self):
        self.conn.search('OU=Users,OU=Development,OU=Slany,DC=winlab,DC=3key,DC=company','(objectclass=person)')
        return self.conn.entries


############ 

LDAP_URI = "ldap://winlab01.3key.company"
password = "your-password"
username = "cn=your-user,cn=Users,dc=winlab,dc=3key,dc=company"


ldap = Ldap(LDAP_URI, username, password)
if ldap:
    print('User authenticated. Welcome {0}'.format(ldap.who_am_i()))
 

ldap_groups = []
for group in ldap.get_groups():
    ldap_groups.append({"name": group.cn.value, "email" : group.mail.value})





