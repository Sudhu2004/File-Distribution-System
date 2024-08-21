# File-Distribution Tool

**File-Distribution Tool** is a robust file-sharing system that supports multiple protocols, designed for efficient and reliable file distribution across networks. This project was developed as part of the Tally CodeBrewers 2024 Hackathon, where we secured the position of 2nd runner-up under the theme "Wizard of System Programming."

## Project Structure

The repository is organized into three main folders, each implementing file distribution using different protocols: `TCP`, `UDP_ACK`, and `UDP_no_ack`.

### 1. TCP

The `TCP` folder contains the implementation of the file-sharing system using the TCP protocol. This implementation ensures reliable transmission of files and folders between a sender (server) and one or more receivers (clients).

- **Main Components**:
  - **sender_gui.py**: Acts as the server-side application with a graphical user interface built using Tkinter. This is the sender program.
  - **receiver_ui.py**: The client-side application with a Tkinter interface. This is the receiver program.
  - **senderop.py, sender.py, Send_files.py**: These files implement the core logic for the sender, managing file selection, and transmission.
  - **receiverop.py, receiver.py, receiver_operations.py**: These files implement the core logic for the receiver, handling the reception and storage of the files.
  - **bandwidth.py**: Monitors and displays the network bandwidth utilized during file transfers.
  - **group_management.py**: Manages group creation, viewing, and deletion, as well as handling client requests to join groups. This script creates a pickle file to store group management data.

- **Usage**:
  1. Run `sender_gui.py` to start the server.
  2. Run `receiver_ui.py` on client machines to start receiving files.
  3. Monitor network bandwidth with `bandwidth.py`.
  4. Manage groups using `group_management.py`.

### 2. UDP_ACK

The `UDP_ACK` folder implements file transfer using the UDP protocol with acknowledgment mechanisms to ensure reliable delivery.

- **Main Components**:
  - **senderop.py**: 
    - Create, view, and delete groups.
    - Add clients to groups and accept client requests to join groups.
    - Add files to the pending list for sending to a group.
  - **receiverop.py**: Handles the receiving end of the file transfer, ensuring that files are correctly acknowledged and received.

- **Usage**:
  1. Run `senderop.py` to manage groups and send files.
  2. Run `receiverop.py` on client machines to receive and acknowledge file transfers.

### 3. UDP_no_ack

The `UDP_no_ack` folder contains an implementation of file transfer using the UDP protocol without any acknowledgment mechanism, making it suitable for less reliable but faster transmission scenarios.

- **Main Components**:
  - **admin.py**: The admin-side script for sending files to clients.
  - **member.py (located in the Client folder)**: The client-side script for receiving files.

- **Usage**:
  1. Run `admin.py` to start sending files.
  2. Run `member.py` on client machines to receive files.

## Getting Started

### Prerequisites

- Python 3.x
- Tkinter library for GUI components
- `pickle` module for group management

### Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/File-Distribution-Tool.git
cd File-Distribution-Tool
```
## Running the Project

### For TCP-based file distribution:

1. Navigate to the `TCP` folder.
2. Run `sender_gui.py` on the server machine.
3. Run `receiver_ui.py` on the client machine(s).

### For UDP with acknowledgment:

1. Navigate to the `UDP_ACK` folder.
2. Run `senderop.py` to manage groups and send files.
3. Run `receiverop.py` on client machines to receive files.

### For UDP without acknowledgment:

1. Navigate to the `UDP_no_ack` folder.
2. Run `admin.py` to send files.
3. Run `member.py` from the `Client` folder to receive files.

