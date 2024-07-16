# upload-certs.py

Script to demonstrate uploading certificates via API call. It supports uploading
single PEM formatted certificates or uploading CT log files, which are CSV formatted.

Usage:
```
./upload-certs/upload-certs.py -h
usage: upload-certs.py [-h] --URL URL --cert CERT --key KEY [--trusted] [--insecure] {importPEM,importCTlog} files [files ...]

upload-certs.py an example how to use API to upload certificates into CZERTAINLY

positional arguments:
  {importPEM,importCTlog}
                        mode of operation
  files                 list of files

options:
  -h, --help            show this help message and exit
  --URL URL             URL where CZERTAINLY is running (default: https://czertainly.local)
  --cert CERT           PEM file with admin certificate for CZERTAINLY instance
  --key KEY             PEM file with key for admin certificate for CZERTAINLY instance
  --trusted             mark imported certificates as trusted, make no sense for end-entity certs (default: False)
  --insecure            disable certificate validation (default: False)
```

## Upload a single PEM file

Upload one CA in PEM file and mark it trusted (`--trusted` switch). I'm also using `--insecure` switch to ignore

```
./upload-certs/upload-certs.py importPEM --trusted \
    --URL https://czertainly12.local/ --insecure \
    --cert ~/3K/admin.pem --key ~/3K/admin.key \
    /usr/local/share/ca-certificates/SemikRootCA.crt
loading: /usr/local/share/ca-certificates/SemikRootCA.crt ^ trusted valid 2
Total uploaded certs = 1, avg speed = 2.95 certs/sec
```

`^` in output means that cert was uploaded\
`trusted` that it was marked as trusted\
`valid` that it was validated and CZERTAINT should now trust it\
`[0-9]` is return from function `upload_certificate` (1, 2) means it was uploaded, 3 already presented (trust unchecked), more some errors

## Upload trusted PEM files from directories

Very similar as the above, simply using `find` utility to provide list of all files in directories:

```
./upload-certs/upload-certs.py importPEM --trusted \
    --URL https://czertainly12.local/ --insecure \
    --cert ~/3K/admin.pem --key ~/3K/admin.key \
    `find /usr/local/share/ca-certificates /usr/share/ca-certificates/mozilla -type f `
loading: /usr/local/share/ca-certificates/SemikRootCA.crt ^ trusted valid 2
...
loading: /usr/share/ca-certificates/mozilla/SSL.com_Root_Certification_Authority_ECC.crt ^ trusted valid 2
Total uploaded certs = 143, avg speed = 3.00 certs/sec
```

### Upload CT log file

upload-certs.py is able to parse CT log file is separated by comma as produced by [axeman](https://github.com/CaliDog/Axeman). You can use option `-z` to skip some blocks to get still valid certificates. Example of one line from logfile:
```
ct.cloudflare.com/logs/nimbus2024,791661762,4ac17b993730fafaf9890050373c2d8ce8d1853f78f61ab8c39757db225251c7,MIIFAzCCA+ugAwIBAgISBPMo9BGGaotYWFXLPni+CwUrMA0GCSqGSIb3DQEBCwUAMDMxCzAJBgNVBAYTAlVTMRYwFAYDVQQKEw1MZXQncyBFbmNyeXB0MQwwCgYDVQQDEwNSMTAwHhcNMjQwNzExMDQ0NzI3WhcNMjQxMDA5MDQ0NzI2WjAkMSIwIAYDVQQDExlnbGRtZ3d3Ny5sb3Zpbmdzc2Fsb24uY29tMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArE6ILoP2QULGuHZ2gKO7Zx881rvfJeIYg5vUka1mYsr8wLHxN1OYNq8sjoDGQoegdeVlgO1KbvAbz5cuj95dzG50AzU+9Xj9yIZKFKU6vRCfa1fFeTchLaa+RKClLSfIxqij1+EoMsP7znHBb7sHE/m1uJNeeKz7Hg/tLN6eboj8BMM7rgV/uOgEL+33NpQPt5FO9+ER+1ZnnsyCTklCue4DShgUI8SZppRydGSeWZ2jdYvtxcumY7c1ovyjuQ4klfCvZNMsbhz/S0L1A09E8Ohb+uuktfR97V51QYIy6oZ+/K0ybeD80AZlwsReEaoiHFo+ZM9pRsd0kX4XEkNKlQIDAQABo4ICHjCCAhowDgYDVR0PAQH/BAQDAgWgMB0GA1UdJQQWMBQGCCsGAQUFBwMBBggrBgEFBQcDAjAMBgNVHRMBAf8EAjAAMB0GA1UdDgQWBBRjaB9kN4XYRch6gGZBoqyc3xpXNTAfBgNVHSMEGDAWgBS7vMNHpeS8qcbDpHIMEI2iNeHI6DBXBggrBgEFBQcBAQRLMEkwIgYIKwYBBQUHMAGGFmh0dHA6Ly9yMTAuby5sZW5jci5vcmcwIwYIKwYBBQUHMAKGF2h0dHA6Ly9yMTAuaS5sZW5jci5vcmcvMCQGA1UdEQQdMBuCGWdsZG1nd3c3LmxvdmluZ3NzYWxvbi5jb20wEwYDVR0gBAwwCjAIBgZngQwBAgEwggEFBgorBgEEAdZ5AgQCBIH2BIHzAPEAdwB2/4g/Crb7lVHCYcz1h7o0tKTNuyncaEIKn+ZnTFo6dAAAAZCgVRF7AAAEAwBIMEYCIQDVGM2aRyaoGsbrK3pgTYxfOb8GYRg8IvSV88IVrywM0QIhAP+iUEo3L9Ace7jlaA4L+LUqOWxUahKApGy3D7vP4XphAHYASLDja9qmRzQP5WoC+p0w6xxSActW3SyB2bu/qznYhHMAAAGQoFURQgAABAMARzBFAiA5OiyAMwEpT1hTVHqPFdsWwQwYnxGQsmiB2x/2MYmBMgIhAO0seYvYzOpuCdpmTRjMBDBTC0CqXysLt9YADXmqeFVjMA0GCSqGSIb3DQEBCwUAA4IBAQDK7+f7ALeQkF04j292+c99nI+QBHgpfxRkQF2woctVbvu+/sRCzII1VoIjMxmMTUvRz4NqSNgaYbPt+2CgcXsUhuvELXAzAQxcfrWqstasgqEQKDkXfze+EKIQq+W38xbnF57HogwIx6R6aYKIwwwGiED6e21i+ewODlMsHmI77zw+7us0AMXy7/nCcIvCA/nkGIB3+NdStVTYi+NI8RrhF7s3g6XcmT2E2urH8d1pGpYTyCUndpJy/75ZYi1CASwRN4D51zB0EEKT1qJ7+MFwJ86PuMQ7ZL2OA8Xhj0tR63JTO2cJ49Cicg9R+DfsYTCLwOaeabeu8NKP7LijE/79,gldmgww7.lovingssalon.com,1720666047.0,1728442046.0

```

For the following example I've downloaded some CT logs into `~/tmp/certificates/ct.cloudflare.com_logs_nimbus2024/`

```
./upload-certs/upload-certs.py importCTlog \
    --URL https://czertainly12.local/ --insecure \
    --cert ~/3K/admin.pem --key ~/3K/admin.key \
    ~/tmp/certificates/ct.cloudflare.com_logs_nimbus2024/791660737-791661762.csv \
    ~/tmp/certificates/ct.cloudflare.com_logs_nimbus2024/791661761-791662786.csv
loading: /home/semik/tmp/certificates/ct.cloudflare.com_logs_nimbus2024/791660737-791661762.csv ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ loaded certs: 596
Uploaded certs = 596, avg speed = 5.43 certs/sec
loading: /home/semik/tmp/certificates/ct.cloudflare.com_logs_nimbus2024/791661761-791662786.csv ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ loaded certs: 593
Uploaded certs = 1189, avg speed = 5.28 certs/sec
Total uploaded certs = 1189, avg speed = 5.28 certs/sec
```