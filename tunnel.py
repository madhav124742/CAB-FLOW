"""
tunnel.py
Creates a public cloud URL for the local Cab Flow application using pyngrok.
Run with: python tunnel.py
"""

import sys
import time
from pyngrok import ngrok, conf

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8501
    print(f"Creating public tunnel to local port {port}...")
    try:
        tunnel = ngrok.connect(port, "http")
        print("\n========================================================")
        print(f" PUBLIC CLOUD URL: {tunnel.public_url}")
        print(f" Forwarding to:    http://localhost:{port}")
        print("========================================================\n")
        print("Press Ctrl+C to terminate the tunnel.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nTunnel closed.")
        ngrok.kill()
    except Exception as e:
        print(f"Error opening tunnel: {e}")
        print("If an ngrok authtoken is required, get one free at https://dashboard.ngrok.com and run:")
        print("ngrok config add-authtoken <YOUR_TOKEN>")

if __name__ == '__main__':
    main()

