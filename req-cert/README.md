# req-cert.py

Script to demonstrate how to request via CZERTAINLY API.

```
./req-cert.py -h
usage: req-cert.py [-h] --URL URL --cert CERT --key KEY --CA CA --RA_profile RA_PROFILE --csr CSR --out OUT [--insecure] [--verbose]

req-cert.py: an example how to use API to request certificate through CZERTAINLY

options:
  -h, --help            show this help message and exit
  --URL URL             URL where CZERTAINLY is running (default: https://czertainly.local)
  --cert CERT           PEM file with admin certificate for CZERTAINLY instance
  --key KEY             PEM file with key for admin certificate for CZERTAINLY instance
  --CA CA               Name of CA registered in CZERTAINLY instance
  --RA_profile RA_PROFILE
                        RA profile of CA registered in CZERTAINLY instance
  --csr CSR             PEM file Certificate Signing Request
  --out OUT             Where to store the certificate
  --insecure            disable certificate validation (default: False)
  --verbose             be verbose (default: False)
```

Create CSR:
```
openssl req -new -nodes -keyout key.pem -out csr.pem -config openssl.conf
```

Performance testing:
```
time seq 100 200 | parallel -j 10 python3 req-cert.py --URL https://demo.czertainly.online --cert ~/3K/client1.pem --key ~/3K/client1.key --CA ejbca.3key.company  --RA_profile ejbca-tls --csr csr.pem  --out "out/cert_{}.pem"

real  2m44.266s
user  0m28.506s
sys	  0m3.009s
```
Above tries to issue 10 certificates in parallel. Totaly 100 certificates were issued in 164seconds.