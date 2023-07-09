import socket
import threading
from datetime import datetime

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((self.host, self.port))

        # To keep track of the all the clients
        self.clients = {}
        # To keep track of the clients that are currently logged in
        self.active_clients = []
        # To keep track of the chatrooms
        self.chatrooms = {}
        # To keep track of the client sockets
        self.clients_conn = {}
        # To keep track of the client's chatroom
        self.client_room = {}

    def start(self):
        # Start listening for connections
        self.server_sock.listen()
        print(f"Server started on {self.host}:{self.port}")
        # Start accepting connections
        while True:
            client_sock, client_addr = self.server_sock.accept()
            # Create a new thread to handle the client
            threading.Thread(target=self.handle_client, args=(client_sock,)).start()

    def handle_client(self, client_sock):
        # Keep listening for messages from the client
        while True:
            try:
                # Receive message from client
                data = client_sock.recv(1024).decode()
                if not data:
                    break
                data = data.split("|")
                command = data[0]

                # Handle the different commands
                if command == "REGISTER":
                    username = data[1]
                    password = data[2]

                    # Register the user
                    if self.register_user(username, password) == "SUCCESS":
                        self.clients_conn[username] = []
                        self.clients_conn[username].append(client_sock)
                        client_sock.sendall("SUCCESS".encode())
                    else:
                        client_sock.sendall("ERROR: Username already taken".encode())
                
                # Login the user
                elif command == "LOGIN":
                    username = data[1]
                    password = data[2]
                    message = self.login_user(username, password)
                    if "SUCCESS" in message:
                        self.clients_conn[username].append(client_sock)
                        client_sock.sendall(message.encode())
                    else:
                        client_sock.sendall(message.encode())
                        
                # Logout the user 
                elif command == "LOGOUT":
                    username = data[1]
                    if self.logout_user(username) == True:
                        self.clients_conn[username].remove(client_sock)
                        if len(self.clients_conn[username]) == 0:
                            del self.clients_conn[username]
                        client_sock.sendall("SUCCESS".encode())
                    else:
                        client_sock.sendall("ERROR: User not logged in".encode())

                # Create a chatroom
                elif command == "CREATE_CHATROOM":
                    username = data[1]
                    chatroom_name = data[2]
                    message = self.create_chatroom(username,chatroom_name)
                    client_sock.sendall(message.encode())

                # Join a chatroom
                elif command == "JOIN_CHATROOM":
                    username = data[1]
                    chatroom_name = data[2]
                    message = self.join_chatroom(username, chatroom_name)
                    client_sock.sendall(message.encode())

                # Leave a chatroom
                elif command == "LEAVE_CHATROOM":
                    username = data[1]
                    message = self.leave_chatroom(username)
                    client_sock.sendall(message.encode())

                # View all chatrooms
                elif command == "VIEW_CHATROOMS":
                    message = self.view_chatrooms()
                    print(message)
                    client_sock.sendall(message.encode())

                # Send a message
                elif command == "MESSAGE":
                    username = data[1]
                    message = data[2]
                    if self.send_message(username, message) == "SUCCESS":
                        client_sock.sendall("SUCCESS".encode())
                    else:
                        client_sock.sendall("ERROR: Message not sent".encode())

                # View the current info of the user
                elif command == "CURRENT_INFO":
                    username = data[1]
                    message = self.current_info(username)
                    client_sock.sendall(message.encode())
                
            except Exception as e:
                print(e)
                break

        client_sock.close()

    def register_user(self, username, password):
        # Check if username already exists
        if username in self.clients.keys():
            return "ERROR: Username already taken"

        # Register the user
        self.clients[username] = password
        self.active_clients.append(username)
        print(f"Registered user {username} and joined into the system")
        return "SUCCESS"

    def login_user(self, username, password):
        # Check if username exists
        if username not in self.clients:
            return "ERROR: Username does not exist"
        
        # Check if password is correct
        print(self.clients[username], password)
        if self.clients[username] != password:
            return "ERROR: Incorrect password"
        
        # Login the user
        self.active_clients.append(username)
        print(f"Logged in user {username} and joined into the system")
        if username in self.client_room:
            return f"SUCCESS|{self.client_room[username]}"
        return "SUCCESS"

    def logout_user(self, username):
        # Check if username exists
        if username not in self.clients:
            return False
        
        # Remove the user from all chatrooms
        for chatroom in self.chatrooms.keys():
            if username in self.chatrooms[chatroom]:
                self.chatrooms[chatroom].remove(username)
        
        # Logout the user
        if username in self.client_room:
            self.client_room.pop(username)
        if username in self.active_clients:
            self.active_clients.remove(username)
        print(f"Logged out user {username} and left the system")
        return True

    def create_chatroom(self, username, chatroom_name):
        # Check if username exists
        if username not in self.clients:
            print(f"Client {username} not registered")
            return "Client not registered"
        # Check if chatroom already exists
        elif chatroom_name in self.chatrooms:
            print(f"Chatroom {chatroom_name} already exists")
            return "Chatroom already exists"
        # Check if client is already in another chatroom
        elif username in self.client_room.keys():
            print(f"Client {username} already in another chatroom")
            return "Client already in another chatroom"
        else:
            # Create the chatroom
            self.chatrooms[chatroom_name] = []
            self.client_room[username] = chatroom_name
            self.chatrooms[chatroom_name].append(username)
            print(f"Client {username} created chatroom {chatroom_name}")
            return "SUCCESS"

    def join_chatroom(self, username, chatroom_name):
        # Check if username exists
        if username not in self.clients:
            print(f"Username {username} not registered")
            return "Client not registered"
        # Check if chatroom exists
        elif chatroom_name not in self.chatrooms:
            print(f"Chatroom {chatroom_name} does not exist")
            return "Chatroom does not exist"
        else:
            # Check if client is already in another chatroom
            for chatroom in self.chatrooms.keys():
                if username in self.chatrooms[chatroom]:
                    self.client_room.pop(username)
                    self.chatrooms[chatroom].remove(username)
                    print(f"Client {username} left chatroom {chatroom}")
            # Join the chatroom
            self.client_room[username] = chatroom_name
            self.chatrooms[chatroom_name].append(username)
            print(f"Client {username} joined chatroom {chatroom_name}")
            return "SUCCESS"

    def leave_chatroom(self, username):
        # Check if username exists
        chatroom_name = self.client_room[username]
        # Check if chatroom exists
        if chatroom_name not in self.chatrooms:
            print(f"Chatroom {chatroom_name} does not exist")
            return "Chatroom does not exist"
        # Check if username is in chatroom
        if username not in self.chatrooms[chatroom_name]:
            print(f"Username {username} not in chatroom")
            return "Client not in chatroom"

        # Remove all instances of username from chatroom
        self.client_room.pop(username)
        self.chatrooms[chatroom_name].remove(username)
        print(f"Client {username} left chatroom {chatroom_name}")
        return "SUCCESS"

    def view_chatrooms(self):
        message = ""
        # In the format chatroom_name|username1,username2,username3\n
        for chatroom_name in self.chatrooms.keys():
            message += chatroom_name + "|"
            for username in self.chatrooms[chatroom_name]:
                message += username + ","
            message = message[:-1] + "\n"
        return message


    def send_message(self, username, message):
        # Check if username exists
        if username not in self.clients:
            print(f"Username {username} not registered")
            return "Client not registered"
        # Check if username is in chatroom
        if username not in self.client_room:
            print(f"Username {username} not in chatroom")
            return "Client not in chatroom"

        chatroom_name = self.client_room[username]
        for client in self.chatrooms[chatroom_name]:
            # In the format [datetime] username: message
            for client_ind_conn in self.clients_conn[client]:
                try:
                    client_ind_conn.sendall(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {username}: {message}".encode())
                except:
                    print(f"Client {client} disconnected")
                    self.clients_conn[client].remove(client_ind_conn)
                    self.logout_user(client)
                    continue
                
        print(f"Message sent by {username} in chatroom {chatroom_name}")
        return "SUCCESS"

    def current_info(self, username):
        # Check if username exists
        if username not in self.client_room.keys():
            return "ERROR: Client not in chatroom"
        # Check if username is in chatroom
        chatroom_name = self.client_room[username]
        return f"SUCCESS|{chatroom_name}"


if __name__ == '__main__':
    # Create the chat server
    chat_server = ChatServer('127.0.0.1', 5000)
    # Start the chat server
    chat_server.start()