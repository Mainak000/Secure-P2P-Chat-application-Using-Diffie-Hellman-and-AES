import socket
import threading
import os
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from hashlib import sha256

# Dictionary to store incoming connections
conn_list = {}
# Lock to synchronize print statements in threads
print_lock = threading.Lock()
# Variable to track if chat is active
active = False

# From environment variables read p and g.
p = int(os.getenv("P", "23"))  # Prime number 
g = int(os.getenv("Q", "5"))   # Generator 

a = random.randint(2, p - 2)  # Private key
A = pow(g, a, p)  # Public key

# functions for aes key
def AESKey(shared_secret):

    return sha256(str(shared_secret).encode()).digest()

#Functions for diffie hellman key exchange
def KeyExchange(Socket):
    Socket.send(str(A).encode())   
    B = int(Socket.recv(1024).decode())
    shared_secret = pow(B, a, p)
    print(f"Private Key: {a}")
    print(f"Public Key: {A}")
    print(f"Computed Shared Secret Key: {shared_secret}")
    return AESKey(shared_secret)

#Function for encrypted message using AES
def Encryption_msg(aes_key, message):

    c = AES.new(aes_key, AES.MODE_CBC)
    ct_bytes = c.encrypt(pad(message.encode(), AES.block_size))
    return c.iv + ct_bytes

#Functions for decryptes message
def decryption_msg(aes_key, ciphertext):
    iv = ciphertext[:AES.block_size]
    ct = ciphertext[AES.block_size:]
    c = AES.new(aes_key, AES.MODE_CBC, iv)
    decrypted = unpad(c.decrypt(ct), AES.block_size)
    return decrypted.decode()
# Function for managing the chat session
def chat_session(Socket, aes_key):
    def receive():
        try:
            # Continuously receive messages until 'EOM' (End of Message)
            while True:
                encrypted_message = Socket.recv(1024)
                if encrypted_message == b"EOM":
                    print("\nChat Ended.")
                    break
                with print_lock:
                    print(f"\n[Encrypted]: {encrypted_message.hex()}")
                    decrypted_message = decryption_msg(aes_key, encrypted_message)
                    print(f"[Received]: {decrypted_message}")
                    print("[Send]: ", end="", flush=True)
        except:
            print("\nConnection ended.")
        finally:
            Socket.close()

    def send():
        try:
            while True:
                # Send message input by the user
                msg_to_send = input("[Send]: ").strip()
                encrypted_message = Encryption_msg(aes_key, msg_to_send)
                Socket.send(encrypted_message)
                if msg_to_send == "EOM":
                    print("\n[Chat Ended]")
                    break
        except:
            print("\nConnection lost.")
        finally:
            Socket.close()
# Start receiving and sending threads
    recv_thread = threading.Thread(target=receive, daemon=True)
    send_thread = threading.Thread(target=send, daemon=True)
    recv_thread.start()
    send_thread.start()
    recv_thread.join()
    send_thread.join()
# Function to start the P2P chat after establishing connection
def start_p2p_chat(Socket):
    global active
    active = True
    aes_key = KeyExchange(Socket)
    chat_session(Socket, aes_key)
    active = False
# Function to listen for incoming P2P connection requests
def listen_p2p(listen_socket):
    listen_socket.listen(1)
    while True:
        client_socket, addr = listen_socket.accept()
        print(f"\nIncoming chat request from {addr}")
        print("\nPress Enter to accept.")
        conn_list[addr] = client_socket # Add the client to the connection list

def run_client():
    global active
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 50000))
    
    print(client.recv(1024).decode())    # Server greeting
    username = input("Enter your username: ").strip()
    client.send(username.encode())
    
    response = client.recv(1024).decode()
    if response.startswith("Username already in use"):
        print(response)
        client.close()
        return
    # Setup listen socket for incoming P2P requests
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind(("0.0.0.0", 0))
    listen_port = listen_socket.getsockname()[1]
    client.send(f"LISTEN_PORT:{listen_port}".encode())
    
    print(client.recv(1024).decode())   # Wait for the server to confirm listening
    threading.Thread(target=listen_p2p, args=(listen_socket,), daemon=True).start() # Start listening for incoming P2P chat requests
    
    while True:
        if conn_list:
            addr, Socket = conn_list.popitem()
            start_p2p_chat(Socket)  # Start P2P chat with the accepted connection
         
        if not active:   # Show menu for available commands
            print("\nPress 1 to get user details or press 2 to EXIT")
            command = input("Enter command: ").strip()      # Only process if command is not empty
            if command == "1":
                client.send("1".encode())
                user_list = client.recv(1024).decode()
                if "No users available" in user_list:
                    print("\nNo other users available.")
                else:
                    print("\nConnected Users:\n" + user_list)
                    target_user = input("Enter username to chat with: ").strip()
                    rec_ip, rec_port = None, None
                    for line in user_list.split("\n"):
                        info = line.split()
                        if len(info) == 3 and info[0] == target_user:
                            rec_ip, rec_port = info[1], int(info[2])
                            break
                    if rec_ip and rec_port:
                        try:
                            Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            Socket.connect((rec_ip, rec_port))
                            start_p2p_chat(Socket)
                        except ConnectionRefusedError:
                            print(f"{target_user} is not available.")
                    else:
                        print("User not found.")
            elif command == "2":
                client.send("2".encode())
                print("\nDisconnecting...")
                client.close()
                break

run_client()