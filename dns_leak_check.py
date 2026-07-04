#!/usr/bin/env python3
"""
DNS Leak Checker for Proxy Connections

Detects whether DNS resolution is leaking outside your configured proxy path.
Compares direct resolution vs proxied resolution for a target host and flags
mismatches that typically indicate a DNS leak.

Usage:
    python dns_leak_check.py example.com
    python dns_leak_check.py example.com --proxy socks5://127.0.0.1:1080
"""

import argparse
import socket
import sys
import time

try:
    import socks  # PySocks, optional dependency for --proxy support
    HAVE_SOCKS = True
except ImportError:
    HAVE_SOCKS = False


def resolve_direct(host: str):
    """Resolve a hostname using the system's default resolver."""
    start = time.time()
    try:
        ip = socket.gethostbyname(host)
        elapsed = (time.time() - start) * 1000
        return ip, elapsed, None
    except socket.gaierror as e:
        return None, None, str(e)


def resolve_via_proxy(host: str, proxy_url: str):
    """Resolve a hostname through a SOCKS proxy (requires PySocks)."""
    if not HAVE_SOCKS:
        return None, None, "PySocks not installed. Run: pip install PySocks"

    scheme, rest = proxy_url.split("://")
    addr, port = rest.split(":")
    port = int(port)

    proxy_type = {
        "socks5": socks.SOCKS5,
        "socks4": socks.SOCKS4,
        "http": socks.HTTP,
    }.get(scheme)

    if proxy_type is None:
        return None, None, f"Unsupported proxy scheme: {scheme}"

    default_socket = socket.socket
    socks.set_default_proxy(proxy_type, addr, port, rdns=True)
    socket.socket = socks.socksocket

    start = time.time()
    try:
        ip = socket.gethostbyname(host)
        elapsed = (time.time() - start) * 1000
        return ip, elapsed, None
    except Exception as e:
        return None, None, str(e)
    finally:
        socket.socket = default_socket


def main():
    parser = argparse.ArgumentParser(description="Check for DNS leaks in proxy-routed traffic.")
    parser.add_argument("host", help="Hostname to test, e.g. example.com")
    parser.add_argument("--proxy", help="Proxy URL, e.g. socks5://127.0.0.1:1080")
    args = parser.parse_args()

    print(f"Resolving '{args.host}' directly...")
    direct_ip, direct_ms, direct_err = resolve_direct(args.host)

    if direct_err:
        print(f"  Direct resolution failed: {direct_err}")
    else:
        print(f"  Direct IP: {direct_ip}  ({direct_ms:.1f} ms)")

    if not args.proxy:
        print("\nNo --proxy given, skipping proxy comparison.")
        print("Run again with --proxy socks5://host:port to compare paths.")
        sys.exit(0)

    print(f"\nResolving '{args.host}' via proxy {args.proxy}...")
    proxy_ip, proxy_ms, proxy_err = resolve_via_proxy(args.host, args.proxy)

    if proxy_err:
        print(f"  Proxy resolution failed: {proxy_err}")
        sys.exit(1)

    print(f"  Proxy IP: {proxy_ip}  ({proxy_ms:.1f} ms)")

    print("\n--- Result ---")
    if direct_ip and proxy_ip and direct_ip == proxy_ip:
        print("Same IP returned on both paths.")
        print("This can be normal for anycast/CDN hosts, but if you expected")
        print("the proxy to route through a different network, verify your")
        print("proxy client isn't bypassing DNS to the local resolver.")
    elif direct_ip and proxy_ip:
        print("Different IPs returned - resolution paths diverge as expected.")
        print("No leak detected based on this check alone.")
    else:
        print("Could not complete comparison due to earlier errors.")


if __name__ == "__main__":
    main()
