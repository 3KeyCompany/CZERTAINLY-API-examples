#!/usr/bin/env python3

import argparse
import base64
import json
import time
import requests
import urllib3
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

TIMEOUT=30
AUTHORITIES = '/api/v1/authorities'
RAPROFILES = '/api/v1/raProfiles'
OPERATIONS_AUTHORITIES = '/api/v2/operations/authorities/'
CERTIFICATE = '/api/v1/certificates'
HEADERS = {'Accept': 'application/json'}

def load_csr(
        file_path: str
) -> int:
    """Load CSR file."""
    with open(file_path, 'r', encoding="utf-8") as file:
        csr = file.read().strip()

    return csr

def get_ca_uuid(config, name):
    """Function to get CA UID based on it's name."""
    url = f"{config.URL}/{AUTHORITIES}"

    res = requests.get(url, timeout=TIMEOUT,
                       headers=HEADERS, cert=(config.cert, config.key),
                       verify=not config.insecure)

    if res.status_code == 200:
        data = res.json()
        for item in data:
            if item.get("name") == name:
                return item.get("uuid")

    return None  # If not found or request failed

def get_ra_profile_uuid(config, ca_uuid, name):
    """Function to get RA Profile UID based on it's name."""
    url = f"{config.URL}/{RAPROFILES}"

    res = requests.get(url, timeout=TIMEOUT,
                       headers=HEADERS, cert=(config.cert, config.key),
                       verify=not config.insecure)

    if res.status_code == 200:
        data = res.json()

        for item in data:
            if item.get("authorityInstanceUuid") == ca_uuid and item.get("name") == name:
                return item.get("uuid")

    return None  # If not found or request failed

# https://docs.czertainly.com/api/core-client-operations
# /api/v2/operations/authorities/{authorityUuid}/raProfiles/{raProfileUuid}/certificates
def request_certificate(config, ca_uuid, ra_profile_uuid, csr_b64):
    """Function to request certificate."""
    url = f"{config.URL}{OPERATIONS_AUTHORITIES}{ca_uuid}/raProfiles/{ra_profile_uuid}/certificates"

    body = {
        "format": "pkcs10",
        "request": csr_b64
    }

    res = requests.post(url, timeout=TIMEOUT,
                        headers=HEADERS, cert=(config.cert, config.key),
                        verify=not config.insecure, json=body)

    if res.status_code == 200:
        data = res.json()
        return data.get("uuid")
    else:
        print(f"Error: {res.status_code} - {res.text}")
        return None

# https://docs.czertainly.com/api/core-certificate#tag/Certificate-Inventory/operation/downloadCertificate
def get_certificate(config, crt_uuid, max_retries=100, retry_delay=0.2):
    """Function to get certificate."""
    url = f"{config.URL}/{CERTIFICATE}/{crt_uuid}/raw"

    attempt = 0
    while attempt < max_retries:
        res = requests.get(url, timeout=TIMEOUT,
                           headers=HEADERS, cert=(config.cert, config.key),
                           verify=not config.insecure,
                           params = { 'encoding': 'pem' })

        if res.status_code == 200:
            data = res.json()

            return data.get("content")
        elif res.status_code == 422:
            if config.verbose:
                print(f"Received 422, retrying in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})")
            time.sleep(retry_delay)
            attempt += 1
        else:
            print(f"Error: received status code {res.status_code} - {res.text}")
            break

    print(f"Error: {res.status_code} - {res.text}")
    return None  # If not found or request failed

def show_certificate_info(pem_data: str):
    # Ensure PEM is bytes
    cert = x509.load_pem_x509_certificate(pem_data.encode('utf-8'), default_backend())

    print(f"Issuer: {cert.issuer.rfc4514_string()}")
    print(f"Subject: {cert.subject.rfc4514_string()}")
    print(f"Serial Number: {cert.serial_number}")
    print(f"Not Before: {cert.not_valid_before}")
    print(f"Not After:  {cert.not_valid_after}")
    print(f"Signature Algorithm: {cert.signature_algorithm_oid._name}")
    print(f"Public Key Algorithm: {cert.public_key().__class__.__name__}")

def main():
    """Main."""
    parser = argparse.ArgumentParser(
        description="req-cert.py: an example how to use API to request "
                    "certificate through CZERTAINLY")

    parser.add_argument('--URL', required=True, default='https://czertainly.local',
                        help='URL where CZERTAINLY is running  (default: %(default)s)' )
    parser.add_argument('--cert', required=True,
                        help='PEM file with admin certificate for CZERTAINLY instance' )
    parser.add_argument('--key', required=True,
                        help='PEM file with key for admin certificate for CZERTAINLY instance' )
    parser.add_argument('--CA', required=True,
                        help='Name of CA registered in CZERTAINLY instance' )
    parser.add_argument('--RA_profile', required=True,
                        help='RA profile of CA registered in CZERTAINLY instance')
    parser.add_argument('--csr', required=True,
                        help='PEM file Certificate Signing Request' )
    parser.add_argument('--out', required=True,
                        help='Where to store the certificate' )
    parser.add_argument('--insecure', action='store_true', default=False,
                        help='disable certificate validation (default: %(default)s)')
    parser.add_argument('--verbose', action='store_true', default=False,
                        help='be verbose (default: %(default)s)')

    args = parser.parse_args()

    if args.insecure:
        urllib3.disable_warnings()

    csr = load_csr(args.csr)
    csr_b64 = base64.b64encode(csr.encode('utf-8')).decode('utf-8')

    if args.verbose:
        print(f"loading: {args.csr}")
        print(f"CSR: {csr_b64}")

    ca_uuid = get_ca_uuid(args, args.CA)
    if ca_uuid is None:
        print(f"CA with name \"{args.CA}\" not found")
        exit(1)
    if args.verbose:
        print(f"CA named \"{args.CA}\" has UUID: {ca_uuid}")

    ra_profile_uuid = get_ra_profile_uuid(args, ca_uuid, args.RA_profile)
    if ra_profile_uuid is None:
        print(f"RA Profile with name \"{args.RA_profile}\" not found")
        exit(1)
    if args.verbose:
        print(f"RA Profile profile named \"{args.RA_profile}\" has UUID: {ra_profile_uuid}")

    crt_uuid = request_certificate (args, ca_uuid, ra_profile_uuid, csr_b64)
    if crt_uuid is None:
        print(f"Certificate request failed")
        exit(1)
    if args.verbose:
        print(f"Requested certificate got UUID: {crt_uuid}")

    cert = get_certificate(args, crt_uuid)
    if cert is None:
        print(f"Certificate download failed")
        exit(1)
    cert_pem = base64.b64decode(cert.encode('utf-8')).decode('utf-8')
    if args.verbose:
        show_certificate_info(cert_pem)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(cert_pem)


if __name__ == "__main__":
    main()