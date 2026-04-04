# Log4Shell (CVE-2021-44228) — Live Demo Script

**Setup before presenting:**
Open 4 terminal windows (or use a terminal multiplexer). Arrange them so all are visible simultaneously.

- **Terminal 1 (Top-Left):** LDAP Server (Attacker)
- **Terminal 2 (Top-Right):** HTTP Payload Server + C2 (Attacker)
- **Terminal 3 (Bottom-Left):** Vulnerable Application (Victim)
- **Terminal 4 (Bottom-Right):** Attacker CLI (Exploit Launcher)

---

## Step 1: Set the Scene — The Attacker's Infrastructure

*Start by launching both attacker servers.*

**What to type (Terminal 1):**
```bash
cd demos/log4shell_attack/malicious_ldap_server
python3 ldap_server.py
```

**What to type (Terminal 2):**
```bash
cd demos/log4shell_attack/malicious_http_server
python3 http_payload_server.py
```

**What to say:**
> *"To understand Log4Shell, we first need to see the attacker's setup. The attacker has two servers running on the internet. The first is a rogue LDAP server — this is the entry point that Log4j will connect to. The second is an HTTP server that hosts the malicious Java class file AND listens for beacon callbacks from compromised machines. Both are running and waiting silently."*

---

## Step 2: The Victim Application

*Start the vulnerable application.*

**What to type (Terminal 3):**
```bash
cd demos/log4shell_attack/vulnerable_app
python3 vulnerable_app.py
```

**What to say:**
> *"On the victim side, we have a typical Java web application — this could be a Minecraft server, a Spring Boot API, an Apache Struts application, or anything else that uses Log4j for logging. Notice it's running Apache Log4j version 2.14.1, which is vulnerable to CVE-2021-44228. This is just like millions of real servers that were exposed in December 2021."*

---

## Step 3: The Attack — Injecting the JNDI Payload

*This is the key moment. Point at Terminal 4.*

**What to type (Terminal 4):**
```bash
cd demos/log4shell_attack/attacker_cli
python3 attacker.py
```

**What to say (BEFORE hitting enter):**
> *"Now the attacker sends a simple HTTP request to the victim application. But look at the User-Agent header — instead of a normal browser string, they've injected a malicious JNDI lookup: dollar-sign, curly-brace, jndi:ldap://attacker-server/Exploit. This single string is the entire exploit. It could be placed in any input field that gets logged — a username, a search query, even a Minecraft chat message. Let me fire it..."*

*(Hit Enter.)*

---

## Step 4: Watch the Exploit Chain Unfold

*Immediately after hitting enter, point to each terminal in sequence.*

**What to say:**
> *"Watch what happens across all four terminals:*
>
> *First, look at Terminal 3 — the victim application. It received our HTTP request and innocently passed the User-Agent header to Log4j for logging. But Log4j version 2.14.1 has a feature called 'message lookup substitution'. When it sees the dollar-jndi pattern, it doesn't treat it as a string — it actually tries to RESOLVE it.*
>
> *You can see Log4j is now performing a JNDI lookup. It connects to the attacker's LDAP server on port 1389.*
>
> *Now look at Terminal 1 — the LDAP server received the connection. It sends back a crafted LDAP referral that says: 'the object you're looking for? Download it from this HTTP URL.' This redirects the victim to our malicious HTTP server.*
>
> *Terminal 3 again — Log4j follows the redirect and downloads Exploit.class from the attacker's HTTP server. Look at Terminal 2 — it just served the malicious Java class to the victim.*
>
> *And now the critical moment — the JVM loads and instantiates the downloaded class. Its static initialiser runs automatically, achieving Remote Code Execution. The payload collects the victim's hostname, username, OS info, and architecture, then drops a backdoor file to prove file-write access, and finally beacons all the stolen data back to the attacker's C2 server.*
>
> *Terminal 2 — there it is. The C2 server just received the beacon. The attacker now has full system information and has proven they can write files to the victim's filesystem. Game over."*

---

## Step 5: Show the Evidence — Backdoor File

*Switch to the victim's filesystem.*

**What to type (Terminal 4, after attack completes):**
```bash
cd ../vulnerable_app
ls
cat LOG4SHELL_BACKDOOR.txt
```

**What to say:**
> *"If incident responders examine the victim server, they'll find this file. The attacker's payload created it to prove arbitrary file-write capability. In a real attack, this could have been a web shell for persistent access, a crypto-mining binary, ransomware, or SSH keys for a permanent backdoor. The entire compromise happened from a single logged string — no credentials, no authentication bypass, no complex exploit chain. Just six characters — dollar, curly-brace, jndi — in any logged input field."*

---

## Step 6: Discuss Mitigations

**What to say:**
> *"This vulnerability was so devastating because it hit at the intersection of three design decisions:*
>
> *First — Log4j's message lookup feature was enabled by default. There was no reason for a logging library to perform network requests, but it did.*
>
> *Second — JNDI supports remote class loading via LDAP by default in older JVM versions. The combination of logging + JNDI + remote classloading created a one-step RCE.*
>
> *Third — Log4j is embedded in virtually every Java application. It was a transitive dependency that many developers didn't even know they had.*
>
> *The mitigations, as shown in our diagram, operate at multiple layers:*
> - *Patch Log4j to 2.17.0+ (which disables message lookups entirely)*
> - *Block with WAF — detect and reject requests containing jndi patterns*
> - *Disable JNDI lookup — set the JVM flag `-Dlog4j2.formatMsgNoLookups=true`*
> - *Block outbound LDAP connections via network firewall rules*
> - *Use EDR to detect suspicious class loading or shell spawning*
>
> *Defense in depth — no single mitigation is sufficient on its own."*

---

## Cleanup

After the demo, press `Ctrl+C` in each terminal and run:
```bash
rm demos/log4shell_attack/vulnerable_app/LOG4SHELL_BACKDOOR.txt
```

## Quick Alternative: Single-Terminal Demo

If managing 4 terminals during a live presentation is too complex, use the all-in-one launcher instead:
```bash
cd demos/log4shell_attack
python3 run_all.py
```
This runs the entire attack chain automatically and shows the results sequentially.
