# proxy-dns-leak-check

A small CLI tool to detect DNS leaks when routing traffic through proxies (residential, mobile, datacenter). It compares direct DNS resolution against resolution through your configured proxy and flags mismatches that typically indicate a leak.

## Why this matters

If your traffic goes through a proxy but DNS lookups still hit your local ISP resolver, you get a leak: the proxy hides your IP from the destination server, but your DNS queries still reveal where you actually are. This is a common, quiet failure mode in scraping, multi-account, and geo-testing setups.

Background reading: [Advanced DNS Troubleshooting for Proxy-Routed Infrastructure](https://dev.to/sota_support_d59338642d7b/advanced-dns-troubleshooting-for-proxy-routed-infrastructure-9mh) covers the underlying diagnosis workflow this tool automates the first step of.

## Install

```bash
git clone https://github.com/SotaProxy/proxy-dns-leak-check.git
cd proxy-dns-leak-check
pip install PySocks   # optional, only needed for --proxy comparisons
```

## Usage

```bash
# Direct resolution only
python dns_leak_check.py example.com

# Compare direct vs proxy resolution
python dns_leak_check.py example.com --proxy socks5://127.0.0.1:1080
```

## Example output

```
Resolving 'example.com' directly...
  Direct IP: 93.184.216.34  (12.4 ms)

Resolving 'example.com' via proxy socks5://127.0.0.1:1080...
  Proxy IP: 198.51.100.7  (187.2 ms)

--- Result ---
Different IPs returned - resolution paths diverge as expected.
No leak detected based on this check alone.
```

## Limitations

This is a single-host, single-run check, not a continuous monitor. Some legitimate cases (anycast, CDN-backed domains) will show the same IP on both paths without indicating a real leak. Use it as a first signal, not a final verdict, and cross-check with `dig`/`nslookup` against multiple resolvers for anything that matters operationally.

## Related

- [Multiple Account Management: A Secure, Scalable Framework](https://dev.to/sota_support_d59338642d7b/multiple-account-management-a-secure-scalable-framework-1k8e) — proxy selection and session discipline for multi-account operations.
- [SotaProxy](https://sotaproxy.com/?utm_source=github&utm_medium=readme&utm_campaign=dns_leak_check) — residential, mobile, datacenter, and ISP proxies.

## License

MIT
