#!/usr/bin/python3

import argparse
import base64
import time
import requests
import urllib3
from cryptography import x509
from cryptography.hazmat.primitives import serialization

# this is ugly, but I'm testing with several instances of CZERTAINLY and
# adding trust new and new selfsing cert is boring


TIMEOUT=30
CERTIFICATES_UPLOAD_URI  = '/api/v1/certificates/upload'
CERTIFICATES_UPDATE_URI  = '/api/v1/certificates'
CERTIFICATES_DETAILS_URI = '/api/v1/certificates'
HEADERS = {'Accept': 'application/json'}

trusted_certs = [
    '/usr/share/ca-certificates/mozilla',
    '/usr/local/share/ca-certificates'
    '/home/semik/3K/trusted-certs'
]

def certificate_upload(config, PEM):
    """Function to upload certificate via API."""
    url = f"{config.URL}/{CERTIFICATES_UPLOAD_URI}"
    body = {
               'certificate': PEM
    }

    res = requests.post(url, timeout=TIMEOUT,
                        headers=HEADERS, cert=(config.cert, config.key),
                        verify=not config.insecure, json = body)
    return(res)

def certificate_set_trusted(config, uuid):
    """Function to set certificate identified by uuid as trusted."""
    url = f"{config.URL}/{CERTIFICATES_UPDATE_URI}/{uuid}"
    body = {
        'trustedCa': True
    }

    res = requests.patch(url, timeout=TIMEOUT,
                        headers=HEADERS, cert=(config.cert, config.key),
                        verify=not config.insecure, json = body)
    return(res)

def certificate_validate(config, uuid):
    """Function to actualy execute certificate validation, setting it as trusted is not enought."""
    url = f"{config.URL}/{CERTIFICATES_DETAILS_URI}/{uuid}/validate"

    res = requests.get(url, timeout=TIMEOUT,
                       headers=HEADERS, cert=(config.cert, config.key),
                       verify=not config.insecure)
    return(res)

def certificate_get_details(config, uuid):
    """Function to get certificate details in json structure."""
    url = f"{config.URL}/{CERTIFICATES_DETAILS_URI}/{uuid}"

    res = requests.get(url, timeout=TIMEOUT,
                       headers=HEADERS, cert=(config.cert, config.key),
                       verify=not config.insecure)
    return(res)

def upload_certificate(config, PEM:str):
    """Upload certificate in PEM format passed as simple string."""
    r = certificate_upload(config, PEM)

    if (r.status_code == 201):
        print(" ^", flush=True, end="")
        # 201 successful upload
        # or maybe already present but we want to be sure it is trusted
        if config.trusted:
            uuid = r.json()['uuid']
            r = certificate_set_trusted(config, uuid)
            if r.status_code == 204:
                print(" trusted", flush=True, end="")
                # Succesffuly set as trusted.
                # To get setting efective we need get details to force CZERTAINLY revalidate cert.
                r = certificate_validate(config, uuid)
                if r.status_code == 200:
                    print(' ' + str(r.json()['resultStatus']), end="")
                    return 2
                else:
                    return 6
            elif (r.status_code == 504) and ("Gateway Time-out" in str(r.text)):
                return 5
            else:
                raise Exception("Failed to set certificate as trusted: " + str(r.text))
        return 1
    elif (r.status_code == 400) and ("already exists" in str(r.text)):
        # certificate is already present in CZERTAINLY, it would be nice to be
        # sure it is also trusted ...
        return 3
    elif (r.status_code == 504) and ("Gateway Time-out" in str(r.text)):
        # it would be nice to retry, but I'm to lazy begginer
        return 4
    else:
        raise Exception("Failed to upload certificate: " + str(r.text))

def load_ctlog_file(
        config,
        file_path: str
) -> int:
    """Parse CT log file and upload all certificates one by one."""
    cnt = 0
    with open(file_path, 'r', encoding="utf-8") as file:
        for line in file:
            # Remove whitespace and newlines, then split by comma
            elements = line.strip().split(',')

            # certificate is 4th element of CSV log file
            cert = elements[3]

            res = upload_certificate(config, cert)
            if res < 3:
                cnt += 1

    return cnt

def main():
    """Main."""
    parser = argparse.ArgumentParser(
        description="upload-certs.py: an example how to use API to upload "
                    "certificates into CZERTAINLY")

    parser.add_argument('mode', choices=['importPEM', 'importCTlog'],
                        help="mode of operation")
    parser.add_argument('files', nargs='+',
                        help="list of files")
    parser.add_argument('--URL', required=True, default='https://czertainly.local',
                        help='URL where CZERTAINLY is running  (default: %(default)s)')
    parser.add_argument('--cert', required=True,
                        help='PEM file with admin certificate for CZERTAINLY instance' )
    parser.add_argument('--key', required=True,
                        help='PEM file with key for admin certificate for CZERTAINLY instance' )
    parser.add_argument('--trusted', action='store_true', default=False,
                        help='mark imported certificates as trusted, make no sense for end-entity certs (default: %(default)s)')
    parser.add_argument('--insecure', action='store_true', default=False,
                        help='disable certificate validation (default: %(default)s)')

    args = parser.parse_args()

    if args.insecure:
        urllib3.disable_warnings()

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
            res = upload_certificate(args, base64_encoded_cert)
            cnt += 1 if res < 3 else 0
            print(' ' + str(res))
    elif args.mode == 'importCTlog':
        for file in args.files:
            print(f"loading: {file}", flush=True, end="")

            add = load_ctlog_file(args, file)
            print(' loaded certs: ' + str(add))
            cnt += add
            duration = time.time() - start_time
            speed = cnt / duration if duration > 0 else 0
            print(f'Uploaded certs = {cnt}, avg speed = {speed:.2f} certs/sec')

    duration = time.time() - start_time
    speed = cnt / duration if duration > 0 else 0
    print(f'Total uploaded certs = {cnt}, avg speed = {speed:.2f} certs/sec')

if __name__ == "__main__":
    main()