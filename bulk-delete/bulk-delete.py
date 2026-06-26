#!/usr/bin/env python3
"""
CZERTAINLY bulk delete tool for certificates and discoveries.

The platform returns items newest-first, so the last page holds the oldest
objects. Each round: fetch page 1 to learn totalPages, jump to that last
page, delete those items, then wait for async deletion to confirm. Repeat.

Use --dry-run to preview without deleting (walks pages last→first to show
items in oldest-first order).

Usage examples:

  # Preview 500 oldest failed certificates (cert auth)
  python bulk-delete.py --url https://czertainly.example.com \\
    --cert admin.pem --key admin.key \\
    certificates --state failed --limit 500 --dry-run

  # Delete all failed + expired certificates
  python bulk-delete.py --url https://czertainly.example.com \\
    --cert admin.pem --key admin.key \\
    certificates --state failed expired

  # Delete 200 oldest failed discoveries (OAuth2)
  python bulk-delete.py --url https://czertainly.example.com \\
    --client-id myapp --client-secret mysecret \\
    --keycloak-url https://czertainly.example.com/kc \\
    discoveries --status FAILED --limit 200
"""

import argparse
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_BATCH_SIZE = 100
DEFAULT_REALM = "CZERTAINLY"
VERIFY_INITIAL_WAIT = 10   # seconds before first check
VERIFY_RETRY_INTERVAL = 10  # seconds between retries
VERIFY_MAX_WAIT = 300       # give up after this many seconds total


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

def get_oauth_token(keycloak_url, realm, client_id, client_secret, verify_ssl):
    token_url = f"{keycloak_url}/realms/{realm}/protocol/openid-connect/token"
    resp = requests.post(token_url, data={
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }, verify=verify_ssl, timeout=30)
    resp.raise_for_status()
    return resp.json()["access_token"]


def build_session(args):
    verify_ssl = not args.insecure

    session = requests.Session()
    session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})
    session.verify = verify_ssl

    if args.cert and args.key:
        session.cert = (args.cert, args.key)
    else:
        # Store credentials so refresh_token() can re-authenticate after long waits
        session._oauth = (args.keycloak_url, args.realm,
                          args.client_id, args.client_secret, verify_ssl)
        refresh_token(session)

    return session


def refresh_token(session):
    """Refresh the OAuth Bearer token. No-op for certificate-authenticated sessions."""
    if not hasattr(session, "_oauth"):
        return
    keycloak_url, realm, client_id, client_secret, verify_ssl = session._oauth
    token = get_oauth_token(keycloak_url, realm, client_id, client_secret, verify_ssl)
    session.headers["Authorization"] = f"Bearer {token}"


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def wait_until_deleted(session, check_urls):
    """Poll until all URLs return 404 or VERIFY_MAX_WAIT is exceeded.

    Returns True if all confirmed deleted, False if still present after timeout.
    """
    time.sleep(VERIFY_INITIAL_WAIT)
    elapsed = VERIFY_INITIAL_WAIT

    while True:
        if all(session.get(url, timeout=15).status_code == 404 for url in check_urls):
            print(f"  Confirmed deleted after {elapsed}s.")
            return True
        if elapsed >= VERIFY_MAX_WAIT:
            return False
        print(f"  Still waiting ... ({elapsed}s elapsed)")
        time.sleep(VERIFY_RETRY_INTERVAL)
        elapsed += VERIFY_RETRY_INTERVAL


# ---------------------------------------------------------------------------
# Certificates
# ---------------------------------------------------------------------------

def fetch_certificates_page(session, base_url, filters, batch_size, page):
    resp = session.post(f"{base_url}/api/v1/certificates", json={
        "filters": filters,
        "itemsPerPage": batch_size,
        "pageNumber": page,
    }, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("certificates", []), data.get("totalPages", 0), data.get("totalItems", 0)


def run_certificates(session, base_url, states, limit, batch_size, dry_run):
    """Delete certificates from oldest to newest using last-page strategy.

    If state filtering does not work as expected, call:
      GET /api/v1/certificates/search
    to discover available fieldIdentifier and fieldSource values.
    """
    filters = []
    if states:
        filters.append({
            "fieldSource": "property",
            "fieldIdentifier": "CERTIFICATE_STATE",
            "condition": "EQUALS",
            "value": states,
        })

    if dry_run:
        # Walk pages last→first to show items in oldest-first order
        _, total_pages, _ = fetch_certificates_page(session, base_url, filters, batch_size, 1)
        count = 0
        for page in range(total_pages, 0, -1):
            certs, _, _ = fetch_certificates_page(session, base_url, filters, batch_size, page)
            for cert in certs:
                name = cert.get("commonName") or cert.get("subjectDn") or "unknown"
                print(f"  {cert['uuid']}  {name}  [{cert.get('state', '')}]")
                count += 1
                if limit and count >= limit:
                    return
        return

    deleted_total = 0
    batch_num = 0
    # Cache the last page number to avoid a redundant page-1 probe each round.
    # Reset to None whenever the cached page turns up empty (platform drained it).
    cached_last_page = None

    while True:
        if limit and deleted_total >= limit:
            break

        if cached_last_page is not None:
            # Fetch directly — saves one API call per batch
            certs, total_pages, total_items = fetch_certificates_page(
                session, base_url, filters, batch_size, cached_last_page)
            if not certs:
                # Platform emptied this page before us; re-discover
                cached_last_page = None
                continue
        else:
            # Probe page 1 to learn current totalPages, then jump to the last page
            _, total_pages, total_items = fetch_certificates_page(
                session, base_url, filters, batch_size, 1)
            if total_pages == 0:
                break
            certs, total_pages, total_items = fetch_certificates_page(
                session, base_url, filters, batch_size, total_pages)
            if not certs:
                break

        # If limit would be exceeded, take only the tail (oldest within the page)
        if limit:
            remaining = limit - deleted_total
            certs = certs[max(0, len(certs) - remaining):]

        batch_num += 1
        uuids = [c["uuid"] for c in certs]
        resp = session.post(f"{base_url}/api/v1/certificates/delete",
                            json={"uuids": uuids}, timeout=60)
        resp.raise_for_status()
        deleted_total += len(uuids)
        print(f"  Batch {batch_num}: page {total_pages}/{total_pages}, "
              f"{total_items} matching, deleted {len(uuids)} (total: {deleted_total})")

        if not wait_until_deleted(session, [
            f"{base_url}/api/v1/certificates/{uuids[0]}",
            f"{base_url}/api/v1/certificates/{uuids[-1]}",
        ]):
            print(f"  Warning: items still visible after {VERIFY_MAX_WAIT}s, continuing anyway")

        refresh_token(session)  # token may have expired during long verify waits
        cached_last_page = total_pages - 1 if total_pages > 1 else None


# ---------------------------------------------------------------------------
# Discoveries
# ---------------------------------------------------------------------------

def fetch_discoveries_page(session, base_url, filters, batch_size, page):
    resp = session.post(f"{base_url}/api/v1/discoveries/list", json={
        "filters": filters,
        "itemsPerPage": batch_size,
        "pageNumber": page,
    }, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("discoveries", []), data.get("totalPages", 0), data.get("totalItems", 0)


def run_discoveries(session, base_url, statuses, limit, batch_size, dry_run):
    """Delete discoveries from oldest to newest using last-page strategy.

    If status filtering does not work as expected, call:
      GET /api/v1/discoveries/search
    to discover available fieldIdentifier and fieldSource values.
    """
    filters = []
    if statuses:
        filters.append({
            "fieldSource": "property",
            "fieldIdentifier": "DISCOVERY_STATUS",
            "condition": "EQUALS",
            "value": statuses,
        })

    if dry_run:
        _, total_pages, _ = fetch_discoveries_page(session, base_url, filters, batch_size, 1)
        count = 0
        for page in range(total_pages, 0, -1):
            discoveries, _, _ = fetch_discoveries_page(session, base_url, filters, batch_size, page)
            for disc in discoveries:
                print(f"  {disc['uuid']}  {disc.get('name', 'unknown')}  [{disc.get('status', '')}]")
                count += 1
                if limit and count >= limit:
                    return
        return

    deleted_total = 0
    batch_num = 0
    cached_last_page = None

    while True:
        if limit and deleted_total >= limit:
            break

        if cached_last_page is not None:
            discoveries, total_pages, total_items = fetch_discoveries_page(
                session, base_url, filters, batch_size, cached_last_page)
            if not discoveries:
                cached_last_page = None
                continue
        else:
            _, total_pages, total_items = fetch_discoveries_page(
                session, base_url, filters, batch_size, 1)
            if total_pages == 0:
                break
            discoveries, total_pages, total_items = fetch_discoveries_page(
                session, base_url, filters, batch_size, total_pages)
            if not discoveries:
                break

        if limit:
            remaining = limit - deleted_total
            discoveries = discoveries[max(0, len(discoveries) - remaining):]

        batch_num += 1
        uuids = [d["uuid"] for d in discoveries]
        resp = session.delete(f"{base_url}/api/v1/discoveries", json=uuids, timeout=60)
        resp.raise_for_status()
        deleted_total += len(uuids)
        print(f"  Batch {batch_num}: page {total_pages}/{total_pages}, "
              f"{total_items} matching, deleted {len(uuids)} (total: {deleted_total})")

        if not wait_until_deleted(session, [
            f"{base_url}/api/v1/discoveries/{uuids[0]}",
            f"{base_url}/api/v1/discoveries/{uuids[-1]}",
        ]):
            print(f"  Warning: items still visible after {VERIFY_MAX_WAIT}s, continuing anyway")

        refresh_token(session)  # token may have expired during long verify waits
        cached_last_page = total_pages - 1 if total_pages > 1 else None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Bulk delete certificates or discoveries from CZERTAINLY",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument("--url", required=True,
                        help="CZERTAINLY base URL (e.g. https://czertainly.example.com)")
    parser.add_argument("--insecure", action="store_true",
                        help="Disable SSL certificate verification")

    auth = parser.add_argument_group("authentication (choose cert or OAuth)")
    auth.add_argument("--cert", metavar="FILE", help="Client certificate PEM file")
    auth.add_argument("--key", metavar="FILE", help="Client certificate key PEM file")
    auth.add_argument("--client-id", metavar="ID", help="OAuth2 client ID")
    auth.add_argument("--client-secret", metavar="SECRET", help="OAuth2 client secret")
    auth.add_argument("--keycloak-url", metavar="URL", help="Keycloak base URL")
    auth.add_argument("--realm", default=DEFAULT_REALM,
                      help=f"Keycloak realm (default: {DEFAULT_REALM})")

    subparsers = parser.add_subparsers(dest="command", required=True)

    cert_cmd = subparsers.add_parser("certificates", help="Delete certificates")
    cert_cmd.add_argument("--state", nargs="+", metavar="STATE",
                          help="Filter by state, e.g. --state failed expired revoked")
    cert_cmd.add_argument("--limit", type=int, metavar="N",
                          help="Delete N oldest (default: all matching)")
    cert_cmd.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE,
                          metavar="N", help=f"UUIDs per delete call (default: {DEFAULT_BATCH_SIZE})")
    cert_cmd.add_argument("--dry-run", action="store_true",
                          help="Show what would be deleted without deleting")

    disc_cmd = subparsers.add_parser("discoveries", help="Delete discoveries")
    disc_cmd.add_argument("--status", nargs="+", metavar="STATUS",
                          help="Filter by status, e.g. --status FAILED IN_PROGRESS")
    disc_cmd.add_argument("--limit", type=int, metavar="N",
                          help="Delete N oldest (default: all matching)")
    disc_cmd.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE,
                          metavar="N", help=f"UUIDs per delete call (default: {DEFAULT_BATCH_SIZE})")
    disc_cmd.add_argument("--dry-run", action="store_true",
                          help="Show what would be deleted without deleting")

    args = parser.parse_args()

    has_cert_auth = bool(args.cert and args.key)
    has_oauth = bool(args.client_id and args.client_secret and args.keycloak_url)
    if not has_cert_auth and not has_oauth:
        parser.error(
            "Provide either --cert + --key, "
            "or --client-id + --client-secret + --keycloak-url"
        )

    print(f"Connecting to {args.url} ...")
    session = build_session(args)

    if args.command == "certificates":
        state_label = f" (state: {', '.join(args.state)})" if args.state else ""
        limit_label = f", limit {args.limit}" if args.limit else ""
        print(f"{'[dry-run] ' if args.dry_run else ''}Deleting certificates{state_label}{limit_label} ...")
        run_certificates(session, args.url, args.state, args.limit, args.batch_size, args.dry_run)

    elif args.command == "discoveries":
        status_label = f" (status: {', '.join(args.status)})" if args.status else ""
        limit_label = f", limit {args.limit}" if args.limit else ""
        print(f"{'[dry-run] ' if args.dry_run else ''}Deleting discoveries{status_label}{limit_label} ...")
        run_discoveries(session, args.url, args.status, args.limit, args.batch_size, args.dry_run)

    if args.dry_run:
        print("Dry run complete — nothing was deleted.")
    else:
        print("Done.")


if __name__ == "__main__":
    main()
