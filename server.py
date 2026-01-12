import socket
from _thread import *
from player import BattleshipsGame
import pickle

# Use a local interface; binding to a non-existent IP on Windows makes listen() fail
server = "127.0.0.1"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    raise SystemExit(f"Bind failed: {e}")

s.listen(2)
print("Waiting for a connection, Server Started")

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
                else:
                    reply = players[1]
                
                # Process new shots from this player on opponent's board
                for shot_x, shot_y in data.shots_fired:
                    # Check if this shot hasn't been processed yet on opponent's board
                    if reply.own_board[shot_y][shot_x] == 0 or reply.own_board[shot_y][shot_x] == 1:
                        hit = reply.receive_shot(shot_x, shot_y)
                        data.update_opponent_board(shot_x, shot_y, hit)
                
                # Process new shots from opponent on this player's board
                for shot_x, shot_y in reply.shots_fired:
                    # Check if this shot hasn't been processed yet on this player's board
                    if data.own_board[shot_y][shot_x] == 0 or data.own_board[shot_y][shot_x] == 1:
                        hit = data.receive_shot(shot_x, shot_y)
                        reply.update_opponent_board(shot_x, shot_y, hit)
                
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
