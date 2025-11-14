import socket
import threading

ConnectedUsers = {}  # Stores username 
User_counter = 1  

#This function handles the communication of the client
def ClientHandle(client_socket, ip, username):
    global User_counter  
    try:
        while True:
            request = client_socket.recv(1024).decode().strip()

            if request.startswith("LISTEN_PORT:"):
                ListenPort(request, username, ip, client_socket)

            elif request == "1":  # Get Users
                GetUsers(username, client_socket)

            elif request == "2":  # EXIT
                Exits(username, client_socket)
                break

            else:
                client_socket.send("Invalid request".encode())

    except Exception as e:
        print(f"[ERROR] Connection error with {username}: {e}")
    finally:
        remove_user(username)  
        client_socket.close()


#This function stores the user ip and port
def ListenPort(request, username, ip, client_socket):

    listen_port = int(request.split(":")[1])

    # Store the user's IP and listening port
    ConnectedUsers[username] = (ip, listen_port)

    # Print user details 
    global User_counter 
    print(f"{User_counter} . {username} is connected from the {ip} and Port Number :{listen_port}")
    User_counter += 1  

    client_socket.send("Listening port is created for the user".encode())


#This fucntion handles the fetching of the connected user list
def GetUsers(username, client_socket):
    
    user_list = "\n".join(
        f"{u} {data[0]} {data[1]}" for u, data in ConnectedUsers.items() if u != username
    )
    client_socket.send(user_list.encode() if user_list else "No users are available right now.".encode())

#This function handles the exit of a client
def Exits(username, client_socket):
    
    print(f" {username} is disconnected.")
    remove_user(username)  # Remove user from list
    client_socket.send("Disconnected".encode())  

#The function removes the user from the list
def remove_user(username):
    
    ConnectedUsers.pop(username, None)

# This fucntion used for client concurrent connections
def register_client(client_socket, ip):
    
    try:
        client_socket.send("Welcome to chat application!".encode())
        username = client_socket.recv(1024).decode().strip()

        if username in ConnectedUsers:
            client_socket.send("Username is already in use. Enter different user name".encode())
            client_socket.close()
        else:
            print(f"{username} is connected from {ip}")
            client_socket.send("hello".encode())
            
            # Start handling client messages
            threading.Thread(target=ClientHandle, args=(client_socket, ip, username), daemon=True).start()
    except Exception as e:
        print(f"Registration is failed: {e}")
        client_socket.close()

#The fucntion for running the server
def run_server():
    
    # Create and configure the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 50000))
    server_socket.listen(5)

    print(" Listening on port 50000...")

    while True:
        client_socket, (ip, _) = server_socket.accept()
        threading.Thread(target=register_client, args=(client_socket, ip), daemon=True).start()

run_server()

