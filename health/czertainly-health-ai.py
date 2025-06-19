#!/usr/bin/env python3

import requests
import yaml
import re
import argparse
import sys
import urllib3
import json
from urllib.parse import quote
from requests.exceptions import RequestException


def load_config(path: str):
    with open(path, 'r') as file:
        return yaml.safe_load(file)


def fetch(url, headers=None, cert=None, key=None, insecure=False, trusted_ca=None, debug=False):
    if debug:
        print(f"[DEBUG] Fetching URL: {url}")
    try:
        if insecure:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        cert_pair = (cert, key) if cert and key else None
        verify = not insecure if not trusted_ca else trusted_ca
        response = requests.get(url, headers=headers, cert=cert_pair, verify=verify, timeout=5)
        return response.status_code, response.text
    except RequestException as e:
        return None, str(e)


def encode_headers(headers_list):
    if not headers_list:
        return None
    return {
        k: quote(v, safe='')
        for header in headers_list
        for k, v in header.items()
    }


def check_component(name, url, valid_output, headers=None, cert=None, key=None, insecure=False, trusted_ca=None, debug=False):
    status_code, content = fetch(url, headers, cert, key, insecure, trusted_ca, debug=debug)
    if status_code is None:
        return {
            "name": name,
            "status": "error",
            "message": f"Unable to fetch from {url} - {content}"
        }
    if re.search(valid_output, content):
        return {
            "name": name,
            "status": "ok"
        }
    else:
        return {
            "name": name,
            "status": "fail",
            "message": f"Unexpected response from {url}: {content}"
        }


def extract_url_info(component, use_public):
    url_info = component.get("public" if use_public else "local")
    headers = encode_headers(url_info.get("headers")) if isinstance(url_info, dict) else None
    url = url_info.get("url") if isinstance(url_info, dict) else url_info
    valid_output = component.get("validOutput")
    return url, headers, valid_output


def extract_tls_config(group):
    cert = group.get("cert")
    key = group.get("key")
    insecure = group.get("insecure", False)
    trusted_ca = group.get("trustedCA")
    return cert, key, insecure, trusted_ca


def process_component(component, use_public, cert, key, insecure, trusted_ca, json_only, debug, results):
    name = component.get("name")
    url, headers, valid_output = extract_url_info(component, use_public)
    if url and valid_output:
        result = check_component(name, url, valid_output, headers, cert, key, insecure, trusted_ca, debug)
    else:
        result = {"name": name, "status": "skip", "message": "No URL or validOutput defined"}

    results.append(result)

    if not json_only:
        status = result["status"].upper()
        message = result.get("message", "")
        if status != "SKIP" or debug:
            print(f"[{status}] {name}" + (f": {message}" if message else ""))


def process_group(group, use_public, json_only, debug, results):
    if not json_only:
        print(f"\n== {group.get('name')} ==")

    components = group.get("components", [])
    cert, key, insecure, trusted_ca = extract_tls_config(group)

    for comp in components:
        process_component(comp, use_public, cert, key, insecure, trusted_ca, json_only, debug, results)

    if "iterate" in group:
        iterate_info = group["iterate"]
        iterate_url_info = iterate_info.get("public" if use_public else "local")
        headers = encode_headers(iterate_url_info.get("headers")) if isinstance(iterate_url_info, dict) else None
        base_url = iterate_url_info.get("url") if isinstance(iterate_url_info, dict) else iterate_url_info
        valid_output = iterate_info.get("validOutput", ".*")

        if base_url:
            try:
                if debug:
                    print(f"[DEBUG] Fetching connector list from: {base_url}")
                cert_pair = (cert, key) if cert and key else None
                verify = not insecure if not trusted_ca else trusted_ca
                response = requests.get(base_url, headers=headers, cert=cert_pair, verify=verify, timeout=5)
                if response.status_code != 200:
                    message = f"Connector list: HTTP {response.status_code} from {base_url}"
                    if not json_only:
                        print(f"[FAIL] {message}")
                    results.append({"name": "Connector list", "status": "fail", "message": message})
                    return
                if not json_only:
                    print(f"[OK] Connector list")
                results.append({"name": "Connector list", "status": "ok"})

                connectors = response.json()
                for connector in connectors:
                    name = connector.get("name") or connector.get("url")
                    if use_public:
                        uuid = connector.get("uuid")
                        if not uuid:
                            results.append({"name": name, "status": "skip", "message": "Missing UUID"})
                            if debug and not json_only:
                                print(f"[SKIP] {name}: Missing UUID")
                            continue
                        connector_url = f"{base_url.rstrip('/')}/{uuid}/health"
                    else:
                        connector_url = connector.get("url")

                    if connector_url:
                        result = check_component(
                            f"Connector: {name}",
                            connector_url,
                            ".*",
                            headers,
                            cert,
                            key,
                            insecure,
                            trusted_ca,
                            debug=debug
                        )
                        results.append(result)
                        if not json_only:
                            status = result["status"].upper()
                            message = result.get("message", "")
                            print(f"[{status}] Connector: {name}" + (f": {message}" if message else ""))
            except Exception as e:
                message = f"Failed to fetch or parse connector list from {base_url}: {e}"
                if not json_only:
                    print(f"[ERROR] {message}")
                results.append({"name": "Connector list", "status": "error", "message": message})
        else:
            msg = f"Iteration for group {group.get('name')}: Missing URL"
            if debug and not json_only:
                print(f"[SKIP] {msg}")
            results.append({"name": f"Iterate: {group.get('name')}", "status": "skip", "message": msg})


def calculate_overall_status(results):
    statuses = [r["status"] for r in results]
    if any(s == "error" for s in statuses):
        return "critical"
    if any(s == "fail" for s in statuses):
        return "warning"
    return "ok"


def main():
    parser = argparse.ArgumentParser(description="CZERTAINLY Health Checker from YAML")
    parser.add_argument("-c", "--config", default="config.yaml", help="Path to YAML config file")
    parser.add_argument("--use-public", action="store_true", help="Use public URLs instead of local ones")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--json-only", action="store_true", help="Output only JSON without printing status messages")
    parser.add_argument("--debug", action="store_true", help="Enable debug output (show fetched URLs and SKIPs)")
    args = parser.parse_args()

    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Failed to load config: {e}")
        sys.exit(1)

    results = []
    for group in config:
        process_group(group, args.use_public, args.json_only, args.debug, results)

    if args.json or args.json_only:
        summary = {
            "status": calculate_overall_status(results),
            "results": results
        }
        print(json.dumps(summary, indent=2))

        exit_code = {"ok": 0, "warning": 1, "critical": 2}[summary["status"]]
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
