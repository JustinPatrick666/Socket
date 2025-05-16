import socket
import json
import threading
import sys

HOST = '127.0.0.1'
PORT = 5555

def receive_messages(conn):
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                print("Disconnected from server.")
                break
            msg = json.loads(data.decode())
            print(f"[{msg['from']}]: {msg.get('text', '')}")
        except:
            break
    sys.exit()

def main():
    username = input("Enter your username: ").strip()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(username.encode())

        thread = threading.Thread(target=receive_messages, args=(s,))
        thread.start()

        while True:
            cmd = input()
            if not cmd:
                continue

            if cmd.startswith("/p "):
                parts = cmd[3:].split(" ", 1)
                if len(parts) < 2:
                    print("Usage: /p <username> message")
                    continue
                target, text = parts
                msg = {
                    "type": "private",
                    "from": username,
                    "to": target,
                    "text": text
                }
                s.sendall(json.dumps(msg).encode())

            elif cmd.startswith("/g "):
                parts = cmd[3:].split(" ", 1)
                if len(parts) < 2:
                    print("Usage: /g <groupname> message")
                    continue
                group, text = parts
                msg = {
                    "type": "group",
                    "from": username,
                    "group": group,
                    "text": text
                }
                s.sendall(json.dumps(msg).encode())

            elif cmd.startswith("/b "):
                text = cmd[3:]
                msg = {
                    "type": "broadcast",
                    "from": username,
                    "text": text
                }
                s.sendall(json.dumps(msg).encode())

            elif cmd.startswith("/join "):
                group = cmd.split(" ")[1]
                msg = {
                    "type": "join_group",
                    "from": username,
                    "group": group
                }
                s.sendall(json.dumps(msg).encode())

            elif cmd.startswith("/leave "):
                group = cmd.split(" ")[1]
                msg = {
                    "type": "leave_group",
                    "from": username,
                    "group": group
                }
                s.sendall(json.dumps(msg).encode())

            elif cmd == "/exit":
                print("Exiting...")
                break

            else:
                print("Unknown command")

if __name__ == "__main__":
    main()