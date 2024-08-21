import socket
import threading
import logging
import time
from group_management import GroupManager
from sender import FileSender

class FileTransferManager:
    def __init__(self):
        self.manager = GroupManager()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('192.168.0.100', 5005))  # Server address and port
        
        # Start threads to handle authentication and join requests
        threading.Thread(target=self.handle_client_requests, args=(self.sock, self.manager), daemon=True).start()

    def create_group(self, group_name):
        self.manager.create_group(group_name)

    def delete_group(self, group_name):
        self.manager.delete_group(group_name)

    def add_client_to_group(self, group_name, client_name):
        self.manager.add_client_to_group(group_name, client_name)

    def remove_client_from_group(self, group_name, client_name):
        self.manager.remove_client_from_group(group_name, client_name)

    def list_groups(self):
        # groups = self.manager.list_groups()
        # print(f"Available groups: {groups}")
        return self.manager.list_groups() or []

    def add_file_to_pending_list(self, group_name, folder_path):
        folder_path = folder_path.replace('\\', '/')
        self.manager.add_pending_file(group_name, folder_path)

    def send_pending_files(self):
        logging.basicConfig(level=logging.INFO)
        pending_folders = self.manager.get_pending_files()

        def transfer_files_for_group(group_name, file_list, ip_port_list):
            threads = []

            for file_path in pending_folders[group_name]:
                file_sender = FileSender(ip_port_list, folder_path=file_path, group_name=group_name)

                def transfer_file(sender, file_path, max_retries=5):
                    retry_count = 0
                    while retry_count < max_retries:
                        success = sender.start_server()
                        if success:
                            self.manager.clear_pending_file_from_group(group_name, file_path)
                            logging.info(f"Successfully sent file: {file_path} to group: {group_name}")
                            break
                        else:
                            retry_count += 1
                            logging.warning(f"Retry {retry_count} for file: {file_path} in group: {group_name}")
                            clients = self.manager.get_group_members(group_name)
                            ip_port_list = self.manager.clients
                            sender.ip_port_list = self.manager.clients
                            time.sleep(5)
                    if retry_count == max_retries:
                        logging.error(f"Failed to send file: {file_path} to group: {group_name} after {max_retries} attempts")

                thread = threading.Thread(target=transfer_file, args=(file_sender, file_path))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

        group_threads = []
        for group_name, file_list in self.manager.pending_files.items():
            logging.info(f"Starting file transfers for group: {group_name}")
            clients = self.manager.get_group_members(group_name)
            ip_port_list = self.manager.clients

            group_thread = threading.Thread(target=transfer_files_for_group, args=(group_name, file_list, ip_port_list))
            group_threads.append(group_thread)
            group_thread.start()

        for thread in group_threads:
            thread.join()

    def view_pending_files_status(self):
        pending_status = self.manager.get_pending_status()
        print(f"Pending files status: {pending_status}")
        return pending_status

    def view_join_requests(self):
        join_requests = self.manager.get_pending_requests()
        print(f"Pending join requests: {join_requests}")
        return join_requests

    def approve_join_request(self, group_name, client_name):
        self.manager.approve_join_request(group_name, client_name)

    def view_client_groups(self, client_name):
        groups = self.manager.get_client_groups(client_name)
        print(f"Groups for client {client_name}: {groups}")

    def view_group_members(self, group_name):
        members = self.manager.get_group_members(group_name)
        print(f"Current members in group {group_name}: {members}")

    def handle_client_requests(self, sock, manager):
        while True:
            try:
                data, client_address = sock.recvfrom(1024)
                print(f"Received request from client: {client_address}")
                request_type = data.decode().split(',')[0]

                if request_type == "AUTH":
                    # Handle authentication request
                    _, login_id, password = data.decode().split(',')
                    threading.Thread(target=self.handle_authentication, args=(sock, manager, login_id, password, client_address), daemon=True).start()

                elif request_type == "MY_GROUPS":
                    # Handle request to list client's groups
                    _, client_login_id = data.decode().split(',')
                    group_list = manager.client_groups.get(client_login_id, [])
                    group_list_str = ','.join(group_list)
                    sock.sendto(group_list_str.encode(), client_address)

                elif request_type == "REQUEST_GROUPS":
                    # Handle request to list all available groups
                    self.send_group_list(sock, client_address, manager)

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

    def handle_authentication(self, sock, manager, login_id, password, client_address):
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

    def send_group_list(self, sock, client_address, manager):
        groups = manager.list_groups()
        group_list = ",".join(groups).encode()
        print(f"Sending group list: {groups}")
        sock.sendto(group_list, client_address)

    def run(self):
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
                self.create_group(group_name)
            elif choice == "2":
                group_name = input("Enter the group IP to delete: ")
                self.delete_group(group_name)
            elif choice == "3":
                group_name = input("Enter the group IP: ")
                client_name = input("Enter the client IP: ")
                self.add_client_to_group(group_name, client_name)
            elif choice == "4":
                group_name = input("Enter the group IP: ")
                client_name = input("Enter the client IP: ")
                self.remove_client_from_group(group_name, client_name)
            elif choice == "5":
                self.list_groups()
            elif choice == "6":
                group_name = input("Enter the group IP: ")
                folder_path = input("Enter the Folder Path to add to pending list: ")
                self.add_file_to_pending_list(group_name, folder_path)
            elif choice == "7":
                self.send_pending_files()
            elif choice == "8":
                self.view_pending_files_status()
            elif choice == "9":
                self.view_join_requests()
            elif choice == "10":
                group_name = input("Enter the group IP: ")
                client_name = input("Enter the client IP: ")
                self.approve_join_request(group_name, client_name)
            elif choice == "11":
                client_name = input("Enter the client IP: ")
                self.view_client_groups(client_name)
            elif choice == "12":
                group_name = input("Enter the group IP: ")
                self.view_group_members(group_name)
            elif choice == "13":
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")

# Example usage of the FileTransferManager class
if __name__ == "__main__":
    ftm = FileTransferManager()
    
    # Example calls to the functions with parameters
    ftm.create_group("192.168.1.1")
    ftm.add_client_to_group("192.168.1.1", "192.168.1.2")
    ftm.add_file_to_pending_list("192.168.1.1", "/path/to/file")
    ftm.send_pending_files()
    ftm.view_client_groups("192.168.1.2")
    ftm.view_group_members("192.168.1.1")
