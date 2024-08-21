import socket
import os
from datetime import datetime
import time
from receiver import FileReceiver
import threading

class ReceiverClient:
    def __init__(self, server_ip, unicast_port, port_file):
        self.server_ip = server_ip
        self.unicast_port = unicast_port
        self.port_file = port_file
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (self.server_ip, self.unicast_port)

    def send_auth_request(self, login_id, password):
        while True:
            credentials = f"AUTH,{login_id},{password}".encode()
            self.sock.sendto(credentials, self.server_address)
            self.sock.settimeout(5)  # Set a timeout for the authentication response
            try:
                response, _ = self.sock.recvfrom(1024)
                if response == b"AUTH_SUCCESS":
                    print("Authentication successful!")
                    return {True , "Authentication successful!"}
                else:
                    print("Authentication failed! Retrying...")
                    return {False,"Authentication failed! Retrying..."}
            except socket.timeout:
                print("Authentication request timed out. Retrying...")
                return {False, "Authentication request timed out. Retrying..."}

    def request_and_list_groups(self):
        self.sock.sendto(b"REQUEST_GROUPS", self.server_address)
        try:
            response, _ = self.sock.recvfrom(1024)
            groups = response.decode().split(',')
            print(f"Available groups: {groups}")
            return groups
        except Exception as e:
            print(f"Error listing groups: {e}")
            return None

    def request_to_join_group(self, group_ip, login_id):
        request = f"JOIN_GROUP,{group_ip},{login_id}".encode()
        self.sock.sendto(request, self.server_address)
        print(f"Join request sent for group {group_ip}.")

    def view_my_groups(self, login_id):
        request = f"MY_GROUPS,{login_id}".encode()
        self.sock.sendto(request, self.server_address)
        try:
            response, _ = self.sock.recvfrom(1024)
            my_groups = response.decode().split(',')
            print(f"Groups you are a part of: {my_groups}")
            return my_groups
        except Exception as e:
            print(f"Error listing your groups: {e}")
            return []

    def save_local_port(self, local_port):
        """Save the local port to a text file."""
        with open(self.port_file, 'w') as file:
            file.write(str(local_port))
        print(f"Local port {local_port} saved to {self.port_file}")

    def start_receiver_in_background(self, local_port):
        receiver = FileReceiver(local_port)
        receiver_thread = threading.Thread(target=receiver.start_server, daemon=True)
        receiver_thread.start()

    def display_menu(self):
        print("\nReceiver Menu:")
        print("1. Request and List Available Groups")
        print("2. Join Group")
        print("3. View My Groups")
        print("4. Exit")

    def handle_authentication(self, login_id, password):
        check, sysout = self.send_auth_request(login_id, password)
        if not check:
            return {check, sysout}

        local_port = self.sock.getsockname()[1]
        print(f"Local port used: {local_port}")
        self.save_local_port(local_port)

        time.sleep(1)
        self.start_receiver_in_background(local_port)
        return {check, sysout}

