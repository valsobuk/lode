import socket
import pickle
import sys


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.56.1"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.p = self.connect()

    def getP(self):
        return self.p

    def connect(self):
        try:
            print(f"Connecting to server at {self.server}:{self.port}...")
            self.client.settimeout(5)  # 5 second timeout
            self.client.connect(self.addr)
            print("Connected! Waiting for game data...")
            data = self.client.recv(2048)
            if not data:
                print("Error: Server closed connection")
                return None
            self.client.settimeout(None)  # Remove timeout after connection
            return pickle.loads(data)
        except socket.timeout:
            print(f"Error: Connection timeout - couldn't reach {self.server}:{self.port}")
            print("Make sure:")
            print(f"  1. Server is running on {self.server}")
            print("  2. Both computers are on the same network")
            print("  3. Firewall allows connections on port 5555")
            return None
        except socket.error as e:
            print(f"Connection error: {e}")
            print(f"Could not connect to {self.server}:{self.port}")
            print("Make sure the server IP address is correct")
            return None
        except Exception as e:
            print(f"Unexpected error during connection: {e}")
            import traceback
            traceback.print_exc()
            return None

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(f"Network error: {e}")
            return None
        except Exception as e:
            print(f"Error sending data: {e}")
            return None