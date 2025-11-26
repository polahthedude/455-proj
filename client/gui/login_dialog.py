"""Login and registration dialog"""
import tkinter as tk
from tkinter import ttk, messagebox
import yaml
import threading
from queue import Queue
from pathlib import Path
from client.api_client import APIClient
from client.auth_manager import AuthManager


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
        
        self.api_client = APIClient(config['client']['server_url'])
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
            text="Zero-knowledge encryption",
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
        self.status_label.config(text="Checking server...", foreground="blue")
        self.window.update()
        
        if self.api_client.health_check():
            self.status_label.config(text="Server is online ✓", foreground="green")
            messagebox.showinfo(
                "Connection Success",
                "Successfully connected to server!\\n\\n"
                "Server is running and ready to accept requests."
            )
        else:
            self.status_label.config(text="Server is offline ✗", foreground="red")
            messagebox.showerror(
                "Connection Failed",
                "Cannot connect to server.\\n\\n"
                "Please check:\\n"
                "• Server is running (run start_server.bat)\\n"
                "• Server address in config.yaml is correct\\n"
                "• No firewall blocking port 5000\\n\\n"
                "Default server: http://127.0.0.1:5000"
            )
    
    def handle_login(self):
        """Handle login button click"""
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
                    "• Server is running (run start_server.bat)\n"
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


if __name__ == '__main__':
    dialog = LoginDialog()
    result = dialog.show()
    if result:
        print("Login successful!")
    else:
        print("Login cancelled")
