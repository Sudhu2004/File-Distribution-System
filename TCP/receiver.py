# import socket
# import os
# import struct
# import signal
# import sys
# from datetime import datetime

# class FileReceiver:
#     def __init__(self, server_port=53638):
#         self.server_port = server_port
#         self.save_path = self.generate_save_path()
#         self.sock = None

#     def generate_save_path(self):
#         # Create a directory name with a timestamp
#         timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#         save_path = f"{timestamp}_received_folder"
#         os.makedirs(save_path, exist_ok=True)
#         return save_path

#     def receive_file(self, conn):
#         try:
#             # Read the file name length
#             name_len = struct.unpack('I', conn.recv(4))[0]
#             # Read the file name
#             file_name = conn.recv(name_len).decode()
#             # Full path where the file will be saved
#             full_path = os.path.join(self.save_path, file_name)
#             os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
#             # Read file size
#             file_size = struct.unpack('Q', conn.recv(8))[0]

#             # Receive the file contents
#             with open(full_path, 'wb') as f:
#                 received = 0
#                 while received < file_size:
#                     data = conn.recv(4096)
#                     if not data:
#                         break
#                     f.write(data)
#                     received += len(data)
            
#             print(f"Received file: {file_name}")

#             # Send acknowledgment back to the server
#             conn.send(b'ACK')
#         except Exception as e:
#             print(f"Error receiving file: {e}")

#     def receive_folder(self, conn):
#         try:
#             # Read the number of files
#             num_files = struct.unpack('I', conn.recv(4))[0]
#             for _ in range(num_files):
#                 self.receive_file(conn)
#             return True
#         except Exception as e:
#             print(f"Error receiving folder: {e}")
#             return False

#     def handle_shutdown(self, signal, frame):
#         print("\nShutting down receiver gracefully...")
#         if self.sock:
#             self.sock.close()
#         sys.exit(0)

#     def start_server(self):
#         # Register the shutdown signal handler
#         signal.signal(signal.SIGINT, self.handle_shutdown)

#         self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.sock.bind(('0.0.0.0', self.server_port))
#         while True:
#             self.sock.listen(1)
#             print(f"Receiver listening on port {self.server_port}...")

#             conn, addr = self.sock.accept()
#             print(f"Connection from {addr}")
#             self.receive_folder(conn)
#             conn.close()

# PORT_FILE = 'local_port.txt'

# def read_local_port():
#     """Read the local port from the text file."""
#     if not os.path.exists(PORT_FILE):
#         print(f"No port file found: {PORT_FILE}")
#         return None

#     with open(PORT_FILE, 'r') as file:
#         port = file.read().strip()
#         if port.isdigit():
#             return int(port)
#         else:
#             print(f"Invalid data in port file: {port}")
#             return None


# if __name__ == "__main__":
#     retrieved_port = read_local_port()
#     receiver = FileReceiver(server_port=retrieved_port)  # Change port as needed
#     receiver.start_server()


# import os
# import sys
# import socket
# import signal
# import threading
# import struct
# from datetime import datetime

# class FileReceiver:
#     def __init__(self, server_port=53638):
#         self.server_port = server_port
#         self.save_path = ""
#         self.sock = None

#     def generate_save_path(self,combined_name):
#         try:
#             # Split the combined name into group name and directory name
#             group_name, dir_name = combined_name.split(',', 1)

#             # Create the base directory with the group name
#             base_path = group_name
            
#             if not os.path.exists(base_path):
#                 os.makedirs(base_path)
#                 print(f"Created base directory: {base_path}")

#             # Create a timestamped subdirectory under the base directory
#             timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#             subdirectory_name = f"{timestamp}_{dir_name}"
#             final_path = os.path.join(base_path, subdirectory_name)

#             if not os.path.exists(final_path):
#                 os.makedirs(final_path)
#                 print(f"Created final directory: {final_path}")

#             return final_path
#         except Exception as e:
#             print(f"Error creating directories: {e}")
#             return None

# # C:\Users\sudhr\OneDrive\Desktop\github
# # C:\Users\sudhr\OneDrive\Desktop\CP

#     def receive_file(self, conn):
#         try:
#             # Read the file name length
#             name_len = struct.unpack('I', conn.recv(4))[0]
#             # Read the file name
#             file_name = conn.recv(name_len).decode()
#             # Full path where the file will be saved
#             full_path = os.path.join(self.save_path, file_name)
#             os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
#             # Read file size
#             file_size = struct.unpack('Q', conn.recv(8))[0]

#             # Receive the file contents
#             with open(full_path, 'wb') as f:
#                 received = 0
#                 while received < file_size:
#                     data = conn.recv(4096)
#                     if not data:
#                         break
#                     f.write(data)
#                     received += len(data)
            
#             print(f"Received file: {file_name}")

#             # Send acknowledgment back to the server
#             conn.send(b'ACK')
#         except Exception as e:
#             print(f"Error receiving file: {e}")

#     def receive_folder(self, conn):
#         try:
#             # Receive Group name
#             combined_name_len = struct.unpack('I', conn.recv(4))[0]
#             combined_name = conn.recv(combined_name_len).decode('utf-8')

#             self.save_path = self.generate_save_path(combined_name)
#             if not self.save_path:
#                 print(f"Failed to create save path for group and directory: {combined_name}")
#                 return False

#             # Read the number of files
#             num_files = struct.unpack('I', conn.recv(4))[0]
#             for _ in range(num_files):
#                 self.receive_file(conn)
#             return True
#         except Exception as e:
#             print(f"Error receiving folder: {e}")
#             return False

#     def start_server(self):
#         # Register the shutdown signal handler

#         self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.sock.bind(('0.0.0.0', self.server_port))
#         while True:
#             self.sock.listen(1)
#             print(f"Receiver listening on port {self.server_port}...")

#             conn, addr = self.sock.accept()
#             print(f"Connection from {addr}")
#             self.receive_folder(conn)
#             conn.close()


import os
import socket
import struct
from datetime import datetime
from tqdm import tqdm

class FileReceiver:
    def __init__(self, server_port=53638):
        self.server_port = server_port
        self.save_path = ""

    def generate_save_path(self, combined_name):
        try:
            group_name, dir_name = combined_name.split(',', 1)
            base_path = group_name

            if not os.path.exists(base_path):
                os.makedirs(base_path)
                print(f"Created base directory: {base_path}")

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            subdirectory_name = f"{timestamp}_{dir_name}"
            final_path = os.path.join(base_path, subdirectory_name)

            if not os.path.exists(final_path):
                os.makedirs(final_path)
                print(f"Created final directory: {final_path}")

            return final_path
        except Exception as e:
            print(f"Error creating directories: {e}")
            return None

    # def receive_file(self, conn):
    #     try:
    #         name_len = struct.unpack('I', conn.recv(4))[0]
    #         file_name = conn.recv(name_len).decode()

    #         full_path = os.path.join(self.save_path, file_name)
    #         os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
    #         file_size = struct.unpack('Q', conn.recv(8))[0]

    #         with open(full_path, 'wb') as f:
    #             received = 0
    #             while received < file_size:
    #                 data = conn.recv(4096)
    #                 if not data:
    #                     break
    #                 f.write(data)
    #                 received += len(data)
            
    #         print(f"Received file: {file_name}")

    #         conn.send(b'ACK')
    #     except Exception as e:
    #         print(f"Error receiving file: {e}")

    # def receive_folder(self, conn):
    #     try:
    #         combined_name_len = struct.unpack('I', conn.recv(4))[0]
    #         combined_name = conn.recv(combined_name_len).decode('utf-8')

    #         self.save_path = self.generate_save_path(combined_name)
    #         if not self.save_path:
    #             print(f"Failed to create save path for group and directory: {combined_name}")
    #             return False

    #         num_files = struct.unpack('I', conn.recv(4))[0]
    #         for _ in range(num_files):
    #             self.receive_file(conn)
    #         return True
    #     except Exception as e:
    #         print(f"Error receiving folder: {e}")
    #         return False

    def receive_file(self, conn, pbar):
        try:
            name_len = struct.unpack('I', conn.recv(4))[0]
            file_name = conn.recv(name_len).decode()

            full_path = os.path.join(self.save_path, file_name)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            file_size = struct.unpack('Q', conn.recv(8))[0]

            with open(full_path, 'wb') as f:
                received = 0
                while received < file_size:
                    data = conn.recv(4096)
                    if not data:
                        break
                    f.write(data)
                    received += len(data)
            
            # Dynamic print statement with tqdm progress bar
            pbar.set_description(f"Receiving: {file_name} \n")

            conn.send(b'ACK')
            pbar.update(1)
        except Exception as e:
            print(f"Error receiving file: {e}")

    def receive_folder(self, conn):
        try:
            combined_name_len = struct.unpack('I', conn.recv(4))[0]
            combined_name = conn.recv(combined_name_len).decode('utf-8')

            self.save_path = self.generate_save_path(combined_name)
            if not self.save_path:
                print(f"Failed to create save path for group and directory: {combined_name}")
                return False

            num_files = struct.unpack('I', conn.recv(4))[0]

            # Initialize the progress bar
            with tqdm(total=num_files, desc="Receiving Files", unit="file", dynamic_ncols=True) as pbar:
                for _ in range(num_files):
                    self.receive_file(conn, pbar)
            print()  # To move to the next line after the progress bar
            return True
        except Exception as e:
            print(f"Error receiving folder: {e}")
            return False

    def start_server(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('0.0.0.0', self.server_port))
        while True:
            self.sock.listen(1)
            print(f"Receiver listening on port {self.server_port}...")

            conn, addr = self.sock.accept()
            print(f"Connection from {addr}")
            self.receive_folder(conn)
            conn.close()

if __name__ == "__main__":
    receiver = FileReceiver(server_port=53638)
    receiver.start_server()
