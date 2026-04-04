# Axios Supply Chain Attack Demo

This demo safely simulates the March 2026 supply chain attack on the Axios npm package, specifically demonstrating the phantom dependency injection (`plain-crypto-js`), the `postinstall` dropper payload, and the anti-forensics techniques.

## Setup & Execution

### Step 1: Start the Attacker C2 Server
In your **first terminal**, navigate to the `attacker_c2` directory and start the listener:
```bash
cd "/Users/jacksonetherchainstake/SC3010 Com Security/Project/demos/axios_attack/attacker_c2"
python3 server.py
```
*Leave this terminal open and visible to your professor.*

### Step 2: Trigger the Attack on the Victim Machine
In a **second terminal**, navigate to the `victim_project` directory. You will act as an innocent developer running a standard `npm install`:
```bash
cd "/Users/jacksonetherchainstake/SC3010 Com Security/Project/demos/axios_attack/victim_project"
npm install
```

### Step 3: Observe the Results
1. Look at Terminal 1. You will instantly see the C2 server receive the beacon indicating system compromise.
2. Look at Terminal 2. The `npm install` finished silently, like normal.
3. Show your professor the **Anti-Forensics trick**:
   ```bash
   cd node_modules/plain-crypto-js
   ls
   cat package.json
   ```
   Notice that `setup.js` has completely deleted itself, and `package.json` no longer contains the `"postinstall"` hook. The payload replaced its own files to cover its tracks!

## Cleanup
To reset the demo between runs, you must replace the deleted malicious payload. We simulate this by reinstalling:
```bash
# In the victim_project directory
rm -rf node_modules
```
*Note: Since the demo deletes its own `setup.js` from the original source file locally during `npm install` with local bindings, you may need to recreate the malicious package if you want to run it twice.*
