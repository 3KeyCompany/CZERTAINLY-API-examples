import os
import shutil
import requests
import json
import base64
import time
import sys
import argparse
from urllib.parse import quote
from cryptography import x509
from cryptography.hazmat.primitives import serialization

# this is ugly, but I'm testing with several instances of CZERTAINLY and adding trust new and new selfsing cert is boring
import urllib3
urllib3.disable_warnings()


czertainly_hostname = 'https://czertainly12.local'

certificates_upload_uri  = '/api/v1/certificates/upload'
certificates_update_uri  = '/api/v1/certificates'
certificates_details_uri = '/api/v1/certificates'

admin_cert_file = '/home/semik/3K/admin.pem'
admin_key_file = '/home/semik/3K/admin.key'
headers = {'Accept': 'application/json'}
max_certs = 250000-131746

trusted_certs = [
    '/usr/share/ca-certificates/mozilla',
    '/usr/local/share/ca-certificates'
    '/home/semik/3K/trusted-certs'
]

def certificate_upload(PEM):
    url = czertainly_hostname + certificates_upload_uri
    body = {
               'certificate': PEM
    }

    res = requests.post(url,
                          headers=headers, cert=(admin_cert_file, admin_key_file),
                          verify=False, json = body)
    return(res)

def certificate_set_trusted(uuid):
    url = czertainly_hostname + certificates_update_uri + "/" + uuid
    body = {
        'trustedCa': True
    }

    res = requests.patch(url,
                        headers=headers, cert=(admin_cert_file, admin_key_file),
                        verify=False, json = body)
    return(res)

def certificate_validate(uuid):
    url = czertainly_hostname + certificates_details_uri + "/" + uuid + "/validate"

    res = requests.get(url,
                       headers=headers, cert=(admin_cert_file, admin_key_file),
                       verify=False)
    return(res)

def certificate_get_details(uuid):
    url = czertainly_hostname + certificates_details_uri + "/" + uuid

    res = requests.get(url,
                       headers=headers, cert=(admin_cert_file, admin_key_file),
                       verify=False)
    return(res)

def upload_certificate(PEM:str, trusted:bool):
    r = certificate_upload(PEM)

    if (r.status_code == 201):
        print(" ^", flush=True, end="")
        # 201 successful upload
        # or maybe already present but we want to be sure it is trusted
        if trusted:
            uuid = r.json()['uuid']
            r = certificate_set_trusted(uuid)
            if r.status_code == 204:
                print(" trusted", flush=True, end="")
                # Succesffuly set as trusted.
                # To get setting efective we need get details to force CZERTAINLY revalidate cert.
                r = certificate_validate(uuid)
                if r.status_code == 200:
                    print(' ' + str(r.json()['resultStatus']), end="")
                    r = certificate_get_details(uuid)
                    if r.status_code == 200:
                        return 2
                    else:
                        return 7
                else:
                    return 6
            elif (r.status_code == 504) and ("Gateway Time-out" in str(r.text)):
                return 5
            else:
                raise Exception("Failed to set certificate as trusted: " + str(r.text))
        return 1
    elif (r.status_code == 400) and ("already exists" in str(r.text)):
        # certificate is already present in CZERTAINLY, it would be nice to be sure it is also trusted ...
        return 3
    elif (r.status_code == 504) and ("Gateway Time-out" in str(r.text)):
        # it would be nice to retry, but I'm to lazy begginer
        return 4
    else:
        raise Exception("Failed to upload certificate: " + str(r.text))

def load_CTlog_file(file_path:str):
    cnt = 0
    with open(file_path, 'r') as file:
        for line in file:
            # Remove whitespace and newlines, then split by comma
            elements = line.strip().split(',')

            cert = elements[3]
            # hostnames from certificate are 5th element and they are separated by space
            name = elements[4].strip().split(' ')[0]

            res = upload_certificate(cert, False)
            if res < 3:
                cnt += 1

    return cnt

parser = argparse.ArgumentParser(description="upload-certs.py an example how to use API to upload certificates into CZERTAINLY")

parser.add_argument('mode', choices=['importPEM', 'importCTlog'], help="Mode of operation")
parser.add_argument('files', nargs='+', help="List of files")
parser.add_argument('--trusted', action='store_true', help="Mark the import as trusted")

args = parser.parse_args()

# for stats
start_time = time.time()
cnt=0

if args.mode == 'importPEM':
    for file in args.files:
        print(f"loading: {file}", end="")

        cert_file = open(file, 'rb')
        pem = cert_file.read()
        certificate = x509.load_pem_x509_certificate(pem)
        certificate_bytes = certificate.public_bytes(serialization.Encoding.DER)
        base64_encoded_cert = base64.b64encode(certificate_bytes).decode('utf-8')
        res = upload_certificate(base64_encoded_cert, args.trusted)
        cnt += 1 if res < 3 else 0
        print(' ' + str(res))
elif args.mode == 'importCTlog':
    for file in args.files:
        print(f"loading: {file}", flush=True, end="")

        add = load_CTlog_file(file)
        print(' loaded certs: ' + str(add))
        cnt += add
        duration = time.time() - start_time
        speed = cnt / duration if duration > 0 else 0
        print(f'Uploaded certs = {cnt}, avg speed = {speed:.2f} certs/sec')

duration = time.time() - start_time
speed = cnt / duration if duration > 0 else 0
print(f'Total uploaded certs = {cnt}, avg speed = {speed:.2f} certs/sec')
