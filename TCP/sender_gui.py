import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from Send_files import FileTransferManager
import os
import shutil
import threading

class SenderGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("File Sender")
        self.master.geometry("500x400")

        self.ftm = FileTransferManager()
        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill="both")

        self.groups_frame = ttk.Frame(self.notebook)
        self.files_frame = ttk.Frame(self.notebook)
        self.requests_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.groups_frame, text="Groups")
        self.notebook.add(self.files_frame, text="Files")
        self.notebook.add(self.requests_frame, text="Requests")

        self.create_groups_widgets()
        self.create_files_widgets()
        self.create_requests_widgets()

    def create_groups_widgets(self):
        self.groups_listbox = tk.Listbox(self.groups_frame, width=40, height=10)
        self.groups_listbox.pack(pady=10)

        ttk.Button(self.groups_frame, text="Create Group", command=self.create_group).pack(pady=5)
        ttk.Button(self.groups_frame, text="Delete Group", command=self.delete_group).pack(pady=5)
        ttk.Button(self.groups_frame, text="Add Client to Group", command=self.add_client_to_group).pack(pady=5)
        ttk.Button(self.groups_frame, text="Remove Client from Group", command=self.remove_client_from_group).pack(pady=5)
        ttk.Button(self.groups_frame, text="Refresh Groups", command=self.refresh_groups).pack(pady=5)

    def create_files_widgets(self):
        self.files_listbox = tk.Listbox(self.files_frame, width=40, height=10)
        self.files_listbox.pack(pady=10)

        ttk.Button(self.files_frame, text="Add File to Pending List", command=self.add_file_to_pending_list).pack(pady=5)
        ttk.Button(self.files_frame, text="Send Pending Files", command=self.send_pending_files).pack(pady=5)
        ttk.Button(self.files_frame, text="View Pending Files Status", command=self.view_pending_files_status).pack(pady=5)

    def create_requests_widgets(self):
        self.requests_listbox = tk.Listbox(self.requests_frame, width=40, height=10)
        self.requests_listbox.pack(pady=10)

        ttk.Button(self.requests_frame, text="View Join Requests", command=self.view_join_requests).pack(pady=5)
        ttk.Button(self.requests_frame, text="Approve Join Request", command=self.approve_join_request).pack(pady=5)

    def create_group(self):
        group_name = simpledialog.askstring("Create Group", "Enter the group name:")
        if group_name:
            self.ftm.create_group(group_name)
            self.refresh_groups()
            messagebox.showinfo("Success", f"Group '{group_name}' created.")

    def delete_group(self):
        selected = self.groups_listbox.curselection()
        if selected:
            group_name = self.groups_listbox.get(selected[0])
            self.ftm.delete_group(group_name)
            self.refresh_groups()
            messagebox.showinfo("Success", f"Group '{group_name}' deleted.")
        else:
            messagebox.showwarning("Warning", "Please select a group to delete")

    def add_client_to_group(self):
        group_name = simpledialog.askstring("Add Client", "Enter the group name:")
        client_name = simpledialog.askstring("Add Client", "Enter the client name:")
        if group_name and client_name:
            self.ftm.add_client_to_group(group_name, client_name)
            messagebox.showinfo("Success", f"Client '{client_name}' added to group '{group_name}'.")

    def remove_client_from_group(self):
        group_name = simpledialog.askstring("Remove Client", "Enter the group name:")
        client_name = simpledialog.askstring("Remove Client", "Enter the client name:")
        if group_name and client_name:
            self.ftm.remove_client_from_group(group_name, client_name)
            messagebox.showinfo("Success", f"Client '{client_name}' removed from group '{group_name}'.")

    def refresh_groups(self):
        self.groups_listbox.delete(0, tk.END)
        groups = self.ftm.list_groups()
        if groups is None:
            print("No groups found or list_groups returned None")
            return
        for group in groups:
            self.groups_listbox.insert(tk.END, group)

    def add_file_to_pending_list(self):
        group_name = simpledialog.askstring("Add File/Folder", "Enter the group name:")
        if not group_name:
            return

        upload_type = simpledialog.askstring("Upload Type", "Enter 'file' for file upload or 'folder' for folder upload:")
        self.files_listbox.delete(0, tk.END)
        self.files_listbox.insert(tk.END, f"{group_name}")
        if upload_type.lower() == 'file':
            file_path = filedialog.askopenfilename(title="Select File to Add")
            if file_path:
                folder_name = os.path.splitext(os.path.basename(file_path))[0]
                folder_path = os.path.join(os.path.dirname(file_path), folder_name)
                os.makedirs(folder_path, exist_ok=True)
                
                new_file_path = os.path.join(folder_path, os.path.basename(file_path))
                shutil.copy2(file_path, new_file_path)
                
                self.ftm.add_file_to_pending_list(group_name, folder_path)
                self.files_listbox.insert(tk.END, f"|-{folder_path}")

                messagebox.showinfo("File Added", f"File {os.path.basename(file_path)} has been added to a new folder and is pending upload.")
        
        elif upload_type.lower() == 'folder':
            folder_path = filedialog.askdirectory(title="Select Folder to Add")
            if folder_path:
                self.ftm.add_file_to_pending_list(group_name, folder_path)
                self.files_listbox.insert(tk.END, f"|-{folder_path}")

                messagebox.showinfo("Folder Added", f"Folder {os.path.basename(folder_path)} has been added and is pending upload.")
        
        else:
            messagebox.showerror("Invalid Input", "Please enter either 'file' or 'folder'.")

    def send_pending_files(self):
        self.ftm.send_pending_files()
        self.files_listbox.delete(0, tk.END)
        messagebox.showinfo("Success", "Pending files sent.")

    def view_pending_files_status(self):
        self.files_listbox.delete(0, tk.END)
        status = self.ftm.view_pending_files_status()
        if status:
            for group, num in status.items():
                self.files_listbox.insert(tk.END, f"{group}: {num}")
        else:
            messagebox.showinfo("No Pending Files","No Files to Send")

    def view_join_requests(self):
        self.requests_listbox.delete(0, tk.END)
        requests = self.ftm.view_join_requests()
        if requests:
            for group, clients in requests.items():
                for client in clients:
                    self.requests_listbox.insert(tk.END, f"{group}: {client}")
        else:
            messagebox.showinfo("No Requests", "No join requests found.")

    def approve_join_request(self):
        selected = self.requests_listbox.curselection()
        if selected:
            request = self.requests_listbox.get(selected[0])
            group, client = request.split(": ")
            self.ftm.approve_join_request(group, client)
            self.view_join_requests()
        else:
            messagebox.showwarning("Warning", "Please select a join request to approve")

if __name__ == "__main__":
    root = tk.Tk()
    app = SenderGUI(root)
    root.mainloop()
