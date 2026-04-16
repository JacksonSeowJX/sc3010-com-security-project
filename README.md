# SC3010 Computer Security Project

Welcome to the project repository! This repository contains code demonstrations and research dedicated to modern cyberattacks, specifically contrasting application-layer input attacks versus developer supply chain attacks.

## Case Studies

### 1. Log4Shell (CVE-2021-44228)
*The "Exploiting What You Run" Paradigm*
- **Target:** Apache Log4j2 Logging Framework
- **Vector:** JNDI Injection via malicious LDAP payloads triggered by string parsing.
- **Demo Status:** In Progress (Branch: `feature/log4shell-analysis`)

### 2. Axios npm Supply Chain Attack (March 2026)
*The "Exploiting How You Build" Paradigm*
- **Target:** Axios npm package build pipeline
- **Vector:** Phantom dependency injection (`plain-crypto-js`) executing OS-detecting droppers via hidden NPM `postinstall` hooks.
- **Anti-Forensics:** The payload dynamically swapped its own `package.json` decoy and deleted itself from the disk upon execution to completely hide evidence from incident responders.
- **Demo Status:** Completed (Directory: `demos/axios_attack/`)

## Repository Structure

- `/demos/`: Contains interactive, locally-contained, completely safe code simulations for the classroom presentation.
- `/misc/`: Contains presentation scripts and video recording guides.

## Setup & Contributions
If you are a group member contributing to this repository:
1. Clone the repository and run `git fetch`.
2. Checkout your specific feature branch (e.g., `git checkout feature/log4shell-analysis`).
3. Develop your demo inside the `/demos/` folder without touching existing case studies.
4. Push your branch and open a Pull Request to merge your work back into `main` before the presentation.