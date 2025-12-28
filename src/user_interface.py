import os
import json
from pathlib import Path
import customtkinter
import tkinter as tk
from tkinter import messagebox, filedialog
from cryptography.fernet import Fernet


ROOT_DIR = Path(__file__).parent.resolve()
BLUE = f"{'#1f6aa5'}"
RED = f"{'#c91658'}"
BLACK = f"{'#0d0c0d'}"
RESET = f"{'#ffffff'}"


def get_keys_directory() -> Path:
    """Get a user-writable directory for storing encryption keys.
    Returns a Path object to ~/Documents/TinyEncryptor_Keys/
    Creates the directory if it doesn't exist.
    """
    # Use Documents folder which is always writable
    keys_dir = Path.home() / "Documents" / "TinyEncryptor_Keys"
    
    # Create directory if it doesn't exist
    try:
        keys_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create keys directory at {keys_dir}: {e}")
        # Fallback to home directory if Documents is not accessible
        keys_dir = Path.home() / ".tinyencryptor_keys"
        keys_dir.mkdir(parents=True, exist_ok=True)
    
    return keys_dir


def load_settings() -> dict:
    """Load settings from JSON file, return default settings if file doesn't exist"""
    default_settings = {
        "theme": "System",  # Default theme
    }
    
    # Use the same directory as keys for settings
    settings_file = get_keys_directory() / "settings.json"
    
    try:
        if settings_file.exists():
            with open(settings_file, "r") as f:
                settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**default_settings, **settings}
        return default_settings
    except Exception as e:
        print(f"Error loading settings: {e}")
        return default_settings


def save_settings(settings: dict) -> bool:
    """Save settings to JSON file"""
    # Use the same directory as keys for settings
    settings_file = get_keys_directory() / "settings.json"
    
    try:
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False


class App(customtkinter.CTk):
    def __init__(
        self,
        geometry,
        title,
        button,
        title_label,
        main_frame,
        left_frame=None,
        right_frame=None,
        button_label=None,
        dropdown_map=None,
        buttons_data=None,
        info_label=None,
        info_text=None,
        button_text=None,
        description=None,
        info_content=None,
    ):
        super().__init__()

        # Set window properties using parent methods, don't override them
        self.geometry(geometry)
        self.title(title)

        # add widgets to app
        self.button = button
        # Main title at the top
        self.title_label = title_label
        # Create main container frame
        self.main_frame = main_frame
        # Left frame for buttons
        self.left_frame = left_frame
        # Right frame for labels
        self.right_frame = right_frame
        # Button instructions in left frame
        self.button_label = button_label
        # Define dropdown items for each main button
        self.dropdown_map = dropdown_map
        # Buttons with blue shadow effect
        self.buttons_data = buttons_data
        # Information panel in right frame
        self.info_label = info_label
        self.info_text = info_text
        self.button_text = button_text
        self.description = description
        self.info_content = info_content

    def show_dropdown(
        self, parent, anchor_widget: tk.Widget, items: list[str], menu_action_callback
    ):
        """Show a native Tk dropdown menu anchored to a widget"""
        menu = tk.Menu(parent, tearoff=0)
        for item in items:
            menu.add_command(
                label=item, command=lambda val=item: menu_action_callback(val)
            )
        # Position menu just under the anchor widget
        x = anchor_widget.winfo_rootx()
        y = anchor_widget.winfo_rooty() + anchor_widget.winfo_height()
        try:
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def on_button_click(self, event, txt, btn):
        self.items = self.dropdown_map.get(txt)
        if self.items:
            self.show_dropdown(
                self,
                btn,
                self.items,
                lambda val: menu_action(self, self.info_text, val),
            )
        else:
            menu_action(self, self.info_text, txt)


def display_message_dialog(parent, title: str, message: str):
    """Display a message in a dialog window"""
    msg_dialog = customtkinter.CTkToplevel(parent)
    msg_dialog.title(title)
    msg_dialog.geometry("800x700")
    msg_dialog.grab_set()

    # Message textbox
    message_text = customtkinter.CTkTextbox(
        msg_dialog, width=750, font=customtkinter.CTkFont(size=11), wrap="word"
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
        hover_color="#144870",
    )
    close_btn.pack(pady=20)


def clear_info(info_text):
    """Clear the information panel"""
    info_text.configure(state="normal")
    info_text.delete("1.0", "end")
    info_text.configure(state="disabled")


def set_info(
    info_text,
    content: str,
    color: str = None,
    bold: bool = False,
    italic: bool = False,
):
    """Set content in the information panel with custom formatting
    Note: bold and italic parameters are not used due to customtkinter limitations
    """
    # Auto-detect appropriate text color based on theme if not specified
    if color is None:
        current_mode = customtkinter.get_appearance_mode()
        if current_mode.lower() == "dark":
            color = "#FFFFFF"  # White text for dark mode
        else:
            color = BLACK  # Black text for light mode
    
    info_text.configure(state="normal")
    info_text.delete("1.0", "end")
    info_text.insert("1.0", content)

    # Apply color formatting using tags with dynamic tag names based on color
    tag_name = f"color_{color.replace('#', '')}"
    info_text.tag_add(tag_name, "1.0", "end")
    info_text.tag_config(tag_name, foreground=color)
    info_text.configure(state="disabled")


def ask_passphrase() -> str | None:
    """Ask user for passphrase"""
    dialog = customtkinter.CTkInputDialog(
        text="Enter passphrase (optional)", title="Passphrase"
    )
    return dialog.get_input()


def choose_files(multiple: bool = True) -> list[str]:
    """Choose files using file dialog"""
    if multiple:
        return list(filedialog.askopenfilenames(title="Select Files"))
    sel = filedialog.askopenfilename(title="Select File")
    return [sel] if sel else []


def retrieve_rsa_keys(type: str) -> str:
    """Retrieve RSA keys from files"""
    import main

    result = main.retrieve_rsa_keys()

    if result and result[0]:
        _, private_key, public_key = result
        return public_key if type == "public" else private_key
    else:
        return "❌ Key files not found. Please generate or import keys first."


def import_keys(
    public_key_text, private_key_text, passphrase_text, info_text, key_dialog
):
    """Import RSA keys from text widgets"""
    public_key = public_key_text.get("1.0", "end").strip()
    private_key = private_key_text.get("1.0", "end").strip()
    passphrase = passphrase_text.get("1.0", "end").strip()

    if not public_key or not private_key:
        messagebox.showerror("Error", "Both public and private keys are required!")
        return

    # Validate minimum lengths
    if len(public_key) < 200:
        messagebox.showerror(
            "Error",
            f"Public key seems to short ({len(public_key)} chars). Expected at least 200 characters.",
        )
        return

    if len(private_key) < 500:
        messagebox.showerror(
            "Error",
            f"Private key seems to short ({len(private_key)} chars). Expected at least 500 characters.",
        )
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
            passphrase=passphrase if passphrase else None,
        )

        if result and result[0]:
            messagebox.showinfo("Success", "RSA keys imported successfully!")
            passphrase_info = f"{os.linesep}Passphrase: {'provided' if passphrase else 'not provided'}"
            set_info(
                info_text,
                f"✓ RSA keys imported and saved{os.linesep}Public Key: {len(public_key)} chars{os.linesep}Private Key: {len(private_key)} chars{passphrase_info}",
            )
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
        messagebox.showerror(
            "Error", f"Import failed: {str(e)}\n\nCheck console for details."
        )


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
            font=customtkinter.CTkFont(size=14, weight="bold"),
        )
        instructions.pack(pady=(20, 10))

        # Public Key section
        pub_label = customtkinter.CTkLabel(
            key_dialog,
            text="Public Key:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
        )
        pub_label.pack(pady=(10, 5), anchor="w", padx=20)

        public_key_text = customtkinter.CTkTextbox(
            key_dialog, height=150, width=650, font=customtkinter.CTkFont(size=11)
        )
        public_key_text.pack(pady=5, padx=20)

        # Private Key section
        priv_label = customtkinter.CTkLabel(
            key_dialog,
            text="Private Key:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
        )
        priv_label.pack(pady=(10, 5), anchor="w", padx=20)

        private_key_text = customtkinter.CTkTextbox(
            key_dialog, height=150, width=650, font=customtkinter.CTkFont(size=11)
        )
        private_key_text.pack(pady=5, padx=20)

        passphrase_label = customtkinter.CTkLabel(
            key_dialog,
            text="(Optional) If your private key is encrypted, please provide the passphrase below.",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            height=1,
            width=650,
        )
        passphrase_label.pack(pady=(10, 5), anchor="w", padx=20)
        passphrase_text = customtkinter.CTkTextbox(
            key_dialog, height=10, width=650, font=customtkinter.CTkFont(size=11)
        )
        passphrase_text.pack(pady=5, padx=20)

        # Import button
        import_btn = customtkinter.CTkButton(
            key_dialog,
            text="Import Keys",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            command=lambda: import_keys(
                public_key_text,
                private_key_text,
                passphrase_text,
                info_text,
                key_dialog,
            ),
            fg_color="#1f6aa5",
            hover_color="#144870",
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
            set_info(
                info_text,
                "❌ Key files not found. Please generate or import keys first.",
            )

        return
    if choice in {"2048-bit", "3072-bit", "4096-bit"}:
        clear_info(info_text)
        set_info(info_text, f"Generate RSA key pair ({choice})")

        # Import main module
        # import main

        # Create a dialog for key generation with optional passphrase
        gen_dialog = customtkinter.CTkToplevel(app)
        gen_dialog.title(f"Generate {choice} RSA Key Pair")
        gen_dialog.geometry("700x600")
        gen_dialog.grab_set()

        # Instructions
        instructions = customtkinter.CTkLabel(
            gen_dialog,
            text=f"Generate {choice} RSA Key Pair\nEnter an optional passphrase to encrypt the private key",
            font=customtkinter.CTkFont(size=14, weight="bold"),
        )
        instructions.pack(pady=(20, 10))

        # Passphrase section
        pass_label = customtkinter.CTkLabel(
            gen_dialog,
            text="Passphrase (optional - leave empty for no encryption):",
            font=customtkinter.CTkFont(size=12),
        )
        pass_label.pack(pady=(10, 5))

        passphrase_entry = customtkinter.CTkEntry(
            gen_dialog,
            width=600,
            height=40,
            # show="*",
            placeholder_text="Enter passphrase or leave empty",
        )
        passphrase_entry.pack(pady=5)

        # Generate button callback
        def on_generate():
            import main

            passphrase = passphrase_entry.get().strip()

            # Extract key size from choice
            key_size = int(choice.replace("-bit", ""))
            gen_dialog.destroy()
            # Generate RSA key pair
            private_key, public_key, _ = main.generate_rsa_key_pair(
                passphrase=passphrase if passphrase else None, key_size=key_size
            )

            if private_key and public_key:
                # Save to files in user-writable directory
                try:
                    keys_dir = get_keys_directory()
                    private_key_path = keys_dir / "private_key.pem"
                    public_key_path = keys_dir / "public_key.pem"
                    
                    with open(private_key_path, "w") as f:
                        f.write(private_key)
                    with open(public_key_path, "w") as f:
                        f.write(public_key)

                    # Prepare message for info panel
                    message = f"✓ Successfully generated {choice} RSA key pair\n"
                    message += f"✓ Keys saved to: {keys_dir}\n"
                    passphrase_to_display = None

                    if passphrase:
                        message += "✓ Private key encrypted with passphrase\n\n"
                        message += "=" * 50 + "\n"
                        message += (
                            f"Save this Passphrase - it will only be displayed once\n"
                        )
                        passphrase_to_display = passphrase
                        message += (
                            "\n"  # Placeholder for passphrase that will be inserted
                        )
                        message += "=" * 50 + "\n\n"
                    else:
                        message += (
                            "⚠️ Private key NOT encrypted (no passphrase provided)\n\n"
                        )

                    message += "=== PUBLIC KEY ===\n"
                    message += public_key + "\n\n"
                    message += "=== PRIVATE KEY (Keep this secret!) ===\n"
                    message += private_key

                    # Display message using set_info
                    set_info(info_text, message)

                    # Now append passphrase in red if present
                    if passphrase_to_display:
                        info_text.configure(state="normal")
                        # Find the position after "Save this Passphrase - it will only be displayed once\n"
                        content = info_text.get("1.0", "end")
                        insert_marker = (
                            "Save this Passphrase - it will only be displayed once\n"
                        )
                        marker_pos = content.find(insert_marker)
                        if marker_pos != -1:
                            # Calculate line and column for insertion
                            lines_before = content[
                                : marker_pos + len(insert_marker)
                            ].count("\n")
                            insert_pos = f"{lines_before + 1}.0"
                            info_text.insert(insert_pos, f"[{passphrase_to_display}]\n")
                            end_pos = f"{lines_before + 2}.0"
                            info_text.tag_add("passphrase_red", insert_pos, end_pos)
                            info_text.tag_config("passphrase_red", foreground=RED)
                        info_text.configure(state="disabled")

                except Exception as e:
                    messagebox.showerror(
                        "Error", f"Failed to save keys to files: {str(e)}"
                    )
            else:
                messagebox.showerror("Error", "Key generation failed")

        generate_btn = customtkinter.CTkButton(
            gen_dialog,
            text="Generate Keys",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            command=on_generate,
            fg_color="#1f6aa5",
            hover_color="#144870",
        )
        generate_btn.pack(pady=20)
        # generate_btn.destroy()
        return
    if choice == "Public Key":
        clear_info(info_text)
        public_key = retrieve_rsa_keys("public")
        set_info(info_text, public_key)
        return
    if choice == "Private Key":
        clear_info(info_text)
        messagebox.showwarning(
            "Security Warning", "Be cautious when handling private keys!"
        )
        private_key = retrieve_rsa_keys("private")
        set_info(info_text, private_key)
        return
    if choice == "Encrypt Data":
        import main

        message = ""
        clear_info(info_text)
        set_info(info_text, "Enter data to encrypt in the dialog.")

        # Create a dialog window for data encryption
        encrypt_dialog = customtkinter.CTkToplevel(app)
        encrypt_dialog.title("Encrypt Data")
        encrypt_dialog.geometry("700x500")
        encrypt_dialog.grab_set()

        # Instructions
        instructions = customtkinter.CTkLabel(
            encrypt_dialog,
            text="Enter the data you want to encrypt below:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
        )
        instructions.pack(pady=(20, 10))

        # Data input section
        data_label = customtkinter.CTkLabel(
            encrypt_dialog,
            text="Data to Encrypt:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
        )
        data_label.pack(pady=(10, 5), anchor="w", padx=20)

        data_text = customtkinter.CTkTextbox(
            encrypt_dialog, height=200, width=650, font=customtkinter.CTkFont(size=11)
        )
        data_text.pack(pady=5, padx=20)

        # Encrypt button
        def perform_encryption(message=message):
            data_to_encrypt = data_text.get("1.0", "end").strip()

            if not data_to_encrypt:
                messagebox.showerror("Error", "Please enter data to encrypt!")
                return

            try:
                # Call the encryption function
                encrypted_dict, key = main.encrypt_data_not_binary(data_to_encrypt)

                if encrypted_dict and key:
                    # Extract the encrypted data from the dictionary
                    # The key is the encryption key (as string), value is encrypted data
                    key_str = key.decode() if isinstance(key, bytes) else key
                    encrypted_data = encrypted_dict.get(key_str, "")

                    # Prepare message for info panel
                    message += f"✓ Data encrypted successfully\n\n"
                    message += f"===== ORIGINAL DATA =====\n"
                    message += f"{data_to_encrypt}\n\n"
                    message += "==END OF ORIGINAL DATA==\n"
                    message += "========================\n\n"
                    message += "=== ENCRYPTED DATA ===\n"
                    message += f"{encrypted_data}\n\n"
                    message += "=== ENCRYPTION KEY ===\n"
                    message += f"{key_str}\n\n"
                    message += "⚠️ Save both the encrypted data and key securely!"

                    # Display result using set_info
                    set_info(info_text, message)

                    messagebox.showinfo(
                        "Success",
                        "Data encrypted successfully!\nCheck the information panel for encrypted data and key.",
                    )
                    encrypt_dialog.destroy()
                else:
                    messagebox.showerror(
                        "Error", "Encryption failed. Please try again."
                    )
            except Exception as e:
                import traceback

                error_details = traceback.format_exc()
                print(f"Encryption error details:\n{error_details}")
                messagebox.showerror(
                    "Error",
                    f"Encryption failed: {str(e)}\n\nCheck console for details.",
                )

        encrypt_btn = customtkinter.CTkButton(
            encrypt_dialog,
            text="Encrypt",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            command=perform_encryption,
            fg_color="#1f6aa5",
            hover_color="#144870",
        )
        encrypt_btn.pack(pady=20)

        return
    if choice == "Encrypt File":
        clear_info(info_text)
        set_info(info_text, "Select files to encrypt...")

        # Create a dialog window for file encryption
        file_encrypt_dialog = customtkinter.CTkToplevel(app)
        file_encrypt_dialog.title("Encrypt Files")
        file_encrypt_dialog.geometry("700x600")
        file_encrypt_dialog.grab_set()

        # Instructions
        instructions = customtkinter.CTkLabel(
            file_encrypt_dialog,
            text="Select files to encrypt\nEncrypted files will be saved as: file<encrypted>.ext",
            font=customtkinter.CTkFont(size=14, weight="bold"),
        )
        instructions.pack(pady=(20, 10))

        # Selected files display
        files_label = customtkinter.CTkLabel(
            file_encrypt_dialog,
            text="Selected Files:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
        )
        files_label.pack(pady=(10, 5), anchor="w", padx=20)

        files_listbox = customtkinter.CTkTextbox(
            file_encrypt_dialog,
            height=200,
            width=650,
            font=customtkinter.CTkFont(size=11),
        )
        files_listbox.pack(pady=5, padx=20)
        files_listbox.configure(state="disabled")

        # Store selected files
        selected_files = []

        # Choose files button
        def choose_files_to_encrypt():
            nonlocal selected_files
            selected_files = choose_files(multiple=True)

            if selected_files:
                files_listbox.configure(state="normal")
                files_listbox.delete("1.0", "end")
                files_listbox.insert("1.0", "\n".join(selected_files))
                files_listbox.configure(state="disabled")

        choose_btn = customtkinter.CTkButton(
            file_encrypt_dialog,
            text="Choose Files",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            command=choose_files_to_encrypt,
            fg_color="#1f6aa5",
            hover_color="#144870",
        )
        choose_btn.pack(pady=10)

        # Encrypt button
        def perform_file_encryption():
            import main
            from cryptography.fernet import Fernet

            if not selected_files:
                messagebox.showerror("Error", "Please select files to encrypt!")
                return

            try:
                new_files = []
                file_keys = []
                encrypted_data_list = []

                # Encrypt each file
                for file_path in selected_files:
                    encrypted_data, file_key, original_name = (
                        main.encrypt_file_with_fernet(file_path)
                    )

                    if encrypted_data and file_key:
                        # Create encrypted filename: file<encrypted>.ext
                        file_parts = os.path.splitext(original_name)
                        encrypted_filename = (
                            f"{file_parts[0]}<encrypted>{file_parts[1]}"
                        )
                        encrypted_file_path = os.path.join(
                            os.path.dirname(file_path), encrypted_filename
                        )

                        # Save encrypted data to file
                        with open(encrypted_file_path, "w") as f:
                            f.write(encrypted_data)

                        new_files.append(encrypted_file_path)
                        file_keys.append(file_key)
                        encrypted_data_list.append(
                            (original_name, encrypted_filename, file_key)
                        )

                if new_files:
                    # Prepare message for info panel
                    message = f"✓ Successfully encrypted {len(new_files)} file(s)\n\n"
                    message += "=== ORIGINAL FILES ===\n"
                    for orig_file in selected_files:
                        message += f"{orig_file}\n"
                    message += "\n=== ENCRYPTED FILES ===\n"
                    for new_file in new_files:
                        message += f"{new_file}\n"

                    #       # Display encryption keys - one per file with clear separation
                    #       message += "\n" + "="*50 + "\n"
                    #       message += "=== ENCRYPTION KEYS ===\n"
                    #       message += "="*50 + "\n"
                    mykeys = []
                    # for _, (_, _,key) in enumerate(encrypted_data_list, 1):
                    # message += f"\n--- FILE {i} ---\n"
                    # message += f"Original: {orig_name}\n"
                    # message += f"Encrypted: {enc_name}\n"
                    #      message += f"KEY: \n {key}\n"
                    for key in encrypted_data_list:
                        mykeys.append(f"{key[2]}")
                    #      if i < len(encrypted_data_list):
                    #          message += "-" * 40 + "\n"
                    message += "\n" + "=" * 50 + "\n"
                    message += f"KEYS IN STRICT ORDER\n\n"
                    for i, row in enumerate(mykeys, 1):
                        message += f"{row}\n"  # Show first 20 chars

                    message += "\n" + "=" * 50 + "\n"
                    message += "⚠️ IMPORTANT: Save these encryption keys securely!\n"
                    message += "You will need them to decrypt the files later.\n"
                    message += "=" * 50

                    # Display result using set_info
                    set_info(info_text, message)

                    messagebox.showinfo(
                        "Success",
                        f"Successfully encrypted {len(new_files)} file(s)!\nCheck the information panel for details.",
                    )
                    file_encrypt_dialog.destroy()
                else:
                    messagebox.showerror(
                        "Error", "File encryption failed. Please try again."
                    )
            except Exception as e:
                import traceback

                error_details = traceback.format_exc()
                print(f"File encryption error details:\n{error_details}")
                messagebox.showerror(
                    "Error",
                    f"File encryption failed: {str(e)}\n\nCheck console for details.",
                )

        encrypt_files_btn = customtkinter.CTkButton(
            file_encrypt_dialog,
            text="Encrypt Files",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            command=perform_file_encryption,
            fg_color="#1f6aa5",
            hover_color="#144870",
        )
        encrypt_files_btn.pack(pady=20)

        return
    if choice == "Decrypt Data":
        clear_info(info_text)
        set_info(info_text, "Enter encrypted data and key to decrypt...")

        # Create a dialog window for data decryption
        decrypt_dialog = customtkinter.CTkToplevel(app)
        decrypt_dialog.title("Decrypt Data")
        decrypt_dialog.geometry("700x600")
        decrypt_dialog.grab_set()

        # Instructions
        instructions = customtkinter.CTkLabel(
            decrypt_dialog,
            text="Enter the encrypted data and encryption key below:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
        )
        instructions.pack(pady=(20, 10))

        # Encrypted data section
        encrypted_label = customtkinter.CTkLabel(
            decrypt_dialog,
            text="Encrypted Data:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
        )
        encrypted_label.pack(pady=(10, 5), anchor="w", padx=20)

        encrypted_text = customtkinter.CTkTextbox(
            decrypt_dialog, height=200, width=650, font=customtkinter.CTkFont(size=11)
        )
        encrypted_text.pack(pady=5, padx=20)

        # Key section
        key_label = customtkinter.CTkLabel(
            decrypt_dialog,
            text="Encryption Key:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
        )
        key_label.pack(pady=(10, 5), anchor="w", padx=20)

        key_entry = customtkinter.CTkEntry(
            decrypt_dialog, width=650, height=40, font=customtkinter.CTkFont(size=11)
        )
        key_entry.pack(pady=5, padx=20)

        # Decrypt button
        def perform_data_decryption():
            import main

            encrypted_data = encrypted_text.get("1.0", "end").strip()
            key = key_entry.get().strip()

            if not encrypted_data or not key:
                messagebox.showerror(
                    "Error", "Please enter both encrypted data and key!"
                )
                return

            try:
                # Call the decryption function
                decrypted_result = main.decrypt_data_not_binary(encrypted_data, key)

                if decrypted_result:
                    # Prepare message for info panel
                    message = "✓ Data decrypted successfully\n\n"
                    message += "=== ENCRYPTED DATA ===\n"
                    message += f"{encrypted_data}\n\n"
                    message += "=== DECRYPTED DATA ===\n"
                    message += f"{decrypted_result}\n\n"
                    message += "=== KEY USED ===\n"
                    message += f"{key}"

                    # Display result using set_info
                    set_info(info_text, message)

                    messagebox.showinfo(
                        "Success",
                        "Data decrypted successfully!\nCheck the information panel for decrypted data.",
                    )
                    decrypt_dialog.destroy()
                else:
                    messagebox.showerror(
                        "Error",
                        "Decryption failed. Please check your encrypted data and key.",
                    )
            except Exception as e:
                import traceback

                error_details = traceback.format_exc()
                print(f"Decryption error details:\n{error_details}")
                messagebox.showerror(
                    "Error",
                    f"Decryption failed: {str(e)}\n\nCheck console for details.",
                )

        decrypt_btn = customtkinter.CTkButton(
            decrypt_dialog,
            text="Decrypt",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            command=perform_data_decryption,
            fg_color="#1f6aa5",
            hover_color="#144870",
        )
        decrypt_btn.pack(pady=20)

        return
    if choice == "Decrypt File":
        clear_info(info_text)
        set_info(info_text, "Select encrypted files to decrypt...")

        # Create a dialog window for file decryption
        file_decrypt_dialog = customtkinter.CTkToplevel(app)
        file_decrypt_dialog.title("Decrypt Files")
        file_decrypt_dialog.geometry("700x600")
        file_decrypt_dialog.grab_set()

        # Instructions
        instructions = customtkinter.CTkLabel(
            file_decrypt_dialog,
            text="Select encrypted files (file<encrypted>.ext format)\nEnter encryption keys (one per line, matching file order):",
            font=customtkinter.CTkFont(size=14, weight="bold"),
        )
        instructions.pack(pady=(20, 10))

        # Selected files display
        files_label = customtkinter.CTkLabel(
            file_decrypt_dialog,
            text="Selected Encrypted Files:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
        )
        files_label.pack(pady=(10, 5), anchor="w", padx=20)

        files_listbox = customtkinter.CTkTextbox(
            file_decrypt_dialog,
            height=150,
            width=650,
            font=customtkinter.CTkFont(size=11),
        )
        files_listbox.pack(pady=5, padx=20)
        files_listbox.configure(state="disabled")

        # Store selected files
        selected_files = []

        # Choose files button
        def choose_files_to_decrypt():
            nonlocal selected_files
            selected_files = choose_files(multiple=True)

            if selected_files:
                files_listbox.configure(state="normal")
                files_listbox.delete("1.0", "end")
                files_listbox.insert("1.0", "\n".join(selected_files))
                files_listbox.configure(state="disabled")

        choose_btn = customtkinter.CTkButton(
            file_decrypt_dialog,
            text="Choose Encrypted Files",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            command=choose_files_to_decrypt,
            fg_color="#1f6aa5",
            hover_color="#144870",
        )
        choose_btn.pack(pady=10)

        # Key section - Changed to textbox for multiple keys
        key_label = customtkinter.CTkLabel(
            file_decrypt_dialog,
            text="Encryption Keys (one per line, in same order as files):",
            font=customtkinter.CTkFont(size=14, weight="bold"),
        )
        key_label.pack(pady=(10, 5), anchor="w", padx=20)

        key_textbox = customtkinter.CTkTextbox(
            file_decrypt_dialog,
            width=650,
            height=120,
            font=customtkinter.CTkFont(size=11),
        )
        key_textbox.pack(pady=5, padx=20)

        # Decrypt button
        def perform_file_decryption():
            import main

            if not selected_files:
                messagebox.showerror("Error", "Please select files to decrypt!")
                return

            # Get all keys from textbox (one per line)
            keys_text = key_textbox.get("1.0", "end").strip()
            if not keys_text:
                messagebox.showerror("Error", "Please enter the encryption key(s)!")
                return

            # Split keys by line, remove blank lines, and strip whitespace
            keys = [line.strip() for line in keys_text.splitlines() if line.strip()]

            # Debug: print keys to console
            print(f"Number of files: {len(selected_files)}")
            print(f"Number of keys parsed: {len(keys)}")
            for i, key in enumerate(keys, 1):
                print(
                    f"Key {i} (length {len(key)}): {key[:20]}..."
                )  # Show first 20 chars

            # Check if number of keys matches number of files
            if len(keys) != len(selected_files):
                messagebox.showerror(
                    "Error",
                    f"Number of keys ({len(keys)}) doesn't match number of files ({len(selected_files)})!\n\n"
                    f"Please provide one key per line, matching the order of selected files.\n\n"
                    f"Keys found: {len(keys)}\nFiles selected: {len(selected_files)}",
                )
                return

            try:
                decrypted_files = []
                decryption_info = []
                failed_files = []

                # Decrypt each file with its corresponding key
                for file_path, key in zip(selected_files, keys):
                    try:
                        # Read encrypted data from file
                        with open(file_path, "r") as f:
                            encrypted_data = f.read().strip()

                        # Remove <encrypted> from filename to get original name
                        original_filename = os.path.basename(file_path).replace(
                            "<encrypted>", ""
                        )
                        output_path = os.path.join(
                            os.path.dirname(file_path), original_filename
                        )

                        # Decrypt the file
                        success = main.decrypt_file_with_fernet(
                            encrypted_data, key, output_path
                        )

                        print(
                            f"Decryption result for {os.path.basename(file_path)}: {success} (type: {type(success)})"
                        )

                        if success:
                            decrypted_files.append(output_path)
                            decryption_info.append(
                                (
                                    os.path.basename(file_path),
                                    original_filename,
                                    key,
                                    True,
                                )
                            )
                        else:
                            failed_files.append(os.path.basename(file_path))
                            decryption_info.append(
                                (
                                    os.path.basename(file_path),
                                    original_filename,
                                    key,
                                    False,
                                )
                            )
                    except Exception as e:
                        failed_files.append(os.path.basename(file_path))
                        decryption_info.append(
                            (os.path.basename(file_path), original_filename, key, False)
                        )
                        print(f"Error decrypting {file_path}: {e}")

                if decrypted_files or failed_files:
                    # Prepare message for info panel
                    message = ""
                    if decrypted_files:
                        message += (
                            f"✓ Successfully decrypted {len(decrypted_files)} file(s)\n"
                        )
                    if failed_files:
                        message += f"❌ Failed to decrypt {len(failed_files)} file(s)\n"
                    message += "\n"

                    # Show detailed info for each file
                    message += "=" * 50 + "\n"
                    message += "=== DECRYPTION DETAILS ===\n"
                    message += "=" * 50 + "\n"

                    for i, (enc_name, dec_name, key, success) in enumerate(
                        decryption_info, 1
                    ):
                        message += f"\n--- FILE {i} ---\n"
                        message += f"Encrypted: {enc_name}\n"
                        message += f"Decrypted: {dec_name}\n"
                        message += f"Key Used: {key}\n"
                        message += (
                            f"Status: {'✓ Success' if success else '❌ Failed'}\n"
                        )
                        if i < len(decryption_info):
                            message += "-" * 40 + "\n"

                    message += "\n" + "=" * 50 + "\n"
                    if decrypted_files:
                        message += "✓ Successful files have been restored to their original names\n"
                    if failed_files:
                        message += "❌ Failed files may have incorrect keys\n"
                    message += "=" * 50

                    # Display result using set_info
                    set_info(info_text, message)

                    # Show appropriate message
                    if decrypted_files and not failed_files:
                        messagebox.showinfo(
                            "Success",
                            f"Successfully decrypted {len(decrypted_files)} file(s)!\nCheck the information panel for details.",
                        )
                    elif decrypted_files and failed_files:
                        messagebox.showwarning(
                            "Partial Success",
                            f"Decrypted {len(decrypted_files)} file(s), but {len(failed_files)} failed!\nCheck the information panel for details.",
                        )
                    else:
                        messagebox.showerror(
                            "Error",
                            f"All {len(failed_files)} file(s) failed to decrypt!\nPlease check your keys.",
                        )

                    file_decrypt_dialog.destroy()
                else:
                    messagebox.showerror(
                        "Error", "File decryption failed. Please check your key."
                    )
            except Exception as e:
                import traceback

                error_details = traceback.format_exc()
                print(f"File decryption error details:\n{error_details}")
                messagebox.showerror(
                    "Error",
                    f"File decryption failed: {str(e)}\n\nCheck console for details.",
                )

        decrypt_files_btn = customtkinter.CTkButton(
            file_decrypt_dialog,
            text="Decrypt Files",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            command=perform_file_decryption,
            fg_color="#1f6aa5",
            hover_color="#144870",
        )
        decrypt_files_btn.pack(pady=20)

        return
    if choice == "Theme":
        clear_info(info_text)
        set_info(info_text, "Theme settings: configure application appearance")

        # Create a dialog window for theme settings
        theme_dialog = customtkinter.CTkToplevel(app)
        theme_dialog.title("Theme Settings")
        theme_dialog.geometry("600x500")
        theme_dialog.grab_set()

        # Instructions
        instructions = customtkinter.CTkLabel(
            theme_dialog,
            text="Configure Application Theme",
            font=customtkinter.CTkFont(size=18, weight="bold"),
        )
        instructions.pack(pady=(20, 10))

        # Current theme display
        current_theme = customtkinter.get_appearance_mode()
        current_label = customtkinter.CTkLabel(
            theme_dialog,
            text=f"Current Theme: {current_theme}",
            font=customtkinter.CTkFont(size=14),
        )
        current_label.pack(pady=10)

        # Theme selection
        theme_label = customtkinter.CTkLabel(
            theme_dialog,
            text="Select Theme:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
        )
        theme_label.pack(pady=(20, 10))

        theme_var = customtkinter.StringVar(value=current_theme)

        # Theme radio buttons
        themes = ["Light", "Dark", "System"]
        for theme in themes:
            radio = customtkinter.CTkRadioButton(
                theme_dialog,
                text=theme,
                variable=theme_var,
                value=theme,
                font=customtkinter.CTkFont(size=13),
            )
            radio.pack(pady=5)

        # Apply button
        def apply_theme():
            selected_theme = theme_var.get()
            customtkinter.set_appearance_mode(selected_theme.lower())
            
            # Save theme to settings file
            settings = load_settings()
            settings["theme"] = selected_theme
            save_settings(settings)
            
        
            set_info(
                info_text,
                f"✓ Theme changed to: {selected_theme}\n\nThe new theme has been applied and saved to settings.",
            )
            messagebox.showinfo(
                "Success", f"Theme changed to {selected_theme} and saved successfully!"
            )
            theme_dialog.destroy()

        apply_btn = customtkinter.CTkButton(
            theme_dialog,
            text="Apply Theme",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            command=apply_theme,
            fg_color="#1f6aa5",
            hover_color="#144870",
        )
        apply_btn.pack(pady=30)

        return
    if choice == "Security":
        clear_info(info_text)
        set_info(info_text, "Security settings: manage key storage and security options")

        # Create a dialog window for security settings
        security_dialog = customtkinter.CTkToplevel(app)
        security_dialog.title("Security Settings")
        security_dialog.geometry("700x600")
        security_dialog.grab_set()

        # Instructions
        instructions = customtkinter.CTkLabel(
            security_dialog,
            text="Security Configuration",
            font=customtkinter.CTkFont(size=18, weight="bold"),
        )
        instructions.pack(pady=(20, 10))

        # Security information
        info_frame = customtkinter.CTkFrame(security_dialog)
        info_frame.pack(pady=20, padx=30, fill="both", expand=True)

        security_info = customtkinter.CTkTextbox(
            info_frame,
            height=300,
            width=600,
            font=customtkinter.CTkFont(size=12),
            wrap="word",
        )
        security_info.pack(pady=10, padx=10, fill="both", expand=True)

        security_text = """Security Best Practices:

1. Key Storage:
   • Store private keys in secure locations
   • Use strong passphrases for key encryption
   • Never share private keys via insecure channels
   • Regularly backup keys to secure locations

2. Key Management:
   • Rotate keys periodically for high-security applications
   • Use different key pairs for different purposes
   • Delete old keys securely when no longer needed

3. Encryption Guidelines:
   • Use 4096-bit RSA keys for maximum security
   • Always verify encrypted data integrity
   • Keep encryption software updated

4. File Security:
   • Encrypted files: {encrypted_location}
   • Key files: {key_location}
   • Always maintain backup copies

Current Security Status:
✓ RSA encryption available
✓ Fernet symmetric encryption active
✓ Key files stored locally

⚠️ Warning: This application stores keys locally. 
For production use, consider hardware security modules (HSM)."""

        # Replace placeholders with actual paths
        encrypted_location = str(ROOT_DIR)
        key_location = str(get_keys_directory())
        security_text = security_text.replace("{encrypted_location}", encrypted_location)
        security_text = security_text.replace("{key_location}", key_location)

        security_info.insert("1.0", security_text)
        security_info.configure(state="disabled")

        # Close button
        close_btn = customtkinter.CTkButton(
            security_dialog,
            text="Close",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            command=security_dialog.destroy,
            fg_color="#1f6aa5",
            hover_color="#144870",
        )
        close_btn.pack(pady=20)

        set_info(
            info_text,
            "Security settings displayed.\n\nReview security best practices in the dialog window.",
        )

        return
    if choice == "Paths":
        clear_info(info_text)
        set_info(info_text, "Path settings: view and configure file locations")

        # Create a dialog window for path settings
        paths_dialog = customtkinter.CTkToplevel(app)
        paths_dialog.title("Path Settings")
        paths_dialog.geometry("700x600")
        paths_dialog.grab_set()

        # Instructions
        instructions = customtkinter.CTkLabel(
            paths_dialog,
            text="Application Paths Configuration",
            font=customtkinter.CTkFont(size=18, weight="bold"),
        )
        instructions.pack(pady=(20, 10))

        # Paths information frame
        paths_frame = customtkinter.CTkFrame(paths_dialog)
        paths_frame.pack(pady=20, padx=30, fill="both", expand=True)

        # Display current paths
        paths_label = customtkinter.CTkLabel(
            paths_frame,
            text="Current Application Paths:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
        )
        paths_label.pack(pady=(10, 5), anchor="w", padx=10)

        paths_info = customtkinter.CTkTextbox(
            paths_frame,
            height=300,
            width=600,
            font=customtkinter.CTkFont(size=12),
            wrap="word",
        )
        paths_info.pack(pady=10, padx=10, fill="both", expand=True)

        # Build path information
        keys_dir = get_keys_directory()
        paths_text = f"""Application Directory Paths:

1. Root Directory:
   {ROOT_DIR}
   • Contains main application files

2. Key Files Directory:
   {keys_dir}
   • Public Key: {keys_dir / 'public_key.pem'}
   • Private Key: {keys_dir / 'private_key.pem'}

3. Working Directory:
   {os.getcwd()}
   • Current working directory
   • Default location for encrypted/decrypted files

4. Home Directory:
   {Path.home()}
   • User home directory

File Naming Conventions:
• Encrypted files: filename<encrypted>.ext
• Decrypted files: filename.ext (original name restored)
• Key files: *_key.pem format

Note: You can select different directories when 
encrypting or decrypting files using the file dialogs."""

        paths_info.insert("1.0", paths_text)
        paths_info.configure(state="disabled")

        # Open directory button
        def open_root_dir():
            import subprocess
            import platform

            system = platform.system()
            try:
                if system == "Darwin":  # macOS
                    subprocess.run(["open", str(ROOT_DIR)])
                elif system == "Windows":
                    subprocess.run(["explorer", str(ROOT_DIR)])
                else:  # Linux and others
                    subprocess.run(["xdg-open", str(ROOT_DIR)])
                messagebox.showinfo(
                    "Success", f"Opened directory: {ROOT_DIR}"
                )
            except Exception as e:
                messagebox.showerror(
                    "Error", f"Failed to open directory: {str(e)}"
                )

        def open_keys_dir():
            import subprocess
            import platform

            system = platform.system()
            keys_dir = get_keys_directory()
            try:
                if system == "Darwin":  # macOS
                    subprocess.run(["open", str(keys_dir)])
                elif system == "Windows":
                    subprocess.run(["explorer", str(keys_dir)])
                else:  # Linux and others
                    subprocess.run(["xdg-open", str(keys_dir)])
                messagebox.showinfo(
                    "Success", f"Opened keys directory: {keys_dir}"
                )
            except Exception as e:
                messagebox.showerror(
                    "Error", f"Failed to open directory: {str(e)}"
                )

        open_dir_btn = customtkinter.CTkButton(
            paths_dialog,
            text="Open Root Directory",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            command=open_root_dir,
            fg_color="#1f6aa5",
            hover_color="#144870",
        )
        open_dir_btn.pack(pady=10)

        open_keys_btn = customtkinter.CTkButton(
            paths_dialog,
            text="Open Keys Directory",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            command=open_keys_dir,
            fg_color="#1f6aa5",
            hover_color="#144870",
        )
        open_keys_btn.pack(pady=10)

        # Close button
        close_btn = customtkinter.CTkButton(
            paths_dialog,
            text="Close",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            command=paths_dialog.destroy,
            fg_color="#1f6aa5",
            hover_color="#144870",
        )
        close_btn.pack(pady=10)

        set_info(
            info_text,
            f"Path settings displayed.\n\nRoot directory: {ROOT_DIR}\nWorking directory: {os.getcwd()}",
        )

        return


def show_main_menu(title: str) -> None:
    # Load and apply saved theme before creating the app
    settings = load_settings()
    saved_theme = settings.get("theme", "System")
    customtkinter.set_appearance_mode(saved_theme.lower())
    
    app = App(
        geometry="1000x1000",
        title=title,
        button=None,  # Initialize as None, will set later
        title_label=None,
        main_frame=None,
        left_frame=None,
        right_frame=None,
        button_label=None,
        dropdown_map=None,
        buttons_data=None,
        info_label=None,
        info_text=None,
        button_text=None,
        description=None,
        info_content=None,
    )
    # Now create the widgets
    app.title_label = customtkinter.CTkLabel(
        app,
        text="Encryptor Main Menu",
        font=customtkinter.CTkFont(size=24, weight="bold"),
    )
    app.title_label.pack(pady=20)

    app.main_frame = customtkinter.CTkFrame(app, fg_color="transparent")
    app.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

    app.left_frame = customtkinter.CTkFrame(app.main_frame, width=300)
    app.left_frame.pack(side="left", fill="y", padx=(0, 10))
    app.left_frame.pack_propagate(False)

    app.right_frame = customtkinter.CTkFrame(app.main_frame)
    app.right_frame.pack(side="right", fill="both", expand=True)

    app.button_label = customtkinter.CTkLabel(
        app.left_frame,
        text="Choose an option:",
        font=customtkinter.CTkFont(size=18, weight="bold"),
    )
    app.button_label.pack(pady=(20, 15))

    app.dropdown_map = {
        "Import RSA Key": ["RSA Key Data", "RSA Key File"],
        "Generate RSA Key Pair": ["2048-bit", "3072-bit", "4096-bit"],
        "Display the RSA Keys": ["Public Key", "Private Key"],
        "Encrypt/Decrypt": [
            "Encrypt Data",
            "Encrypt File",
            "Decrypt Data",
            "Decrypt File",
        ],
        "Settings": ["Theme", "Security", "Paths"],
        "Help": ["User Guide", "FAQ", "About"],
    }

    app.buttons_data = [
        ("Import RSA Key", "Import existing RSA keys from files"),
        ("Generate RSA Key Pair", "Create new RSA public/private key pair"),
        ("Display the RSA Keys", "Display stored RSA keys information"),
        ("Encrypt/Decrypt", "Encrypt or decrypt data/files"),
        ("Settings", "Configure application preferences and options"),
        ("Help", "Access user guide and support information"),
        ("Exit", "Close the application safely"),
    ]

    app.info_label = customtkinter.CTkLabel(
        app.right_frame,
        text="Information Panel",
        font=customtkinter.CTkFont(size=20, weight="bold"),
    )
    app.info_label.pack(pady=(20, 15))

    app.info_text = customtkinter.CTkTextbox(
        app.right_frame, height=300, width=350, font=customtkinter.CTkFont(size=14)
    )
    app.info_text.pack(pady=10, padx=20, fill="both", expand=True)

    # Create buttons with blue shadow
    for i, (button_text, description) in enumerate(app.buttons_data):
        button = customtkinter.CTkButton(
            app.left_frame,
            text=button_text,
            font=customtkinter.CTkFont(size=16, weight="bold"),
            fg_color="#1f6aa5",
            hover_color="#144870",
            border_width=2,
            border_color="#4a9eff",
            command=lambda txt=button_text: None,
        )
        button.pack(pady=4, padx=20, fill="x")
        button.bind(
            "<Button-1>",
            lambda e, txt=button_text, btn=button: app.on_button_click(e, txt, btn),
        )

    app.info_content = """Welcome to TinyEncryptor!

    This application provides secure encryption and 
    decryption capabilities using industry-standard 
    algorithms.

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

    # Set initial content with theme-aware colors
    set_info(app.info_text, app.info_content)

    app.mainloop()


def main():
    show_main_menu("TinyEncryptor Main Menu")


if __name__ == "__main__":
    main()
