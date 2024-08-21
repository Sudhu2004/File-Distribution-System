import socket
import time
import threading
import hashlib
import pickle
import os
import ssl

from sender import FileSender
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
