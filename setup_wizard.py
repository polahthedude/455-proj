"""
Simple configuration GUI for first-time setup
Shows dialog to set server URL
"""
import tkinter as tk
from tkinter import ttk, messagebox
import yaml
from pathlib import Path


class SetupDialog:
    """First-time setup dialog"""
    
    def __init__(self):
        self.result = None
        self.root = tk.Tk()
        self.root.title("Cloud Storage - First Time Setup")
        self.root.geometry("500x300")
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (250)
        y = (self.root.winfo_screenheight() // 2) - (150)
        self.root.geometry(f"+{x}+{y}")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI elements"""
        # Header
        header = ttk.Label(
            self.root,
            text="Welcome to Cloud Storage",
            font=("Arial", 16, "bold")
        )
        header.pack(pady=20)
        
        # Instructions
        instructions = ttk.Label(
            self.root,
            text="Please enter your cloud storage server URL:",
            wraplength=450
        )
        instructions.pack(pady=10)
        
        # URL entry frame
        entry_frame = ttk.Frame(self.root)
        entry_frame.pack(pady=20, padx=40, fill=tk.X)
        
        ttk.Label(entry_frame, text="Server URL:").pack(anchor=tk.W)
        
        self.url_entry = ttk.Entry(entry_frame, width=50)
        self.url_entry.pack(fill=tk.X, pady=5)
        self.url_entry.insert(0, "http://localhost:5000")
        
        # Examples
        examples = ttk.Label(
            self.root,
            text="Examples:\n"
                 "Local: http://localhost:5000\n"
                 "Network: http://192.168.1.100:5000\n"
                 "Internet: https://yourdomain.com",
            font=("Arial", 9),
            foreground="gray"
        )
        examples.pack(pady=10)
        
        # Buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20)
        
        ttk.Button(
            button_frame,
            text="Save and Continue",
            command=self.save_config
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel
        ).pack(side=tk.LEFT, padx=5)
        
    def save_config(self):
        """Save configuration"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter a server URL")
            return
        
        if not url.startswith(("http://", "https://")):
            messagebox.showerror(
                "Error",
                "URL must start with http:// or https://"
            )
            return
        
        try:
            # Load config
            config_path = Path("config.yaml")
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Update server URL
            config['client']['server_url'] = url
            
            # Save config
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            self.result = url
            self.root.destroy()
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to save configuration:\n{str(e)}"
            )
    
    def cancel(self):
        """Cancel setup"""
        self.root.destroy()
    
    def show(self):
        """Show dialog and return result"""
        self.root.mainloop()
        return self.result


def check_first_run():
    """Check if this is first run (config has default URL)"""
    try:
        config_path = Path("config.yaml")
        if not config_path.exists():
            return True
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        url = config.get('client', {}).get('server_url', '')
        return url == "http://127.0.0.1:5000" or url == "http://localhost:5000"
    except:
        return True


if __name__ == '__main__':
    if check_first_run():
        dialog = SetupDialog()
        result = dialog.show()
        if result:
            print(f"Configuration saved: {result}")
        else:
            print("Setup cancelled")
    else:
        print("Already configured")
