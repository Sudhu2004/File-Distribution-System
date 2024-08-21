import socket
import threading
import os
from datetime import datetime
import time

# Function to send authentication request
received_files = set()  # A set to keep track of received file IDs

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

# Function to receive a file from the server
def receive_file(ackSock, group_ip, port,server_address):
    CHUNK_SIZE = 1024

    # Create a UDP socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)  # Increase receive buffer size

        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock.bind(('', port))

        # Join the multicast group
        mreq = socket.inet_aton(group_ip) + socket.inet_aton('0.0.0.0')
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    except Exception as e:
        print("You are not part of any group\n")

    while True:
        try:
            
            print("Receive Start")

            # Get the current timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            # Get the current directory where the script is being executed
            current_directory = os.path.dirname(os.path.abspath(__file__))

            # Create the directory named after the group_ip under the current directory if it doesn't exist
            group_directory = os.path.join(current_directory, group_ip)
            if not os.path.exists(group_directory):
                os.makedirs(group_directory)

            metadata, _ = sock.recvfrom(CHUNK_SIZE)
            try:
                # Attempt to decode and split metadata
                decoded_metadata = metadata.decode('utf-8')
                filename, file_id = decoded_metadata.split('|')
            except Exception as e:
                print(f"File {filename} with ID {file_id} already received. Skipping...")
                continue  # Skip to the next iteration if decoding fails

            if file_id in received_files:
                ackSock.sendto(f"ACK{login_id}".encode(),server_address)
                # time.sleep(2)
                continue
            print("Receive End")

            time.sleep(0.5)
            received_files.add(file_id)

            # Create the output filename with the timestamp
            output_filename = os.path.join(group_directory, f"{timestamp}_{filename}")
            print(f"Output File: {output_filename}")
            with open(output_filename, 'wb') as file:
                while True:
                    chunk, _ = sock.recvfrom(CHUNK_SIZE)
                    if chunk == b"EOF":
                        ack_message = "ACK"
                        ackSock.sendto(ack_message.encode(), server_address)
                        break
                    file.write(chunk)
            
            # Send an ACK back to the server with the file ID
            print("ACK Sent")
            # ackSock.sendto(f"ACK|{file_id}".encode(), server_address)
            
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

SERVER_IP = '192.168.0.100'
UNICAST_PORT = 5005
login_id = ""
def main():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (SERVER_IP, UNICAST_PORT)  # Address of the sender server

        # Authentication
        login_id = input("Enter your login ID: ")
        password = input("Enter your password: ")
        print(login_id)
        if not send_auth_request(sock, server_address, login_id, password):
            return

        # Get the groups the receiver is currently part of
        my_groups = view_my_groups(sock, server_address, login_id)

        # Start a thread to continuously listen for files on each group IP
        for group_ip in my_groups:
            threading.Thread(target=receive_file, args=(sock, group_ip, 5004,server_address), daemon=True).start()
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
                    threading.Thread(target=receive_file, args=(sock, group_ip, 5004,server_address), daemon=True).start()
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
