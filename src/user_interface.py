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


 #   app.mainloop()
 
  #  app.mainloop()








    
    
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

    # Contextual sub-menu which will be configured dynamically
    sub_menu = customtkinter.CTkOptionMenu(
        master=left_frame,
        values=[],
        command=lambda c: print(f"Import type: {c}")
    )
    # Keep it hidden until needed
    # We will pack/unpack it in the handler below

    # Handler to update sub-menu based on choice
    def menu_action(choice: str):
        if choice == "Import RSA Key":
            sub_menu.configure(values=["Fernet", "RSA Key"]) 
            sub_menu.pack(pady=10, padx=20, fill="x")
        elif choice == "Generate RSA Key Pair":
            sub_menu.configure(values=["2048-bit", "3072-bit", "4096-bit"]) 
            sub_menu.pack(pady=10, padx=20, fill="x")
        elif choice == "Retrieve RSA Keys":
            sub_menu.configure(values=["Public Key", "Private Key", "All Keys"]) 
            sub_menu.pack(pady=10, padx=20, fill="x")
        elif choice == "Batch Encrypt/Decrypt":
            sub_menu.configure(values=["Encrypt Batch", "Decrypt Batch"]) 
            sub_menu.pack(pady=10, padx=20, fill="x")
        elif choice == "Settings":
            sub_menu.configure(values=["Theme", "Security", "Paths"]) 
            sub_menu.pack(pady=10, padx=20, fill="x")
        elif choice == "Help":
            sub_menu.configure(values=["User Guide", "FAQ", "About"]) 
            sub_menu.pack(pady=10, padx=20, fill="x")
        elif choice == "Exit":
            # Hide submenu and exit
            try:
                sub_menu.pack_forget()
            except Exception:
                pass
            app.destroy()
        else:
            # Hide submenu for actions without options
            try:
                sub_menu.pack_forget()
            except Exception:
                pass
    
    # Buttons with blue shadow effect
    buttons_data = [
        ("Import RSA Key", "Import existing RSA keys from files"),
        ("Encrypt", "Encrypt files using RSA or Fernet encryption"),
        ("Decrypt", "Decrypt previously encrypted files"),
        ("Generate RSA Key Pair", "Create new RSA public/private key pair"),
        ("Retrieve RSA Keys", "Display stored RSA keys information"),
        ("Fernet Key Management", "Manage symmetric Fernet encryption keys"),
        ("Batch Encrypt/Decrypt", "Process multiple files at once"),
        ("Settings", "Configure application preferences and options"),
        ("Help", "Access user guide and support information"),
        ("Exit", "Close the application safely")
    ]
    
    # Create buttons with blue shadow
    for i, (button_text, description) in enumerate(buttons_data):
        button = customtkinter.CTkButton(
            left_frame, 
            text=button_text, 
            font=customtkinter.CTkFont(size=16, weight="bold"),
            fg_color="#1f6aa5",  # Blue color
            hover_color="#144870",  # Darker blue on hover
            border_width=2,
            border_color="#4a9eff",  # Light blue border for shadow effect
            command=lambda txt=button_text: menu_action(txt)
        )
        button.pack(pady=4, padx=20, fill="x")

    # Also provide a global options dropdown to trigger the same handler
    options = [
        "Import RSA Key",
        "Generate RSA Key Pair",
        "Retrieve RSA Keys",
        "Batch Encrypt/Decrypt",
        "Settings",
        "Help",
        "Exit"
    ]
    option_menu = customtkinter.CTkOptionMenu(
        master=left_frame,
        values=options,
        command=menu_action
    )
    option_menu.pack(pady=12, padx=20, fill="x")
    
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
• File Processing: Encrypt/decrypt text files easily

Instructions:
1. Generate or import RSA keys first
2. Choose encryption method
3. Select files to process
4. Save or share encrypted files securely
5. Maintain Multiple RSA Key Pairs for different use cases

Security Notice:
Keep your private keys secure and never share them. Always backup your keys in a safe location."""
    
    info_text.insert("0.0", info_content)
    info_text.configure(state="disabled")  # Make it read-only
    
    app.mainloop()
    
def main():
    show_main_menu("TinyEncryptor Main Menu")






    
    
    
    
    
    
    











        
if __name__ == "__main__":
    main()