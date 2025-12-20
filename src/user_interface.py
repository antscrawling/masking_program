import os
from  pathlib import Path
import customtkinter
import tkinter as tk
from tkinter import messagebox, filedialog 

ROOT_DIR = Path(__file__).parent.resolve()


def display_message_dialog(parent, title: str, message: str):
    """Display a message in a dialog window"""
    msg_dialog = customtkinter.CTkToplevel(parent)
    msg_dialog.title(title)
    msg_dialog.geometry("800x700")
    msg_dialog.grab_set()
    
    # Message textbox
    message_text = customtkinter.CTkTextbox(
        msg_dialog,
        width=750,
        font=customtkinter.CTkFont(size=11),
        wrap="word"
    )
    message_text.pack(pady=20, padx=20, fill="both", expand=True)
    message_text.insert("1.0", message)
    message_text.configure(state="disabled")
    
    # Close button
    close_btn = customtkinter.CTkButton(
        msg_dialog,
        text="Close",
        font=customtkinter.CTkFont(size=14, weight="bold"),
        command=msg_dialog.destroy,
        fg_color="#1f6aa5",
        hover_color="#144870"
    )
    close_btn.pack(pady=20)


def clear_info(info_text):
    """Clear the information panel"""
    info_text.configure(state="normal")
    info_text.delete("1.0", "end")
    info_text.configure(state="disabled")


def set_info(info_text, content: str):
    """Set content in the information panel"""
    info_text.configure(state="normal")
    info_text.delete("1.0", "end")
    info_text.insert("1.0", content)
    info_text.configure(state="disabled")


def ask_passphrase() -> str | None:
    """Ask user for passphrase"""
    dialog = customtkinter.CTkInputDialog(text="Enter passphrase (optional)", title="Passphrase")
    return dialog.get_input()


def choose_files(multiple: bool = True) -> list[str]:
    """Choose files using file dialog"""
    if multiple:
        return list(filedialog.askopenfilenames(title="Select Files"))
    sel = filedialog.askopenfilename(title="Select File")
    return [sel] if sel else []


def retrieve_rsa_keys(type : str) -> str:
    """Retrieve RSA keys from files"""
    import main
    result = main.retrieve_rsa_keys()
    
    if result and result[0]:
        _, private_key, public_key = result
        return public_key if type=="public" else private_key
    else:
        return "❌ Key files not found. Please generate or import keys first."


def show_dropdown(parent, anchor_widget: tk.Widget, items: list[str], menu_action_callback):
    """Show a native Tk dropdown menu anchored to a widget"""
    menu = tk.Menu(parent, tearoff=0)
    for item in items:
        menu.add_command(label=item, command=lambda val=item: menu_action_callback(val))
    # Position menu just under the anchor widget
    x = anchor_widget.winfo_rootx()
    y = anchor_widget.winfo_rooty() + anchor_widget.winfo_height()
    try:
        menu.tk_popup(x, y)
    finally:
        menu.grab_release()


def menu_action(app, info_text, choice: str):
    """Handler for dropdown selections and Exit"""
    if choice == "Exit":
        app.destroy()
        return
    if choice == "RSA Key Data":
        clear_info(info_text)
        set_info(info_text, "Import RSA key: paste keys in the dialog.")
        
        # Create a dialog window for pasting RSA keys
        key_dialog = customtkinter.CTkToplevel(app)
        key_dialog.title("Import RSA Keys")
        key_dialog.geometry("700x600")
        key_dialog.grab_set()
        
        # Instructions
        instructions = customtkinter.CTkLabel(
            key_dialog, 
            text="Paste your RSA keys below (base64 format or PEM format)\nExtra spaces and newlines will be automatically cleaned up",
            font=customtkinter.CTkFont(size=14, weight="bold")
        )
        instructions.pack(pady=(20, 10))
        
        # Public Key section
        pub_label = customtkinter.CTkLabel(
            key_dialog,
            text="Public Key:",
            font=customtkinter.CTkFont(size=14, weight="bold")
        )
        pub_label.pack(pady=(10, 5), anchor="w", padx=20)
        
        public_key_text = customtkinter.CTkTextbox(
            key_dialog,
            height=150,
            width=650,
            font=customtkinter.CTkFont(size=11)
        )
        public_key_text.pack(pady=5, padx=20)
        
        # Private Key section
        priv_label = customtkinter.CTkLabel(
            key_dialog,
            text="Private Key:",
            font=customtkinter.CTkFont(size=14, weight="bold")
        )
        priv_label.pack(pady=(10, 5), anchor="w", padx=20)
        
        private_key_text = customtkinter.CTkTextbox(
            key_dialog,
            height=150,
            width=650,
            font=customtkinter.CTkFont(size=11)
        )
        private_key_text.pack(pady=5, padx=20)
        
        passphrase_label = customtkinter.CTkLabel(
            key_dialog,
            text="(Optional) If your private key is encrypted, please provide the passphrase below.",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            height=1,
            width=650
        )
        passphrase_label.pack(pady=(10, 5), anchor="w", padx=20)
        passphrase_text = customtkinter.CTkTextbox(
            key_dialog,
            height=10,
            width=650,
            font=customtkinter.CTkFont(size=11)
        )
        passphrase_text.pack(pady=5, padx=20)
       
        # Import button
        def import_keys():
            public_key = public_key_text.get("1.0", "end").strip()
            private_key = private_key_text.get("1.0", "end").strip()
            passphrase = passphrase_text.get("1.0", "end").strip()
            
            if not public_key or not private_key:
                messagebox.showerror("Error", "Both public and private keys are required!")
                return
            
            # Validate minimum lengths
            if len(public_key) < 200:
                messagebox.showerror("Error", f"Public key seems too short ({len(public_key)} chars). Expected at least 200 characters.")
                return
                
            if len(private_key) < 500:
                messagebox.showerror("Error", f"Private key seems too short ({len(private_key)} chars). Expected at least 500 characters.")
                return
            
            # Import main module to access import function
            try:
                import sys
                sys.path.insert(0, str(ROOT_DIR))
                import main
                
                # Call the import function from main.py with passphrase if provided
                result = main.import_external_rsa_keys(
                    private=private_key, 
                    public=public_key, 
                    passphrase=passphrase if passphrase else None
                )
                
                if result and result[0]:
                    messagebox.showinfo("Success", "RSA keys imported successfully!")
                    passphrase_info = f"{os.linesep}Passphrase: {'provided' if passphrase else 'not provided'}"
                    set_info(info_text, f"✓ RSA keys imported and saved{os.linesep}Public Key: {len(public_key)} chars{os.linesep}Private Key: {len(private_key)} chars{passphrase_info}")
                    key_dialog.destroy()
                else:
                    error_msg = "Failed to import keys. Please check:\n"
                    error_msg += "• Keys are in valid format\n"
                    error_msg += "• Private key passphrase is correct (if encrypted)\n"
                    error_msg += "• No extra text mixed with key data"
                    messagebox.showerror("Import Failed", error_msg)
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                print(f"Import error details:\n{error_details}")
                messagebox.showerror("Error", f"Import failed: {str(e)}\n\nCheck console for details.")
        
        import_btn = customtkinter.CTkButton(
            key_dialog,
            text="Import Keys",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            command=import_keys,
            fg_color="#1f6aa5",
            hover_color="#144870"
        )
        import_btn.pack(pady=20)
        
        return
    if choice == "RSA Key File":
        clear_info(info_text)
        
        # Import main module to access key retrieval function
        import main
        
        # Check if key files exist and retrieve them
        result = main.retrieve_rsa_keys()
        
        if result and result[0]:
            _, private_key, public_key = result
            
            # Display both keys in the info panel
            display_text = "✓ Keys are existing\n\n"
            display_text += "=== PUBLIC KEY ===\n"
            display_text += public_key + "\n\n"
            display_text += "=== PRIVATE KEY (Keep this secret!) ===\n"
            display_text += private_key
            
            set_info(info_text, display_text)
        else:
            set_info(info_text, "❌ Key files not found. Please generate or import keys first.")
        
        return
    if choice in {"2048-bit", "3072-bit", "4096-bit"}:
        clear_info(info_text)
        set_info(info_text, f"Generate RSA key pair ({choice})")
        
        # Import main module
        import main
        
        # Create a dialog for key generation with optional passphrase
        gen_dialog = customtkinter.CTkToplevel(app)
        gen_dialog.title(f"Generate {choice} RSA Key Pair")
        gen_dialog.geometry("700x600")
        gen_dialog.grab_set()
        
        # Instructions
        instructions = customtkinter.CTkLabel(
            gen_dialog, 
            text=f"Generate {choice} RSA Key Pair\nEnter an optional passphrase to encrypt the private key",
            font=customtkinter.CTkFont(size=14, weight="bold")
        )
        instructions.pack(pady=(20, 10))
        
        # Passphrase section
        pass_label = customtkinter.CTkLabel(
            gen_dialog,
            text="Passphrase (optional - leave empty for no encryption):",
            font=customtkinter.CTkFont(size=12)
        )
        pass_label.pack(pady=(10, 5))
        
        passphrase_entry = customtkinter.CTkEntry(
            gen_dialog,
            width=600,
            height=40,
            show="*",
            placeholder_text="Enter passphrase or leave empty"
        )
        passphrase_entry.pack(pady=5)
        
        # Function to generate keys
        def generate_keys():
            passphrase = passphrase_entry.get().strip()
            
            # Extract key size from choice
            key_size = int(choice.replace("-bit", ""))
            
            # Generate RSA key pair
            private_key, public_key, _ = main.generate_rsa_key_pair(
                passphrase=passphrase if passphrase else None, 
                key_size=key_size
            )
            
            if private_key and public_key:
                # Save to files
                try:
                    with open('private_key.pem', 'w') as f:
                        f.write(private_key)
                    with open('public_key.pem', 'w') as f:
                        f.write(public_key)
                    
                    # Prepare message for dialog
                    message = f"✓ Successfully generated {choice} RSA key pair\n"
                    if passphrase:
                        message += "✓ Private key encrypted with passphrase\n\n"
                    else:
                        message += "⚠️ Private key NOT encrypted (no passphrase provided)\n\n"
                    
                    message += "=== PUBLIC KEY ===\n"
                    message += public_key + "\n\n"
                    message += "=== PRIVATE KEY (Keep this secret!) ===\n"
                    message += private_key
                    
                    # Display keys in dialog
                    display_message_dialog(app, f"{choice} RSA Key Pair", message)
                    
                    # Update info panel
                    set_info(info_text, f"✓ Keys generated and saved to private_key.pem and public_key.pem")
                    
                    gen_dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save keys to files: {str(e)}")
            else:
                messagebox.showerror("Error", "Key generation failed")
        
        generate_btn = customtkinter.CTkButton(
            gen_dialog,
            text="Generate Keys",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            command=generate_keys,
            fg_color="#1f6aa5",
            hover_color="#144870"
        )
        generate_btn.pack(pady=20)
        
        return
    if choice == "Public Key":
        clear_info(info_text)
        public_key = retrieve_rsa_keys('public')
        set_info(info_text, public_key)
        return
    if choice == "Private Key":
        clear_info(info_text)   
        messagebox.showwarning("Security Warning", "Be cautious when handling private keys!")
        private_key = retrieve_rsa_keys('private')
        set_info(info_text, private_key)
        return
    if choice == "Encrypt Data":
        clear_info(info_text)
        set_info(info_text, "Enter data to encrypt in a forthcoming dialog.")
        return
    if choice == "Encrypt File":
        clear_info(info_text)
        files = choose_files(multiple=True)
        set_info(info_text, f"Selected files to encrypt: {os.linesep}" + os.linesep.join(files))
        return
    if choice == "Decrypt Data":
        clear_info(info_text)
        set_info(info_text, "Enter encrypted data and key/passphrase in a forthcoming dialog.")
        return
    if choice == "Decrypt File":
        clear_info(info_text)
        files = choose_files(multiple=True)
        set_info(info_text, f"Selected files to decrypt: {os.linesep}" + os.linesep.join(files))
        return


def show_main_menu(title: str) -> None:
    app = customtkinter.CTk()
    app.geometry("1000x1000")
    app.title(title)
    
    
    # Main title at the top
    title_label = customtkinter.CTkLabel(app, text="Encryptor Main Menu", font=customtkinter.CTkFont(size=24, weight="bold"))
    title_label.pack(pady=20)
    
    # Create main container frame
    main_frame = customtkinter.CTkFrame(app, fg_color="transparent")

    main_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    # Left frame for buttons
    left_frame = customtkinter.CTkFrame(main_frame, width=300)
    left_frame.pack(side="left", fill="y", padx=(0, 20))
    left_frame.pack_propagate(False)
    
    # Right frame for labels
    right_frame = customtkinter.CTkFrame(main_frame)
    right_frame.pack(side="right", fill="both", expand=True)
    
    # Button instructions in left frame
    button_label = customtkinter.CTkLabel(left_frame, text="Choose an option:", 
                                         font=customtkinter.CTkFont(size=18, weight="bold"))
    button_label.pack(pady=(20, 15))

    # Removed CTkOptionMenu sub_menu; we'll use a native tk.Menu popup per button

    # Define dropdown items for each main button
    dropdown_map: dict[str, list[str]] = {
        "Import RSA Key": ["RSA Key Data", "RSA Key File"],
        "Generate RSA Key Pair": ["2048-bit", "3072-bit", "4096-bit"],
        "Retrieve RSA Keys": ["Public Key", "Private Key"],
        "Encrypt/Decrypt": ["Encrypt Data", "Encrypt File", "Decrypt Data", "Decrypt File"],
        "Settings": ["Theme", "Security", "Paths"],
        "Help": ["User Guide", "FAQ", "About"],
    }

    # Buttons with blue shadow effect
    buttons_data = [
        ("Import RSA Key", "Import existing RSA keys from files"),
        ("Generate RSA Key Pair", "Create new RSA public/private key pair"),
        ("Retrieve RSA Keys", "Display stored RSA keys information"),
        ("Encrypt/Decrypt", "Encrypt or decrypt data/files"),
        ("Settings", "Configure application preferences and options"),
        ("Help", "Access user guide and support information"),
        ("Exit", "Close the application safely")
    ]
    
    # Information panel in right frame
    info_label = customtkinter.CTkLabel(right_frame, text="Information Panel", 
                                       font=customtkinter.CTkFont(size=20, weight="bold"))
    info_label.pack(pady=(20, 15))
    
    # Scrollable text widget for information
    info_text = customtkinter.CTkTextbox(right_frame, height=300, width=350,
                                        font=customtkinter.CTkFont(size=14))
    info_text.pack(pady=10, padx=20, fill="both", expand=True)
    
    # Create buttons with blue shadow
    for i, (button_text, description) in enumerate(buttons_data):
        button = customtkinter.CTkButton(
            left_frame,
            text=button_text,
            font=customtkinter.CTkFont(size=16, weight="bold"),
            fg_color="#1f6aa5",
            hover_color="#144870",
            border_width=2,
            border_color="#4a9eff",
            command=lambda txt=button_text: None
        )
        button.pack(pady=4, padx=20, fill="x")

        # Attach dropdown on left-click if items exist
        def on_button_click(event, txt=button_text, btn=button):
            items = dropdown_map.get(txt)
            if items:
                show_dropdown(app, btn, items, lambda val: menu_action(app, info_text, val))
            else:
                menu_action(app, info_text, txt)

        button.bind("<Button-1>", on_button_click)
    
    # Insert default information
    info_content = """Welcome to TinyEncryptor!

This application provides secure encryption and decryption capabilities using industry-standard algorithms.

Features:
• RSA Encryption: Asymmetric encryption for secure key exchange
• Fernet Encryption: Symmetric encryption for fast file encryption
• Key Management: Generate, import, and manage encryption keys
• File Processing: Encrypt/decrypt data or files with ease

Instructions:
1. Generate or import RSA keys first
2. Choose encryption method
3. Select files to process
4. Save or share encrypted files securely
5. Maintain Multiple RSA Key Pairs for different use cases

Decryption Process:
1. Enter or select the encrypted data/file
2. Provide the correct key/passphrase
3. Save the decrypted output securely

Security Notice:
Keep your private keys secure and never share them. Always backup your keys in a safe location."""
    
    info_text.insert("0.0", info_content)
    info_text.configure(state="disabled")  # Make it read-only
    
    app.mainloop()


def main():
    show_main_menu("TinyEncryptor Main Menu")
                            

        
if __name__ == "__main__":
    main()