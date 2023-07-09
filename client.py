import socket
import threading

class ChatClient:
    # Constructor
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = None
        self.chatroom = None
        self.logged_in = False

    # Connect to server
    def connect(self):
        self.socket.connect((self.host, self.port))
    
    # Register a new user
    def register(self, username, password):
        # Check if user is already logged in
        if self.logged_in:
            print("You are already logged in.")
            return
        # Send registration request to server
        self.socket.sendall(f"REGISTER|{username}|{password}".encode())
        response = self.socket.recv(1024).decode()

        # Check if registration was successful
        if response == "SUCCESS":
            print("Registration successful!")
            self.username = username
            self.logged_in = True
        else:
            print(f"Registration failed: {response}")
            
    def login(self, username, password):
        # Check if user is already logged in
        if self.logged_in:
            print("You are already logged in.")
            return

        # Send login request to server
        self.socket.sendall(f"LOGIN|{username}|{password}".encode())
        response = self.socket.recv(1024).decode()

        # Check if login was successful
        if response == "SUCCESS":
            print("Login successful!")
            self.username = username
            self.logged_in = True
            return

        # If login failed, check if user is already logged in
        response = response.split("|")
        if response[0] == "SUCCESS":
            print("Login successful!")
            self.username = username
            self.logged_in = True

            if len(response) > 1:
                self.chatroom = response[1]
                print(f"Joined chatroom {self.chatroom}")
        else:
            print(f"Login failed: {response}")

    def logout(self):
        # Check if user is logged in
        if self.logged_in:
            self.socket.sendall(f"LOGOUT|{self.username}".encode())
            response = self.socket.recv(1024).decode()
            # Check if logout was successful
            if "SUCCESS" in response:
                self.logged_in = False
                print("Logout successful.")
            else:
                print("Logout failed.")
        else:
            print("You are not currently logged in.")
    
    def send_message(self, message):
        # Send message to server
        if self.logged_in and self.chatroom:
            self.socket.sendall(f"MESSAGE|{self.username}|{message}".encode())
        # Check if user is logged in
        elif self.logged_in == False:
            print("You must be logged in to send messages.")
            return
        # Check if user is in a chatroom
        elif self.chatroom == None:
            print("You must be in a chatroom to send messages.")
            return

        # Check if message was sent successfully
        response = self.socket.recv(1024).decode()
        if "ERROR: Message not sent" in response:
            print(f"Error: {response}")
        else:
            while "SUCCESS" not in response:
                response = self.socket.recv(1024).decode()
            print("Message sent!")

    
    def receive_messages(self):
        # Receive messages from server
        while True:
            self.timeout = 60
            self.socket.settimeout(self.timeout)
            try:
                data = self.socket.recv(1024).decode()
                if not data:
                    break
                print(data)
            except socket.timeout:
                if self.logged_in == False:
                    break
                else:
                    msg = "Do you want to continue? (y/n): "
                    choice = input(msg)
                    if choice == "y":
                        continue
                    else:
                        break

    def create_chatroom(self, chatroom_name):
        # Send chatroom creation request to server
        if self.logged_in and self.chatroom == None:
            self.socket.sendall(f"CREATE_CHATROOM|{self.username}|{chatroom_name}".encode())
        # Check if user is logged in
        elif self.logged_in == False:
            print("You must be logged in to create chatrooms.")
            return
        # Check if user is in a chatroom
        elif self.chatroom != None:
            print("You must leave your current chatroom before creating a new one.")
            return

        # Check if chatroom was created successfully
        response = self.socket.recv(1024).decode()
        if response == "SUCCESS":
            print("Chatroom created!")
            self.chatroom = chatroom_name
        else:
            print("Chatroom creation failed.")

    def join_chatroom(self, chatroom_name):
        # Send chatroom join request to server
        if self.logged_in and self.chatroom == None:
            self.socket.sendall(f"JOIN_CHATROOM|{self.username}|{chatroom_name}".encode())
        # Check if user is logged in
        elif self.logged_in == False:
            print("You must be logged in to join chatrooms.")
            return
        # Check if user is in a chatroom
        elif self.chatroom != None:
            print("You must leave your current chatroom before joining a new one.")
            return
        
        # Check if chatroom was joined successfully
        response = self.socket.recv(1024).decode()
        print(response)
        if response == "SUCCESS":
            print("Chatroom joined!")
            self.chatroom = chatroom_name
        else:
            print("Chatroom join failed.")

    def leave_chatroom(self):
        # Send chatroom leave request to server
        if self.logged_in and self.chatroom:
            self.socket.sendall(f"LEAVE_CHATROOM|{self.username}|{self.chatroom}".encode())
        # Check if user is logged in
        elif self.logged_in == False:
            print("You must be logged in to leave chatrooms.")
            return
        # Check if user is in a chatroom
        elif self.chatroom == None:
            print("You must be in a chatroom to leave it.")
            return

        # Check if chatroom was left successfully
        response = self.socket.recv(1024).decode()
        if response == "SUCCESS":
            print("Chatroom left!")
            self.chatroom = None
        else:
            print("Chatroom leave failed.")

    def view_chatrooms(self):
        # Send chatroom view request to server
        self.socket.sendall(f"VIEW_CHATROOMS".encode())
        response = self.socket.recv(1024).decode()
        print(response)

    def print_current_info(self):
        # Send current info request to server
        print(f"Username: {self.username}")
        self.socket.sendall(f"CURRENT_INFO|{self.username}".encode())
        response = self.socket.recv(1024).decode()
        if "SUCCESS" in response:
            self.chatroom = response.split('|')[1]
            print(f"Chatroom: {response.split('|')[1]}")
        else:
            self.chatroom = None
            print("Chatroom: None")

        

if __name__ == '__main__':
    client = ChatClient()
    client.connect()

    # Make a better menu
    print("=====================================")
    print("Welcome to the Chat Arena!")
    print("=====================================")
    while True:
        print("\nWhat would you like to do?")
        print("-------------------------------------")
        print("1. Register")
        print("2. Login")
        print("3. Send message")
        print("4. Create chatroom")
        print("5. Join chatroom")
        print("6. Leave chatroom")
        print("7. Receive messages")
        print("8. View chatrooms")
        print("9. Print current info")
        print("10. Logout")
        print("11. Exit\n")

        choice = input("Enter your choice: ")

        # Check if user wants to exit
        if choice == "1":
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            client.register(username, password)
        elif choice == "2":
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            client.login(username, password)
        elif choice == "3":
            message = input("Enter your message: ")
            client.send_message(message)
        elif choice == "4":
            chatroom = input("Enter the name of the chatroom: ")
            client.create_chatroom(chatroom)
        elif choice == "5":
            chatroom = input("Enter the name of the chatroom: ")
            client.join_chatroom(chatroom)
        elif choice == "6":
            client.leave_chatroom()
        elif choice == "7":
            client.receive_messages()
        elif choice == "8":
            client.view_chatrooms()
        elif choice == "9":
            client.print_current_info()
        elif choice == "10":
            client.logout()
        elif choice == "11":
            if client.logged_in:
                client.logout()
            client.socket.close()
            break
        else:
            print("Invalid choice.")

        
    
