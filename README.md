README - P2P Encrypted Chat Application

Summary of Implementation

This project implements a peer-to-peer (P2P) encrypted chat application using Diffie-Hellman key exchange for secure key generation and AES encryption for message security. The implementation consists of two components: a server that manages user registrations and connections and a client that allows users to initiate secure P2P chats.

Server Implementation

1. Maintains a list of connected users along with their IP addresses and listening ports.

2. Assigns unique usernames.

3. Responds to user requests to fetch the list of available users.

4. Supports user disconnection handling.

5. Allows concurrent connections using multi-threading.

Client Implementation

1. Connects to the server and registers with a unique username.

2. Sets up a listening socket to accept incoming P2P chat requests.

3. Implements Diffie-Hellman key exchange to establish a secure AES key.

4. Uses AES encryption for secure message exchange.

5. Supports sending and receiving encrypted messages.

6. Provides a command-based interface for users to list active connections and initiate chats.

7. Supports ending a chat session by typing EOM

Instructions for Execution

1. Prerequisites

Python 3.x

Install required dependencies using:

pip install pycryptodome

2. Running the Server

Open a terminal and navigate to the project directory.

Run the following command:

python server.py

3. Running the Client

Open a terminal and navigate to the project directory.

for multiple client ,open multiple terminal

Run the following command:

python client.py

4. Follow the on-screen prompts to enter a username and interact with the system.

5. Users can initiate P2P chats by selecting a connected user from the list.

6. Messages are encrypted before transmission and decrypted upon reception.

Shared Code and Discussions

The Diffie-Hellman key exchange and AES encryption implementation are based on standard cryptographic practices.

Parts of the socket programming logic were inspired by open-source tutorials and modified to fit the needs of this application.
