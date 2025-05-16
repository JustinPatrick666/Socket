import socket
import threading
import json

HOST = '127.0.0.1'
PORT = 5555

clients = {}  # {username: (conn, addr)}
groups = {}   # {groupname: [usernames]}

def broadcast_message(message):
    for conn in [clients[user][0] for user in clients]:
        try:
            conn.sendall(json.dumps(message).encode())
        except:
            pass

def send_to_group(group, message, sender):
    if group not in groups:
        return
    for username in groups[group]:
        if username != sender and username in clients:
            try:
                clients[username][0].sendall(json.dumps(message).encode())
            except:
                pass

def send_to_user(target, message, sender):
    if target not in clients:
        print(f"User {target} not found.")
        return
    try:
        clients[target][0].sendall(json.dumps(message).encode())
    except Exception as e:
        print(f"Error sending to {target}: {e}")

def handle_client(conn, addr):
    username = None
    try:
        data = conn.recv(1024)
        if not data:
            return
        username = data.decode().strip()
        print(f"{username} connected from {addr}")
        clients[username] = (conn, addr)

        while True:
            data = conn.recv(1024)
            if not data:
                break
            try:
                msg_obj = json.loads(data.decode())
                print("Received:", msg_obj)

                if msg_obj['type'] == 'private':
                    send_to_user(msg_obj['to'], msg_obj, msg_obj['from'])
                elif msg_obj['type'] == 'group':
                    send_to_group(msg_obj['group'], msg_obj, msg_obj['from'])
                elif msg_obj['type'] == 'broadcast':
                    broadcast_message(msg_obj)
                elif msg_obj['type'] == 'join_group':
                    group = msg_obj['group']
                    if group not in groups:
                        groups[group] = []
                    if username not in groups[group]:
                        groups[group].append(username)
                    print(f"{username} joined group {group}")
                elif msg_obj['type'] == 'leave_group':
                    group = msg_obj['group']
                    if group in groups and username in groups[group]:
                        groups[group].remove(username)
                    print(f"{username} left group {group}")
            except Exception as e:
                print(f"Error handling message: {e}")
    finally:
        if username in clients:
            del clients[username]
        print(f"{username} disconnected")
        conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server started on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()

if __name__ == '__main__':
    start_server()