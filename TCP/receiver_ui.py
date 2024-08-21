import tkinter as tk
from tkinter import ttk, messagebox
from receiver_operations import ReceiverClient

class ReceiverGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("File Receiver")
        self.master.geometry("400x300")
        self.login_id = ""
        SERVER_IP = '192.168.0.100'
        UNICAST_PORT = 5005
        PORT_FILE = 'local_port.txt'
        self.client = ReceiverClient(SERVER_IP, UNICAST_PORT, PORT_FILE)
        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill="both")

        self.login_frame = ttk.Frame(self.notebook)
        self.main_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.login_frame, text="Login")
        self.notebook.add(self.main_frame, text="Main", state="disabled")

        self.create_login_widgets()
        self.create_main_widgets()

    def create_login_widgets(self):
        ttk.Label(self.login_frame, text="Login ID:").grid(row=0, column=0, padx=5, pady=5)
        self.login_id_entry = ttk.Entry(self.login_frame)
        self.login_id_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.login_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self.login_frame, text="Login", command=self.login).grid(row=2, column=0, columnspan=2, pady=10)

    def create_main_widgets(self):
        self.group_listbox = tk.Listbox(self.main_frame, width=40, height=10)
        self.group_listbox.pack(pady=10)

        ttk.Button(self.main_frame, text="List Available Groups", command=self.list_groups).pack(pady=5)
        ttk.Button(self.main_frame, text="Join Group", command=self.join_group).pack(pady=5)
        ttk.Button(self.main_frame, text="View My Groups", command=self.view_groups).pack(pady=5)

    def login(self):
        self.login_id = self.login_id_entry.get()
        password = self.password_entry.get()
        check, sysout = self.client.handle_authentication(self.login_id, password)
        if not check:
            messagebox.showwarning("Warning", sysout)
        else:
            self.notebook.tab(self.main_frame, state='normal')  # Enable the main_frame tab
            self.notebook.select(self.main_frame)  # Switch to the main_frame
            messagebox.showinfo("Info", "Login successful!")

    def list_groups(self):
        rec_groups = self.client.request_and_list_groups()
        self.group_listbox.delete(0, tk.END)
        for group in rec_groups:
            self.group_listbox.insert(tk.END, group)

    def join_group(self):
        selected = self.group_listbox.curselection()
        if selected:
            group_ip = self.group_listbox.get(selected[0])
            self.client.request_to_join_group(group_ip, self.login_id)
            messagebox.showinfo("Info", f"Join request sent for group {group_ip}")
        else:
            messagebox.showwarning("Warning", "Please select a group to join")

    def view_groups(self):
        my_groups = self.client.view_my_groups(self.login_id)
        if my_groups:
            messagebox.showinfo("My Groups", f"Groups you are a part of: {', '.join(my_groups)}")
        else:
            messagebox.showinfo("My Groups", "You are not part of any groups")

if __name__ == "__main__":
    root = tk.Tk()
    app = ReceiverGUI(root)
    root.mainloop()
