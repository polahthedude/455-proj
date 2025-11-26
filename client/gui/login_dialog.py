"""Login and registration dialog"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yaml
import threading
from queue import Queue
from pathlib import Path
from client.api_client import APIClient
from client.auth_manager import AuthManager

 # ...existing code...

import socket
from typing import Optional, Any


class LoginDialog:
    """Login and registration dialog"""
    
    def __init__(self, parent=None):
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("CSC-455-Homelab-Project-Cloud - Login")
        self.window.geometry("450x600")
        self.window.resizable(True, True)
        self.window.minsize(400, 500)
        
        # Load config
        config_path = Path(__file__).parent.parent.parent / 'config.yaml'
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Default server IPs for dropdown
        self.default_server_ips = [
            "127.0.0.1:5000",
            "localhost:5000",
            "192.168.1.100:5000"
        ]
        self.server_ip_history = self.default_server_ips.copy()
        self.selected_server_ip = tk.StringVar(value=self.default_server_ips[0])
        self.api_client = None  # Will be set on login/check
        self.auth_manager = AuthManager()
        
        self.result = None
        self.task_queue = Queue()
        self.setup_ui()
        self._process_queue()
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup UI components"""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="🔐 CSC-455-Homelab-Project-Cloud",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Subtitle
        subtitle_label = ttk.Label(
            main_frame,
            text="Secure encrypted storage",
            font=("Arial", 10)
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Login tab
        self.login_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.login_frame, text="Login")
        self.setup_login_tab()
        
        # Register tab
        self.register_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.register_frame, text="Register")
        self.setup_register_tab()
        
        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="",
            foreground="blue"
        )
        self.status_label.pack()
    
    def setup_login_tab(self):
        """Setup login tab"""
        # Server IP dropdown
        ttk.Label(self.login_frame, text="Server IP:").pack(anchor=tk.W, pady=(10, 5))
        self.server_ip_combo = ttk.Combobox(
            self.login_frame,
            textvariable=self.selected_server_ip,
            values=self.server_ip_history,
            width=40
        )
        self.server_ip_combo.pack(fill=tk.X, pady=(0, 10))
        # Username
        ttk.Label(self.login_frame, text="Username:").pack(anchor=tk.W, pady=(10, 5))
        self.login_username = ttk.Entry(self.login_frame, width=40)
        self.login_username.pack(fill=tk.X, pady=(0, 10))
        
        # Password
        ttk.Label(self.login_frame, text="Password:").pack(anchor=tk.W, pady=(0, 5))
        self.login_password = ttk.Entry(self.login_frame, width=40, show="*")
        self.login_password.pack(fill=tk.X, pady=(0, 20))
        
        # Remember me
        self.remember_var = tk.BooleanVar()
        ttk.Checkbutton(
            self.login_frame,
            text="Remember me",
            variable=self.remember_var
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Login button
        login_btn = ttk.Button(
            self.login_frame,
            text="Login",
            command=self.handle_login,
            width=20
        )
        login_btn.pack(pady=(0, 10))
        
        # Check server button
        check_btn = ttk.Button(
            self.login_frame,
            text="Check Server Connection",
            command=self.check_server_connection,
            width=20
        )
        check_btn.pack(pady=(0, 5))
        
        # Bind Enter key
        self.login_password.bind('<Return>', lambda e: self.handle_login())
    
    def setup_register_tab(self):
        """Setup register tab with scrollbar"""
        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(self.register_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.register_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Now add all content to scrollable_frame instead of register_frame
        # Username
        ttk.Label(scrollable_frame, text="Username:").pack(anchor=tk.W, pady=(10, 5), padx=10)
        self.register_username = ttk.Entry(scrollable_frame, width=40)
        self.register_username.pack(fill=tk.X, pady=(0, 10), padx=10)
        
        # Email
        ttk.Label(scrollable_frame, text="Email:").pack(anchor=tk.W, pady=(0, 5), padx=10)
        self.register_email = ttk.Entry(scrollable_frame, width=40)
        self.register_email.pack(fill=tk.X, pady=(0, 10), padx=10)
        
        # Password
        ttk.Label(scrollable_frame, text="Password:").pack(anchor=tk.W, pady=(0, 5), padx=10)
        self.register_password = ttk.Entry(scrollable_frame, width=40, show="*")
        self.register_password.pack(fill=tk.X, pady=(0, 10), padx=10)
        
        # Confirm password
        ttk.Label(scrollable_frame, text="Confirm Password:").pack(anchor=tk.W, pady=(0, 5), padx=10)
        self.register_confirm = ttk.Entry(scrollable_frame, width=40, show="*")
        self.register_confirm.pack(fill=tk.X, pady=(0, 10), padx=10)
        
        # Password requirements
        req_text = "Password Requirements:\n• At least 12 characters\n• Uppercase and lowercase letters\n• Numbers\n• Special characters (!@#$%^&*)"
        req_label = ttk.Label(
            scrollable_frame,
            text=req_text,
            font=("Arial", 9),
            foreground="#666666",
            justify=tk.LEFT
        )
        req_label.pack(anchor=tk.W, pady=(5, 20), padx=10)
        
        # Register button
        register_btn = ttk.Button(
            scrollable_frame,
            text="Register Account",
            command=self.handle_register,
            width=25
        )
        register_btn.pack(pady=(0, 20))
        
        # Info label
        info_label = ttk.Label(
            scrollable_frame,
            text="Your encryption keys will be generated\nautomatically during registration.",
            font=("Arial", 8),
            foreground="#888888",
            justify=tk.CENTER
        )
        info_label.pack(pady=(0, 10))
    
    def check_server_connection(self):
        """Check if server is reachable"""
        # Update APIClient with selected server IP
        server_ip = self.selected_server_ip.get().strip()
        if not server_ip:
            messagebox.showerror("Error", "Please enter a server IP and port (e.g. 192.168.1.100:5000)")
            return
        # Add to history if not present
        if server_ip not in self.server_ip_history:
            self.server_ip_history.insert(0, server_ip)
            self.server_ip_combo['values'] = self.server_ip_history
        self.selected_server_ip.set(server_ip)
        self.api_client = APIClient(f"http://{server_ip}")
        self.status_label.config(text="Checking server...", foreground="blue")
        self.window.update()
        
        if self.api_client.health_check():
            self.status_label.config(text="Server is online ✓", foreground="green")
            self.server_ip_combo.set(server_ip)
            messagebox.showinfo("Connection Success", "Successfully connected to server!\n\nServer is running and ready to accept requests.")
        else:
            self.status_label.config(text="Server is offline ✗", foreground="red")
            messagebox.showerror("Connection Failed", "Cannot connect to server.\n\nPlease check:\n• Server is running (use the provided start script or Docker)\n• Server address is correct\n• No firewall blocking port 5000\n\nDefault server: http://your-server-ip:5000")
    
    def handle_login(self):
        """Handle login button click"""
        # Update APIClient with selected server IP
        server_ip = self.selected_server_ip.get().strip()
        if not server_ip:
            messagebox.showerror("Error", "Please enter a server IP and port (e.g. 192.168.1.100:5000)")
            return
        # Add to history if not present
        if server_ip not in self.server_ip_history:
            self.server_ip_history.insert(0, server_ip)
            self.server_ip_combo['values'] = self.server_ip_history
        self.selected_server_ip.set(server_ip)
        self.api_client = APIClient(f"http://{server_ip}")
        username = self.login_username.get().strip()
        password = self.login_password.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return
        
        self.status_label.config(text="Connecting to server...", foreground="blue")
        self.window.update()
        
        # Call API
        success, response = self.api_client.login(username, password)
        
        if success:
            self.status_label.config(text="Loading encryption keys...", foreground="blue")
            self.window.update()
            self.server_ip_combo.set(server_ip)
            
            # Login to auth manager
            token = response.get('token')
            user_id = response.get('user', {}).get('id')
            
            if self.auth_manager.login(username, password, token, user_id):
                self.status_label.config(text="Login successful!", foreground="green")
                self.result = {
                    'auth_manager': self.auth_manager,
                    'api_client': self.api_client
                }
                self.window.after(500, self.window.destroy)
            else:
                self.status_label.config(text="Error loading encryption keys", foreground="red")
                
                # Check if keys exist
                if self.auth_manager.key_manager.keys_exist():
                    error_msg = (
                        "Could not decrypt encryption keys.\n\n"
                        "This usually means:\n"
                        "• Wrong password (use the SAME password you used during registration)\n"
                        "• Corrupted key files\n\n"
                        f"Keys are located at:\n{self.auth_manager.key_manager.keys_dir}\n\n"
                        "You may need to delete these files and register again."
                    )
                else:
                    error_msg = (
                        "No encryption keys found.\n\n"
                        "This is your first time logging in.\n"
                        "Keys should have been created during registration.\n\n"
                        f"Expected location:\n{self.auth_manager.key_manager.keys_dir}"
                    )
                
                messagebox.showerror("Login Error", error_msg)
        else:
            message = response.get('message', 'Login failed')
            self.status_label.config(text="", foreground="red")
            
            # Show detailed error based on type
            if response.get('auth_error'):
                messagebox.showerror(
                    "Authentication Failed",
                    f"{message}\n\n"
                    "Please check:\n"
                    "• Username and password are correct\n"
                    "• Account exists (try registering if new user)\n"
                    "• Server is running"
                )
            elif response.get('connection_error'):
                messagebox.showerror(
                    "Connection Error",
                    f"{message}\n\n"
                    "Please ensure:\n"
                    "• Server is running (use the provided start script or Docker)\n"
                    "• Server address is correct in config.yaml\n"
                    "• No firewall blocking the connection"
                )
            elif response.get('timeout_error'):
                messagebox.showerror(
                    "Timeout Error",
                    f"{message}\n\n"
                    "The server may be overloaded or not responding.\n"
                    "Please try again in a moment."
                )
            else:
                messagebox.showerror("Login Error", message)
    
    def _process_queue(self):
        """Process tasks from background threads safely on main thread"""
        try:
            while not self.task_queue.empty():
                task = self.task_queue.get_nowait()
                task()
        except:
            pass
        
        # Schedule next check
        if self.window.winfo_exists():
            self.window.after(100, self._process_queue)
    
    def handle_register(self):
        """Handle register button click"""
        username = self.register_username.get().strip()
        email = self.register_email.get().strip()
        password = self.register_password.get()
        confirm = self.register_confirm.get()
        
        if not all([username, email, password, confirm]):
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        # Disable register button to prevent double-clicks
        register_btn = None
        for widget in self.register_frame.winfo_children():
            if isinstance(widget, tk.Canvas):
                # Find the button in the scrollable frame
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Frame):
                        for subchild in child.winfo_children():
                            if isinstance(subchild, ttk.Button) and subchild.cget('text') == 'Register Account':
                                register_btn = subchild
                                break
        
        if register_btn:
            register_btn.config(state='disabled')
        
        # Run registration in background thread to prevent GUI freeze
        def register_thread():
            try:
                # Update status on main thread
                self.task_queue.put(lambda: self.status_label.config(text="Generating encryption keys...", foreground="blue"))
                
                # Generate keys and get public key
                public_key = self.auth_manager.get_public_key()
                if not public_key:
                    # Generate new keys using auth_manager's crypto handler and key manager
                    print(f"[REGISTER] Generating new keys for {username}...")
                    private_key, public_key = self.auth_manager.crypto_handler.generate_rsa_keypair()
                    # Save keys using auth_manager's key manager
                    print(f"[REGISTER] Saving keys to: {self.auth_manager.key_manager.keys_dir}")
                    self.auth_manager.key_manager.save_keys(private_key, public_key, password)
                    
                    # Verify keys were saved
                    if self.auth_manager.key_manager.keys_exist():
                        print(f"[REGISTER] Keys saved successfully")
                    else:
                        print(f"[REGISTER] WARNING: Keys were NOT saved properly!")
                        raise Exception("Failed to save encryption keys")
                else:
                    print(f"[REGISTER] Using existing public key")
                
                # Update status on main thread
                self.task_queue.put(lambda: self.status_label.config(text="Registering account...", foreground="blue"))
                
                # Call API
                success, response = self.api_client.register(username, email, password, public_key)
                
                # Handle result on main thread
                def handle_result():
                    if register_btn:
                        register_btn.config(state='normal')
                    
                    if success:
                        self.status_label.config(text="Registration successful! Please login.", foreground="green")
                        messagebox.showinfo(
                            "Registration Successful",
                            f"Account created for {username}!\n\n"
                            "Your encryption keys have been generated and saved securely.\n\n"
                            "Please login to start uploading files."
                        )
                        self.notebook.select(0)  # Switch to login tab
                        self.login_username.delete(0, tk.END)
                        self.login_username.insert(0, username)
                        self.login_password.focus()
                    else:
                        message = response.get('message', 'Registration failed')
                        self.status_label.config(text="", foreground="red")
                        
                        # Show detailed error
                        if response.get('connection_error'):
                            messagebox.showerror(
                                "Connection Error",
                                f"{message}\n\n"
                                "Cannot reach the server.\n"
                                "Please make sure the server is running."
                            )
                        else:
                            messagebox.showerror("Registration Error", message)
                
                self.task_queue.put(handle_result)
                
            except Exception as e:
                def handle_error():
                    if register_btn:
                        register_btn.config(state='normal')
                    self.status_label.config(text="", foreground="red")
                    messagebox.showerror(
                        "Registration Error",
                        f"An unexpected error occurred:\n{str(e)}\n\n"
                        "Please try again or contact support."
                    )
                
                self.task_queue.put(handle_error)
        
        # Start background thread
        thread = threading.Thread(target=register_thread, daemon=True)
        thread.start()
    
    def show(self):
        """Show dialog and wait for result"""
        self.window.wait_window()
        return self.result


class CloudStorageGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cloud Storage Client")
        self.root.geometry("800x600")
        
        # Load config
        self.config = self.load_config()
        # APIClient is used for server communication
        self.client: Optional[Any] = None
        self.connected = False
        
        self.create_widgets()
        
    def load_config(self):
        config_path = Path("config.yaml")
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {
            'server': {
                'host': 'localhost',
                'port': 8080
            }
        }
    
    def save_config(self):
        """Save current connection settings to config"""
        self.config['server']['host'] = self.host_entry.get()
        self.config['server']['port'] = int(self.port_entry.get())
        
        config_path = Path("config.yaml")
        with open(config_path, 'w') as f:
            yaml.dump(self.config, f)
    
    def create_widgets(self):
        # Connection frame
        conn_frame = ttk.LabelFrame(self.root, text="Server Connection", padding=10)
        conn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(conn_frame, text="Server IP:").grid(row=0, column=0, sticky="w", padx=5)
        self.host_entry = ttk.Entry(conn_frame, width=30)
        self.host_entry.insert(0, self.config['server']['host'])
        self.host_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(conn_frame, text="Port:").grid(row=0, column=2, sticky="w", padx=5)
        self.port_entry = ttk.Entry(conn_frame, width=10)
        self.port_entry.insert(0, str(self.config['server']['port']))
        self.port_entry.grid(row=0, column=3, padx=5)
        
        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self.connect_to_server)
        self.connect_btn.grid(row=0, column=4, padx=5)
        
        # Debug button
        self.debug_btn = ttk.Button(conn_frame, text="🔍 Debug", command=self.show_debug_info)
        self.debug_btn.grid(row=0, column=5, padx=5)
        
        self.status_label = ttk.Label(conn_frame, text="Not connected", foreground="red")
        self.status_label.grid(row=1, column=0, columnspan=6, pady=5)
        
        # File operations frame
        ops_frame = ttk.LabelFrame(self.root, text="File Operations", padding=10)
        ops_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(ops_frame)
        btn_frame.pack(fill="x", pady=5)
        
        ttk.Button(btn_frame, text="Upload File", command=self.upload_file).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Download File", command=self.download_file).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete File", command=self.delete_file).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Refresh List", command=self.refresh_file_list).pack(side="left", padx=5)
        
        # File list
        list_frame = ttk.Frame(ops_frame)
        list_frame.pack(fill="both", expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.file_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.file_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        # Status bar
        self.progress_label = ttk.Label(self.root, text="Ready", relief="sunken")
        self.progress_label.pack(fill="x", side="bottom", padx=10, pady=5)
    
    def connect_to_server(self):
        host = self.host_entry.get().strip()
        port = self.port_entry.get().strip()
        
        if not host or not port:
            messagebox.showerror("Error", "Please enter both server IP and port")
            return
        
        try:
            port = int(port)
            self.client = APIClient(f"http://{host}:{port}")
            
            # Test connection
            files = self.client.list_files()
            
            self.connected = True
            self.status_label.config(text=f"Connected to {host}:{port}", foreground="green")
            self.connect_btn.config(text="Disconnect", command=self.disconnect_from_server)
            
            # Save config for next time
            self.save_config()
            
            # Populate file list
            self.refresh_file_list()
            
            messagebox.showinfo("Success", f"Connected to server at {host}:{port}")
            
        except ValueError:
            messagebox.showerror("Error", "Port must be a number")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to server:\n{str(e)}")
            self.connected = False
            self.status_label.config(text="Not connected", foreground="red")
    
    def disconnect_from_server(self):
        self.client = None
        self.connected = False
        self.status_label.config(text="Not connected", foreground="red")
        self.connect_btn.config(text="Connect", command=self.connect_to_server)
        self.file_listbox.delete(0, tk.END)
        messagebox.showinfo("Disconnected", "Disconnected from server")
    
    def check_connection(self):
        if not self.connected or not self.client:
            messagebox.showwarning("Not Connected", "Please connect to a server first")
            return False
        return True
    
    def upload_file(self):
        if not self.check_connection():
            return
        
        file_path = filedialog.askopenfilename(title="Select file to upload")
        if not file_path:
            return
        
        def upload_thread():
            try:
                self.progress_label.config(text=f"Uploading {Path(file_path).name}...")
                self.client.upload_file(file_path)
                self.root.after(0, lambda: self.progress_label.config(text="Upload complete"))
                self.root.after(0, self.refresh_file_list)
                self.root.after(0, lambda: messagebox.showinfo("Success", "File uploaded successfully"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Upload failed:\n{str(e)}"))
                self.root.after(0, lambda: self.progress_label.config(text="Upload failed"))
        
        threading.Thread(target=upload_thread, daemon=True).start()
    
    def download_file(self):
        if not self.check_connection():
            return
        
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file to download")
            return
        
        filename = self.file_listbox.get(selection[0])
        save_path = filedialog.asksaveasfilename(
            title="Save file as",
            initialfile=filename,
            defaultextension=Path(filename).suffix
        )
        
        if not save_path:
            return
        
        def download_thread():
            try:
                self.progress_label.config(text=f"Downloading {filename}...")
                self.client.download_file(filename, save_path)
                self.root.after(0, lambda: self.progress_label.config(text="Download complete"))
                self.root.after(0, lambda: messagebox.showinfo("Success", f"File downloaded to:\n{save_path}"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Download failed:\n{str(e)}"))
                self.root.after(0, lambda: self.progress_label.config(text="Download failed"))
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def delete_file(self):
        if not self.check_connection():
            return
        
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file to delete")
            return
        
        filename = self.file_listbox.get(selection[0])
        
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete:\n{filename}"):
            return
        
        try:
            self.client.delete_file(filename)
            self.refresh_file_list()
            self.progress_label.config(text=f"Deleted {filename}")
            messagebox.showinfo("Success", "File deleted successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Delete failed:\n{str(e)}")
    
    def refresh_file_list(self):
        if not self.check_connection():
            return
        
        try:
            files = self.client.list_files()
            self.file_listbox.delete(0, tk.END)
            for file in files:
                self.file_listbox.insert(tk.END, file)
            self.progress_label.config(text=f"Found {len(files)} file(s)")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh file list:\n{str(e)}")
    
    def show_debug_info(self):
        """Show detailed connection debug information"""
        host = self.host_entry.get()
        port = self.port_entry.get()
        
        debug_info = []
        debug_info.append("=== CONNECTION DEBUG INFO ===\n")
        debug_info.append(f"Target Server: {host}:{port}\n")
        debug_info.append(f"Full URL: http://{host}:{port}\n\n")
        
        # Get local machine info
        debug_info.append("=== LOCAL MACHINE INFO ===\n")
        try:
            hostname = socket.gethostname()
            debug_info.append(f"Hostname: {hostname}\n")
            
            # Get all local IP addresses
            debug_info.append("\nLocal IP Addresses:\n")
            addrs = socket.getaddrinfo(hostname, None)
            seen_ips = set()
            for addr in addrs:
                ip = addr[4][0]
                if ip not in seen_ips and ':' not in ip:  # Filter out IPv6
                    seen_ips.add(ip)
                    debug_info.append(f"  • {ip}\n")
        except Exception as e:
            debug_info.append(f"Could not get local info: {e}\n")
        
        # Test DNS resolution
        debug_info.append("\n=== DNS RESOLUTION TEST ===\n")
        try:
            resolved_ip = socket.gethostbyname(host)
            debug_info.append(f"'{host}' resolves to: {resolved_ip}\n")
        except socket.gaierror as e:
            debug_info.append(f"❌ Cannot resolve '{host}': {e}\n")
        except Exception as e:
            debug_info.append(f"❌ Error resolving '{host}': {e}\n")
        
        # Test connection
        debug_info.append("\n=== CONNECTION TEST ===\n")
        port_open = False
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(3)
            result = test_socket.connect_ex((host, int(port)))
            test_socket.close()
            
            if result == 0:
                port_open = True
                debug_info.append(f"✅ Port {port} is OPEN and accepting connections\n")
            else:
                debug_info.append(f"❌ Port {port} is CLOSED or unreachable (error code: {result})\n")
                debug_info.append("\nPossible issues:\n")
                debug_info.append("  • Server is not running\n")
                debug_info.append("  • Firewall is blocking the port\n")
                debug_info.append("  • Wrong host/port configuration\n")
        except ValueError:
            debug_info.append(f"❌ Invalid port number: {port}\n")
        except Exception as e:
            debug_info.append(f"❌ Connection test failed: {e}\n")
        
        # Try to get server debug info
        if port_open:
            debug_info.append("\n=== SERVER INFO ===\n")
            try:
                import requests
                response = requests.get(f"http://{host}:{port}/debug/info", timeout=3)
                if response.status_code == 200:
                    server_info = response.json()
                    debug_info.append(f"Server Hostname: {server_info.get('server_hostname', 'N/A')}\n")
                    debug_info.append(f"Server Listening On: {server_info.get('listening_on', 'N/A')}\n")
                    debug_info.append(f"Storage Path: {server_info.get('storage_path', 'N/A')}\n")
                    
                    if 'server_ip_addresses' in server_info:
                        debug_info.append("\nServer IP Addresses:\n")
                        for ip in server_info['server_ip_addresses']:
                            debug_info.append(f"  • {ip}\n")
                    
                    if 'accessible_urls' in server_info:
                        debug_info.append("\nAccessible URLs:\n")
                        for url in server_info['accessible_urls']:
                            debug_info.append(f"  • {url}\n")
                    
                    if 'warning' in server_info:
                        debug_info.append(f"\n⚠️  WARNING: {server_info['warning']}\n")
                    
                    if 'note' in server_info:
                        debug_info.append(f"\nℹ️  {server_info['note']}\n")
                else:
                    debug_info.append("Could not retrieve server debug info\n")
            except Exception as e:
                debug_info.append(f"Could not retrieve server info: {e}\n")
        
        # Check if client is connected
        debug_info.append("\n=== CLIENT STATUS ===\n")
        if self.connected and self.client:
            debug_info.append("✅ Client is connected\n")
            debug_info.append(f"Client base URL: {self.client.base_url}\n")
        else:
            debug_info.append("❌ Client is not connected\n")
        
        # Network troubleshooting tips
        debug_info.append("\n=== TROUBLESHOOTING TIPS ===\n")
        debug_info.append("If connection fails:\n")
        debug_info.append("1. Verify server is running: Check server console/logs\n")
        debug_info.append("2. Check firewall: Ensure port is open on both client and server\n")
        debug_info.append("3. Test locally first: Try 'localhost' or '127.0.0.1'\n")
        debug_info.append("4. For remote access: Use server's LAN IP (192.168.x.x)\n")
        debug_info.append("5. For cloud access: Configure port forwarding on router\n")
        debug_info.append("6. Check config.yaml: Verify server host is '0.0.0.0' not 'localhost'\n")
        
        # Show in a scrollable text window
        debug_window = tk.Toplevel(self.root)
        debug_window.title("Connection Debug Information")
        debug_window.geometry("600x500")
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(debug_window)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        text_widget = tk.Text(text_frame, wrap="word", yscrollcommand=scrollbar.set, font=("Courier", 9))
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=text_widget.yview)
        
        # Insert debug info
        text_widget.insert("1.0", "".join(debug_info))
        text_widget.config(state="disabled")
        
        # Copy to clipboard button
        def copy_to_clipboard():
            self.root.clipboard_clear()
            self.root.clipboard_append("".join(debug_info))
            messagebox.showinfo("Copied", "Debug info copied to clipboard!")
        
        button_frame = ttk.Frame(debug_window)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame, text="Copy to Clipboard", command=copy_to_clipboard).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Close", command=debug_window.destroy).pack(side="left", padx=5)


def main():
    root = tk.Tk()
    app = CloudStorageGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
