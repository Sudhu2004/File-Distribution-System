import socket
import os
from datetime import datetime
import time
from receiver import FileReceiver
import threading

# Function to send authentication request
def send_auth_request(sock, server_address, login_id, password):
    while True:
        credentials = f"AUTH,{login_id},{password}".encode()
        sock.sendto(credentials, server_address)
        sock.settimeout(5)  # Set a timeout for the authentication response
        try:
            response, _ = sock.recvfrom(1024)
            if response == b"AUTH_SUCCESS":
                print("Authentication successful!")
                return True
            else:
                print("Authentication failed! Retrying...")
                return False
        except socket.timeout:
            print("Authentication request timed out. Retrying...")

# Function to request and list available groups from the server
def request_and_list_groups(sock, server_address):
    sock.sendto(b"REQUEST_GROUPS", server_address)
    try:
        response, _ = sock.recvfrom(1024)
        groups = response.decode().split(',')
        print(f"Available groups: {groups}")
    except Exception as e:
        print(f"Error listing groups: {e}")

# Function to request to join a group
def request_to_join_group(sock, server_address, group_ip, login_id):
    request = f"JOIN_GROUP,{group_ip},{login_id}".encode()
    sock.sendto(request, server_address)
    print(f"Join request sent for group {group_ip}.")

# Function to view the groups the receiver is currently part of
def view_my_groups(sock, server_address, login_id):
    request = f"MY_GROUPS,{login_id}".encode()
    sock.sendto(request, server_address)
    try:
        response, _ = sock.recvfrom(1024)
        my_groups = response.decode().split(',')
        print(f"Groups you are a part of: {my_groups}")
        return my_groups
    except Exception as e:
        print(f"Error listing your groups: {e}")
        return []

# C:/Users/sudhr/OneDrive/Desktop/6th Sem
# Main function to interact with the receiver
SERVER_IP = '192.168.0.101'
UNICAST_PORT = 5005
PORT_FILE = 'local_port.txt'
def save_local_port(local_port):
    """Save the local port to a text file."""
    with open(PORT_FILE, 'w') as file:
        file.write(str(local_port))
    print(f"Local port {local_port} saved to {PORT_FILE}")

# Function to start the FileReceiver in a background thread
def start_receiver_in_background(local_port):
    receiver = FileReceiver(local_port)
    receiver_thread = threading.Thread(target=receiver.start_server, daemon=True)
    receiver_thread.start()

# Start the receiver in the background

def main():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (SERVER_IP, UNICAST_PORT)  # Address of the sender server

        # Authentication

        login_id = input("Enter your login ID: ")
        password = input("Enter your password: ")
        if not send_auth_request(sock, server_address, login_id, password):
            return

        local_port = sock.getsockname()[1]
        print(f"Local port used: {local_port}")
        save_local_port(local_port)
        
        time.sleep(1)
        start_receiver_in_background(local_port)

        time.sleep(2)
        
        while True:
            print("\nReceiver Menu:")
            print("1. Request and List Available Groups")
            print("2. Join Group")
            print("3. View My Groups")
            print("4. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                request_and_list_groups(sock, server_address)
            elif choice == "2":
                group_ip = input("Enter the group IP to join: ")
                request_to_join_group(sock, server_address, group_ip, login_id)
            elif choice == "3":
                view_my_groups(sock, server_address, login_id)
            elif choice == "4":
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")
    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
