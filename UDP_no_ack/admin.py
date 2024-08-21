import socket
import time
import threading


# Group Management System with Authentication
class GroupManager:
    def __init__(self):
        self.groups = {}
        self.credentials = {"user1": "pass1", "user2": "pass2"}  # Example credentials
        self.pending_files = {}  # Stores files to be sent when receivers are active
        self.join_requests = {}  # Stores join requests for each group
        self.client_groups = {}  # Tracks which clients are in which groups
        self.active_members = {}  # Tracks active members in each group
        self.lock = threading.Lock()  # Lock for thread-safe access to shared resources

    def create_group(self, group_ip):
        with self.lock:
            if group_ip not in self.groups:
                self.groups[group_ip] = []
                self.pending_files[group_ip] = []
                self.join_requests[group_ip] = []
                self.active_members[group_ip] = 0  # Initialize active member count
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
                    print(f"Client {client_ip} removed from group {group_ip}.")
                else:
                    print(f"Client {client_ip} is not in group {group_ip}.")
            else:
                print(f"Group {group_ip} does not exist.")

    def list_groups(self):
        return list(self.groups.keys())

    def authenticate(self, username, password):
        return self.credentials.get(username) == password

    def add_pending_file(self, group_ip, filename):
        with self.lock:
            if group_ip in self.pending_files:
                self.pending_files[group_ip].append(filename)
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

    def get_pending_status(self):
        with self.lock:
            return {group_ip: len(files) for group_ip, files in self.pending_files.items()}

    def add_join_request(self, group_ip, client_ip):
        with self.lock:
            if group_ip in self.join_requests:
                self.join_requests[group_ip].append(client_ip)
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


# Function to send files to active receivers
def send_pending_files(manager, group_ip, port):
    CHUNK_SIZE = 1024
    # Create a UDP socket
    pending_files = manager.get_pending_files(group_ip)
    for filename in pending_files:
        try:
            print(f"Sending pending file {filename} to group {group_ip}")
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            sock.sendto(filename.encode(), (group_ip, port))
            
            with open(filename, 'rb') as file:
                while chunk := file.read(CHUNK_SIZE):
                    sock.sendto(chunk, (group_ip, port))
                # Send EOF to indicate the end of the file
                sock.sendto(b"EOF", (group_ip, port))

            print(f"File {filename} sent successfully to group {group_ip}.")
        except Exception as e:
            print(f"Error sending file: {e}")
        finally:
            sock.close()
    manager.clear_pending_files(group_ip)

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
            else:
                sock.sendto(b"AUTH_FAIL", client_address)
        except Exception as e:
            print(f"Error during authentication: {e}")


# Function to handle client requests including authentication and group operations
def handle_client_requests(sock, manager):
    while True:
        try:
            data, client_address = sock.recvfrom(1024)
            # Handle different types of requests
            if data.decode().startswith("AUTH"):
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