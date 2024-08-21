# import socket
# import os
# import struct
# import time

# class FileSender:
#     def __init__(self, ip_port_list, folder_path='D:/FTPSystem/Server/tcpProtocol'):
#         self.ip_port_list = ip_port_list
#         self.folder_path = folder_path

#     def send_file(self, conn, file_path, base_path):
#         try:
#             # Get relative file path
#             rel_path = os.path.relpath(file_path, base_path)
#             # Send file name length and name
#             conn.send(struct.pack('I', len(rel_path)))
#             conn.send(rel_path.encode())
#             # Send file size
#             file_size = os.path.getsize(file_path)
#             conn.send(struct.pack('Q', file_size))
            
#             # Send file contents
#             with open(file_path, 'rb') as f:
#                 while True:
#                     data = f.read(4096)
#                     if not data:
#                         break
#                     conn.sendall(data)
            
#             # Wait for acknowledgment from client
#             ack = conn.recv(3)
#             if ack == b'ACK':
#                 print(f"Acknowledgment received for file: {rel_path}")
#                 return True
#             else:
#                 print(f"No acknowledgment received for file: {rel_path}")
#                 return False
#         except Exception as e:
#             print(f"Error sending file {rel_path}: {e}")
#             return False

#     def send_folder(self, conn, folder_path):
#         try:
#             # Collect all files in the folder
#             files_to_send = []
#             for root, dirs, files in os.walk(folder_path):
#                 for file in files:
#                     files_to_send.append(os.path.join(root, file))
            
#             # Send the number of files
#             conn.send(struct.pack('I', len(files_to_send)))

#             for file_path in files_to_send:
#                 if not self.send_file(conn, file_path, folder_path):
#                     return False
#             return True
#         except Exception as e:
#             print(f"Error sending folder: {e}")
#             return False

#     def start_server(self):
#         while True:
#             inactive_receivers = []
#             for ip, port in self.ip_port_list:
#                 try:
#                     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                     sock.settimeout(5)  # Set a timeout for the connection attempt
#                     sock.connect((ip, port))
#                     print(f"Connected to {ip}:{port}")
                    
#                     if self.send_folder(sock, self.folder_path):
#                         print(f"Files successfully sent to {ip}:{port}")
#                     else:
#                         inactive_receivers.append((ip, port))
                    
#                     sock.close()
#                 except (socket.timeout, ConnectionRefusedError):
#                     print(f"{ip}:{port} is inactive or unreachable.")
#                     inactive_receivers.append((ip, port))
#                 except Exception as e:
#                     print(f"Error connecting to {ip}:{port}: {e}")
#                     inactive_receivers.append((ip, port))
            
#             if inactive_receivers:
#                 print(f"Retrying inactive receivers after a delay...")
#                 time.sleep(10)  # Wait before retrying inactive receivers
#                 self.ip_port_list = inactive_receivers  # Only retry inactive receivers
#             else:
#                 break  # Exit the loop if all receivers have successfully received the files

# if __name__ == "__main__":
#     # Replace with the actual list of receiver IP addresses and their ports
#     ip_port_list = [('10.20.45.167', 12345), ('10.20.45.170', 12346)]
#     file_sender = FileSender(ip_port_list)
#     file_sender.start_server()

###->>Above code works


# import socket
# import os
# import struct
# import time
# import threading
# from collections import deque
# from pathlib import Path

# class FileSender:
#     def __init__(self, ip_port_list, folder_path='D:/FTPSystem/Server/tcpProtocol',group_name = '', max_retries=3):
#         self.ip_port_list = ip_port_list
#         self.folder_path = folder_path
#         self.max_retries = max_retries
#         self.retry_queue = deque()
#         self.group_name = group_name

#     def send_file(self, conn, file_path, base_path):
#         try:
#             rel_path = os.path.relpath(file_path, base_path)
#             conn.send(struct.pack('I', len(rel_path)))
#             conn.send(rel_path.encode())
#             file_size = os.path.getsize(file_path)
#             conn.send(struct.pack('Q', file_size))
            
#             with open(file_path, 'rb') as f:
#                 while True:
#                     data = f.read(4096)
#                     if not data:
#                         break
#                     conn.sendall(data)
            
#             ack = conn.recv(3)
#             if ack == b'ACK':
#                 print(f"Acknowledgment received for file: {rel_path}")
#                 return True
#             else:
#                 print(f"No acknowledgment received for file: {rel_path}")
#                 return False
#         except Exception as e:
#             print(f"Error sending file {rel_path}: {e}")
#             return False

#     def send_folder(self, conn, folder_path):
#         try:
#                 # Send the group name
#             # Send the group name
#             combined_name = f"{self.group_name},{os.path.basename(folder_path.rstrip('/'))}"

#             # Send the combined name
#             conn.send(struct.pack('I', len(combined_name)))
#             conn.send(combined_name.encode('utf-8'))

#             # Collect all files in the folder
#             files_to_send = []
#             for root, dirs, files in os.walk(folder_path):
#                 for file in files:
#                     files_to_send.append(os.path.join(root, file))

#             # Send the number of files
#             conn.send(struct.pack('I', len(files_to_send)))

#             for file_path in files_to_send:
#                 if not self.send_file(conn, file_path, folder_path):
#                     return False
#             return True
#         except Exception as e:
#             print(f"Error sending folder: {e}")
#             return False

#     def handle_client(self, ip, port, retry_count=0):
#         try:
#             sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             sock.settimeout(5)
#             sock.connect((ip, port))
#             print(f"Connected to {ip}:{port}")
            
#             if self.send_folder(sock, self.folder_path):
#                 print(f"Files successfully sent to {ip}:{port}")
#             else:
#                 print(f"Failed to send files to {ip}:{port}")
            
#             sock.close()
#         except (socket.timeout, ConnectionRefusedError):
#             print(f"{ip}:{port} is inactive or unreachable.")
#             if retry_count < self.max_retries:
#                 print(f"Retrying {ip}:{port} (Attempt {retry_count + 1}) after delay...")
#                 time.sleep(10)
#                 self.handle_client(ip, port, retry_count + 1)
#             else:
#                 print(f"Maximum retries reached for {ip}:{port}. Adding to retry queue.")
#                 self.retry_queue.append((ip, port))
#         except Exception as e:
#             print(f"Error connecting to {ip}:{port}: {e}")

#     def process_retry_queue(self):
#         while self.retry_queue:
#             ip, port = self.retry_queue.popleft()
#             print(f"Retrying {ip}:{port} from retry queue.")
#             self.handle_client(ip, port)

#     def start_server(self):
#         threads = []
#         for ip, port in self.ip_port_list:
#             thread = threading.Thread(target=self.handle_client, args=(ip, port))
#             thread.start()
#             threads.append(thread)
        
#         for thread in threads:
#             thread.join()
        
#         # Process any remaining items in the retry queue after all initial attempts
#         if self.retry_queue:
#             print("Processing retry queue...")
#             self.process_retry_queue()


# if __name__ == "__main__":
#     # Replace with the actual list of receiver IP addresses and their ports
#     ip_port_list = [('10.20.45.167', 12345)]
#     file_sender = FileSender(ip_port_list)
#     file_sender.start_server()


import socket
import os
import struct
from pathlib import Path
import threading
import concurrent.futures
from tqdm import tqdm


class FileSender:
    def __init__(self, clients, folder_path='D:/FTPSystem/Server/tcpProtocol', group_name='', max_retries=3):
        self.clients = clients  # {client_name: (client_ip, client_port)}
        self.folder_path = folder_path
        self.max_retries = max_retries
        self.group_name = group_name

    # def send_file(self, conn, file_path, base_path):
    #     try:
    #         rel_path = os.path.relpath(file_path, base_path)

    #         # Send file name length and name
    #         conn.send(struct.pack('I', len(rel_path)))
    #         conn.send(rel_path.encode())

    #         # Send file size
    #         file_size = os.path.getsize(file_path)
    #         conn.send(struct.pack('Q', file_size))
            
    #         # Send file contents
    #         with open(file_path, 'rb') as f:
    #             while True:
    #                 data = f.read(4096)
    #                 if not data:
    #                     break
    #                 conn.sendall(data)
            
    #         # Wait for acknowledgment from client
    #         ack = conn.recv(3)
    #         if ack == b'ACK':
    #             print(f"Acknowledgment received for file: {rel_path}")
    #             return True
    #         else:
    #             print(f"No acknowledgment received for file: {rel_path}")
    #             return False
    #     except Exception as e:
    #         print(f"Error sending file {rel_path}: {e}")
    #         return False

    # def send_folder(self, conn, folder_path):
    #     try:
    #         # Send the group name and folder name
    #         combined_name = f"{self.group_name},{os.path.basename(folder_path.rstrip('/'))}"
    #         conn.send(struct.pack('I', len(combined_name)))
    #         conn.send(combined_name.encode('utf-8'))

    #         # Collect all files in the folder
    #         files_to_send = []
    #         for root, dirs, files in os.walk(folder_path):
    #             for file in files:
    #                 files_to_send.append(os.path.join(root, file))

    #         # Send the number of files
    #         conn.send(struct.pack('I', len(files_to_send)))

    #         for file_path in files_to_send:
    #             if not self.send_file(conn, file_path, folder_path):
    #                 return False
    #         return True
    #     except Exception as e:
    #         print(f"Error sending folder: {e}")
    #         return False


    def send_file(self, conn, file_path, base_path, pbar):
        try:
            rel_path = os.path.relpath(file_path, base_path)

            # Send file name length and name
            conn.send(struct.pack('I', len(rel_path)))
            conn.send(rel_path.encode())

            # Send file size
            file_size = os.path.getsize(file_path)
            conn.send(struct.pack('Q', file_size))
            
            # Send file contents
            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(4096)
                    if not data:
                        break
                    conn.sendall(data)
            
            # Wait for acknowledgment from client
            ack = conn.recv(3)
            if ack == b'ACK':
                pbar.set_description(f"Receiving: {file_path}\n")
                return True
            else:
                return False
        except Exception as e:
            print(f"Error sending file {rel_path}: {e}")
            return False

    def send_folder(self, conn, folder_path):
        try:
            # Send the group name and folder name
            combined_name = f"{self.group_name},{os.path.basename(folder_path.rstrip('/'))}"
            conn.send(struct.pack('I', len(combined_name)))
            conn.send(combined_name.encode('utf-8'))

            # Collect all files in the folder
            files_to_send = []
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    files_to_send.append(os.path.join(root, file))

            # Send the number of files
            conn.send(struct.pack('I', len(files_to_send)))

            # Initialize the progress bar
            with tqdm(total=len(files_to_send), desc="Sending Files", unit="file", dynamic_ncols=True) as pbar:
                for file_path in files_to_send:
                    if not self.send_file(conn, file_path, folder_path, pbar):
                        return False
                    pbar.update(1)  # Update the progress bar upon receiving acknowledgment
            return True
        except Exception as e:
            print(f"Error sending folder: {e}")
            return False

    def handle_client(self, client_name, client_info):
        ip, port = client_info
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((ip, port))
            print(f"Connected to {client_name} at {ip}:{port}")
            
            if self.send_folder(sock, self.folder_path):
                print(f"Files successfully sent to {client_name} at {ip}:{port}")
            else:
                print(f"Failed to send files to {client_name} at {ip}:{port}")
                return False
            
            sock.close()
            return True
        except (socket.timeout, ConnectionRefusedError):
            print(f"{client_name} at {ip}:{port} is inactive or unreachable.")
            return False
        except Exception as e:
            print(f"Error connecting to {client_name} at {ip}:{port}: {e}")
            return False

    def start_server(self):
        # threads = []
        # success = True

        # for client_name, client_info in self.clients.items():
        #     thread = threading.Thread(target=self.handle_client, args=(client_name, client_info))
        #     thread.start()
        #     threads.append(thread)
        
        # for thread in threads:
        #     thread.join()

        # for client_name, client_info in self.clients.items():
        #     if not self.handle_client(client_name, client_info):
        #         success = False
        #         print(f"Aborting. Failed to send files to {client_name} at {client_info[0]}:{client_info[1]}")
        #         break
        
        # return success

        success = True
        results = []

        # Use ThreadPoolExecutor to handle threading
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Launch threads for each client and store the future objects
            futures = {
                executor.submit(self.handle_client, client_name, client_info): client_name
                for client_name, client_info in self.clients.items()
            }

            # As each thread completes, capture its result
            for future in concurrent.futures.as_completed(futures):
                client_name = futures[future]
                try:
                    result = future.result()  # This will capture the return value of handle_client
                    if not result:
                        success = False
                        print(f"Aborting. Failed to send files to {client_name} at {self.clients[client_name][0]}:{self.clients[client_name][1]}")
                        break  # If a failure is detected, break out of the loop
                    results.append((client_name, result))  # Collect successful results if needed
                except Exception as e:
                    success = False
                    print(f"Exception occurred for {client_name}: {e}")
                    break

        return success

if __name__ == "__main__":
    # Replace with the actual list of receiver IP addresses and their ports
    clients = {
        'Client1': ('10.20.45.167', 12345),
        # Add more clients as needed
    }
    file_sender = FileSender(clients)
    file_sender.start_server()
