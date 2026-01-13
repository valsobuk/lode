import socket
from _thread import *
from player import BattleshipsGame
import pickle

# Bind to all interfaces (0.0.0.0) to accept connections from any network interface
server = ""
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    raise SystemExit(f"Bind failed: {e}")

s.listen(2)

# Get and display the server's IP address (more reliable method)
def get_local_ip():
    """Get the local IP address that can be reached from other machines"""
    try:
        # Connect to a remote address (doesn't actually connect)
        # This gets the IP of the interface used for outgoing connections
        s_test = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s_test.connect(("8.8.8.8", 80))  # Google DNS, just to find our IP
        ip = s_test.getsockname()[0]
        s_test.close()
        return ip
    except:
        # Fallback: get all IP addresses
        import socket as sock
        hostname = sock.gethostname()
        try:
            return sock.gethostbyname(hostname)
        except:
            return "127.0.0.1"

# Get all network interfaces (for debugging)
def get_all_ips():
    """Get all IP addresses of this machine"""
    import socket as sock
    ips = []
    hostname = sock.gethostname()
    try:
        # Get hostname IP
        host_ip = sock.gethostbyname(hostname)
        if host_ip not in ips:
            ips.append(host_ip)
    except:
        pass
    
    # Try the UDP method
    try:
        s_test = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s_test.connect(("8.8.8.8", 80))
        udp_ip = s_test.getsockname()[0]
        s_test.close()
        if udp_ip not in ips:
            ips.append(udp_ip)
    except:
        pass
    
    return ips

local_ip = get_local_ip()
all_ips = get_all_ips()

print(f"Server Started on port {port}")
print(f"Primary Server IP: {local_ip}")
if len(all_ips) > 1:
    print(f"All available IPs: {', '.join(all_ips)}")
    print("If connection fails, try using one of the other IPs in network.py")
print("Make sure clients use the correct IP address in network.py")
print("Waiting for connections...")

# Initialize two battleships games
players = [BattleshipsGame(0), BattleshipsGame(1)]

def threaded_client(conn, player):
    conn.send(pickle.dumps(players[player]))
    reply = ""
    while True:
        try:
            data = pickle.loads(conn.recv(2048))
            players[player] = data

            if not data:
                print("Disconnected")
                break
            else:
                # Send opponent's game state
                if player == 1:
                    reply = players[0]
                    opponent_idx = 0
                else:
                    reply = players[1]
                    opponent_idx = 1
                
                # Synchronize current_turn from shared state
                data.current_turn = players[opponent_idx].current_turn
                
                # Process new shots from this player on opponent's board (only if it's their turn)
                for shot_x, shot_y in data.shots_fired:
                    # Check if this shot hasn't been processed yet on opponent's board
                    if reply.own_board[shot_y][shot_x] == 0 or reply.own_board[shot_y][shot_x] == 1:
                        # Only process if it's this player's turn
                        if data.current_turn == data.player_id:
                            hit = reply.receive_shot(shot_x, shot_y)
                            data.update_opponent_board(shot_x, shot_y, hit)
                            # If miss, switch turn to opponent; if hit, stay on same player
                            if not hit:
                                data.current_turn = reply.player_id
                
                # Process new shots from opponent on this player's board
                for shot_x, shot_y in reply.shots_fired:
                    # Check if this shot hasn't been processed yet on this player's board
                    if data.own_board[shot_y][shot_x] == 0 or data.own_board[shot_y][shot_x] == 1:
                        hit = data.receive_shot(shot_x, shot_y)
                        reply.update_opponent_board(shot_x, shot_y, hit)
                
                # Synchronize current_turn to shared state (both players should have same turn)
                players[player].current_turn = data.current_turn
                players[opponent_idx].current_turn = data.current_turn
                reply.current_turn = data.current_turn
                
                # Update winner status
                if data.game_over:
                    data.winner = reply.player_id
                    reply.winner = reply.player_id
                if reply.game_over:
                    reply.winner = data.player_id
                    data.winner = data.player_id

                print(f"Player {player} - Shots: {len(data.shots_fired)}, Hits: {len(data.hits)}")

            # Return both updated states so client can refresh its own board and opponent view
            conn.sendall(pickle.dumps((players[player], reply)))
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            break

    print("Lost connection")
    conn.close()

currentPlayer = 0
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1
