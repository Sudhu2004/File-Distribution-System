

import socket
import time
import threading
import hashlib
import pickle
import os

sent_files = {}

class GroupManager:
    def __init__(self, filename='group_manager_state.pkl'):
        self.filename = filename
        self.lock = threading.Lock()  # Lock for thread-safe access to shared resources
        if os.path.exists(self.filename):
            self.load_state()
        else:
            self.groups = {}
            self.credentials = {"user1": "pass1", "user2": "pass2"}  # Example credentials
            self.pending_files = {}  # Stores files to be sent when receivers are active
            self.join_requests = {}  # Stores join requests for each group
            self.client_groups = {}  # Tracks which clients are in which groups
            self.active_members = {}  # Tracks active members in each group

    def save_state(self):
        with open(self.filename, 'wb') as file:
            pickle.dump({
                'groups': self.groups,
                'credentials': self.credentials,
                'pending_files': self.pending_files,
                'join_requests': self.join_requests,
                'client_groups': self.client_groups,
                'active_members': self.active_members
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

    def create_group(self, group_ip):
        with self.lock:
            if group_ip not in self.groups:
                self.groups[group_ip] = []
                self.pending_files[group_ip] = []
                self.join_requests[group_ip] = []
                self.active_members[group_ip] = 0  # Initialize active member count
                self.save_state()  # Save state after modification
                print(f"Group {group_ip} created.")
            else:
                print(f"Group {group_ip} already exists.")

    def delete_group(self, group_ip):
        with self.lock:
            if group_ip in self.groups:
                del self.groups[group_ip]
                del self.pending_files[group_ip]
                del self.join_requests[group_ip]
                del self.active_members[group_ip]
                for client_ip in list(self.client_groups):
                    if group_ip in self.client_groups[client_ip]:
                        self.client_groups[client_ip].remove(group_ip)
                        if not self.client_groups[client_ip]:
                            del self.client_groups[client_ip]
                self.save_state()  # Save state after modification
                print(f"Group {group_ip} deleted.")
            else:
                print(f"Group {group_ip} does not exist.")

    def add_client_to_group(self, group_ip, client_ip):
        if group_ip in self.groups:
            if client_ip not in self.groups[group_ip]:
                self.groups[group_ip].append(client_ip)
                self.active_members[group_ip] += 1  # Increase active member count
                if client_ip not in self.client_groups:
                    self.client_groups[client_ip] = []
                self.client_groups[client_ip].append(group_ip)
                self.save_state()  # Save state after modification
                print(f"Client {client_ip} added to group {group_ip}.")
            else:
                print(f"Client {client_ip} is already in group {group_ip}.")
        else:
            print(f"Group {group_ip} does not exist.")

    def remove_client_from_group(self, group_ip, client_ip):
        with self.lock:
            if group_ip in self.groups:
                if client_ip in self.groups[group_ip]:
                    self.groups[group_ip].remove(client_ip)
                    self.active_members[group_ip] -= 1  # Decrease active member count
                    if client_ip in self.client_groups:
                        self.client_groups[client_ip].remove(group_ip)
                        if not self.client_groups[client_ip]:
                            del self.client_groups[client_ip]
                    self.save_state()  # Save state after modification
                    print(f"Client {client_ip} removed from group {group_ip}.")
                else:
                    print(f"Client {client_ip} is not in group {group_ip}.")
            else:
                print(f"Group {group_ip} does not exist.")

    def list_groups(self):
        return list(self.groups.keys())

    def authenticate(self, username, password):
        return self.credentials.get(username) == password

    def hash_filename(self, filename):
        """Generate a SHA-256 hash for the given filename."""
        sha256 = hashlib.sha256()
        sha256.update(filename.encode('utf-8'))
        return sha256.hexdigest()

    def add_pending_file(self, group_ip, filename):
        if group_ip not in self.pending_files:
            self.pending_files[group_ip] = []

        file_id = self.hash_filename(filename)
        if any(file_id == self.hash_filename(f) for f in self.pending_files[group_ip]):
            print("Please change the Original File Name")
            return

        with self.lock:
            if group_ip in self.pending_files:
                self.pending_files[group_ip].append(filename)
                self.save_state()  # Save state after modification
                print(f"File {filename} added to pending list for group {group_ip}.")
            else:
                print(f"Group {group_ip} does not exist.")

    def get_pending_files(self, group_ip):
        with self.lock:
            return self.pending_files.get(group_ip, [])

    def clear_pending_files(self, group_ip):
        with self.lock:
            if group_ip in self.pending_files:
                self.pending_files[group_ip] = []
                self.save_state()  # Save state after modification

    def clear_pending_file_from_group(self, group_ip, filename):
        with self.lock:
            if group_ip in self.pending_files:
                if filename in self.pending_files[group_ip]:
                    self.pending_files[group_ip].remove(filename)
                    self.save_state()
    
    def get_pending_status(self):
        with self.lock:
            return {group_ip: len(files) for group_ip, files in self.pending_files.items()}

    def add_join_request(self, group_ip, client_ip):
        with self.lock:
            if group_ip in self.join_requests:
                self.join_requests[group_ip].append(client_ip)
                self.save_state()  # Save state after modification
                print(f"Join request from {client_ip} for group {group_ip} added.")
            else:
                print(f"Group {group_ip} does not exist.")

    def get_join_requests(self, group_ip):
        with self.lock:
            return self.join_requests.get(group_ip, [])

    def approve_join_request(self, group_ip, client_ip):
        if group_ip in self.join_requests and client_ip in self.join_requests[group_ip]:
            self.join_requests[group_ip].remove(client_ip)
            self.add_client_to_group(group_ip, client_ip)
            self.save_state()  # Save state after modification
            print(f"Join request from {client_ip} approved for group {group_ip}.")
        else:
            if group_ip not in self.join_requests:
                print(f"Group IP : {group_ip} not found!")
            elif client_ip not in self.join_requests[group_ip]:
                print(f"Client IP : {client_ip} not found!")

    def get_client_groups(self, client_ip):
        with self.lock:
            return self.client_groups.get(client_ip, [])

    def get_active_member_count(self, group_ip):
        with self.lock:
            return self.active_members.get(group_ip, 0)

    def get_pending_requests(self):
        with self.lock:
            return {group_ip: clients for group_ip, clients in self.join_requests.items() if clients}

    def get_group_members(self, group_ip):
        with self.lock:
            return self.groups.get(group_ip, [])

# Function to check if the receiver is active
def check_receiver_active(receiver_ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as check_sock:
            check_sock.settimeout(5)  # Set a timeout for the ping
            check_sock.sendto(b"PING", (receiver_ip, port))
            response, _ = check_sock.recvfrom(1024)
            return response == b"PONG"
    except Exception as e:
        print(f"Error checking receiver status: {e}")
        return False

def get_file_hash(filename):
    """Generate a hash for the file to uniquely identify it."""
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def send_file(filename, group_ip, file_id, sock, MCAST_PORT, CHUNK_SIZE):
    sock.sendto(f"{filename}|{file_id}".encode(), (group_ip, MCAST_PORT))
    time.sleep(1)
    with open(filename, 'rb') as file:
        while chunk := file.read(CHUNK_SIZE):
            sock.sendto(chunk, (group_ip, MCAST_PORT))
        sock.sendto(b"EOF", (group_ip, MCAST_PORT))

receivers = [] # global because the ACK is handled in a seperate thread function 
def resend_files(manager, group_ip, port, resendlist):
    CHUNK_SIZE = 1024
    ACK_TIMEOUT = 10

    anotherresendlist = set()

    for filename in resendlist:
        try:
            
            receivers.clear()
            time.sleep(3)
            print(f"Resending file {filename} to group {group_ip}")
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            file_id = get_file_hash(filename)
            send_file(filename, group_ip, file_id, sock, port, CHUNK_SIZE)
            

            # while len(receivers) != len(manager.groups[group_ip]):
            #     print(len(receivers))
            #     print(len(manager.groups[group_ip]))
            #     time.sleep(1)

            start = time.time()
            while time.time() - start < 10:
                print(len(receivers))
                if len(receivers) == len(manager.groups[group_ip]):
                    break
                print("Waiting")
                time.sleep(1)

            print(f"ACKs received from {len(receivers)}/{len(manager.groups[group_ip])} clients.")
            if len(receivers) >= len(manager.groups[group_ip]):
                print(f"All clients in group {group_ip} have received the file {filename}.")
                manager.clear_pending_file_from_group(group_ip, filename)
                resendlist.clear()
                break
            else:
                anotherresendlist.add(filename)
                print("Not all clients received the file, resending after a short delay...")
                time.sleep(10)
        except Exception as e:
            print(f"Error resending file: {e}")
        finally:
            sock.close()

        if len(receivers) < len(manager.groups[group_ip]):
            print("Not all users have received the file. Starting a resend thread.")
            # Start a thread to resend the file to those who haven't received it
            resend_thread = threading.Thread(target=resend_files, args=(manager, group_ip, port,resendlist))
            resend_thread.daemon = True
            resend_thread.start()



def send_pending_files(manager, group_ip, port):
    CHUNK_SIZE = 1024
    # Create a UDP socket for sending files
    if group_ip not in sent_files:
        sent_files[group_ip] = set()
    
    pending_files = manager.get_pending_files(group_ip)
    

    resendlist = set()
    totalFiles = 0
    for filename in pending_files:
        try:
            receivers.clear()
            time.sleep(3)
            print(f"Sending pending file {filename} to group {group_ip}")
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)  # Increase receive buffer size

            
            file_id = get_file_hash(filename)
            
            send_file(filename, group_ip, file_id, sock, port, CHUNK_SIZE)
            print("File Sent: waiting for ACK")
            
            # if len(receivers) != len(manager.groups[group_ip]):
            #         print(len(receivers))
            #         print(len(manager.groups[group_ip]))
            #         print("Waiting")
            #         time.sleep(1)

            start = time.time()
            while time.time() - start < 5:
                if len(receivers) == len(manager.groups[group_ip]):
                    print(f"File {filename} sent successfully to all in the group {group_ip}.")
                    break
                print("Waiting")
                time.sleep(1)
                
            print(f"ACKs received from {len(receivers)}/{len(manager.groups[group_ip])} clients.")
            sent_files[group_ip].add(file_id)
            if len(receivers) < len(manager.groups[group_ip]):
                resendlist.add(filename)


        except Exception as e:
            print(f"Error sending file: {e}")
        finally:
            sock.close()

        if len(receivers) < len(manager.groups[group_ip]):
            print("Not all users have received the file. Starting a resend thread.")
            # Start a thread to resend the file to those who haven't received it
            resend_thread = threading.Thread(target=resend_files, args=(manager, group_ip, port,resendlist))
            resend_thread.daemon = True
            resend_thread.start()
        else:
            receivers.clear()
            manager.clear_pending_file_from_group(group_ip, filename)
         
        

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
            print(f"Client Address: {client_address}")
            # Handle different types of requests
          
            if data.decode().startswith("ACK"):
                print(data.decode())
                receivers.append(data.decode())
                print(receivers)
                print(f"Received ACK from {client_address[0]}")
            elif data.decode().startswith("AUTH"):
                parts = data.decode().split(',')
                _, loginId, passWD = parts
                threading.Thread(target=handle_authentication, args=(sock, manager, loginId, passWD, client_address), daemon=True).start()
            elif data.decode().startswith("MY_GROUPS"):
                _, client_login_id = data.decode().split(",")
                # Retrieve the list of groups for the client
                group_list = manager.client_groups.get(client_login_id, [])
                # Join the list into a comma-separated string
                group_list_str = ','.join(group_list)
                # Send the list of groups back to the client
                sock.sendto(group_list_str.encode(), client_address)
            elif data.decode().startswith("REQUEST_GROUPS"):
                send_group_list(sock, client_address, manager)
            elif data.decode().startswith("JOIN_GROUP"):
                group_ip, client_ip = data.decode().split(",")[1:]
                manager.add_join_request(group_ip, client_ip)
            elif data.decode().startswith("REQUEST_MEMBERS"):
                group_ip = data.decode().split(",")[1]
                members = manager.get_group_members(group_ip)
                members_list = ",".join(members).encode()
                sock.sendto(members_list, client_address)
        except Exception as e:
            pass
            # print(f"Error handling client requests: {e}")



# Main function for sender
def main():
    try:
        manager = GroupManager()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('192.168.0.100', 5005))  # Server address and port

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
            print("12. Check Active Receivers")
            print("13. View Group Members")
            print("14. Exit")

            choice = input("Enter your choice: ")

            if choice == "1":
                group_ip = input("Enter the group IP: ")
                manager.create_group(group_ip)
            elif choice == "2":
                group_ip = input("Enter the group IP to delete: ")
                manager.delete_group(group_ip)
            elif choice == "3":
                group_ip = input("Enter the group IP: ")
                client_ip = input("Enter the client IP: ")
                manager.add_client_to_group(group_ip, client_ip)
            elif choice == "4":
                group_ip = input("Enter the group IP: ")
                client_ip = input("Enter the client IP: ")
                manager.remove_client_from_group(group_ip, client_ip)
            elif choice == "5":
                groups = manager.list_groups()
                print(f"Available groups: {groups}")
            elif choice == "6":
                group_ip = input("Enter the group IP: ")
                filename = input("Enter the filename to add to pending list: ")
                manager.add_pending_file(group_ip, filename)
            elif choice == "7":
                group_ip = input("Enter the group IP: ")
                port = 5004  # Port for file transfer
                threading.Thread(target=send_pending_files, args=(manager, group_ip, port), daemon=True).start()
            elif choice == "8":
                pending_status = manager.get_pending_status()
                print(f"Pending files status: {pending_status}")
            elif choice == "9":
                join_requests = manager.get_pending_requests()
                print(f"Pending join requests: {join_requests}")
            elif choice == "10":
                group_ip = input("Enter the group IP: ")
                client_ip = input("Enter the client IP: ")
                manager.approve_join_request(group_ip, client_ip)
            elif choice == "11":
                client_ip = input("Enter the client IP: ")
                groups = manager.get_client_groups(client_ip)
                print(f"Groups for client {client_ip}: {groups}")
            elif choice == "12":
                group_ip = input("Enter the group IP: ")
                port = 5006  # Port for checking receiver status
                if check_receiver_active(group_ip, port):
                    print(f"Receiver {group_ip} is active.")
                else:
                    print(f"Receiver {group_ip} is not active.")
            elif choice == "13":
                group_ip = input("Enter the group IP: ")
                members = manager.get_group_members(group_ip)
                print(f"Current members in group {group_ip}: {members}")
            elif choice == "14":
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