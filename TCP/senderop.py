import socket
import time
import threading
import hashlib
import pickle
import os
import ssl

from sender import FileSender
sent_files = {}

class GroupManager:
    def __init__(self, filename='group_manager_state.pkl'):
        self.filename = filename
        self.lock = threading.Lock()
        if os.path.exists(self.filename):
            self.load_state()
        else:
            self.groups = {}  # {group_name: [client_name1, client_name2, ...]}
            self.credentials = {"user1": "pass1", "user2": "pass2"}
            self.pending_files = {}  # {group_name: [filename1, filename2, ...]}
            self.join_requests = {}  # {group_name: [client_name1, client_name2, ...]}
            self.client_groups = {}  # {client_name: [group_name1, group_name2, ...]}
            self.active_members = {}  # {group_name: [client_name1, client_name2, ...]}
            self.clients = {}  # {client_name: (client_ip, client_port)}

    def save_state(self):
        with open(self.filename, 'wb') as file:
            pickle.dump({
                'groups': self.groups,
                'credentials': self.credentials,
                'pending_files': self.pending_files,
                'join_requests': self.join_requests,
                'client_groups': self.client_groups,
                'active_members': self.active_members,
                'clients': self.clients
            }, file)

    def load_state(self):
        with open(self.filename, 'rb') as file:
            state = pickle.load(file)
            self.groups = state['groups']
            self.credentials = state['credentials']
            self.pending_files = state['pending_files']
            self.join_requests = state['join_requests']
            self.client_groups = state['client_groups']
            self.active_members = state['active_members']
            self.clients = state['clients']

    def create_group(self, group_name):
        with self.lock:
            if group_name not in self.groups:
                self.groups[group_name] = []
                self.pending_files[group_name] = []
                self.join_requests[group_name] = []
                self.active_members[group_name] = []
                self.save_state()
                print(f"Group {group_name} created.")
            else:
                print(f"Group {group_name} already exists.")

    def delete_group(self, group_name):
        with self.lock:
            if group_name in self.groups:
                del self.groups[group_name]
                del self.pending_files[group_name]
                del self.join_requests[group_name]
                del self.active_members[group_name]
                for client_name in list(self.client_groups):
                    if group_name in self.client_groups[client_name]:
                        self.client_groups[client_name].remove(group_name)
                        if not self.client_groups[client_name]:
                            del self.client_groups[client_name]
                self.save_state()
                print(f"Group {group_name} deleted.")
            else:
                print(f"Group {group_name} does not exist.")

    def add_client_to_group(self, group_name, client_name):
        if group_name in self.groups:
            if client_name not in self.groups[group_name]:
                self.groups[group_name].append(client_name)
                self.active_members[group_name].append(client_name)
                if client_name not in self.client_groups:
                    self.client_groups[client_name] = []
                self.client_groups[client_name].append(group_name)
                self.save_state()
                print(f"Client {client_name} added to group {group_name}.")
            else:
                print(f"Client {client_name} is already in group {group_name}.")
        else:
            print(f"Group {group_name} does not exist.")

    def remove_client_from_group(self, group_name, client_name):
        with self.lock:
            if group_name in self.groups:
                if client_name in self.groups[group_name]:
                    self.groups[group_name].remove(client_name)
                    self.active_members[group_name].remove(client_name)
                    if client_name in self.client_groups:
                        self.client_groups[client_name].remove(group_name)
                        if not self.client_groups[client_name]:
                            del self.client_groups[client_name]
                    self.save_state()
                    print(f"Client {client_name} removed from group {group_name}.")
                else:
                    print(f"Client {client_name} is not in group {group_name}.")
            else:
                print(f"Group {group_name} does not exist.")

    
    def list_groups(self):
        return list(self.groups.keys())

    def authenticate(self, username, password):
        return self.credentials.get(username) == password

    def hash_filename(self, filename):
        """Generate a SHA-256 hash for the given filename."""
        sha256 = hashlib.sha256()
        sha256.update(filename.encode('utf-8'))
        return sha256.hexdigest()

    def add_pending_file(self, group_name, folder_name):
        if group_name not in self.pending_files:
            self.pending_files[group_name] = []

        file_id = self.hash_filename(folder_name)
        if any(file_id == self.hash_filename(f) for f in self.pending_files[group_name]):
            print("Please change the Original File Name")
            return

        with self.lock:
            if group_name in self.pending_files:
                self.pending_files[group_name].append(folder_name)
                self.save_state()  # Save state after modification
                print(f"File {folder_name} added to pending list for group {group_name}.")
            else:
                print(f"Group {group_name} does not exist.")

    def get_pending_files(self):
        with self.lock:
            return self.pending_files

    def clear_pending_files(self, group_name):
        with self.lock:
            if group_name in self.pending_files:
                self.pending_files[group_name] = []
                self.save_state()  # Save state after modification

    def clear_pending_file_from_group(self, group_name, folder_name):
        with self.lock:
            if group_name in self.pending_files:
                if folder_name in self.pending_files[group_name]:
                    self.pending_files[group_name].remove(folder_name)
                    self.save_state()
    
    def get_pending_status(self):
        with self.lock:
            return {group_name: len(folder_name) for group_name, folder_name in self.pending_files.items()}

    def add_join_request(self, group_name, client_name):
        with self.lock:
            if group_name in self.join_requests:
                self.join_requests[group_name].append(client_name)
                self.save_state()  # Save state after modification
                print(f"Join request from {client_name} for group {group_name} added.")
            else:
                print(f"Group {group_name} does not exist.")

    def get_join_requests(self, group_name):
        with self.lock:
            return self.join_requests.get(group_name, [])

    def approve_join_request(self, group_name, client_name):
        if group_name in self.join_requests and client_name in self.join_requests[group_name]:
            self.join_requests[group_name].remove(client_name)
            self.add_client_to_group(group_name, client_name)
            self.save_state()  # Save state after modification
            print(f"Join request from {client_name} approved for group {group_name}.")
        else:
            if group_name not in self.join_requests:
                print(f"Group IP : {group_name} not found!")
            elif client_name not in self.join_requests[group_name]:
                print(f"Client IP : {client_name} not found!")

    def get_client_groups(self, client_name):
        with self.lock:
            return self.client_groups.get(client_name, [])
        
    def add_client(self, client_name, client_ip, client_port):
        with self.lock:
            self.clients[client_name] = (client_ip, client_port)
            self.save_state()
            print(f"Client {client_name} added with IP {client_ip} and port {client_port}.")

    def get_client_info(self, client_name):
        return self.clients.get(client_name)
    
    def get_active_member_count(self, group_name):
        with self.lock:
            return self.active_members.get(group_name, 0)

    def get_pending_requests(self):
        with self.lock:
            return {group_name: client_name for group_name, client_name in self.join_requests.items() if client_name}

    def get_group_members(self, group_name):
        with self.lock:
            return self.groups.get(group_name, [])


###-> NO Multithreading
        
# def send_pending_files(manager):
#     pending_folders = manager.get_pending_files()
#     for group_name, file_list in manager.pending_files.items():
#         print(f"Group: {group_name}")
#         clients = manager.get_group_members(group_name)
#         ip_port_list = [manager.get_client_info(user) for user in clients]
        
#         file_sender = FileSender(ip_port_list, folder_path=pending_folders[group_name])
#         for files in pending_folders[group_name]:
#             file_sender = FileSender(ip_port_list, folder_path=files)
#             file_sender.start_server()
#             manager.clear_pending_file_from_group(group_name, files)


## Multithreading Only for files
# def send_pending_files(manager):
#     pending_folders = manager.get_pending_files()
    
#     for group_name, file_list in manager.pending_files.items():
#         print(f"Group: {group_name}")
#         clients = manager.get_group_members(group_name)
#         ip_port_list = [manager.get_client_info(user) for user in clients]
        
#         # Create a list to keep track of threads
#         threads = []
        
#         for file_path in pending_folders[group_name]:
#             # Create a new FileSender instance for each file
#             file_sender = FileSender(ip_port_list, folder_path=file_path)
            
#             # Define a target function for the thread
#             def transfer_file(sender, file_path):
#                 sender.start_server()
#                 manager.clear_pending_file_from_group(group_name, file_path)

#             # Create and start a thread for each file
#             thread = threading.Thread(target=transfer_file, args=(file_sender, file_path))
#             threads.append(thread)
#             thread.start()
        
#         # Optionally, wait for all threads to finish
#         for thread in threads:
#             thread.join()


## Multithreading for groups as well as files
import logging

def send_pending_files(manager):
    logging.basicConfig(level=logging.INFO)
    pending_folders = manager.get_pending_files()
    
    def transfer_files_for_group(group_name, file_list, ip_port_list):
        threads = []
        
        for file_path in pending_folders[group_name]:
            file_sender = FileSender(ip_port_list, folder_path=file_path, group_name=group_name)
            
            def transfer_file(sender, file_path, max_retries=5):
                retry_count = 0
                while retry_count < max_retries:
                    success = sender.start_server()
                    if success:
                        manager.clear_pending_file_from_group(group_name, file_path)
                        logging.info(f"Successfully sent file: {file_path} to group: {group_name}")
                        break
                    else:
                        retry_count += 1
                        logging.warning(f"Retry {retry_count} for file: {file_path} in group: {group_name}")
                        clients = manager.get_group_members(group_name)
                        ip_port_list = [manager.get_client_info(user) for user in clients]
                        sender.ip_port_list = manager.clients
                        time.sleep(5)
                if retry_count == max_retries:
                    logging.error(f"Failed to send file: {file_path} to group: {group_name} after {max_retries} attempts")

            thread = threading.Thread(target=transfer_file, args=(file_sender, file_path))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()

    group_threads = []
    for group_name, file_list in manager.pending_files.items():
        logging.info(f"Starting file transfers for group: {group_name}")
        clients = manager.get_group_members(group_name)
        ip_port_list = manager.clients
        
        group_thread = threading.Thread(target=transfer_files_for_group, args=(group_name, file_list, ip_port_list))
        group_threads.append(group_thread)
        group_thread.start()
    
    for thread in group_threads:
        thread.join()


# Function to send available groups to the client
def send_group_list(sock, client_address, manager):
    groups = manager.list_groups()
    group_list = ",".join(groups).encode()
    print(f"Sending group list: {groups}")
    sock.sendto(group_list, client_address)


# Function to handle client authentication
def handle_authentication(sock, manager, login_id, password, client_address):
    while True:
        try:
            if login_id and password:
                if manager.authenticate(login_id, password):
                    sock.sendto(b"AUTH_SUCCESS", client_address)
                    manager.add_client(login_id, client_address[0], client_address[1])
                    print(f"Client {client_address} authenticated successfully.")
                    break  # Stop the thread after successful authentication
                else:
                    sock.sendto(b"WRONG_CRED", client_address)
                    print(f"Client {client_address} authentication failed.")
                    return
            else:
                sock.sendto(b"AUTH_FAIL", client_address)
        except Exception as e:
            print(f"Error during authentication: {e}")



# Function to handle client requests including authentication and group operations
def handle_client_requests(sock, manager):
    while True:
        try:
            data, client_address = sock.recvfrom(1024)
            print(f"Received request from client: {client_address}")
            request_type = data.decode().split(',')[0]

            if request_type == "AUTH":
                # Handle authentication request
                _, login_id, password = data.decode().split(',')
                threading.Thread(target=handle_authentication, args=(sock, manager, login_id, password, client_address), daemon=True).start()
            
            elif request_type == "MY_GROUPS":
                # Handle request to list client's groups
                _, client_login_id = data.decode().split(',')
                group_list = manager.client_groups.get(client_login_id, [])
                group_list_str = ','.join(group_list)
                sock.sendto(group_list_str.encode(), client_address)
            
            elif request_type == "REQUEST_GROUPS":
                # Handle request to list all available groups
                send_group_list(sock, client_address, manager)
            
            elif request_type == "JOIN_GROUP":
                # Handle request to join a group
                _, group_name, client_login_id = data.decode().split(',')
                manager.add_join_request(group_name, client_login_id)
            
            elif request_type == "REQUEST_MEMBERS":
                # Handle request to list members of a group
                _, group_name = data.decode().split(',')
                members = manager.get_group_members(group_name)
                members_list = ','.join(members)
                sock.sendto(members_list.encode(), client_address)

        except Exception as e:
            print(f"Error handling client requests: {e}")


# Main function for sender
def main():
    try:
        manager = GroupManager()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('192.168.0.101', 5005))  # Server address and port
        
        # Start threads to handle authentication and join requests
        threading.Thread(target=handle_client_requests, args=(sock, manager), daemon=True).start()
        
        while True:
            print("\nSender Menu:")
            print("1. Create Group")
            print("2. Delete Group")
            print("3. Add Client to Group")
            print("4. Remove Client from Group")
            print("5. List Groups")
            print("6. Add File to Pending List")
            print("7. Send Pending Files")
            print("8. View Pending Files Status")
            print("9. View Join Requests")
            print("10. Approve Join Request")
            print("11. View Client Groups")
            print("12. View Group Members")
            print("13. Exit")

            choice = input("Enter your choice: ")

            if choice == "1":
                group_name = input("Enter the group IP: ")
                manager.create_group(group_name)
            elif choice == "2":
                group_name = input("Enter the group IP to delete: ")
                manager.delete_group(group_name)
            elif choice == "3":
                group_name = input("Enter the group IP: ")
                client_name = input("Enter the client IP: ")
                manager.add_client_to_group(group_name, client_name)
            elif choice == "4":
                group_name = input("Enter the group IP: ")
                client_name = input("Enter the client IP: ")
                manager.remove_client_from_group(group_name, client_name)
            elif choice == "5":
                groups = manager.list_groups()
                print(f"Available groups: {groups}")
            elif choice == "6":
                group_name = input("Enter the group IP: ")
                folder_path = input("Enter the Folder Path to add to pending list: ")
                folder_path = folder_path.replace('\\', '/')
                manager.add_pending_file(group_name, folder_path)
            elif choice == "7":
                send_pending_files(manager)
            elif choice == "8":
                pending_status = manager.get_pending_status()
                print(f"Pending files status: {pending_status}")
            elif choice == "9":
                join_requests = manager.get_pending_requests()
                print(f"Pending join requests: {join_requests}")
            elif choice == "10":
                group_name = input("Enter the group IP: ")
                client_name = input("Enter the client IP: ")
                manager.approve_join_request(group_name, client_name)
            elif choice == "11":
                client_name = input("Enter the client IP: ")
                groups = manager.get_client_groups(client_name)
                print(f"Groups for client {client_name}: {groups}")
            elif choice == "12":
                group_name = input("Enter the group IP: ")
                members = manager.get_group_members(group_name)
                print(f"Current members in group {group_name}: {members}")
            elif choice == "13":
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
