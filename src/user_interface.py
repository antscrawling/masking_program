import os
import subprocess
from  pathlib import Path
import customtkinter
import tkinter as tk
from tkinter import messagebox, filedialog, filedialog 
import tkinter as tk
from tkinter import messagebox

ROOT_DIR = Path(__file__).parent.resolve()




def show_main_menu(title: str) -> None:
    app = customtkinter.CTk()
    app.geometry("900x900")
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
        "Import RSA Key": ["Fernet", "RSA Key"],
        "Generate RSA Key Pair": ["2048-bit", "3072-bit", "4096-bit"],
        "Retrieve RSA Keys": ["Public Key", "Private Key"],
        "Encrypt/Decrypt": ["Encrypt Data", "Encrypt File", "Decrypt Data", "Decrypt File"],
        "Settings": ["Theme", "Security", "Paths"],
        "Help": ["User Guide", "FAQ", "About"],
    }

    # Helpers to interact with the info panel and dialogs
    def clear_info():
        info_text.configure(state="normal")
        info_text.delete("1.0", "end")
        info_text.configure(state="disabled")

    def set_info(content: str):
        info_text.configure(state="normal")
        info_text.delete("1.0", "end")
        info_text.insert("1.0", content)
        info_text.configure(state="disabled")

    def ask_passphrase() -> str | None:
        dialog = customtkinter.CTkInputDialog(text="Enter passphrase (optional)", title="Passphrase")
        return dialog.get_input()

    def choose_files(multiple: bool = True) -> list[str]:
        if multiple:
            return list(filedialog.askopenfilenames(title="Select Files"))
        sel = filedialog.askopenfilename(title="Select File")
        return [sel] if sel else []

    # Handler for dropdown selections and Exit
    def menu_action(choice: str):
        if choice == "Exit":
            app.destroy()
            return
        if choice == "Fernet":
            clear_info()
            set_info("Import Fernet key: paste a key or choose a file.")
            return
        if choice == "RSA Key":
            clear_info()
            set_info("Import RSA key: paste PEM content or choose a file.")
            return
        if choice in {"2048-bit", "3072-bit", "4096-bit"}:
            clear_info()
            passphrase = ask_passphrase() or ""
            set_info(f"Generate RSA key pair ({choice}) with passphrase length: {len(passphrase)}")
            return
        if choice == "Public Key":
            clear_info()
            set_info("Showing stored public RSA keys…")
            return
        if choice == "Private Key":
            clear_info()
            set_info("Showing stored private RSA keys…")
            return
        if choice == "Encrypt Data":
            clear_info()
            set_info("Enter data to encrypt in a forthcoming dialog.")
            return
        if choice == "Encrypt File":
            clear_info()
            files = choose_files(multiple=True)
            set_info(f"Selected files to encrypt: {os.linesep}" + os.linesep.join(files))
            return
        if choice == "Decrypt Data":
            clear_info()
            set_info("Enter encrypted data and key/passphrase in a forthcoming dialog.")
            return
        if choice == "Decrypt File":
            clear_info()
            files = choose_files(multiple=True)
            set_info(f"Selected files to decrypt: {os.linesep}" + os.linesep.join(files))
            return



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
    
    # Create buttons with blue shadow
    # Utility: show a native Tk dropdown menu anchored to a widget
    def show_dropdown(anchor_widget: tk.Widget, items: list[str]):
        menu = tk.Menu(app, tearoff=0)
        for item in items:
            menu.add_command(label=item, command=lambda val=item: menu_action(val))
        # Position menu just under the anchor widget
        x = anchor_widget.winfo_rootx()
        y = anchor_widget.winfo_rooty() + anchor_widget.winfo_height()
        try:
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

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
                show_dropdown(btn, items)
            
            else:
                menu_action(txt)

        button.bind("<Button-1>", on_button_click)

   
    # each button now provides its own dropdown when clicked.
    
    # Information panel in right frame
    info_label = customtkinter.CTkLabel(right_frame, text="Information Panel", 
                                       font=customtkinter.CTkFont(size=20, weight="bold"))
    info_label.pack(pady=(20, 15))
    
    # Scrollable text widget for information
    info_text = customtkinter.CTkTextbox(right_frame, height=300, width=350,
                                        font=customtkinter.CTkFont(size=14))
    info_text.pack(pady=10, padx=20, fill="both", expand=True)
    
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