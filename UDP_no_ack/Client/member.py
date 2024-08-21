import socket
import threading
import os
from datetime import datetime
import time
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
        except socket.timeout:
            print("Authentication request timed out. Retrying...")

# Function to receive a file from the server
def receive_file(group_ip, port):
    CHUNK_SIZE = 1024

    # Create a UDP socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock.bind(('', port))
        
        # Join the multicast group
        mreq = socket.inet_aton(group_ip) + socket.inet_aton('0.0.0.0')
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    except Exception as e:
        print("You are not part of any group\n")

    while True:
        try:
            filename, _ = sock.recvfrom(CHUNK_SIZE)
            original_filename = filename.decode()

            # Get the current timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # Get the current directory where the script is being executed
            current_directory = os.path.dirname(os.path.abspath(__file__))

            # Create the directory named after the group_ip under the current directory if it doesn't exist
            group_directory = os.path.join(current_directory, group_ip)
            if not os.path.exists(group_directory):
                os.makedirs(group_directory)

            # Create the output filename with the timestamp
            output_filename = os.path.join(group_directory, f"{timestamp}_{original_filename}")
            print(f"Output File: {output_filename}")
            with open(output_filename, 'wb') as file:
                while True:
                    chunk, _ = sock.recvfrom(CHUNK_SIZE)
                    if chunk == b"EOF":
                        break
                    file.write(chunk)

            print(f"File {output_filename} received successfully from group {group_ip}.")
        except Exception as e:
            print(f"Error receiving file: {e}")

    sock.close()

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

# Main function to interact with the receiver
def main():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = ('192.168.0.100', 5005)  # Address of the sender server

        # Authentication
        login_id = input("Enter your login ID: ")
        password = input("Enter your password: ")
        if not send_auth_request(sock, server_address, login_id, password):
            return

        # Get the groups the receiver is currently part of
        my_groups = view_my_groups(sock, server_address, login_id)

        # Start a thread to continuously listen for files on each group IP
        for group_ip in my_groups:
            threading.Thread(target=receive_file, args=(group_ip, 5004), daemon=True).start()
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
                my_groups = view_my_groups(sock, server_address, login_id)
                # Start listening to any new groups joined
                for group_ip in my_groups:
                    threading.Thread(target=receive_file, args=(group_ip, 5004), daemon=True).start()
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
