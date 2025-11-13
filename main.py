import requests
import time
import sys
from platform import system
import os
import http.server
import socketserver
import threading

# ------------------------
# SERVER CONFIG
# ------------------------
HOST = "0.0.0.0"   # host10000 (as you said)
PORT = 10000


class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Vishu ")


def execute_server():
    """Start HTTP server at host10000"""
    class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        allow_reuse_address = True

    with ThreadedTCPServer((HOST, PORT), MyHandler) as httpd:
        print(f"Server running at http://{HOST}:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server stopped.")
        finally:
            httpd.server_close()


# ------------------------
# SEND MESSAGES
# ------------------------
def send_messages():
    """Send one message per token sequentially."""
    # Password check
    if not os.path.exists("password.txt"):
        print("password.txt not found!")
        sys.exit()

    with open("password.txt", "r", encoding="utf-8") as f:
        password = f.read().strip()

    entered_password = password  # auto-match for now

    if entered_password != password:
        print("[-] Incorrect Password!")
        sys.exit()

    # Read tokens
    if not os.path.exists("token.txt"):
        print("token.txt not found!")
        sys.exit()

    with open("token.txt", "r", encoding="utf-8") as f:
        tokens = [line.strip() for line in f if line.strip()]

    if not tokens:
        print("token.txt empty!")
        sys.exit()

    # Optional messages file
    messages = []
    if os.path.exists("messages.txt"):
        with open("messages.txt", "r", encoding="utf-8") as f:
            messages = [m.strip() for m in f if m.strip()]

    default_message = "Hello from Vishu!"
    requests.packages.urllib3.disable_warnings()

    # Target URL
    url = f"http://{HOST}:{PORT}/"

    print(f"\n[+] Sending messages to {url}")
    print(f"[+] Total tokens found: {len(tokens)}\n")

    for idx, token in enumerate(tokens, start=1):
        message = messages[idx - 1] if idx <= len(messages) else f"{default_message} #{idx}"

        payload = {"token": token, "message": message}
        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10, verify=False)
            print(f"[{idx}/{len(tokens)}] Sent with token={token[:8]}... | Status={response.status_code}")
        except Exception as e:
            print(f"[{idx}] Error sending message: {e}")

        time.sleep(0.2)  # short delay between tokens


# ------------------------
# CLEAR SCREEN (OPTIONAL)
# ------------------------
def cls():
    if system() == "Linux" or system() == "Darwin":
        os.system("clear")
    elif system() == "Windows":
        os.system("cls")


# ------------------------
# MAIN START
# ------------------------
if __name__ == "__main__":
    # Start HTTP server in background
    server_thread = threading.Thread(target=execute_server, daemon=True)
    server_thread.start()

    time.sleep(1)
    send_messages()
