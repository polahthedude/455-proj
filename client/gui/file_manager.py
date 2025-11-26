"""File manager interface"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from pathlib import Path
from datetime import datetime


class FileManagerFrame(ttk.Frame):
    """File manager interface"""
    
    def __init__(self, parent, api_client, auth_manager):
        super().__init__(parent)
        self.api_client = api_client
        self.auth_manager = auth_manager
        self.files = []
        self.folders = []  # List of folders from server
        self.current_folder = "/"  # Current folder path
        
        self.setup_ui()
        self.refresh_files()
    
    def setup_ui(self):
        """Setup UI components"""
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            toolbar,
            text="📁 New Folder",
            command=self.create_folder
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            toolbar,
            text="📤 Upload File",
            command=self.upload_file
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            toolbar,
            text="📥 Download",
            command=self.download_file
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            toolbar,
            text="🗑 Delete",
            command=self.delete_item
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            toolbar,
            text="🔄 Refresh",
            command=self.refresh_files
        ).pack(side=tk.LEFT, padx=5)
        
        # Storage info
        self.storage_label = ttk.Label(toolbar, text="Storage: 0/100 MB")
        self.storage_label.pack(side=tk.RIGHT, padx=5)
        
        # File list
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ('type', 'size', 'uploaded', 'hash')
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='tree headings',
            yscrollcommand=scrollbar.set
        )
        
        # Column headers
        self.tree.heading('#0', text='Name')
        self.tree.heading('type', text='Type')
        self.tree.heading('size', text='Size')
        self.tree.heading('uploaded', text='Modified')
        self.tree.heading('hash', text='Hash (truncated)')
        
        # Column widths
        self.tree.column('#0', width=250)
        self.tree.column('type', width=80)
        self.tree.column('size', width=100)
        self.tree.column('uploaded', width=150)
        self.tree.column('hash', width=150)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Right-click context menu
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="📁 New Folder", command=self.create_folder)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📥 Download", command=self.download_file)
        self.context_menu.add_command(label="✏️ Rename", command=self.rename_item)
        self.context_menu.add_command(label="🗑 Delete", command=self.delete_item)
        
        # Status bar
        self.status_bar = ttk.Label(
            self,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
        
        # Bindings
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Button-3>', self.show_context_menu)  # Right-click
    
    def format_size(self, size_bytes):
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def on_double_click(self, event):
        """Handle double-click on item"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        
        if values and values[0] == 'Folder':
            # Open folder
            tags = self.tree.item(item, 'tags')
            if tags and tags[0] == '..parent..':
                # Navigate to parent folder
                parent_path = "/".join(self.current_folder.rstrip('/').split('/')[:-1]) + "/"
                if parent_path == "/":
                    parent_path = "/"
                self.current_folder = parent_path
            else:
                # Navigate into folder
                folder_uuid = tags[0] if tags else None
                if folder_uuid:
                    folder_data = next((f for f in self.folders if f.get('folder_uuid') == folder_uuid), None)
                    if folder_data:
                        self.current_folder = folder_data.get('path')
            self.refresh_files()
        else:
            # Download file
            self.download_file()
    
    def show_context_menu(self, event):
        """Show right-click context menu"""
        # Select item under cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
        
        # Show menu
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def create_folder(self):
        """Create a new folder"""
        dialog = tk.Toplevel(self)
        dialog.title("Create New Folder")
        dialog.geometry("350x150")
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Folder Name:").pack(anchor=tk.W, pady=(0, 5))
        
        name_entry = ttk.Entry(frame, width=40)
        name_entry.pack(fill=tk.X, pady=(0, 20))
        name_entry.focus()
        
        def create():
            folder_name = name_entry.get().strip()
            if not folder_name:
                messagebox.showerror("Error", "Please enter a folder name")
                return
            
            # Validate folder name
            if '/' in folder_name or '\\' in folder_name:
                messagebox.showerror("Error", "Folder name cannot contain / or \\")
                return
            
            # Create folder path
            folder_path = f"{self.current_folder}{folder_name}/" if self.current_folder.endswith('/') else f"{self.current_folder}/{folder_name}/"
            
            # Encrypt folder name
            try:
                encrypted_name, name_iv, name_tag = self.auth_manager.crypto_handler.encrypt_string(folder_name)
                encryption_metadata = {
                    'name_iv': name_iv,
                    'name_tag': name_tag
                }
                
                # Send to server
                success, response = self.api_client.create_folder(
                    encrypted_name,
                    folder_path,
                    self.current_folder,
                    encryption_metadata,
                    self.auth_manager.token
                )
                
                if success:
                    self.status_bar.config(text=f"Created folder: {folder_name}")
                    self.refresh_files()
                    dialog.destroy()
                else:
                    message = response.get('message', 'Failed to create folder')
                    messagebox.showerror("Error", message)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create folder: {str(e)}")
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Create", command=create, width=15).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy, width=15).pack(side=tk.LEFT)
        
        name_entry.bind('<Return>', lambda e: create())
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
    
    def rename_item(self):
        """Rename selected item"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to rename")
            return
        
        item = selection[0]
        current_name = self.tree.item(item, 'text')
        values = self.tree.item(item, 'values')
        
        dialog = tk.Toplevel(self)
        dialog.title("Rename")
        dialog.geometry("350x150")
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="New Name:").pack(anchor=tk.W, pady=(0, 5))
        
        name_entry = ttk.Entry(frame, width=40)
        name_entry.insert(0, current_name)
        name_entry.pack(fill=tk.X, pady=(0, 20))
        name_entry.focus()
        name_entry.select_range(0, tk.END)
        
        def rename():
            new_name = name_entry.get().strip()
            if not new_name:
                messagebox.showerror("Error", "Please enter a name")
                return
            
            if values and values[0] == 'Folder':
                # Rename folder
                tags = self.tree.item(item, 'tags')
                if not tags:
                    return
                
                folder_uuid = tags[0]
                
                # Find folder data
                folder_data = next((f for f in self.folders if f.get('folder_uuid') == folder_uuid), None)
                if not folder_data:
                    messagebox.showerror("Error", "Folder not found")
                    return
                
                try:
                    # Encrypt new name
                    encrypted_name, name_iv, name_tag = self.auth_manager.crypto_handler.encrypt_string(new_name)
                    encryption_metadata = {
                        'name_iv': name_iv,
                        'name_tag': name_tag
                    }
                    
                    # Calculate new path
                    parent = folder_data.get('parent_path')
                    new_path = f"{parent}{new_name}/" if parent.endswith('/') else f"{parent}/{new_name}/"
                    
                    # Send to server
                    success, response = self.api_client.rename_folder(
                        folder_uuid,
                        encrypted_name,
                        new_path,
                        encryption_metadata,
                        self.auth_manager.token
                    )
                    
                    if success:
                        self.status_bar.config(text=f"Renamed to: {new_name}")
                        self.refresh_files()
                        dialog.destroy()
                    else:
                        message = response.get('message', 'Failed to rename folder')
                        messagebox.showerror("Error", message)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to rename folder: {str(e)}")
            else:
                # For files, would need server API support
                messagebox.showinfo("Info", "File renaming requires server support (coming soon)")
                dialog.destroy()
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Rename", command=rename, width=15).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy, width=15).pack(side=tk.LEFT)
        
        name_entry.bind('<Return>', lambda e: rename())
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
    
    def delete_item(self):
        """Delete selected item (folder or file)"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return
        
        item = selection[0]
        item_name = self.tree.item(item, 'text')
        values = self.tree.item(item, 'values')
        
        if values and values[0] == 'Folder':
            if not messagebox.askyesno("Confirm", f"Delete folder '{item_name}' and all its contents?"):
                return
            
            tags = self.tree.item(item, 'tags')
            if not tags:
                return
            
            folder_uuid = tags[0]
            
            try:
                # Send to server
                success, response = self.api_client.delete_folder(
                    folder_uuid,
                    self.auth_manager.token
                )
                
                if success:
                    self.status_bar.config(text=f"Deleted folder: {item_name}")
                    self.refresh_files()
                else:
                    message = response.get('message', 'Failed to delete folder')
                    messagebox.showerror("Error", message)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete folder: {str(e)}")
        else:
            # Delete file (existing functionality)
            self.delete_file()
    
    def refresh_files(self):
        """Refresh file list"""
        self.status_bar.config(text="Loading...")
        self.update()
        
        # Load folders
        folders_success, folders_response = self.api_client.list_folders(self.auth_manager.token)
        if folders_success:
            self.folders = folders_response.get('folders', [])
        else:
            self.folders = []
        
        # Load files
        success, response = self.api_client.list_files(self.auth_manager.token)
        
        if success:
            self.files = response.get('files', [])
            storage_used = response.get('storage_used', 0)
            
            # Update storage label
            storage_mb = storage_used / (1024 * 1024)
            quota_mb = 1024  # 1GB
            self.storage_label.config(text=f"Storage: {storage_mb:.1f}/{quota_mb} MB")
            
            # Clear tree
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Add parent folder navigation if not at root
            if self.current_folder != "/":
                parent_path = "/".join(self.current_folder.rstrip('/').split('/')[:-1]) + "/"
                if parent_path == "/":
                    parent_path = "/"
                self.tree.insert('', 0, text="📁 ..", values=('Folder', '', '', ''), 
                               tags=('..parent..',))
            
            # Add folders in current directory
            current_folders = [
                f for f in self.folders 
                if f.get('parent_path') == self.current_folder
            ]
            
            for folder_data in sorted(current_folders, key=lambda x: x.get('path', '')):
                try:
                    # Decrypt folder name
                    enc_metadata = folder_data.get('encryption_metadata', {})
                    encrypted_name = folder_data.get('name_encrypted')
                    name_iv = enc_metadata.get('name_iv')
                    name_tag = enc_metadata.get('name_tag')
                    
                    if encrypted_name and name_iv and name_tag:
                        folder_name = self.auth_manager.crypto_handler.decrypt_string(
                            encrypted_name, name_iv, name_tag
                        )
                    else:
                        folder_name = "Unknown Folder"
                except Exception as e:
                    print(f"[FOLDER] Failed to decrypt folder name: {e}")
                    folder_name = "Unknown Folder"
                
                created = folder_data.get('created_at', '')[:19]
                folder_uuid = folder_data.get('folder_uuid')
                
                self.tree.insert('', tk.END, text=f"📁 {folder_name}", 
                               values=('Folder', '', created, ''),
                               tags=(folder_uuid,))
            
            # Add files (filter by current folder)
            current_files = [f for f in self.files if f.get('folder_path') == self.current_folder]
            
            for file in current_files:
                # Decrypt filename
                try:
                    enc_metadata = file.get('encryption_metadata', {})
                    encrypted_filename = enc_metadata.get('encrypted_filename')
                    filename_iv = enc_metadata.get('filename_iv')
                    filename_tag = enc_metadata.get('filename_tag')
                    
                    if encrypted_filename and filename_iv and filename_tag:
                        # Decrypt the filename
                        filename = self.auth_manager.crypto_handler.decrypt_string(
                            encrypted_filename, filename_iv, filename_tag
                        )
                    else:
                        # Fallback to generic name
                        filename = f"File_{file.get('id')}"
                except Exception as e:
                    print(f"[FILE] Failed to decrypt filename: {e}")
                    filename = f"File_{file.get('id')}"
                
                # Determine file icon based on extension
                if '.' in filename:
                    ext = filename.rsplit('.', 1)[1].lower()
                    if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
                        icon = '🖼️'
                    elif ext in ['mp3', 'wav', 'flac', 'ogg', 'm4a']:
                        icon = '🎵'
                    elif ext in ['mp4', 'avi', 'mkv', 'mov']:
                        icon = '🎬'
                    elif ext in ['pdf']:
                        icon = '📄'
                    elif ext in ['zip', 'rar', '7z', 'tar', 'gz']:
                        icon = '📦'
                    elif ext in ['txt', 'md', 'log']:
                        icon = '📝'
                    else:
                        icon = '📄'
                else:
                    icon = '📄'
                
                size = self.format_size(file.get('size', 0))
                uploaded = file.get('uploaded_at', '')[:19]  # Trim milliseconds
                file_hash = file.get('file_hash', '')[:16] + '...'
                
                self.tree.insert('', tk.END, text=f"{icon} {filename}", 
                               values=('File', size, uploaded, file_hash),
                               tags=(file.get('file_uuid'),))
            
            total_items = len(current_folders) + len(current_files)
            self.status_bar.config(text=f"Loaded {len(current_folders)} folders, {len(current_files)} files | Path: {self.current_folder}")
        else:
            message = response.get('message', 'Failed to load files')
            self.status_bar.config(text=f"Error: {message}")
            
            # Handle specific error types
            if response.get('auth_error') or response.get('status_code') == 401:
                messagebox.showerror(
                    "Authentication Error",
                    "Your session has expired or is invalid.\n\n"
                    "Please logout and login again."
                )
            elif response.get('connection_error'):
                messagebox.showerror(
                    "Connection Error",
                    f"{message}\n\n"
                    "Lost connection to server.\n"
                    "Please check if the server is still running."
                )
            else:
                messagebox.showerror("Error", message)
    
    def upload_file(self):
        """Upload file"""
        file_path = filedialog.askopenfilename(
            title="Select file to upload",
            filetypes=[("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        self.status_bar.config(text="Encrypting and uploading...")
        self.update()
        
        def upload_thread():
            try:
                # Encrypt file
                encrypted_data, metadata = self.auth_manager.crypto_handler.encrypt_file(file_path)
                
                # Add encrypted filename with separate IV and tag
                filename = os.path.basename(file_path)
                encrypted_filename, filename_iv, filename_tag = self.auth_manager.crypto_handler.encrypt_string(filename)
                metadata['encrypted_filename'] = encrypted_filename
                metadata['filename_iv'] = filename_iv
                metadata['filename_tag'] = filename_tag
                
                # Add current folder path
                metadata['folder_path'] = self.current_folder
                
                # Upload
                success, response = self.api_client.upload_file(
                    file_path,
                    encrypted_data,
                    metadata,
                    self.auth_manager.token
                )
                
                if success:
                    self.after(0, lambda: self.status_bar.config(text="Upload successful!"))
                    self.after(0, self.refresh_files)
                    self.after(0, lambda: messagebox.showinfo("Success", "File uploaded successfully!"))
                else:
                    message = response.get('message', 'Upload failed')
                    self.after(0, lambda: self.status_bar.config(text=f"Error: {message}"))
                    
                    # Handle specific error types
                    if response.get('auth_error') or response.get('status_code') == 401:
                        self.after(0, lambda: messagebox.showerror(
                            "Authentication Error",
                            "Your session has expired.\n\n"
                            "Please logout and login again to continue."
                        ))
                    elif response.get('status_code') == 413:
                        self.after(0, lambda: messagebox.showerror(
                            "File Too Large",
                            f"{message}\n\n"
                            "Maximum file size is 100MB.\n"
                            "Please select a smaller file."
                        ))
                    elif response.get('connection_error'):
                        self.after(0, lambda: messagebox.showerror(
                            "Connection Error",
                            f"{message}\n\n"
                            "Lost connection to server during upload."
                        ))
                    else:
                        self.after(0, lambda: messagebox.showerror("Upload Error", message))
                    
            except Exception as e:
                self.after(0, lambda: self.status_bar.config(text=f"Error: {str(e)}"))
                self.after(0, lambda: messagebox.showerror("Error", f"Upload failed: {str(e)}"))
        
        threading.Thread(target=upload_thread, daemon=True).start()
    
    def download_file(self):
        """Download and decrypt file"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file to download")
            return
        
        # Get file UUID from tags
        item = selection[0]
        tags = self.tree.item(item, 'tags')
        if not tags:
            return
        
        file_uuid = tags[0]
        
        # Find file metadata
        file_meta = next((f for f in self.files if f.get('file_uuid') == file_uuid), None)
        if not file_meta:
            return
        
        # Decrypt filename to get original name for save dialog
        original_filename = "download"
        try:
            enc_metadata = file_meta.get('encryption_metadata', {})
            encrypted_filename = enc_metadata.get('encrypted_filename')
            filename_iv = enc_metadata.get('filename_iv')
            filename_tag = enc_metadata.get('filename_tag')
            
            if encrypted_filename and filename_iv and filename_tag:
                original_filename = self.auth_manager.crypto_handler.decrypt_string(
                    encrypted_filename, filename_iv, filename_tag
                )
        except Exception as e:
            print(f"[DOWNLOAD] Failed to decrypt filename: {e}")
        
        # Ask where to save
        save_path = filedialog.asksaveasfilename(
            title="Save file as",
            initialfile=original_filename,
            defaultextension="",
            filetypes=[("All files", "*.*")]
        )
        
        if not save_path:
            return
        
        self.status_bar.config(text="Downloading and decrypting...")
        self.update()
        
        def download_thread():
            try:
                # Download file
                success, data = self.api_client.download_file(file_uuid, self.auth_manager.token)
                
                if not success:
                    error_msg = data.decode('utf-8', errors='ignore') if isinstance(data, bytes) else str(data)
                    self.after(0, lambda: self.status_bar.config(text="Download failed"))
                    
                    # Try to parse error message
                    try:
                        import json
                        error_data = json.loads(error_msg) if isinstance(data, bytes) else {}
                        if error_data.get('status_code') == 401 or error_data.get('auth_error'):
                            self.after(0, lambda: messagebox.showerror(
                                "Authentication Error",
                                "Your session has expired.\n\n"
                                "Please logout and login again."
                            ))
                        else:
                            self.after(0, lambda: messagebox.showerror(
                                "Download Error",
                                error_data.get('message', 'Download failed')
                            ))
                    except:
                        self.after(0, lambda: messagebox.showerror(
                            "Download Error",
                            "Failed to download file. It may have been deleted or you may not have access."
                        ))
                    return
                
                # Decrypt file
                metadata = file_meta.get('encryption_metadata', {})
                decrypted_data = self.auth_manager.crypto_handler.decrypt_file(data, metadata)
                
                # Save file
                with open(save_path, 'wb') as f:
                    f.write(decrypted_data)
                
                self.after(0, lambda: self.status_bar.config(text="Download successful!"))
                self.after(0, lambda: messagebox.showinfo("Success", f"File saved to {save_path}"))
                
            except Exception as e:
                self.after(0, lambda: self.status_bar.config(text=f"Error: {str(e)}"))
                self.after(0, lambda: messagebox.showerror("Error", f"Download failed: {str(e)}"))
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def delete_file(self):
        """Delete file"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file to delete")
            return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this file?"):
            return
        
        # Get file UUID
        item = selection[0]
        tags = self.tree.item(item, 'tags')
        if not tags:
            return
        
        file_uuid = tags[0]
        
        self.status_bar.config(text="Deleting file...")
        self.update()
        
        success, response = self.api_client.delete_file(file_uuid, self.auth_manager.token)
        
        if success:
            self.status_bar.config(text="File deleted successfully")
            self.refresh_files()
        else:
            message = response.get('message', 'Delete failed')
            self.status_bar.config(text=f"Error: {message}")
            
            # Handle specific error types
            if response.get('auth_error') or response.get('status_code') == 401:
                messagebox.showerror(
                    "Authentication Error",
                    "Your session has expired.\n\n"
                    "Please logout and login again."
                )
            elif response.get('status_code') == 404:
                messagebox.showerror(
                    "File Not Found",
                    "This file no longer exists or has already been deleted."
                )
            else:
                messagebox.showerror("Delete Error", message)
