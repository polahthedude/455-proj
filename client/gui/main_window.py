"""Main application window"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from client.gui.login_dialog import LoginDialog
from client.gui.file_manager import FileManagerFrame


class MainWindow:
    """Main application window"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CSC-455-Homelab-Project-Cloud")
        self.root.geometry("900x600")
        
        self.api_client = None
        self.auth_manager = None
        
        # Load theme preference
        self.settings_file = Path.home() / '.csc455_homelab' / 'settings.json'
        self.current_theme = self.load_theme_preference()
        
        # Show login dialog first
        if not self.show_login():
            self.root.destroy()
            return
        
        self.setup_ui()
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
    
    def show_login(self):
        """Show login dialog"""
        self.root.withdraw()  # Hide main window
        
        try:
            dialog = LoginDialog()
            result = dialog.show()
            
            if result:
                self.auth_manager = result['auth_manager']
                self.api_client = result['api_client']
                
                # Verify connection after login
                if not self.api_client.health_check():
                    messagebox.showwarning(
                        "Connection Warning",
                        "Successfully logged in, but server connection appears unstable.\\n\\n"
                        "Some operations may fail. Please check server status."
                    )
                
                self.root.deiconify()  # Show main window
                return True
            return False
        except Exception as e:
            messagebox.showerror(
                "Startup Error",
                f"An error occurred during login:\\n{str(e)}\\n\\n"
                "Please check:\\n"
                "• Server is running\\n"
                "• Configuration is correct\\n"
                "• Network connection is stable"
            )
            return False
    
    def setup_ui(self):
        """Setup main UI"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Upload File", command=self.upload_file)
        file_menu.add_separator()
        file_menu.add_command(label="Logout", command=self.logout)
        file_menu.add_command(label="Exit", command=self.exit_app)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Header
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(
            header,
            text=f"CSC-455-Homelab-Project-Cloud - {self.auth_manager.username}",
            font=("Arial", 14, "bold")
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            header,
            text="Logout",
            command=self.logout
        ).pack(side=tk.RIGHT)
        
        ttk.Button(
            header,
            text="Settings",
            command=self.show_settings
        ).pack(side=tk.RIGHT, padx=5)
        
        # Separator
        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10)
        
        # Main content
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # File manager
        self.file_manager = FileManagerFrame(
            content_frame,
            self.api_client,
            self.auth_manager
        )
        self.file_manager.pack(fill=tk.BOTH, expand=True)
        
        # Footer
        footer = ttk.Frame(self.root)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.encryption_label = ttk.Label(
            footer,
            text="🔐 All files encrypted with AES-256-GCM",
            font=("Arial", 9)
        )
        self.encryption_label.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Apply theme
        self.apply_theme(self.current_theme)
    
    def upload_file(self):
        """Upload file"""
        self.file_manager.upload_file()
    
    def logout(self):
        """Logout user"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.auth_manager.logout()
            self.root.destroy()
            
            # Show login dialog again
            new_app = MainWindow()
            if new_app.auth_manager:
                new_app.run()
    
    def exit_app(self):
        """Exit application"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.destroy()
    
    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.resizable(False, False)
        
        # Center window
        settings_window.update_idletasks()
        x = (settings_window.winfo_screenwidth() // 2) - (settings_window.winfo_width() // 2)
        y = (settings_window.winfo_screenheight() // 2) - (settings_window.winfo_height() // 2)
        settings_window.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(settings_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(
            main_frame,
            text="Application Settings",
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 20))
        
        # Theme selection
        theme_frame = ttk.LabelFrame(main_frame, text="Appearance", padding="10")
        theme_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(theme_frame, text="Theme:").pack(anchor=tk.W, pady=(0, 5))
        
        theme_var = tk.StringVar(value=self.current_theme)
        
        ttk.Radiobutton(
            theme_frame,
            text="Light Theme",
            variable=theme_var,
            value="light",
            command=lambda: self.change_theme("light", settings_window)
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(
            theme_frame,
            text="Dark Theme",
            variable=theme_var,
            value="dark",
            command=lambda: self.change_theme("dark", settings_window)
        ).pack(anchor=tk.W, pady=2)
        
        # User info
        info_frame = ttk.LabelFrame(main_frame, text="Account Information", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(
            info_frame,
            text=f"Username: {self.auth_manager.username}"
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Label(
            info_frame,
            text=f"User ID: {self.auth_manager.user_id}"
        ).pack(anchor=tk.W, pady=2)
        
        # Close button
        ttk.Button(
            main_frame,
            text="Close",
            command=settings_window.destroy,
            width=15
        ).pack(pady=(10, 0))
    
    def load_theme_preference(self):
        """Load saved theme preference"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get('theme', 'light')
        except:
            pass
        return 'light'
    
    def save_theme_preference(self, theme):
        """Save theme preference"""
        try:
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            settings = {}
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
            settings['theme'] = theme
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Failed to save theme preference: {e}")
    
    def change_theme(self, theme, settings_window=None):
        """Change application theme"""
        self.current_theme = theme
        self.apply_theme(theme)
        self.save_theme_preference(theme)
    
    def apply_theme(self, theme):
        """Apply theme to application"""
        if theme == 'dark':
            # Dark theme colors
            bg_color = '#2b2b2b'
            fg_color = '#ffffff'
            select_bg = '#404040'
            select_fg = '#ffffff'
            button_bg = '#404040'
            entry_bg = '#383838'
            accent_color = '#4a9eff'
            
            self.root.configure(bg=bg_color)
            
            # Configure ttk styles
            style = ttk.Style()
            style.theme_use('clam')
            
            style.configure('TFrame', background=bg_color)
            style.configure('TLabel', background=bg_color, foreground=fg_color)
            style.configure('TButton', background=button_bg, foreground=fg_color, borderwidth=1)
            style.map('TButton', background=[('active', select_bg)])
            style.configure('TEntry', fieldbackground=entry_bg, foreground=fg_color, borderwidth=1)
            style.configure('TNotebook', background=bg_color, borderwidth=0)
            style.configure('TNotebook.Tab', background=button_bg, foreground=fg_color, padding=[10, 5])
            style.map('TNotebook.Tab', background=[('selected', select_bg)])
            style.configure('Treeview', background=entry_bg, foreground=fg_color, fieldbackground=entry_bg, borderwidth=0)
            style.map('Treeview', background=[('selected', select_bg)], foreground=[('selected', select_fg)])
            style.configure('Treeview.Heading', background=button_bg, foreground=fg_color, borderwidth=1)
            style.configure('TSeparator', background='#404040')
            style.configure('TLabelframe', background=bg_color, foreground=fg_color, borderwidth=1)
            style.configure('TLabelframe.Label', background=bg_color, foreground=fg_color)
            style.configure('TCheckbutton', background=bg_color, foreground=fg_color)
            style.configure('TRadiobutton', background=bg_color, foreground=fg_color)
            
            # Update encryption label color
            if hasattr(self, 'encryption_label'):
                self.encryption_label.configure(foreground=accent_color)
        else:
            # Light theme (default)
            bg_color = '#f0f0f0'
            fg_color = '#000000'
            accent_color = 'green'
            
            self.root.configure(bg=bg_color)
            
            # Configure ttk styles to default
            style = ttk.Style()
            style.theme_use('vista' if sys.platform == 'win32' else 'clam')
            
            # Update encryption label color
            if hasattr(self, 'encryption_label'):
                self.encryption_label.configure(foreground=accent_color)
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About",
            "CSC-455-Homelab-Project-Cloud v1.0\n\n"
            "A secure encrypted file storage system with\n"
            "client-side encryption.\n\n"
            "Features:\n"
            "• AES-256-GCM encryption\n"
            "• RSA-2048 key management\n"
            "• Encrypted architecture\n"
            "• Dark/Light theme support\n\n"
            "Created for CS 455 Project"
        )
    
    def run(self):
        """Run application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    app = MainWindow()
    if app.auth_manager:
        app.run()


if __name__ == '__main__':
    main()
