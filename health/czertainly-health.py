import requests
import argparse
import urllib3

TIMEOUT=30
CORE_HEALTH  = '/api/v1/health/liveness'
CONNECTORS    = '/api/v1/connectors'
HEADERS = {'Accept': 'application/json'}

class CzertainlyApiFail(Exception):
    pass


def get_czertainly_api(config,url):
    url = f"{config.URL}{url}"

    res = requests.get(url, timeout=TIMEOUT,
                       headers=HEADERS, cert=(config.cert, config.key),
                       verify=not config.insecure)

    if res.status_code == 200:
        rj = res.json()
        if 'status' in rj and rj['status'] == 'UP':
            rj['status'] = 'ok'

        return(rj)

    raise CzertainlyApiFail("Failed to call API: " + str(res.text))

def main():
    """Main."""
    parser = argparse.ArgumentParser(
        description="czertainly-health.py: an example how to use API to check status of CZERTAINLY")

    parser.add_argument('--URL', required=True, default='https://czertainly.local',
                        help='URL where CZERTAINLY is running  (default: %(default)s)')
    parser.add_argument('--cert', required=True,
                        help='PEM file with admin certificate for CZERTAINLY instance' )
    parser.add_argument('--key', required=True,
                        help='PEM file with key for admin certificate for CZERTAINLY instance' )
    parser.add_argument('--insecure', action='store_true', default=False,
                        help='disable certificate validation (default: %(default)s)')
    parser.add_argument('--show-uri', action='store_true', default=False,
                        help='show URI for connectors (default: %(default)s)')

    args = parser.parse_args()

    if args.insecure:
        urllib3.disable_warnings()

    res = 0

    core = get_czertainly_api(args, CORE_HEALTH)
    print(f"CZERTAINLY core: {core['status']}")
    if core['status'] != 'ok':
        res = 1

    connectors = get_czertainly_api(args, CONNECTORS)

    print("Components: ")
    for connector in connectors:
        name = connector['name']
        uuid = connector['uuid']
        uri  = f"/api/v1/connectors/{uuid}/health"

        try:
            conn_health = get_czertainly_api(args, uri)
            status = conn_health['status']
        except CzertainlyApiFail:
            status = 'down'

        if status != 'ok':
            res = 1

        if args.show_uri:
            print(f"  {name}: {status} {uri}")
        else:
            print(f"  {name}: {status}")

    exit(res)


if __name__ == "__main__":
    main()
