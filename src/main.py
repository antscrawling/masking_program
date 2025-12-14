import  cryptography
import os
import pathlib
import sys
import time
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import json
import base64



def open_file(file_path: str) -> dict:
    if not os.path.exists(file_path) :
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    else:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    
def write_file(file_path: str, data: dict) -> None:
    # Load existing data if file exists, otherwise start with empty dict
    existing_data = {}
    if os.path.exists(file_path):
        try:
            existing_data = open_file(file_path)
        except:
            existing_data = {}
    
    # Merge new data with existing data
    existing_data.update(data)
    
    with open(file_path, 'w') as file:
        json.dump(existing_data, file, indent=4)

def generate_rsa_key_pair(passphrase=None):
    """Generate RSA public and private key pair with optional passphrase protection"""
    try:
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        # Get public key from private key
        public_key = private_key.public_key()
        
        # Choose encryption algorithm based on passphrase
        if passphrase:
            encryption_algorithm = serialization.BestAvailableEncryption(passphrase.encode())
            print("Private key will be encrypted with your passphrase.")
        else:
            encryption_algorithm = serialization.NoEncryption()
            print("Private key will not be encrypted (no passphrase provided).")
        
        # Serialize private key to PEM format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        )
        
        # Serialize public key to PEM format (never encrypted)
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem.decode('utf-8'), public_pem.decode('utf-8'), passphrase
    
    except Exception as e:
        print(f'Error generating RSA key pair: {e}')
        return None, None, None

def retrieve_rsa_keys():
    """Retrieve and display saved RSA keys from files"""
    private_key_file = 'private_key.pem'
    public_key_file = 'public_key.pem'
    
    try:
        # Check if files exist
        if not os.path.exists(private_key_file) or not os.path.exists(public_key_file):
            print("RSA key files not found. Please generate keys first using option 3.")
            return False
        
        # Read private key
        with open(private_key_file, 'r') as f:
            private_key = f.read()
        
        # Read public key
        with open(public_key_file, 'r') as f:
            public_key = f.read()
        
        print("\n=== Retrieved RSA Keys ===")
        print("\n--- PRIVATE KEY (Keep this secret!) ---")
        print(private_key)
        print("\n--- PUBLIC KEY (Safe to share) ---")
        print(public_key)
        
        return True
        
    except Exception as e:
        print(f"Error retrieving RSA keys: {e}")
        return False

def import_external_rsa_keys():
    """Import external RSA keys from user input"""
    try:
        print("\n=== Import External RSA Keys ===")
        print("Choose import method:")
        print("1. Paste keys interactively")
        print("2. Use keys from file")
        
        choice = input("Choose method (1-2): ")
        
        if choice == "2":
            return import_keys_from_notes()
        elif choice != "1":
            print("Invalid choice.")
            return False
        
        print("\nInteractive key import:")
        print("1. Paste each key as a single long line, then press Enter")
        print("2. Or paste with proper formatting and type 'DONE' when finished\n")
        
        # Import public key
        print("--- PUBLIC KEY ---")
        print("Paste your public key:")
        public_key_content = ""
        
        try:
            while True:
                line = input()
                
                # Check if it's a DONE command
                if line.strip().upper() == "DONE":
                    break
                
                # Check if this looks like a complete key (long base64 string)
                if len(line.strip()) > 200 and not line.startswith("-----"):
                    public_key_content = line.strip()
                    print("✓ Public key received")
                    break
                
                # Handle regular multi-line input
                public_key_content += line + "\n"
                
                # Check if we have a complete PEM key
                if "-----END" in line:
                    break
                    
        except EOFError:
            if not public_key_content:
                print("❌ No public key provided")
                return False
        
        # Import private key
        print("\n--- PRIVATE KEY ---")
        print("Paste your private key:")
        private_key_content = ""
        
        try:
            while True:
                line = input()
                
                # Check if it's a DONE command
                if line.strip().upper() == "DONE":
                    break
                
                # Check if this looks like a complete key (long base64 string)
                if len(line.strip()) > 500 and not line.startswith("-----"):
                    private_key_content = line.strip()
                    print("✓ Private key received")
                    break
                
                # Handle regular multi-line input
                private_key_content += line + "\n"
                
                # Check if we have a complete PEM key
                if "-----END" in line:
                    break
                    
        except EOFError:
            if not private_key_content:
                print("❌ No private key provided")
                return False
        
        # Format keys properly
        public_key_formatted = format_rsa_key(public_key_content, "PUBLIC")
        private_key_formatted = format_rsa_key(private_key_content, "PRIVATE")
        
        if not public_key_formatted or not private_key_formatted:
            print("❌ Failed to format keys properly.")
            return False
        
        # Validate keys by trying to load them
        try:
            # Test public key
            serialization.load_pem_public_key(public_key_formatted.encode())
            
            # Test private key (might need passphrase)
            try:
                serialization.load_pem_private_key(private_key_formatted.encode(), password=None)
            except (TypeError, ValueError):
                # Key is encrypted, that's okay
                pass
            
            # Save keys to files
            with open('public_key.pem', 'w') as f:
                f.write(public_key_formatted)
            with open('private_key.pem', 'w') as f:
                f.write(private_key_formatted)
            
            print("\n✅ RSA keys imported successfully!")
            print("Keys saved to 'public_key.pem' and 'private_key.pem'")
            
            # Check if private key is encrypted
            if "ENCRYPTED PRIVATE KEY" in private_key_formatted:
                print("🔒 Your private key is encrypted and will require a passphrase to use.")
            else:
                print("⚠️  Your private key is not encrypted.")
            
            return True
            
        except Exception as e:
            print(f"❌ Invalid key format: {e}")
            return False
            
    except Exception as e:
        print(f"Error importing keys: {e}")
        return False

def format_rsa_key(key_content: str, key_type: str) -> str:
    """Format RSA key with proper headers and line breaks"""
    try:
        # Remove existing headers and footers
        content = key_content.replace("-----BEGIN PUBLIC KEY-----", "")
        content = content.replace("-----END PUBLIC KEY-----", "")
        content = content.replace("-----BEGIN PRIVATE KEY-----", "")
        content = content.replace("-----END PRIVATE KEY-----", "")
        content = content.replace("-----BEGIN ENCRYPTED PRIVATE KEY-----", "")
        content = content.replace("-----END ENCRYPTED PRIVATE KEY-----", "")
        
        # Remove all whitespace and newlines
        content = ''.join(content.split())
        
        # Add line breaks every 64 characters
        lines = []
        for i in range(0, len(content), 64):
            lines.append(content[i:i+64])
        
        # Determine headers based on content
        if key_type == "PUBLIC":
            header = "-----BEGIN PUBLIC KEY-----"
            footer = "-----END PUBLIC KEY-----"
        else:
            # Check if it's encrypted by trying to decode and looking for encryption markers
            if "ENCRYPTED" in key_content.upper() or len(content) > 1500:  # Encrypted keys are typically longer
                header = "-----BEGIN ENCRYPTED PRIVATE KEY-----"
                footer = "-----END ENCRYPTED PRIVATE KEY-----"
            else:
                header = "-----BEGIN PRIVATE KEY-----"
                footer = "-----END PRIVATE KEY-----"
        
        # Format with proper headers
        formatted_key = header + "\n" + "\n".join(lines) + "\n" + footer
        return formatted_key
        
    except Exception as e:
        print(f"Error formatting key: {e}")
        return None

def import_keys_from_notes():
    """Import keys from notes.txt file"""
    try:
        # Get all files in current directory
        files = [file for file in pathlib.Path('.').iterdir() if file.is_file()]
        
        if not files:
            print("❌ No files found in current directory.")
            return False
        
        # Display nice file menu
        print("\n=== Available Files ===")
        for i, file in enumerate(files):
            # Add file type indicators
            file_name = file.name
            if file_name.endswith('.txt'):
                icon = "📄"
            elif file_name.endswith('.pem'):
                icon = "🔑"
            elif file_name.endswith('.json'):
                icon = "📊"
            elif file_name.endswith('.py'):
                icon = "🐍"
            else:
                icon = "📁"
            
            print(f"{i:2d}) {icon} {file_name}")
        
        print("\n" + "="*30)
        mychoice = input("Please enter the file number containing RSA keys: ")
        
        if not mychoice.isdigit():
            print("❌ Invalid file number.")
            return False
            
        file_index = int(mychoice)
        if file_index < 0 or file_index >= len(files):
            print("❌ File number out of range.")
            return False
            
        notes_file = str(files[file_index])
        print(f"📖 Selected file: {notes_file}")
        
        if not os.path.exists(notes_file):
            print(f"❌ File {notes_file} not found.")
            return False
        
        
        
        with open(notes_file, 'r') as f:
            content = f.read()
        
        # Extract public key
        public_start = content.find("public key is")
        private_start = content.find("private key")
        
        if public_start == -1 or private_start == -1:
            print("❌ Could not find 'public key is' or 'private key' in notes.txt")
            return False
        
        # Extract public key content
        public_content = content[public_start + len("public key is"):private_start].strip()
        
        # Extract private key content
        paraphrase_start = content.find("paraphrase is")
        if paraphrase_start != -1:
            private_content = content[private_start + len("private key"):paraphrase_start].strip()
        else:
            private_content = content[private_start + len("private key"):].strip()
        
        # Format keys
        public_key_formatted = format_rsa_key(public_content, "PUBLIC")
        private_key_formatted = format_rsa_key(private_content, "PRIVATE")
        
        if not public_key_formatted or not private_key_formatted:
            print("❌ Failed to format keys from notes.txt")
            return False
        
        # Save keys to files
        with open('public_key.pem', 'w') as f:
            f.write(public_key_formatted)
        with open('private_key.pem', 'w') as f:
            f.write(private_key_formatted)
        
        print("\n✅ RSA keys imported from notes.txt successfully!")
        print("Keys saved to 'public_key.pem' and 'private_key.pem'")
        
        # Check if private key is encrypted
        if "ENCRYPTED PRIVATE KEY" in private_key_formatted:
            print("🔒 Your private key is encrypted and will require a passphrase to use.")
        else:
            print("⚠️  Your private key is not encrypted.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing from notes.txt: {e}")
        return False

def encrypt_file_with_fernet(file_path: str) -> tuple:
    """Encrypt a file using Fernet encryption"""
    try:
        # Read file in binary mode
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Encode to base64 for text handling
        file_data_b64 = base64.b64encode(file_data).decode('utf-8')
        
        # Generate key and encrypt
        key = Fernet.generate_key()
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(file_data_b64.encode())
        
        return encrypted_data.decode(), key.decode(), os.path.basename(file_path)
    
    except Exception as e:
        print(f'Error encrypting file: {e}')
        return None, None, None

def decrypt_file_with_fernet(encrypted_data: str, key: str, output_filename: str = None) -> bool:
    """Decrypt a file using Fernet decryption"""
    try:
        # Decrypt the data
        fernet = Fernet(key.encode())
        decrypted_b64 = fernet.decrypt(encrypted_data.encode())
        
        # Decode from base64
        file_data = base64.b64decode(decrypted_b64.decode())
        
        # Generate output filename if not provided
        if not output_filename:
            output_filename = f"decrypted_{int(os.time.time())}.bin"
        
        # Write decrypted file
        with open(output_filename, 'wb') as f:
            f.write(file_data)
        
        print(f"✅ File decrypted and saved as: {output_filename}")
        return True
    
    except Exception as e:
        print(f'Error decrypting file: {e}')
        return False

def encrypt_file_with_rsa(file_path: str, public_key_path: str = 'public_key.pem') -> tuple:
    """Encrypt a file using RSA public key"""
    try:
        # Read file in binary mode
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Check file size - RSA has practical limits
        if len(file_data) > 50000:  # 50KB limit for RSA
            print(f"❌ File is too large ({len(file_data)} bytes) for RSA encryption. Use Fernet encryption for large files.")
            return None, None
        
        # Encode to base64 for text handling
        file_data_b64 = base64.b64encode(file_data).decode('utf-8')
        
        # Use existing RSA encryption function
        print(f"Debug: About to encrypt base64 data of length {len(file_data_b64)}")
        encrypted_result = encrypt_with_rsa_public_key(file_data_b64, public_key_path)
        
        if encrypted_result is None:
            print("❌ RSA encryption returned None")
            return None, None
        
        return encrypted_result, os.path.basename(file_path)
    
    except Exception as e:
        print(f'Error encrypting file with RSA: {e}')
        return None, None

def decrypt_file_with_rsa(encrypted_data: str, output_filename: str = None, private_key_path: str = 'private_key.pem', passphrase: str = None) -> bool:
    """Decrypt a file using RSA private key"""
    try:
        # Decrypt the base64 data
        decrypted_b64 = decrypt_with_rsa_private_key(encrypted_data, private_key_path, passphrase)
        
        if not decrypted_b64:
            return False
        
        # Decode from base64
        file_data = base64.b64decode(decrypted_b64)
        
        # Generate output filename if not provided
        if not output_filename:
            output_filename = f"decrypted_{int(os.time.time())}.bin"
        
        # Write decrypted file
        with open(output_filename, 'wb') as f:
            f.write(file_data)
        
        print(f"✅ File decrypted and saved as: {output_filename}")
        return True
    
    except Exception as e:
        print(f'Error decrypting file with RSA: {e}')
        return False

def show_file_menu(prompt: str) -> str:
    """Show file selection menu and return selected file path"""
    files = [file for file in pathlib.Path('.').iterdir() if file.is_file()]
    
    if not files:
        print("❌ No files found in current directory.")
        return None
    
    print(f"\n=== {prompt} ===")
    for i, file in enumerate(files):
        file_name = file.name
        if file_name.endswith(('.txt', '.md')):
            icon = "📄"
        elif file_name.endswith('.pem'):
            icon = "🔑"
        elif file_name.endswith('.json'):
            icon = "📊"
        elif file_name.endswith('.py'):
            icon = "🐍"
        elif file_name.endswith(('.jpg', '.png', '.gif')):
            icon = "🖼️"
        elif file_name.endswith(('.pdf', '.doc')):
            icon = "📋"
        else:
            icon = "📁"
        
        print(f"{i:2d}) {icon} {file_name}")
    
    print("\n" + "="*30)
    choice = input("Enter file number: ")
    
    if not choice.isdigit():
        print("❌ Invalid file number.")
        return None
    
    file_index = int(choice)
    if file_index < 0 or file_index >= len(files):
        print("❌ File number out of range.")
        return None
    
    return str(files[file_index])

def encrypt_with_rsa_public_key(data: str, public_key_path: str = 'public_key.pem') -> str:
    """Encrypt data using RSA public key"""
    try:
        # Check if public key file exists
        if not os.path.exists(public_key_path):
            print(f"Public key file '{public_key_path}' not found. Please generate RSA keys first.")
            return None
        
        # Load public key
        with open(public_key_path, 'rb') as f:
            public_key = serialization.load_pem_public_key(f.read())
        
        # RSA can only encrypt data smaller than key size, so we'll use chunks
        # For RSA 2048-bit key, max plaintext size is ~245 bytes
        max_chunk_size = 245
        data_bytes = data.encode('utf-8')
        encrypted_chunks = []
        
        # Encrypt in chunks
        for i in range(0, len(data_bytes), max_chunk_size):
            chunk = data_bytes[i:i + max_chunk_size]
            encrypted_chunk = public_key.encrypt(
                chunk,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            encrypted_chunks.append(base64.b64encode(encrypted_chunk).decode('utf-8'))
        
        return '|'.join(encrypted_chunks)  # Join chunks with separator
        
    except Exception as e:
        print(f'Error encrypting with RSA: {e}')
        print(f'Debug info - Data size: {len(data.encode("utf-8"))} bytes')
        return None

def decrypt_with_rsa_private_key(encrypted_data: str, private_key_path: str = 'private_key.pem', passphrase: str = None) -> str:
    """Decrypt data using RSA private key"""
    try:
        # Check if private key file exists
        if not os.path.exists(private_key_path):
            print(f"Private key file '{private_key_path}' not found.")
            return None
        
        # Load private key
        with open(private_key_path, 'rb') as f:
            key_data = f.read()
            
            if passphrase:
                # Try different passphrase variations
                passphrases_to_try = [
                    passphrase,
                    passphrase.strip(),
                    passphrase.replace(' ', ''),
                    passphrase.encode('utf-8'),
                ]
                
                private_key = None
                for pp in passphrases_to_try:
                    try:
                        if isinstance(pp, str):
                            pp = pp.encode('utf-8')
                        private_key = serialization.load_pem_private_key(key_data, password=pp)
                        break
                    except Exception:
                        continue
                
                if private_key is None:
                    print("❌ Could not decrypt private key with provided passphrase.")
                    print("💡 Make sure your passphrase is exactly: 'Jose D. Ibay Jr.'")
                    return None
            else:
                private_key = serialization.load_pem_private_key(key_data, password=None)
        
        # Split encrypted chunks
        encrypted_chunks = encrypted_data.split('|')
        decrypted_chunks = []
        
        # Decrypt each chunk
        for chunk in encrypted_chunks:
            encrypted_bytes = base64.b64decode(chunk.encode('utf-8'))
            decrypted_chunk = private_key.decrypt(
                encrypted_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            decrypted_chunks.append(decrypted_chunk)
        
        # Join all decrypted chunks
        return b''.join(decrypted_chunks).decode('utf-8')
        
    except Exception as e:
        print(f'Error decrypting with RSA: {e}')
        return None

# characcters

def encrypt_data_not_binary(data: str|list) -> dict:
    mydict = {}
    
    if isinstance(data, list):
        # Encrypt each word individually
        for word in data:
            key = Fernet.generate_key()
            fernet = Fernet(key)
            encrypted_word = fernet.encrypt(word.encode())
            mydict[key.decode()] = encrypted_word.decode()
    elif isinstance(data, str|int|float):
        try:
            data = str(data) if not isinstance(data, str) else data
            key = Fernet.generate_key()
            fernet = Fernet(key)
            encrypted_word = fernet.encrypt(data.encode())
            mydict[key.decode()] = encrypted_word.decode()
        except Exception as e:
            print(f'Error encrypting data: {e}')
            return {}
    else:
        print('Unsupported data type for encryption.')
        return {}
    
    write_file('encrypted_data.json', mydict)
    return mydict, key
   
   
    
    #eturn encrypted_data.decode()
    

def decrypt_data_not_binary(orig: str|int|float, key: str) -> str:
    mydict = open_file('encrypted_data.json')
   
    
    
    
    
    
    
    
    
    
   
   
   
   
   
    if isinstance(orig, str|int|float):
        try:
            orig = str(orig) if not isinstance(orig, str) else orig
            if key in mydict:
                encrypted_data = mydict[key]
                fernet = Fernet(key.encode())
                decrypted_data = fernet.decrypt(encrypted_data.encode())
                return decrypted_data.decode()
            else:
                print('Original data does not match the stored data.')
                return ''
        except Exception as e:
            print(f'Error decrypting data: {e}')
            return ''  
                                   
def main():
    print("Hello from masking-program!")
    while True:
        print(""" Choose one of the Options below:
        1. 🔒 Encrypt Data
        2. 🔓 Decrypt Data
        3. 🔑 Generate RSA Key Pair
        4. 📋 Retrieve RSA Keys
        5. 📥 Import External RSA Keys
        6. 🚪 Exit""")  
        option = input("Choose an option (1-6): ")
        if option == '6':
            print("Exiting the program.")
            break
        elif option not in ['1', '2', '3', '4', '5']:
            print("Invalid option. Please choose 1, 2, 3, 4, 5, or 6.")
            continue
        elif option == '1':
            print("\n--- Encryption Options ---")
            print("What would you like to encrypt?")
            print("1. Text Data")
            print("2. File")
            
            data_type = input("Choose option (1-2): ")
            
            if data_type not in ['1', '2']:
                print("Invalid choice. Please select 1 or 2.")
                continue
            
            print("\n--- Encryption Methods ---")
            print("1. Simple Encryption (Fernet)")
            print("2. RSA Public Key Encryption")
            
            encrypt_choice = input("Choose encryption method (1-2): ")
            
            if encrypt_choice not in ['1', '2']:
                print("Invalid choice. Please select 1 or 2.")
                continue
            
            if data_type == '1':
                # Text data encryption
                data_to_encrypt = input("Enter data to encrypt: ")
                print(f'The original data is: [{data_to_encrypt}]')
            else:
                # File encryption
                file_path = show_file_menu("Select File to Encrypt")
                if not file_path:
                    continue
                print(f'📁 Selected file: {file_path}')
            
            if encrypt_choice == '1':
                # Simple Fernet encryption
                if data_type == '1':
                    # Encrypt text data
                    encrypted_result, key = encrypt_data_not_binary(data=data_to_encrypt)
                    print(f'Encrypted data: {encrypted_result}') 
                    print(f'Encryption key: {key} Please save it securely!')
                else:
                    # Encrypt file
                    encrypted_result, key, filename = encrypt_file_with_fernet(file_path)
                    if encrypted_result:
                        print(f'✅ File "{filename}" encrypted successfully!')
                        print(f'Encryption key: {key} Please save it securely!')
                        name, ext = os.path.splitext(filename)
                        while True:
                            save_choice = input("Would you like to save the encryption key to a file? (y/n): ").lower()
                            if not save_choice in ['y', 'n']:
                             
                                print("Invalid choice. Please enter 'y' or 'n'.")
                            elif save_choice == 'y':
                                with open('fernet_encryption_key.txt', 'w') as f:
                                    f.write(filename)
                                    f.write(key)
                                print("💾 Encryption key saved to 'fernet_encryption_key.txt'")
                                break
                            else:
                                break
                        
                        
                        # Save encrypted file with preserved extension
                        name, ext = os.path.splitext(filename)
                        output_file = f"encrypted_{name}{ext if ext else '.txt'}"
                        with open(output_file, 'w') as f:
                            f.write(encrypted_result)
                        print(f'💾 Encrypted file saved as: {output_file}')
                    else:
                        print("❌ Failed to encrypt file.")
                
            elif encrypt_choice == '2':
                # RSA public key encryption
                if data_type == '1':
                    # Encrypt text data
                    encrypted_result = encrypt_with_rsa_public_key(data_to_encrypt)
                    if encrypted_result:
                        print(f'RSA Encrypted data: {encrypted_result}')
                        print("Data encrypted using your RSA public key.")
                        print("Use your RSA private key to decrypt this data.")
                        
                        save_choice = input("Would you like to save the encrypted data to a file? (y/n): ").lower()
                        if save_choice == 'y':
                            with open('rsa_encrypted_data.txt', 'w') as f:
                                f.write(encrypted_result)
                            print("💾 Encrypted data saved to 'rsa_encrypted_data.txt'")
                    else:
                        print("❌ Failed to encrypt with RSA. Make sure you have generated RSA keys first.")
                else:
                    # Encrypt file
                    encrypted_result, filename = encrypt_file_with_rsa(file_path)
                    if encrypted_result:
                        name, ext = os.path.splitext(filename)
                        print(f'✅ File "{filename}" encrypted successfully!')
                        print("Data encrypted using your RSA public key.")
                        print("Use your RSA private key to decrypt this file.")
                        
                        # Save encrypted file with preserved extension
                        output_file = f"{name}_encrypted{ext if ext else '.txt'}"
                        with open(output_file, 'w') as f:
                            f.write(encrypted_result)
                        print(f'💾 Encrypted file saved as: {output_file}')
                    else:
                        print("❌ Failed to encrypt file with RSA.")
            
        elif option == '2':
            print("\n--- Decryption Options ---")
            print("What would you like to decrypt?")
            print("1. Text Data")
            print("2. File")
            
            data_type = input("Choose option (1-2): ")
            
            if data_type not in ['1', '2']:
                print("Invalid choice. Please select 1 or 2.")
                continue
            
            print("\n--- Decryption Methods ---")
            print("1. Simple Decryption (Fernet)")
            print("2. RSA Private Key Decryption")
            
            decrypt_choice = input("Choose decryption method (1-2): ")
            
            if decrypt_choice not in ['1', '2']:
                print("Invalid choice. Please select 1 or 2.")
                continue
            
            if data_type == '1':
                # Text data decryption
                data_to_decrypt = input("Enter data to decrypt: ")
            else:
                # File decryption
                file_path = show_file_menu("Select Encrypted File to Decrypt")
                name, ext = os.path.splitext(file_path)
                if not file_path:
                    continue
                print(f'📁 Selected file: {file_path}')
                
                # Read encrypted data from file
                try:
                    with open(file_path, 'r') as f:
                        data_to_decrypt = f.read().strip()
                    print("✅ Encrypted data loaded from file")
                except Exception as e:
                    print(f"❌ Error reading file: {e}")
                    continue
            
            if decrypt_choice == '1':
                # Simple Fernet decryption
                key = input("Enter the encryption key: ")
                if not data_to_decrypt or not key:
                    print("Both data and key are required for decryption.")
                    continue
                
                if data_type == '1':
                    # Decrypt text data
                    decrypted_result = decrypt_data_not_binary(data_to_decrypt, key)
                    print(f'The decrypted data is [{decrypted_result}]')
                else:
                    # Decrypt file
                    output_filename = input("Enter output filename (or press Enter for auto-generated): ").strip()
                    if not output_filename:
                        output_filename = None
                    
                    success = decrypt_file_with_fernet(data_to_decrypt, key, f'{output_filename}{ext}' )
                    if not success:
                        print("❌ Failed to decrypt file.")
                
            elif decrypt_choice == '2':
                # RSA private key decryption
                if not data_to_decrypt:
                    print("Data is required for decryption.")
                    continue
                
                # Check if private key is encrypted
                passphrase = None
                try:
                    with open('private_key.pem', 'r') as f:
                        key_content = f.read()
                        if "ENCRYPTED PRIVATE KEY" in key_content:
                            passphrase = input("Enter passphrase for private key: ")
                except FileNotFoundError:
                    print("Private key file not found. Generate RSA keys first.")
                    continue
                
                if data_type == '1':
                    # Decrypt text data
                    decrypted_result = decrypt_with_rsa_private_key(data_to_decrypt, passphrase=passphrase)
                    if decrypted_result:
                        print(f'The decrypted data is [{decrypted_result}]')
                    else:
                        print("❌ Failed to decrypt data. Check your private key and passphrase.")
                else:
                    # Decrypt file
                    output_filename = input("Enter output filename (or press Enter for auto-generated): ").strip()
                    if not output_filename:
                        output_filename = None
                    
                    success = decrypt_file_with_rsa(data_to_decrypt, output_filename, passphrase=passphrase)
                    if not success:
                        print("❌ Failed to decrypt file.")
        
        elif option == '3':
            print("Generating RSA Key Pair...")
            
            # Ask for optional passphrase
            use_passphrase = input("Would you like to protect the private key with a passphrase? (y/n): ").lower()
            passphrase = None
            
            if use_passphrase == 'y':
                passphrase = input("Enter passphrase for private key encryption: ")
                if not passphrase.strip():
                    print("Empty passphrase entered. Private key will not be encrypted.")
                    passphrase = None
            
            private_key, public_key, used_passphrase = generate_rsa_key_pair(passphrase)
            
            if private_key and public_key:
                print("\n=== RSA Key Pair Generated Successfully ===")
                if used_passphrase:
                    print("🔒 Private key is encrypted with your passphrase")
                else:
                    print("⚠️  Private key is NOT encrypted")
                
                print("\n--- PRIVATE KEY (Keep this secret!) ---")
                print(private_key)
                print("\n--- PUBLIC KEY (Safe to share) ---")
                print(public_key)
                
                # Option to save keys to files
                save_choice = input("\nWould you like to save the keys to files? (y/n): ").lower()
                if save_choice == 'y':
                    try:
                        with open('private_key.pem', 'w') as f:
                            f.write(private_key)
                        with open('public_key.pem', 'w') as f:
                            f.write(public_key)
                        print("Keys saved to 'private_key.pem' and 'public_key.pem'")
                        if used_passphrase:
                            print("⚠️  Remember your passphrase! You'll need it to use the private key.")
                    except Exception as e:
                        print(f"Error saving keys to files: {e}")
            else:
                print("Failed to generate RSA key pair.")
        
        elif option == '4':
            print("Retrieving saved RSA keys...")
            retrieve_rsa_keys()
        
        elif option == '5':
            print("Importing external RSA keys...")
            import_external_rsa_keys()

def test():   
    x2nd_data_to_encrypt = "Anothugjhg itive Data 4567 example."
    # mylist, mylen = determine_words_from_data(data=x2nd_data_to_encrypt)
    encrypted_result, key = encrypt_data_not_binary(data=x2nd_data_to_encrypt)
    print(f'Test encryption result: {encrypted_result}')
    print(f'Test decrypted data: [{decrypt_data_not_binary(x2nd_data_to_encrypt, key.decode())}]')

    
if __name__ == "__main__":
   main()
   test()